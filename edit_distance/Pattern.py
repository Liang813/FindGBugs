# -*-coding:GBK -*-
def pattern_match(str1, str2):
    diff_buggy = str1
    diff_fix = str2
    is_api = api_pattern(diff_buggy, diff_fix)
    is_ips = ips_pattern(diff_buggy, diff_fix)
    is_tp = tp_pattern(diff_buggy, diff_fix)
    is_zd = zd_pattern(diff_buggy, diff_fix)
    is_shp = shp_pattern(diff_buggy, diff_fix)
    is_judge = judge_pattern(diff_buggy, diff_fix)
    is_var = var_pattern(diff_buggy, diff_fix)
    result = []
    if is_api is not None:
        result.append(is_api)
    if is_ips is not None:
        result.append(is_ips)
    if is_tp is not None:
        result.append(is_tp)
    if is_zd is not None:
        result.append(is_zd)
    if is_shp is not None:
        result.append(is_shp)
    if is_judge is not None:
        result.append(is_judge)
    if is_var is not None:
        result.append(is_var)
    return result


def api_pattern(str1, str2):
    """
        API misuse类的搜索规则
    """
    buggy_count = str1.count('keyword')
    fix_count = str2.count('keyword')
    # 先判断没有大的节点在里面，有大节点的话有很大可能是这个commit提交了很多代码，包括添加了新的方法  Name不算大节点
    # big_node = ["Call", ""]
    """
        Important!!!
    """
    # if 大节点 not in str1 and str2
    if buggy_count != fix_count or ('keyword' not in str1 and 'keyword' in str2):
        return 'API misuse'
    if 'keyword' in str1 and 'keyword' in str2:
        location_buggy = str1.find('keyword')
        location_fix = str2.find('keyword')
        if location_buggy == location_fix:
            return 'API misuse'


"""
    IPS类的搜索规则
"""


def ips_pattern(str1, str2):
    if ("attr='clip_by_value'" not in str1 and "attr='clip_by_value'" in str2) or (
            'clip_by_value' not in str1 and 'clip_by_value' in str2):
        return 'IPS'
    if ("attr='reduce_mean'" not in str1 and "attr='reduce_mean'" in str2) or (
            'reduce_mean' not in str1 and 'reduce_mean' in str2):
        return 'IPS'
    if (
            "attr='softmax_cross_entropy_with_logits'" not in str1 and "attr='softmax_cross_entropy_with_logits'" in str2) or (
            'softmax_cross_entropy_with_logits' not in str1 and 'softmax_cross_entropy_with_logits' in str2):
        return 'IPS'
    if 'op=Div()' not in str1 and 'op=Div()' in str2:  # 是否需要判断learning rate以区分除零运算
        return 'IPS'
    if ("attr='softmax'" not in str1) and ("attr='nn'" and "attr='softmax'" in str2):
        return 'IPS'
    if ('StandardSca' not in str1 and 'StandardSca' in str2) or (
            'StandardSca' in str1 and 'StandardSca' not in str2) or (
            'MinMaxSca' not in str1 and 'MinMaxSca' in str2) or ('MinMaxSca' in str1 and 'MinMaxSca' not in str2):
        return 'IPS'


"""
    type mismatch类的搜索规则
"""


def tp_pattern(str1, str2):
    if "attr='dtype'" not in str1 and "attr='dtype'" in str2:
        return 'type mismatch'
    if "id='int'" not in str1 and "id='int'" in str2:
        return 'type mismatch'
    if "id='float'" not in str1 and "id='float'" in str2:
        return 'type mismatch'
    if "id='list'" not in str1 and "id='list'" in str2:
        return 'type mismatch'
    if ("attr='eval'" not in str1 and "attr='eval'" in str2) or ('eval' not in str1 and 'eval' in str2):
        return 'type mismatch'


"""
    zero division类的搜索规则
"""


def zd_pattern(str1, str2):
    if "attr='maximum'" not in str1 and "attr='maximum'" in str2:
        return 'zero division'
    if "id='max'" not in str1 and "id='max'" in str2:
        return 'zero division'
    if ("id='torch'" and "attr='clamp_min'" not in str1) and ("id='torch'" and "attr='clamp_min'" in str2):
        return 'zero division'


"""
    shape mismatch类的搜索规则
"""


def shp_pattern(str1, str2):
    if "arg='axis'" not in str1 and "arg='axis'" in str2:
        return 'shape mismatch'
    if "attr='shape'" in str1 and ("tf" and "attr='shape'") in str2:
        return 'shape mismatch'
    if ("attr='squeeze'" not in str1 and "attr='squeeze'" in str2) or (
            "attr='squeeze'" in str1 and "attr='squeeze'" not in str2):
        return 'shape mismatch'


"""
    添加判断类的搜索规则
"""


def judge_pattern(str1, str2):
    if ('ops=[Is()]' and 'NameConstant(value=None)' not in str1) and (
            'ops=[Is()]' and 'NameConstant(value=None)' in str2):
        return 'add judge'


"""
    variable initialization类的搜索规则
"""


def var_pattern(str1, str2):
    if "attr = 'initialize_all_variables'" not in str1 and "attr = 'initialize_all_variables'" in str2:
        return 'variable initialization'
    if "attr = 'initialize_all_variables'" in str1 and ("attr='group'" and "attr='initialize_local_variables'" in str2):
        return 'variable initialization'
