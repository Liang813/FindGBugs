# -*-coding:GBK -*-
def pattern_match(str1, str2, str3):

    diff_buggy = str1
    diff_fix = str2
    str_pre_tree = str3
    is_api = api_pattern(diff_buggy, diff_fix)
    is_ips = ips_pattern(diff_buggy, diff_fix, str_pre_tree)
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
    # if len(result) == 0:
    #     if is_api is not None:
    #         result.append(is_api)
    return result


def api_pattern(str1, str2):
    """
        API misuse类的搜索规则
    """
    buggy_count = str1.count('keyword(')
    fix_count = str2.count('keyword(')

    """
        Important!!!
    """

    if buggy_count != fix_count:
        return 'API misuse'
    if 'keyword(' in str1 and 'keyword(' in str2:
        location_buggy = str1.find('keyword(')
        location_fix = str2.find('keyword(')
        if location_buggy != location_fix:
            return 'API misuse'


"""
    IPS类的搜索规则
"""


def ips_pattern(str1, str2, str3):
    str1_clip = str1.count("attr='clip_by_value'")
    str2_clip = str2.count("attr='clip_by_value'")
    if str1_clip != str2_clip:
        return 'IPS'
    str1_reduce = str1.count("attr='reduce_mean'")
    str2_reduce = str2.count("attr='reduce_mean'")
    if str2_reduce != str1_reduce:
        return 'IPS'
    str1_cross = str1.count('cross_entropy_with_logits')
    str2_cross = str2.count('cross_entropy_with_logits')
    if str1_cross != str2_cross:
        return 'IPS'
    if 'op=Div()' not in str1 and 'op=Div()' in str2 and 'learning_rate' in str3:
        return 'IPS'
    if ("attr='softmax'" not in str1) and ("attr='nn'" and "attr='softmax'" in str2):
        return 'IPS'
    str1_softmax = str1.count("attr='softmax'")
    str2_softmax = str2.count("attr='softmax'")
    if str1_softmax != str2_softmax:
        return 'IPS'
    str1_standard = str1.count('StandardSca')
    str2_standard = str2.count('StandardSca')
    str1_minmax = str1.count('MinMaxSca')
    str2_minmax = str2.count('MinMaxSca')
    if str1_standard != str2_standard or str1_minmax != str2_minmax:
        return 'IPS'


"""
    type mismatch类的搜索规则
"""


def tp_pattern(str1, str2):
    if "g='dtyp" not in str1 and "g='dtyp" in str2:    # "arg='dtype'"
        return 'type mismatch'
    # if "id='int'" not in str1 and "id='int'" in str2:
    #     return 'type mismatch'
    str1_float32 = str1.count('float32')
    str2_float32 = str2.count('float32')
    str1_float16 = str1.count('float16')
    str2_float16 = str2.count('float16')
    str1_int32 = str1.count('int32')
    str2_int32 = str2.count('int32')
    str1_int64 = str1.count('int64')
    str2_int64 = str2.count('int64')
    if str1_int32 != str2_int32:
        return 'type mismatch'
    if str1_int64 != str2_int64:
        return 'type mismatch'
    if str1_float32 != str2_float32:
        return 'type mismatch'
    if str1_float16 != str2_float16:
        return 'type mismatch'
    if "Call(func=Name(id='list'" not in str1 and "Call(func=Name(id='list'" in str2:
        return 'type mismatch'
    if "attr='eval', ctx=Load()), args=[], keywords=[])" not in str1 and "attr='eval', ctx=Load()), args=[], keywords=[])" in str2:
        return 'type mismatch'


"""
    zero division类的搜索规则
"""


def zd_pattern(str1, str2):
    if "attr='maximum'" not in str1 and 'Num(' not in str1 and "attr='maximum'" in str2 and 'Num(' in str2:
        return 'zero division'
    if "id='max'" not in str1 and 'Num(' not in str1 and "id='max'" in str2 and 'Num(' in str2:
        return 'zero division'
    if ("id='torch'" and "attr='clamp_min'" not in str1) and ("id='torch'" and "attr='clamp_min'" in str2):
        return 'zero division'


"""
    shape mismatch类的搜索规则
"""


def shp_pattern(str1, str2):
    if "arg='axis'" not in str1 and "arg='axis'" in str2:
        return 'shape mismatch'
    if "attr='shape'" in str1 and "id='tf'" in str2 and "attr='shape'" in str2:
        return 'shape mismatch'
    if ("attr='squeeze'" not in str1 and "attr='squeeze'" in str2) or (
            "attr='squeeze'" in str1 and "attr='squeeze'" not in str2):
        return 'shape mismatch'
    str1_squeeze = str1.count("attr='squeeze'")
    str2_squeeze = str2.count("attr='squeeze'")
    if str1_squeeze != str2_squeeze:
        return 'shape mismatch'


"""
    添加判断类的搜索规则
"""


def judge_pattern(str1, str2):
    if 'ops=[Is()]' not in str1 and 'None' not in str1 and 'ops=[Is()]' in str2 and 'value=None' in str2:
        return 'add judge'


"""
    variable initialization类的搜索规则
"""


def var_pattern(str1, str2):
    if ("attr='initialize_all_variables'" not in str1 and "attr='initialize_all_variables'" in str2) or ('initialize_all_variables' not in str1 and 'initialize_all_variables' in str2):
        return 'variable initialization'
    if (('group' and "attr='initialize_local_variables'" not in str1) and ('group' and "attr='initialize_local_variables'" in str2)) or (('group' and "attr='initialize_local_variables'" not in str2) and ('group' and "attr='initialize_local_variables'" in str1)):
        return 'variable initialization'
