'''
serialzier mixin for node
'''

from ....oneid_meta.models import Dept, Group


class NodeSerialzierMixin():
    '''
    node serializer 部分公用功能
    '''

    node_type = ''

    @property
    def node_prefix(self):
        '''
        形如 `g_`
        '''
        return self.node_cls.NODE_PREFIX

    @property
    def node_type_plural(self):
        '''
        形如 `depts`
        '''
        return self.node_type + 's'

    @property
    def node_cls(self):
        '''
        Dept or Group
        '''
        if self.node_type == 'dept':
            return Dept
        if self.node_type == 'group':
            return Group
        raise ValueError("node type must be one of `dept` or `group`")

    def flat_tree(self, data=None):
        '''
        将树状结构以列表输出
        '''
        if data is None:
            data = self.data

        nodes = data.pop(self.children_name, [])
        yield data['info']
        for node in nodes:
            flat_tree_generator = self.flat_tree(node)
            try:
                this = next(flat_tree_generator)
            except StopIteration:
                return
            this['parent_uid'] = data['info']['uid']
            this['parent_node_uid'] = self.node_prefix + data['info']['uid']
            yield this

            for sub_node in flat_tree_generator:
                sub_node['parent_uid'] = node['info']['uid']
                sub_node['parent_node_uid'] = self.node_prefix + node['info']['uid']
                yield sub_node

    def aggregate_headcount(self, data):
        '''
        :params dict data:
        {
            "depts": [$self]
            "info": {},
            "users": [{"user_id": 1, "username": "a"}]
        }
        这里按user_id统计
        TODO: implent by to_present...
        '''
        users = set(user['user_id'] for user in data['users'])
        for sub_data in data[self.children_name]:
            users = users | self.aggregate_headcount(sub_data)
        data['headcount'] = len(users)
        return users

    def trim_visible_tree(self, node=None):
        '''
        根据是否可见对结构进行裁剪
        '''
        if node is None:
            node = self.data
        visible = node.pop('visible')
        node[self.children_name] = [self.trim_visible_tree(sub_node) for sub_node in node[self.children_name]]
        node[self.children_name] = [sub_node for sub_node in node[self.children_name] if sub_node is not None]
        if visible:
            return node

        if node[self.children_name]:
            if self.context.get('user_required', False):
                node['users'] = []
            return node

        return None
