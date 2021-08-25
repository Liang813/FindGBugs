def pattern_match(str1, str2):
    buggy_type = ""
    buggy_count = str1.count('keyword')
    fix_count = str2.count('keyword')
    # 先判断没有大的节点在里面，有大节点的话有很大可能是这个commit提交了很多代码，包括添加了新的方法  Name不算大节点
    big_node = ["Call", ""]
    """
        Important!!!
    """
    # if 大节点 not in str1 and str2
    if buggy_count != fix_count or ('keyword' not in str1 and 'keyword' in str2):
        buggy_type = 'API misuse'
        return buggy_type
    if 'keyword' in str1 and 'keyword' in str2:
        location_buggy = str1.find('keyword')
        location_fix = str2.find('keyword')
        if location_buggy == location_fix:
            buggy_type = 'API misuse'
            return buggy_type
