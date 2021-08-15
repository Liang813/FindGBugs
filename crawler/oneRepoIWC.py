# -*- coding: utf-8 -*-
# Get bug information in the form of <issue,commit> for a single library

import random
import time
from time import sleep

import github
from github import Github
import pandas as pd

# Enter your Github token
user_token = [
    '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',
    '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',
    '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'
]

g = Github(user_token[random.randint(0, len(user_token) - 1)])


def get_one_repo(keywords):
    repo = g.get_repo(full_name_or_id=keywords)
    print(repo)
    return repo

# 遍历issues，获取issue与commit信息
def get_relations(repo_issues, repo_name, repo_owner):
    relations = []
    for issue in repo_issues:
        issue_number = issue.number
        issue_title = issue.title
        issue_title.encode('utf-8', 'ignore')
        issue_label = ''
        # if issue.labels is not None:
        #     for label in issue.labels:
        #         issue_label = label.name
        #         issue_label.encode('utf-8', 'ignore')
        issue_html_url = issue.html_url
        issue_html_url.encode('utf-8', 'ignore')
        # 去除掉Pull Request，只要issue
        if 'pull' not in issue_html_url:
            issue_events = issue.get_events()
            commit_ids = []
            for issue_event in issue_events:
                if issue_event.commit_id is not None:
                    commit_id = issue_event.commit_id
                    commit_ids.append(commit_id)

            if len(commit_ids) == 1:
                relation_tup = tuple()
                commit_info = repo.get_commit(commit_id)
                commit_message = commit_info.commit.message

                if '#' or 'issue' in commit_message and 'Merge' not in commit_message:            # 新修改
                    if str(issue_number) in commit_message:
                        # commit_number = re.findall(r"(?<=\#)\d+", commit_message)
                        commit_url = commit_info.html_url
                        relation_tup = (issue_html_url, commit_url)
                        relations.append(relation_tup)
            elif len(commit_ids) > 1:
                relation_tup = tuple()
                for cid in commit_ids:
                    commit_info = repo.get_commit(commit_id)
                    commit_message = commit_info.commit.message
                    if '#' or 'issue' in commit_message and 'Merge' not in commit_message:
                        if str(issue_number) in commit_message:
                            # commit_number = re.findall(r"(?<=\#)\d+", commit_message)
                            commit_url = commit_info.html_url
                            relation_tup = (issue_html_url, commit_url)
                            relations.append(relation_tup)
                    break
            else:
                continue

    print(relations)
    return relations


if __name__ == '__main__':
    # keywords = input('Enter your keywords:')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # 批量爬虫
    kws = ['llmhyy/defects4dl','arogozhnikov/einops']

    for i in kws:
        repo = get_one_repo(i)

        repo_name = repo.name
        repo_name.encode('utf-8', 'ignore')
        print(repo_name)
        repo_owner = repo.owner.login
        repo_owner.encode('utf-8', 'ignore')

        repo_issues = repo.get_issues(state='closed')
        relations_info = []

        try:
            relations_info = get_relations(repo_issues, repo_name, repo_owner)
        except github.GithubException:
            sleep(180)
            g = Github(user_token[random.randint(0, len(user_token) - 1)])
        # keyword = keywords.replace('/', '_')

        if len(relations_info) == 0:
            print("没有找到符合要求的bug！")
        else:
            fileName = 'relations_of_' + 'pytorch' + '.csv'
            data = pd.DataFrame(relations_info)
            try:
                csv_headers = ['issue_url', 'commit_url']
                data.to_csv(fileName, header=csv_headers, index=False,
                                mode='a+', encoding='utf-8-sig')

            except UnicodeEncodeError:
                print('Encode error drop the data')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))