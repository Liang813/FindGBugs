# -*-coding:GBK -*-
import re
import csv
import subprocess


def read_csv():
    """
    ��ȡcsv�ļ�,��[repo_name, commit_id]����ʽ����repo_info_list�б���
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


def get_diff_str():
    """
        ʹ��github�ṩ��diff����ֱ�ӻ�ȡ���޸ĵ��ַ���
    :return:ȫ��bug�޸ĵ��ַ�������
    """
    results = []
    repo_info_list = read_csv()
    for repo_info in repo_info_list:
        repo_name = repo_info[0]
        repo_name_str = ''.join(repo_name)  # repo��
        fix_commit = repo_info[1]
        fix_commit_str = ''.join(fix_commit)  # fix commitId
        cmd1 = "cd .."
        cmd2 = "cd D:\\repo_clone\\" + repo_name_str  # clone�Ŀ�Ĵ�ŵ�ַ
        cmd3 = "git diff " + fix_commit_str + " " + fix_commit_str + "~1:"  # git diff����
        cmd = cmd1 + " && " + cmd2 + " && " + cmd3
        d = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        out = d.stdout.readlines()
        result = ""
        for line in out:
            line_str = str(line, encoding="utf-8")
            result = result + line_str
        results.append(result)
    return results


def get_file_content():
    """
    ��ȡ�޸�ǰ����ļ�����
    :return: nums[]
    """
    repo_info_list = read_csv()
    two_version_infos = []
    for repo_info in repo_info_list:
        # �洢�޸�ǰ�������汾���ļ�����
        now_files_str = ""
        pre_files_str = ""
        # ����洢�޸�ǰ�������汾���ļ�����
        two_version_files = []
        # �ֱ��ȡrepo������commitId
        repo_name = repo_info[0]
        repo_name_str = ''.join(repo_name)  # repo��
        fix_commit = repo_info[1]
        print(fix_commit)        ### ������fix_commitΪ��
        fix_commit_str = ''.join(fix_commit)  # fix commitId
        commit_url = repo_info[2]
        commit_url_str = ''.join(commit_url)  # fix commit url

        # ��ȡ�޸��ļ���
        cmd1 = "cd .."  # cmd1 = "cd ../"
        cmd2 = "cd D:\\repo_clone\\" + repo_name_str         # clone�Ŀ�Ĵ�ŵ�ַ
        print("fix_commit:")
        print(fix_commit_str)
        cmd3 = "git show --pretty="" --name-only " + fix_commit_str  # �鿴ָ��commit���޸��ļ��������û�������
        cmd = cmd1 + " && " + cmd2 + " && " + cmd3
        # ����޸ĵ��ļ���������
        update_files = []
        # ��ȡ�ļ����󣬻�ȡ���ص���Ϣ����
        d = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        out = d.stdout.readlines()
        for line in out:
            line_str = str(line, encoding="utf-8")
            if '.py' in line_str and 'test' not in line_str:
                update_files.append(line_str)
        # ��ȡ�޸��ļ���Ϊ�յ�Bug��Ϣ�����Կ���ȥ���洢��update_files�У�����ֱ���жϣ�Ȼ�����ʱֱ�ӻ�ȡ�ļ���Ϣ
        if not update_files:
            continue
        print("�޸ĵ��ļ���:")
        print(update_files)
        # print("=============================")

        # git show �����ȡ�޸ĵ��ļ�����
        for file_name in update_files:
            cmd4 = "git show " + fix_commit_str+":" + file_name
            cmd5 = "git show " + fix_commit_str + "~1:" + file_name
            cmd_nowC = cmd1 + " && " + cmd2 + " && " + cmd4
            cmd_preC = cmd1 + " && " + cmd2 + " && " + cmd5
            d_now = subprocess.Popen(cmd_nowC, shell=True, stdout=subprocess.PIPE)
            out_now = d_now.stdout.readlines()
            for line_now in out_now:
                line_str_now = str(line_now, encoding="utf-8")
                now_files_str += line_str_now
            d_pre = subprocess.Popen(cmd_preC, shell=True, stdout=subprocess.PIPE)
            out_pre = d_pre.stdout.readlines()
            for line_pre in out_pre:
                line_str_pre = str(line_pre, encoding="utf-8")
                pre_files_str += line_str_pre
        two_version_files = [repo_name_str, fix_commit_str, pre_files_str, now_files_str, commit_url_str]
        two_version_infos.append(two_version_files)

    return two_version_infos
