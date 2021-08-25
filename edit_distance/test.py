# -*- coding: gbk -*-
import ast
# from collections import Counter

# c = Counter(a=4, b=2, c=0, d=-2)
# d = Counter(a=3, c=2, b=-2)
# c.subtract(d)
# print(c)
from collections import Counter

import astpretty


def ast_walk(str1):
    """
    广度优先遍历树节点，然后将节点存储到一个数组中返回
    :param str1:
    :return: nums[]
    """
    # 存储树节点的集合
    tree_nodes = []
    for node in ast.walk(ast.parse(str1)):
        tree_nodes.append(type(node).__name__)
    # print(tree_nodes)
    return tree_nodes


def get_node_number(node_list):
    """
    使用python collections自带的Counter函数计算每个节点出现的次数
    :param node_list:
    :return: node_tuple
    """
    cnt = Counter()
    for word in node_list:
        cnt[word] += 1
    node_tuple = cnt
    # print(node_tuple)
    return node_tuple


if __name__ == '__main__':
    # fix前
    str1 = ""
    # fix后
    str2 = "self.val_check_batch = max(1, self.val_check_batch)"
    # 显示原树
    str1_tree = ast.dump(ast.parse(str1))
    str2_tree = ast.dump(ast.parse(str2))
    # ast生成的普通的树的形式
    print(str1_tree)
    print(str2_tree)
    # 分别调用广度优先搜索
    node_list_pre = ast_walk(str1_tree)
    node_list_now = ast_walk(str2_tree)
    # 获取各个节点数量
    node_tuple_pre = get_node_number(node_list_pre)
    print(node_tuple_pre)
    node_tuple_now = get_node_number(node_list_now)
    print(node_tuple_now)
    # 计算相差的节点数量
    node_tuple_now.subtract(node_tuple_pre)
    print("相差的节点数：")
    print(node_tuple_now)

    # 使用astpretty工具，更好的显示AST结构
    # astpretty.pprint(ast.parse(str1))

    # 使用广度优先遍历树，并为每个节点设置一个parent属性，用于寻找节点的父节点
    # for node in ast.walk(ast.parse(str1)):
    #     for child in ast.iter_child_nodes(node):
    #         print(ast.dump(child))
    #         child.parent = node
