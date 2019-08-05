"""
serializers for perm
"""
from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed
from common.django.drf.serializer import DynamicFieldsModelSerializer
from common.django.drf.paginator import DefaultListPaginator
from oneid_meta.models import Perm, DeptPerm, UserPerm, GroupPerm
from siteapi.v1.views.utils import gen_uid


class PermSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for Perm with basic info
    """
    perm_id = serializers.IntegerField(source='id', read_only=True)
    uid = serializers.CharField(read_only=True)

    class Meta:    # pylint: disable=missing-docstring
        model = Perm

        fields = (
            'perm_id',
            'uid',
            'name',
            'remark',
            'scope',
            'action',
            'subject',
        )

    def update(self, instance, validated_data):
        if not instance.editable:
            raise MethodNotAllowed('MODIFY protected perm')
        return super().update(instance, validated_data)

    def create(self, validated_data):
        scope = validated_data.get('scope')
        name = validated_data.get('name')
        prefix = f'app_{scope}_'
        uid = gen_uid(name, cls=Perm, prefix=prefix)
        action = uid.replace(prefix, '', 1)
        return Perm.objects.create(name=name, scope=scope, action=action)


class PermWithOwnerSerializer(PermSerializer):
    '''
    在权限信息基础上增加了部分权限白名单、黑名单对象
    '''

    permit_owners = serializers.SerializerMethodField()
    reject_owners = serializers.SerializerMethodField()

    class Meta:    # pylint: disable=missing-docstring
        model = Perm

        fields = (
            'perm_id',
            'uid',
            'name',
            'remark',
            'scope',
            'action',
            'subject',
            'permit_owners',
            'reject_owners',
        )

    def update(self, instance, validated_data):
        if not instance.editable:
            raise MethodNotAllowed('MODIFY protected perm')
        return super().update(instance, validated_data)

    def create(self, validated_data):
        scope = validated_data.get('scope')
        name = validated_data.get('name')
        prefix = f'app_{scope}_'
        uid = gen_uid(name, cls=Perm, prefix=prefix)
        action = uid.replace(prefix, '', 1)
        return Perm.objects.create(name=name, scope=scope, action=action)

    def get_permit_owners(self, instance):
        '''
        获取权限显式拥有者(所有类型)
        '''
        return self.get_owners(instance, status=1)

    def get_reject_owners(self, instance):
        '''
        获取权限显式拒绝者(所有类型)
        '''
        return self.get_owners(instance, status=-1)

    def get_owners(self, instance, status=1):
        '''
        获取权限显式拥有者
        '''
        request = self.context.get("request")
        kwargs = {'status': status, 'perm': instance}

        owner_subject = request.query_params.get('owner_subject', 'all')
        if owner_subject == 'all':
            owner_perms = list(GroupPerm.valid_objects.filter(**kwargs)) + \
                list(DeptPerm.valid_objects.filter(**kwargs)) + \
                    list(UserPerm.valid_objects.filter(**kwargs))

        elif owner_subject == 'user':
            owner_perms = UserPerm.valid_objects.filter(**kwargs)
        elif owner_subject == 'dept':
            owner_perms = DeptPerm.valid_objects.filter(**kwargs)
        elif owner_subject:
            owner_perms = GroupPerm.valid_objects.filter(**kwargs, owner__top=owner_subject)
        else:
            return None

        paginator = DefaultListPaginator()
        paginator.page_query_param = '_odd_page'    # 让page永远为默认值1
        page = paginator.paginate_queryset(owner_perms, request)

        data = {
            'count': paginator.page.paginator.count,
            'results': [{
                'uid': item.owner_uid,
                'name': item.owner.name,
                'subject': item.owner_subject,
            } for item in page]
        }
        data['has_more'] = data['count'] > len(data['results'])

        return data


class PermResultSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for group & dept Perm with basic info and result
    '''
    perm = PermSerializer()

    class Meta:    # pylint: disable=missing-docstring
        model = DeptPerm    # 兼容 GroupPerm

        fields = (
            'perm',
            'status',
            'value',
            'locked',
        )


class UserPermResultSerializer(PermResultSerializer):
    '''
    Serializer for user Perm with basic info and result
    '''

    class Meta:    # pylint: disable=missing-docstring
        model = UserPerm

        fields = (
            'perm',
            'status',
            'dept_perm_value',
            'group_perm_value',
            'node_perm_value',
            'value',
        )


class UserPermDetailSerializer(UserPermResultSerializer):
    '''
    Serializer for user Perm with basic info, result and perm source
    '''

    source = serializers.SerializerMethodField()

    class Meta:    # pylint: disable=missing-docstring
        model = UserPerm

        fields = (
            'perm',
            'status',
            'dept_perm_value',
            'group_perm_value',
            'node_perm_value',
            'value',
            'source',
        )

    def get_source(self, instance):
        '''
        用户授权来源
        '''
        for node in self.get_sopurce_node(instance):
            yield {
                'name': node.name,
                'uid': node.uid,
                'node_uid': node.node_uid,
                'node_subject': node.node_subject,
            }

    def get_sopurce_node(self, instance):    # pylint: disable=no-self-use
        '''
        用户授权来源节点
        '''
        from oneid_meta.models import DeptMember, GroupMember
        if instance.dept_perm_value:
            nodes = set()
            for dept_member in DeptMember.valid_objects.filter(user=instance.owner):
                for node in dept_member.owner.path_up_to():
                    if DeptPerm.valid_objects.filter(owner=node, perm=instance.perm, status=1).exists():
                        if node.node_uid not in nodes:
                            nodes.add(node.node_uid)
                            yield node
                        break
        if instance.group_perm_value:
            nodes = set()
            for group_member in GroupMember.valid_objects.filter(user=instance.owner):
                for node in group_member.owner.path_up_to():
                    if GroupPerm.valid_objects.filter(owner=node, perm=instance.perm, status=1).exists():
                        if node.node_uid not in nodes:
                            nodes.add(node.node_uid)
                            yield node
                        break


class PermListSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for Perms with basic info
    """

    perms = PermSerializer(many=True)

    class Meta:    # pylint: disable=missing-docstring
        model = Perm

        fields = ('perms', )


class PermResultListSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for group & dept Perms with basic info and result
    '''

    perms = PermResultSerializer(many=True)

    class Meta:    # pylint: disable=missing-docstring
        model = DeptPerm    # 兼容 GroupPerm

        fields = ('perms', )


class UserPermResultListSerializer(PermResultListSerializer):
    '''
    Serializer for user Perms with basic info and result
    '''

    perms = UserPermResultSerializer(many=True)

    class Meta:    # pylint: disable=missing-docstring
        model = UserPerm

        fields = ('perms', )


class OwnerSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for perm owner
    '''

    name = serializers.SerializerMethodField()
    uid = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()

    class Meta:    # pylint: disable=missing-docstring
        model = GroupPerm    # 实际还包括 DeptPerm, UserPerm

        fields = (
            'name',
            'uid',
            'subject',
        )

    def get_uid(self, instance):    # pylint: disable=no-self-use
        return instance.owner_uid

    def get_name(self, instance):    # pylint: disable=no-self-use
        return instance.owner.name

    def get_subject(self, instance):    # pylint: disable=no-self-use
        return instance.owner_subject
