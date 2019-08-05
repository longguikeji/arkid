'''
funcs about tree
'''
from ldap3 import LEVEL

from executer.utils.operation import list_diff
from executer.LDAP.client import FILTER_ALL


def dn_lrd_walker(conn, dn):
    '''
    后序遍历
    '''
    conn.search(dn, search_scope=LEVEL, search_filter=FILTER_ALL)
    for entry in conn.entries:
        for child_dn in dn_lrd_walker(conn, entry.entry_dn):
            yield child_dn

    yield dn


def get_all_superior_nodes(nodes, include_root=True):
    '''
    给定一批部门，向上追溯至root，返回路过的所有节点
    包括该批部门本身
    :param list nodes: list for oneid_meta.models.Dept/Group
    :rtype set:
    '''
    all_nodes = set()
    for node in nodes:
        while node:
            if not include_root:
                if node.uid == 'root':
                    break
            if node not in all_nodes:
                all_nodes.add(node)
                node = node.parent
            else:
                break
    return all_nodes


def get_node_path(node):
    '''
    节点向上追溯至root的节点路径，包括该节点，包括root，不包括None
    :param oneid_meta.models.Group/Dept node:
    '''
    path = []
    while node:
        path.append(node)
        node = node.parent
    return path


def get_dn_path(dn):
    '''
    节点向上追溯至root的节点路径
    :example: cn=dev,cn=IT,ou=group,dc=example,dc=org
    - > [
        cn=dev,cn=IT,ou=group,dc=example,dc=org,
        cn=IT,ou=group,dc=example,dc=org,
        ou=group,dc=example,dc=org,
        dc=example,dc=org,
        dc=org,
    ]
    '''
    bits = dn.split(',')
    res = []
    for index in range(len(bits)):
        res.append(','.join(bits[-index - 1:]))
    res.reverse()
    return res


def tree_node_diff(node_1, node_2):
    '''
    节点1向上追溯至root的节点路径 减去 节点2的路径
    :return: {1: 节点1特有节点, 0:两者共有节点 , -1:节点2特有节点}
    :rtype: dict
    '''
    return list_diff(*map(get_node_path, [node_1, node_2]))
