"""
计算两个字符串之间的编辑距离

最小编辑距离定义：
     将一个字符串变成另外一个字符串所用的最少操作数，每次只能增加、删除或者替换一个字符。

    例：
    输入：word1为michaelab ， word2 为 michaelxy
    输出：2

    思路：
    dp[i][j] 作为word1转换为word2的最小编辑距离，计算这个矩阵。
    假设word1[i]和word2[j](此处i = j)分别为：michaelab和 michaelxy
    从后面看起，如果两个字符串的最后一个字符相同，那我们就看dis[i-1][j-1]。
    如果b==y, 那么dis[i][j] = dis[i-1][j-1]
    最后一个字符不同，定义三种操作，添加，删除，修改

    添加：
    也就是在michaelab后面添加一个y，那么word1就变成了michaelaby，此时

              dis[i][j] = 1 + dis[i][j-1]；

    上式中，1代表刚刚的添加操作，添加操作后，word1变成michaelaby，word2为michaelxy。dis[i][j-1]代表从word[i]转换成word[j-1]的最小
    Edit Distance，也就是michaelab转换成michaelx的最小Edit Distance，由于两个字符串尾部的y==y，所以只需要将michaelab变成michaelx就
    可以了，而他们之间的最小Edit Distance就是dis[i][j-1]。

    删除：也就是将michaelab后面的b删除，那么word1就变成了michaela，此时

              dis[i][j] = 1 + dis[i-1][j]；

    替换：也就是将michaelab后面的b替换成y，那么word1就变成了michaelay，此时

              dis[i][j] = 1 + dis[i-1][j-1]；

"""

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
    for i in distance:
        print(i)
    return distance[str1l, str2l]


if __name__ == '__main__':
    a = 'lyk'
    b = 'lyk123'
    result = string_distance(a, b)
    print(result)


