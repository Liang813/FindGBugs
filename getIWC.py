# -*- coding: utf-8 -*-
import re
from time import sleep
import pandas as pd
from github import Github
import random

user_token = [
    '60298e09a51074cbf6d482f50ad975dbe0121a0f',
    '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',
    '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',
    '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'
]

g = Github(user_token[random.randint(0, len(user_token) - 1)])

issueIds = []
relations = []

# 通过关键字来查找库,爬取多个相关库
def get_repositories(keywords):
    repositories = g.search_repositories(query=keywords)
    print('get repositories {}'.format(repositories.totalCount))
    return repositories

# 遍历issues
def get_issue_info(repo_issues, repo_name, repo_owner):
    issue_info_list = set()
    for issue in repo_issues:

        # search commits from issue description

        # if(commits.size == 1 && commit.message contains issueId):
        #     relation = <issue_url, commit_url>


        print(issue)
        issue_patch = issue.pull_request.patch_url
        issue_html_url = issue.html_url
        issue_html_url.encode('utf-8', 'ignore')
        comments = issue.get_comments()
        for comment in comments:
            if '#' in comment.body:
                number = re.findall(r"(?<=\#)\d+", comment.body)
                if number not in issueIds and issue_patch is not None:
                    issueIds.append(number)
                    issue_info_list.add(issue_patch)
            break
        print(issueIds)
        print(issue_patch)
    return issue_info_list


if __name__ == '__main__':
    keywords = input('Enter your keywords:')
    repositories = get_repositories(keywords)
    flag = 0
    for repo in repositories:
        issueIds.clear()
        repo_name = repo.name
        repo_star = repo.stargazers_count
        repo_fork = repo.forks_count
        repo_name.encode('utf-8', 'ignore')
        print(repo_name, repo_star, repo_fork)
        repo_owner = repo.owner.login
        repo_owner.encode('utf-8', 'ignore')

        # 获取repo的全部closed状态的issue
        repo_issues = repo.get_issues(state='closed')
        issue_info_list = []
        try:
            issue_info_list = get_issue_info(repo_issues, repo_name, repo_owner)
        except Exception as e:
            g = Github(user_token[random.randint(0, len(user_token) - 1)])


        if len(issue_info_list) == 0:
            continue

        # flag = 1
        fileName = 'issue_info_of_' + keywords + '.csv'
        data = pd.DataFrame(issue_info_list)
        try:
            if flag == 0:
                csv_headers = ['commit_or_patch_url']
                data.to_csv(fileName, header=csv_headers, index=False,
                            mode='a+', encoding='utf-8-sig')

            else:
                data.to_csv(fileName, header=False, index=False,
                            mode='a+', encoding='utf-8-sig')
            flag += 1
        except UnicodeEncodeError:
            print('Encode error drop the data')
