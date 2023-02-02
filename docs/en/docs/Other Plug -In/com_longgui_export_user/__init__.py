import json
from ninja import Field, Query
from typing import List, Optional
from arkid.core import api as core_api
from api.v1.pages.user_manage.user_list import page as user_list_page
from api.v1.pages.user_manage.user_group import page as user_group_list_page
from api.v1.schema.user import UserItemOut, UserListQueryIn
from api.v1.schema.user_group import UserGroupCreateIn
from arkid.core.extension import create_extension_schema
from arkid.core.translation import gettext_default as _
from arkid.core.api import operation
from arkid.core.constants import *
from django.http import HttpResponse
from arkid.core.extension import Extension
from arkid.extension.models import Extension as Extension_obj
from arkid.core.models import UserGroup, User, SystemPermission
from arkid.extension.models import TenantExtension
from arkid.core.event import READ_FILE, dispatch_event, Event, GROUP_ADD_USER
from arkid.core import actions
from io import BytesIO
from .schema import *
from .error import ErrorCode
from django.contrib.auth.hashers import (
    make_password,
)

import csv
import uuid
import time
import xlwt
import xlrd
import requests
import collections

ExportUserConfigSchema = create_extension_schema(
    'ExportUserConfigSchema',
    __file__,
    base_schema=ExportUserConfigSchema
)


class ExportUserExtension(Extension):

    TYPE = "export_user"

    @property
    def type(self):
        return ExportUserExtension.TYPE

    def load(self):
        self.register_settings_schema(ExportUserConfigSchema)
        super().load()
        
        user_export_path = self.register_api('/user_export/', 'GET', self.user_export, tenant_path=True)
        user_import_path = self.register_api('/user_import/', 'POST', self.user_import, tenant_path=True)
        user_template_export_path = self.register_api('/user_template_export/', 'GET', self.user_template_export, tenant_path=True)
        user_list_page.global_action['arr'] = [
            actions.OpenAction(
                path=user_import_path,
                method=actions.FrontActionMethod.POST,
                name=_('Import', '导入'),
            ),
            actions.ExportAction(
                path=user_template_export_path,
                method=actions.FrontActionMethod.GET,
                name=_('Export Template', '导出模板')
            )
        ]
        user_list_page.global_action['export'] = actions.ExportAction(
            path=user_export_path,
            method=actions.FrontActionMethod.GET,
            name=_('Export', '导出')
        )
        user_group_export_path = self.register_api('/user_group_export/', 'GET', self.user_group_export, tenant_path=True)
        user_group_import_path = self.register_api('/user_group_import/', 'POST', self.user_group_import, tenant_path=True)
        user_group_template_export_path = self.register_api('/user_group_template_export/', 'GET', self.user_group_template_export, tenant_path=True)
        user_group_list_page.global_action['arr'] = [
            actions.OpenAction(
                path=user_group_import_path,
                method=actions.FrontActionMethod.POST,
                name=_('Import', '导入'),
            ),
            actions.ExportAction(
                path=user_group_template_export_path,
                method=actions.FrontActionMethod.GET,
                name=_('Export Template', '导出模板')
            )
        ]
        user_group_list_page.global_action['export'] = actions.ExportAction(
            path=user_group_export_path,
            method=actions.FrontActionMethod.GET,
            name=_('Export', '导出')
        )

    def unload(self):
        super().unload()
        user_list_page.global_action.pop('export')
        user_list_page.global_action.pop('arr')
        user_group_list_page.global_action.pop('export')
        user_group_list_page.global_action.pop('arr')

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def user_group_template_export(self, request, tenant_id:str):
        '''
        用户分组模板导出
        '''
        ug_fields = UserGroupCreateIn.__fields__
        result_list = []
        key_list = []
        app = collections.OrderedDict()
        for key,value in ug_fields.items():
            if key == 'parent':
                key = 'parent_id'
            if value.field_info.title:
                # 存在标题
                if hasattr(value.type_, '__fields__') and key != 'parent_id':
                    for field_value in value.type_.__fields__.values():
                        field_title = field_value.field_info.title
                        field_title = key + ':' + field_title
                        key_list.append(field_title)
                    continue
            key_list.append(key)
        for key in key_list:
            app[key] = key
        result_list.append(app)
        # 找到数据
        extension = self.model
        te = TenantExtension.valid_objects.filter(
            tenant_id=tenant_id,
            extension_id=extension.id,
        ).first()
        if te:
            export_format = te.settings.get('export_format','xls')
        else:
            export_format = 'xls'
        if export_format == 'xls':
            response = self.export_excel(result_list, "user_group_template")
        else:
            response = self.export_csv(request, result_list, "user_group_template")
        return response
    
    def get_response(self, tenant, file_url):
        '''
        获取返回值
        '''
        extension = Extension_obj.active_objects.filter(
            type="storage"
        ).first()
        results = dispatch_event(Event(tag=READ_FILE, tenant=tenant, packages=extension.package, data={"url":file_url}))
        for func, (response, extension) in results:
            return response

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def user_import(self, request, tenant_id:str, data: ImportFileSchemaIn):
        '''
        用户导入
        '''
        tenant = request.tenant
        file_url = data.file
        response = self.get_response(tenant, file_url)
        if 'csv' in file_url:
            data_list = self.import_csv(response)
        else:
            data_list = self.import_excel(response)
        old_tenant_users = tenant.users.all()
        old_tenant_ids = []
        for old_tenant_user in old_tenant_users:
            old_tenant_ids.append(old_tenant_user.id)
        exist_users = User.expand_objects.filter(id__in=old_tenant_ids)
        usernames = []
        mobiles = []
        for exist_user in exist_users:
            username = exist_user.get('username', '')
            mobile = exist_user.get('mobile', '')
            if username:
                usernames.append(username)
            if mobile:
                mobiles.append(mobile)
        # 准备请求头
        ul_fields = UserItemOut.__fields__
        head_dict = {}
        for key,value in ul_fields.items():
            if value.field_info.title:
                # 存在标题
                if hasattr(value.type_, '__fields__'):
                    for field_value in value.type_.__fields__.values():
                        field_title = field_value.field_info.title
                        field_title = key + ':' + field_title
                        head_dict[field_title] = {
                            'base_name': value.name,
                            'id': field_value.name
                        }
        # 结束准备请求
        for data_item in data_list:
            username = str(data_item.get('username', '')).replace('.0', '').strip()
            mobile = data_item.get('mobile', '')
            if mobile:
                mobile = str(int(mobile)).strip()
            if username in usernames:
                return self.error(ErrorCode.FIELDS_VALUE_REPEAT, field='username', value=username)
            if mobile in mobiles:
                return self.error(ErrorCode.FIELDS_VALUE_REPEAT, field='mobile', value=mobile)
        for data_item in data_list:
            user_keys = data_item.keys()

            username = str(data_item.pop('username', '')).replace('.0', '').strip() if 'username' in data_item else ''
            nickname = str(data_item.pop('nickname', '')).replace('.0', '').strip() if 'nickname' in data_item else ''
            mobile = str(data_item.pop('mobile', '')).replace('.0', '').strip() if 'mobile' in data_item else ''
            password = str(data_item.pop('password', '')).replace('.0', '').strip() if 'password' in data_item else ''
            email = str(data_item.pop('email', '')).replace('.0', '').strip() if 'email' in data_item else ''
            user = User(tenant=tenant)
            user.username = username
            if mobile:
                user.mobile = mobile
            if password:
                user.password = make_password(password)
            if nickname:
                user.nickname = nickname
            if email:
                user.email = email
            # 扩展字段
            save_dict_value = {}
            for key,value in data_item.items():
                value = str(value).replace('.0', '').strip()
                head_value = head_dict.get(key, None)
                if head_value:
                    if head_value.get('base_name') not in save_dict_value:
                        save_dict_value[head_value.get('base_name')] = {
                            head_value.get('id'): value
                        }
                    else:
                        save_dict_value[head_value.get('base_name')][head_value.get('id')] = value
            user.save()
            for key,value in save_dict_value.items():
                setattr(user,key,value)
            user.save()
            tenant.users.add(user)
            tenant.save()
        return self.success()

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def user_group_import(self, request, tenant_id:str, data: ImportFileSchemaIn):
        '''
        用户分组导入
        '''
        tenant = request.tenant
        file_url = data.file
        response = self.get_response(tenant, file_url)
        if 'csv' in file_url:
            data_list = self.import_csv(response)
        else:
            data_list = self.import_excel(response)
        # 准备请求头
        ul_fields = UserGroupCreateIn.__fields__
        head_dict = {}
        for key,value in ul_fields.items():
            if key == 'parent':
                key = 'parent_id'
            if value.field_info.title:
                # 存在标题
                if hasattr(value.type_, '__fields__') and key != 'parent_id':
                    for field_value in value.type_.__fields__.values():
                        field_title = field_value.field_info.title
                        field_title = key + ':' + field_title
                        head_dict[field_title] = {
                            'base_name': value.name,
                            'id': field_value.name
                        }
        # 结束准备请求
        for data_item in data_list:
            name = str(data_item.get('name', '')).replace('.0', '').strip() if 'name' in data_item else ''
            parent_id = str(data_item.get('parent_id', '')).replace('.0', '').strip() if 'parent_id' in data_item else ''

            user_group = UserGroup()
            user_group.tenant = tenant
            user_group.name = name
            if parent_id:
                user_group.parent_id = parent_id
            # 扩展字段
            save_dict_value = {}
            for key,value in data_item.items():
                value = str(value).replace('.0', '').strip()
                head_value = head_dict.get(key, None)
                if head_value:
                    if head_value.get('base_name') not in save_dict_value:
                        save_dict_value[head_value.get('base_name')] = {
                            head_value.get('id'): value
                        }
                    else:
                        save_dict_value[head_value.get('base_name')][head_value.get('id')] = value
            user_group.save()

            for key,value in save_dict_value.items():
                setattr(user_group,key,value)
            user_group.save()

            systempermission = SystemPermission()
            systempermission.name = user_group.name
            systempermission.code = 'group_{}'.format(uuid.uuid4())
            systempermission.tenant = tenant
            systempermission.category = 'group'
            systempermission.is_system = True
            systempermission.operation_id = ''
            systempermission.describe = {}
            systempermission.save()
        # 分发一个更新事件(此处只需要更新分组权限就可以)
        dispatch_event(Event(tag=GROUP_ADD_USER, tenant=request.tenant, request=request))
        return self.success()

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def user_template_export(self, request, tenant_id:str):
        '''
        用户模板导出
        '''
        ul_fields = UserItemOut.__fields__
        key_list = []
        result_list = []
        app = collections.OrderedDict()
        for key,value in ul_fields.items():
            if value.field_info.title:
                # 存在标题
                if hasattr(value.type_, '__fields__'):
                    if 'password' not in key_list:
                        # 把密码列手动加到导出数据中
                        key_list.append('password')
                    # 头像不支持导入，所以要去掉
                    if 'avatar' in key_list:
                        key_list.remove('avatar')
                    # 用户id不支持导入
                    if 'id' in key_list:
                        key_list.remove('id')
                    for field_value in value.type_.__fields__.values():
                        field_title = field_value.field_info.title
                        field_title = key + ':' + field_title
                        key_list.append(field_title)
                    continue
            key_list.append(key)
        for key in key_list:
            app[key] = key
        result_list.append(app)
        # 找到数据
        extension = self.model
        te = TenantExtension.valid_objects.filter(
            tenant_id=tenant_id,
            extension_id=extension.id,
        ).first()
        if te:
            export_format = te.settings.get('export_format','xls')
        else:
            export_format = 'xls'
        if export_format == 'xls':
            response = self.export_excel(result_list, "user_template")
        else:
            response = self.export_csv(request, result_list, "user_template")
        return response

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def user_group_export(self, request, tenant_id:str):
        '''
        用户分组导出
        '''
        from arkid.core.perm.permission_data import PermissionData
        usergroups = UserGroup.expand_objects.filter(
            tenant_id=tenant_id,
            is_del=False
        )
        extension = self.model
        te = TenantExtension.valid_objects.filter(
            tenant_id=tenant_id,
            extension_id=extension.id,
        ).first()
        if te:
            export_format = te.settings.get('export_format','xls')
        else:
            export_format = 'xls'
        login_user = request.user
        tenant = request.tenant
        pd = PermissionData()
        ug_fields = UserGroupCreateIn.__fields__
        usergroups = pd.get_manage_user_group(login_user, tenant, usergroups)
        # 头数据
        result_list = []
        key_list = {}
        head_data_dict = {}
        app = collections.OrderedDict()
        # app['id'] = 'id'
        # app['name'] = 'name'
        # app['parent_id'] = 'parent_id'
        for key,value in ug_fields.items():
            if export_format == 'xls':
                if value.field_info.title:
                    # 存在标题
                    if key == 'parent':
                        key = 'parent_id'
                    key_list[key] = value.field_info.title
                    if hasattr(value.type_, '__fields__') and key != 'parent_id':
                        head_data_dict[key] = value.type_.__fields__
                else:
                    # 不存在标题
                    key_list[key] = key
            else:
                if value.field_info.title:
                    # 存在标题
                    if key == 'parent':
                        key = 'parent_id'
                    if hasattr(value.type_, '__fields__') and key != 'parent_id':
                        head_data_dict[key] = value.type_.__fields__
                        for field_value in value.type_.__fields__.values():
                            field_title = field_value.field_info.title
                            field_title = key + ':' + field_title
                            key_list[field_title] = field_title
                    else:
                        key_list[key] = value.field_info.title
                else:
                    # 不存在标题
                    key_list[key] = key
        for key,value  in key_list.items():
            app[key] = value
        result_list.append(app)
        # 体数据
        for usergroup in usergroups:
            app = collections.OrderedDict()
            for key in key_list.keys():
                if export_format == 'xls':
                    user_group_value = usergroup.get(key, None)
                    if user_group_value:
                        app[key] = str(user_group_value)
                    else:
                        app[key] = ''
                else:
                    if ':' in key:
                        key_spilit_arr = key.split(':')
                        custom_field = key_spilit_arr[0]
                        custom_name_field = key_spilit_arr[1]
                        usergroup_custom_value = usergroup.get(custom_field, None)
                        head_data_item = head_data_dict.get(custom_field, None)
                        if head_data_item and usergroup_custom_value:
                            for head_key,head_value in head_data_item.items():
                                head_value_title = head_value.field_info.title
                                if head_value_title == custom_name_field:
                                    app[key] = usergroup_custom_value.get(head_key, '')
                                    break
                        else:
                            app[key] = ''
                    else:
                        user_group_value = usergroup.get(key, None)
                        if user_group_value:
                            app[key] = str(user_group_value)
                        else:
                            app[key] = ''
            # app['id'] = str(usergroup.id)
            # app['name'] = str(usergroup.name)
            # if usergroup.parent:
            #     app['parent_id'] = str(usergroup.parent_id)
            # else:
            #     app['parent_id'] = ''
            result_list.append(app)
        # 找到数据
        if export_format == 'xls':
            response = self.export_excel_head(result_list, "user_group", self.get_style(), head_data_dict=head_data_dict)
        else:
            response = self.export_csv(request, result_list, "user_group")
        return response

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def user_export(self, request, tenant_id:str, query_data: UserListQueryIn=Query(...)):
        '''
        用户导出
        '''
        from arkid.core.perm.permission_data import PermissionData
        users = User.expand_objects.filter(tenant=request.tenant, is_del=False).all()
        login_user = request.user
        tenant = request.tenant
        pd = PermissionData()
        users = pd.get_manage_all_user(login_user, tenant, users)
        ul_fields = UserItemOut.__fields__
        # 找到数据
        extension = self.model
        te = TenantExtension.valid_objects.filter(
            tenant_id=tenant_id,
            extension_id=extension.id,
        ).first()
        if te:
            export_format = te.settings.get('export_format','xls')
        else:
            export_format = 'xls'
        # 准备数据
        # value.type_.__fields__
        # 头数据
        key_list = {}
        result_list = []
        head_data_dict = {}
        app = collections.OrderedDict()
        for key,value in ul_fields.items():
            if export_format == 'xls':
                # xls格式
                if value.field_info.title:
                    # 存在标题
                    key_list[key] = value.field_info.title
                    if hasattr(value.type_, '__fields__'):
                        head_data_dict[key] = value.type_.__fields__
                else:
                    # 不存在标题
                    key_list[key] = key
            else:
                # csv格式
                if value.field_info.title:
                    if hasattr(value.type_, '__fields__'):
                        head_data_dict[key] = value.type_.__fields__
                        for field_value in value.type_.__fields__.values():
                            field_title = field_value.field_info.title
                            field_title = key + ':' + field_title
                            key_list[field_title] = field_title
                            # app[field_title] = key_list[field_title]
                    else:
                        key_list[key] = value.field_info.title
                else:
                    key_list[key] = key
            # app[key] = key_list[key]
        for key,value  in key_list.items():
            app[key] = value
        result_list.append(app)
        # 体数据
        for user in users:
            app = collections.OrderedDict()
            for key in key_list.keys():
                if export_format == 'xls':
                    user_value = user.get(key, None)
                    if user_value:
                        app[key] = str(user_value)
                    else:
                        app[key] = ''
                else:
                    if ':' in key:
                        key_spilit_arr = key.split(':')
                        custom_field = key_spilit_arr[0]
                        custom_name_field = key_spilit_arr[1]
                        user_custom_value = user.get(custom_field, None)
                        head_data_item = head_data_dict.get(custom_field, None)
                        if head_data_item and user_custom_value:
                            for head_key,head_value in head_data_item.items():
                                head_value_title = head_value.field_info.title
                                if head_value_title == custom_name_field:
                                    app[key] = user_custom_value.get(head_key, '')
                                    break
                        else:
                            app[key] = ''
                    else:
                        user_value = user.get(key, None)
                        if user_value:
                            app[key] = str(user_value)
                        else:
                            app[key] = ''
            result_list.append(app)
        if export_format == 'xls':
            response = self.export_excel_head(result_list, "user", self.get_style() ,head_data_dict=head_data_dict)
        else:
            response = self.export_csv(request, result_list, "user")
        return response

    def import_excel(self, response):
        # key_url = os.path.join(UPLOAD_DIR, key)
        # data = xlrd.open_workbook(key_url, encoding_override="gb2312")
        data = xlrd.open_workbook(file_contents=response)
        table = data.sheets()[0]
        nrows = table.nrows
        ncols = table.ncols
        colnames = table.row_values(0)
        list = []
        for rownum in range(1, nrows):
            row = table.row_values(rownum)
            if row:
                app = {}
                for i in range(len(colnames)):
                    app[colnames[i]] = row[i]
                list.append(app)
        return list
    
    def import_csv(self, response):
        decoded_content = response.decode('utf-8-sig')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        list_result = []
        keys = []
        for index, row in enumerate(my_list):
            if index == 0:
                keys.extend(row)
            else:
                app = {}
                for index1, value in enumerate(row):
                    key = keys[index1]
                    app[key] = value
                list_result.append(app)
        return list_result

    def export_csv(self, request, list, name):
        # 文件名信息
        ts = int(time.time())
        key_file = '{}_{}.{}'.format(name, ts, 'csv') if name else 'csv_{}.{}'.format(ts, 'csv')
        # 返回信息
        response = HttpResponse(content_type='text/csv')
        response.write("\ufeff")
        response['Content-Disposition'] = 'attachment;filename={}'.format(key_file)
        # 数据信息
        writer = csv.writer(response)

        for index1, i in enumerate(list):
            row = []
            for index2, key in enumerate(i):
                value = i[key]
                row.append(value)
            writer.writerow(row)
        return response

    def export_excel(self, list, name="", style=None):
        # 文件名信息
        ts = int(time.time())
        key_file = '{}_{}.{}'.format(name, ts, 'xls') if name else 'excel_{}.{}'.format(ts, 'xls')
        # 返回信息
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename={}'.format(key_file)
        # 创建一个文件对象
        xls = xlwt.Workbook(encoding='utf8')
        sheet = xls.add_sheet("reserver")
        # 计算列宽
        length_list = [0 for i in list[0]] if list else []
        for index1, i in enumerate(list):
            for index2, key in enumerate(i):
                length = len(i[key]) + (len(i[key].encode('utf-8')) - len(i[key])) / 2 + 1
                if length > length_list[index2]:
                    length_list[index2] = length
        for index, i in enumerate(length_list):
            sheet.col(index).width = int(256 * i)

        if not style:
            style = xlwt.XFStyle()
        for index1, i in enumerate(list):
            for index2, key in enumerate(i):
                value = i[key]
                sheet.write(index1, index2, value, style)
        output = BytesIO()
        xls.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    def export_excel_head(self, list, name="", style=None, head_data_dict=None):
        # 文件名信息
        ts = int(time.time())
        key_file = '{}_{}.{}'.format(name, ts, 'xls') if name else 'excel_{}.{}'.format(ts, 'xls')
        # 返回信息
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename={}'.format(key_file)
        # 创建一个文件对象
        xls = xlwt.Workbook(encoding='utf8')
        sheet = xls.add_sheet("reserver", cell_overwrite_ok=True)
        # 计算列宽
        length_list = [0 for i in list[0]] if list else []
        for index1, i in enumerate(list):
            for index2, key in enumerate(i):
                try:
                    # 如果是json(不要计算字符串长度，改为直接按标题长度算)
                    eval(i[key])
                    length = 0
                except:
                    # 如果不是json正常计算
                    length = len(i[key]) + (len(i[key].encode('utf-8')) - len(i[key])) / 2 + 1
                if length > length_list[index2]:
                    length_list[index2] = length
        for index, i in enumerate(length_list):
            # 防止单元格宽度太多
            width = int(256 * i)
            if width > 10000:
                width = 10000
            sheet.col(index).width = width

        if not style:
            style = xlwt.XFStyle()
        for row, i in enumerate(list):
            for col, key in enumerate(i):
                field = i[key]
                if row == 0:
                    if key in head_data_dict:
                        # 自定义字段
                        field_infos = head_data_dict.get(key, [])
                        # sheet.write(row, col, field, style)
                        sheet.write_merge(0,0,col,col+(len(field_infos)-1),field,style)
                        for index, field_info in enumerate(field_infos.values()):
                            sheet.write(1, col+index, field_info.field_info.title, style)
                    else:
                        # 非自定义字段
                        sheet.write_merge(0,1,col,col,field,style)
                else:
                    if key in head_data_dict:
                        # 自定义字段
                        field_infos = head_data_dict.get(key, [])
                        json_field = {}
                        if field:
                            try:
                                json_field = eval(field)
                            except:
                                pass
                        for index, field_key in enumerate(field_infos.keys()):
                            sheet.write(row+1, col+index, json_field.get(field_key, ''), style)
                    else:
                        # 非自定义字段
                        sheet.write(row+1, col, field, style)
        output = BytesIO()
        xls.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    def get_style(self):
        alignment = xlwt.Alignment()
        # 左右的对其，水平居中 May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER,
        # HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED,
        # HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        # 上下对齐 May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
        alignment.vert = xlwt.Alignment.VERT_CENTER
        style = xlwt.XFStyle()  # 创建一个样式对象
        style.alignment = alignment  # 将格式Alignment对象加入到样式对象
        return style

extension = ExportUserExtension()