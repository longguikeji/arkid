'''
对象之间常见的运算
'''


def list_diff(list_a, list_b):
    '''
    列表差异分析。
    :return: {1: 前者特有, 0:两种共有, -1:后者特有}
    '''
    set_a = set(list_a)
    set_b = set(list_b)
    return {
        '>': list(set_a - set_b),
        '=': list(set_a & set_b),
        '<': list(set_b - set_a),
    }
