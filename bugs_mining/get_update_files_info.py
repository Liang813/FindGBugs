# -*-coding:GBK -*-
import re
import csv
import subprocess


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


def get_diff_str(repo_name_str, fix_commit_str, commit_url_str):
    """
        使用github提供的git diff方法直接获取到两个commit之间修改的字符串
    :return: 修改的字符串str
    """

    cmd1 = "cd .."
    cmd2 = "cd D:\\repo_clone\\" + repo_name_str  # clone的库的存放地址
    cmd3 = "git diff " + fix_commit_str + " " + fix_commit_str + "~1:"  # git diff命令
    cmd = cmd1 + " && " + cmd2 + " && " + cmd3
    d = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out = d.stdout.readlines()
    diff_str = ""
    # 对diff的结果进行预处理，去除没有修改的语句，只获取+或-后面的语句
    for line in out:
        line_str = str(line, encoding="utf-8")
        if line_str.startswith("-"):
            diff_str = diff_str + line_str
        if line_str.startswith("+"):
            diff_str = diff_str + line_str
    return diff_str


def get_file_content(repo_name_str, fix_commit_str, commit_url_str):
    """
    获取修改前后的文件内容
    :return: nums[]
    """
    # 存储修改前后两个版本的文件内容
    now_files_str = ""
    pre_files_str = ""
    # 获取修改文件名
    cmd1 = "cd .."  # cmd1 = "cd ../"
    cmd2 = "cd D:\\repo_clone\\" + repo_name_str         # clone的库的存放地址
    print("fix_commit:")
    print(fix_commit_str)
    cmd3 = "git show --pretty="" --name-only " + fix_commit_str  # 查看指定commit的修改文件，面向用户的命令
    cmd = cmd1 + " && " + cmd2 + " && " + cmd3
    # 存放修改的文件名的数组
    update_files = []
    # 读取文件对象，获取返回的信息内容
    d = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out = d.stdout.readlines()
    for line in out:
        line_str = str(line, encoding="utf-8")
        if '.py' in line_str and 'test' not in line_str:
            update_files.append(line_str)
    # 获取修改文件不为空的Bug信息，可以考虑去掉存储在update_files中，上面直接判断，然后遍历时直接获取文件信息
    if not update_files:
        print("没有.py结尾的修改文件！")
    print("修改的文件名:")
    print(update_files)

    # git show 命令获取修改的文件内容
    for file_name in update_files:
        cmd4 = "git show " + fix_commit_str+":" + file_name
        cmd5 = "git show " + fix_commit_str + "~1:" + file_name
        cmd_nowC = cmd1 + " && " + cmd2 + " && " + cmd4
        cmd_preC = cmd1 + " && " + cmd2 + " && " + cmd5
        d_now = subprocess.Popen(cmd_nowC, shell=True, stdout=subprocess.PIPE)
        out_now = d_now.stdout.readlines()
        for line_now in out_now:
            line_str_now = str(line_now, encoding="utf-8")
            # 简单的过滤掉#注释
            if '#' not in line_str_now:
                now_files_str += line_str_now
        d_pre = subprocess.Popen(cmd_preC, shell=True, stdout=subprocess.PIPE)
        out_pre = d_pre.stdout.readlines()
        for line_pre in out_pre:
            line_str_pre = str(line_pre, encoding="utf-8")
            if '#' not in line_str_pre:
                pre_files_str += line_str_pre
    two_version_files = [repo_name_str, fix_commit_str, pre_files_str, now_files_str, commit_url_str]

    return two_version_files

