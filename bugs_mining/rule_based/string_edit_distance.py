# -*-coding:GBK -*-
import csv

import numpy as np


def string_distance(str1, str2):

    str1l = len(str1)
    str2l = len(str2)
    distance = np.zeros((str1l + 1, str2l + 1))

    for i in range(0, str1l + 1):
        distance[i, 0] = i
    for i in range(0, str2l + 1):
        distance[0, i] = i

    for i in range(1, str1l + 1):
        for j in range(1, str2l + 1):
            if str1[i - 1] == str2[j - 1]:
                cost = 0
            else:
                cost = 1
            distance[i, j] = min(distance[i - 1, j] + 1, distance[i, j - 1] + 1,
                                 distance[i - 1, j - 1] + cost)  # 分别对应删除、插入和替换
    # for i in distance:
    #     print(i)
    return distance[str1l, str2l]


if __name__ == '__main__':
    # 读取API_misuse.csv中的信息
    with open('../bugs_mining/API_misuse.csv', 'r') as data:
        lines = csv.reader(data)
        info = []
        for i in lines:
            info.append(i)
        for i in range(0, len(info)):
            for j in range(i+1, len(info)):
                res = string_distance(info[i][1], info[j][1])
                a = info[i][0]
                b = info[j][0]
                print(a)
                print(b)
                print("编辑距离为：" + str(res))


