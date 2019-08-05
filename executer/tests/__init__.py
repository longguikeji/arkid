'''
tests for executer
'''

DEPT_DATA = {
    'dept_id': 1,
    'uid': 'dev',
    'name': '开发',
    'remark': '.',
}
PARENT_DEPT_DATA = {
    'dept_id': 2,
    'uid': 'IT',
    'name': 'IT',
    'remark': '.',
}

CHILD_DEPT_1_DATA = {
    'dept_id': 3,
    'uid': 'fe',
    'name': '前端',
    'remark': '.',
}

CHILD_DEPT_2_DATA = {
    'dept_id': 4,
    'uid': 'be',
    'name': '后端',
    'remark': '.',
}

DEPT_2_DATA = {
    'dept_id': 5,
    'uid': 'tmp',
    'name': '临时',
    'remark': '.',
}

GROUP_DATA = {
    'group_id': 1,
    'uid': 'supervisor',
    'name': '监理',
    'remark': '.',
    'accept_user': True,
}
PARENT_GROUP_DATA = {
    'group_id': 2,
    'uid': 'manager',
    'name': '管理',
    'remark': '.',
    'accept_user': True,
}
