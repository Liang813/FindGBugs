
import re
import os
import csv


def read_csv():
    """
    读取csv文件,以[repo_name, commit_id]的形式存入repo_info_list列表中
    :return: nums[]
    """
    with open('../bugs_crawler/relations_of_pytorch.csv', 'r') as data:
        lines = csv.reader(data)
        repo_info_list = []
        for line in lines:
            if 'pull' in line[1]:
                repo_name = re.findall(".*com/(.*)/pull.*", line[1])
                commit_id = re.findall(r"(?<=commits/).+", line[1])
            else:
                repo_name = re.findall(".*com/(.*)/commit.*", line[1])
                commit_id = re.findall(r"(?<=commit/).+", line[1])
            repo_name_sha = [repo_name, commit_id, line[1]]
            repo_info_list.append(repo_name_sha)
    return repo_info_list


def clone_repo(repo_name):
    """
    clone repo
    :param repo_name:
    :return:
    """
    # clone repo到D盘repo_clone目录下
    cmd = 'git clone git://github.com/' + repo_name + '.git' + ' D:\\repo_clone\\' + repo_name
    # 读取文件对象，获取返回的信息内容
    d = os.popen(cmd)
    f = d.read()
    print(f)
    d.close()
    return f


if __name__ == '__main__':
    repo_info_list = read_csv()
    clone_ing_repo = '123456'    # 正在clone的项目
    for repo_info in repo_info_list:
        repo_name = repo_info[0]
        repo_name_str = ''.join(repo_name)  # 将list列表的第一个元素转为字符串
        if repo_name_str.__eq__(clone_ing_repo):
            continue
        clone_ing_repo = repo_name_str
        clone_repo(repo_name_str)
        print(repo_name_str)


