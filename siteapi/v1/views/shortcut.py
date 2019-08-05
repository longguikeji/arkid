'''
views as shortcut
'''

from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from oneid.permissions import IsManagerUser, IsAdminUser
from oneid_meta.models import User, APP
from oneid_meta.models.mixin import TreeNode as Node
from siteapi.v1.serializers.user import UserSerializer
from siteapi.v1.serializers.app import APPSerializer
from executer.core import CLI


class ObjSliceAPIView(APIView):
    '''
    按指定类型的唯一标识 返回节点数据 [GET], [POST]
    '''
    permission_classes = [IsAuthenticated & (IsManagerUser | IsAdminUser)]

    def post(self, request):
        '''
        [POST]
        '''
        data = request.data
        return Response(self.retrieve(request, data))

    def get(self, request):
        data = dict(request.query_params)
        return Response(self.retrieve(request, data))

    def retrieve(self, request, data):
        '''
        获取各类型对象
        '''
        res = {}

        node_uids = data.get('node_uids', [])

        res['nodes'] = self.retrieve_nodes(request, node_uids)

        user_uids = data.get('user_uids', [])
        res['users'] = self.retrieve_users(request, user_uids)

        app_uids = data.get('app_uids', [])
        res['apps'] = self.retrieve_apps(request, app_uids)

        return res

    @staticmethod
    def retrieve_nodes(request, uids):
        '''
        获取节点
        '''
        res = []
        for uid in uids:
            node, _ = Node.retrieve_node(uid)
            if not node or not node.is_visible_to_manager(request.user):
                raise ValidationError({'node_uids': [f'{uid} not found']})
            res.append(node.detail_serializer.data)
        return res

    @staticmethod
    def retrieve_users(request, uids):
        '''
        获取用户
        '''
        res = []
        for uid in uids:
            user = User.valid_objects.filter(username=uid).first()
            if not user or not user.is_visible_to_manager(request.user):
                raise ValidationError({'user_uids': [f'{uid} not found']})
            res.append(UserSerializer(user).data)
        return res

    @staticmethod
    def retrieve_apps(request, uids):
        '''
        获取应用
        '''
        res = []
        for uid in uids:
            app = APP.valid_objects.filter(uid=uid).first()
            if not app or not app.is_visible_to_manager(request.user):
                raise ValidationError({'app_uids': [f'{uid} not found']})
            res.append(APPSerializer(app).data)
        return res


class ObjSliceDeleteAPIView(APIView):
    '''
    按指定类型的唯一标识 批量删除数据
    '''
    permission_classes = [IsAuthenticated & (IsManagerUser | IsAdminUser)]

    def post(self, request):    # pylint: disable=no-self-use
        '''
        批量删除数据
        '''
        users = set()
        user_uids = request.data.get('user_uids', [])
        for user_uid in user_uids:
            user = User.valid_objects.filter(username=user_uid).first()
            if not user or not user.under_manage(request.user):
                raise ValidationError({'user_uids': [f'{user_uid} not found']})
            users.add(user)

        cli = CLI()
        cli.delete_users(users)
        return Response({'user_uids': user_uids})
