# -*-coding:GBK -*-
# 获取代码片段
import re
import csv
import subprocess


def get_csv():
    """
    读取csv文件,以[repo_name, commit_id]的形式存入repo_info_list列表中
    :return: arr[]
    """
    with open('../general_bugs.csv', 'r') as data:
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
            print(repo_info_list)
    return repo_info_list


def get_diff_str(repo_name_str, fix_commit_str):
    """
        使用github提供的git diff方法直接获取到两个commit之间修改的代码片段
    :return: 修改的字符串str
    """

    cmd1 = "cd .."
    cmd2 = "cd D:\\repo_clone\\" + repo_name_str  # clone的库的存放地址
    cmd3 = "git diff " + fix_commit_str + "~1 " + fix_commit_str  # git diff命令
    cmd = cmd1 + " && " + cmd2 + " && " + cmd3
    d = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out = d.stdout.readlines()
    code_snippets = []
    code_snippet = ""
    # 获取字符串形式的代码片段，若不需要字符串形式，使用out即可。
    for line in out:
        line_str = str(line, encoding="utf-8")
        code_snippet = code_snippet + line_str
    code_snippets.append(code_snippet)
    print(code_snippets)
    return code_snippets


# 将代码片段输出到文件中
# import os
#
# filepath = os.getcwd()


# def MakeFile(file_name):
#     temp_path = filepath + file_name
#     file = open(file_name, 'w')
#     file.write('def print_success():')
#     file.write('    print "sucesss"')
#     file.close()
#     print('Execution completed.')


if __name__ == '__main__':
    lists = get_csv()
    for list in lists:
        get_diff_str(str(list[0]), str(list[1]))

    # MakeFile('code_snippet/catalyst.py')

    # 接下来编码代码片段，获取代码片段的向量化表示
