'''
views for data migrate
'''
import csv
import datetime
import io

from django.http import HttpResponse
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

from ....executer.core import CLI
from ....oneid_meta.models import User
from ....oneid_meta.models.mixin import TreeNode
from ....oneid.permissions import IsAdminUser, IsManagerUser
from ....siteapi.v1.serializers.migrate import UserCSVSerializer


class UserCSVExportView(APIView):
    '''
    以csv形式导出指定用户基本信息 [POST]
    '''

    serializer_class = UserCSVSerializer

    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]

    def get_queryset(self):
        '''
        return users
        '''
        user_uids = self.request.data.get('user_uids', [])
        for user_uid in user_uids:
            user = User.valid_objects.filter(username=user_uid).first()
            if not user:
                raise NotFound
            yield user

    def get_data(self):
        '''
        return users data
        '''
        for user in self.get_queryset():
            yield self.serializer_class(user).data

    def post(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        导出
        '''
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, self.serializer_class.Meta.fields)
        writer.writeheader()
        writer.writerows(self.get_data())
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users-{}.csv"'.format(
            datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        return response


class UserCSVImportView(APIView):
    '''
    从csv导入用户至指定部门或组 [POST]
    '''

    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]

    serializer_class = UserCSVSerializer

    @transaction.atomic()
    def post(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        导入
        '''
        users_file = request.FILES.get('users', None)
        if not users_file:
            raise ValidationError({'users': ["this field is required"]})

        node_uid = request.data.get('node_uid', '')

        if node_uid:
            node, _ = TreeNode.retrieve_node(node_uid)
            if not node:
                raise NotFound

        res = self.core_post(users_file, node_uid=node_uid)

        return Response(res)

    @staticmethod
    def core_post(users_file, node_uid):
        '''
        creat or update users
        '''
        cli = CLI()

        reader = csv.DictReader(io.StringIO(users_file.read().decode('utf-8')))
        res = []
        users = []
        for index, row in enumerate(reader):
            username = row.get('username')
            user = User.valid_objects.filter(username=username).first()

            try:
                if user:
                    cli.update_user(user, row)
                else:
                    user = cli.create_user(row)
            except ValidationError as exc:
                raise ValidationError({index + 1: exc.detail})

            users.append(user)    # 重复导入的后果可以接受，故不处理
            res.append(UserCSVSerializer(user).data)

        if node_uid:
            node, node_subject = TreeNode.retrieve_node(node_uid)
            if node_subject == 'dept':
                cli.add_users_to_dept(users, node)
            elif node_subject == 'group':
                cli.add_users_to_group(users, node)
            else:
                raise ValueError

        return res
