'''
urls of apis
'''
# pylint: disable=invalid-name,line-too-long

from django.conf.urls import url, include
from django.urls import path

from siteapi.v1.views.task import (
    ImportDingAPIView,
    OverrideDingAPIView,
    InitNoahAPIView,
    TaskResultAPIView,
)

from siteapi.v1.views.config import (
    OrgConfigAPIView,
    ConfigAPIView,
    AdminAPIView,
    OrgMetaConfigAPIView,
    MetaConfigAPIView,
    CustomFieldListCreateAPIView,
    CustomFieldDetailAPIView,
    NativeFieldListAPIView,
    NativeFieldDetailAPIView,
    StorageConfigAPIView,
)

from siteapi.v1.views import (
    event as event_views,
    node as node_views,
    migrate as migrate_views,
    log as log_views,
    group as group_views,
    dept as dept_views,
    org as org_views,
    user as user_views,
    app as app_views,
    shortcut as shortcut_views,
    perm as perm_views,
    ucenter as ucenter_views,
    qr as qr_views,
    appgroup as app_group_views,
)

from siteapi.v1.views.statistics import UserStatisticView
urlpatterns = [
    # user
    url(r'^user/$', user_views.UserListCreateAPIView.as_view(), name='user_list'),
    # url(r'^user/isolated/$', user_views.UserIsolatedAPIView.as_view(), name='isolated_user_list'),    # FIX
    url(r'^user/(?P<username>[\w]+)/convert/intra/$',
        user_views.UserExtern2IntraView.as_view(),
        name='user_convert_to_intra'),
    url(r'^user/(?P<username>[\w]+)/convert/extern/$',
        user_views.UserIntra2ExternView.as_view(),
        name='user_convert_to_extern'),
    url(r'^user/(?P<username>[\w]+)/$', user_views.UserDetailAPIView.as_view(), name='user_detail'),
    url(r'^user/(?P<username>[\w]+)/password/$', user_views.UserPasswordAPIView.as_view(), name='user_password'),
    url(r'^user/(?P<username>[\w]+)/dept/$', user_views.UserDeptView.as_view(), name='user_dept'),
    url(r'^user/(?P<username>[\w]+)/group/$', user_views.UserGroupView.as_view(), name='user_group'),
    url(r'^user/(?P<username>[\w]+)/node/$', user_views.UserNodeView.as_view(), name='user_node'),
    url(r'^user/(?P<username>[\w]+)/perm/(?P<perm_uid>[\w|-]+)/$',
        perm_views.UserPermDetailView.as_view(),
        name='user_perm_detail'),
    # node
    # url(r'^node/(?P<uid>[\w|-]+)/list/$', node_views.NodeListAPIView.as_view(), name='node_list'), TODO@saas
    url(r'^node/(?P<uid>[\w|-]+)/$', node_views.NodeDetailAPIView.as_view(), name='node_detail'),
    url(r'^node/(?P<uid>[\w|-]+)/tree/$', node_views.ManagerNodeTreeAPIView.as_view(), name='node_tree'),
    url(r'^node/(?P<uid>[\w|-]+)/node/$', node_views.NodeChildNodeAPIView.as_view(), name='node_child_node'),
    url(r'^node/(?P<uid>[\w|-]+)/user/$', node_views.NodeChildUserAPIView.as_view(), name='node_child_user'),
    # group
    # url(r'^group/$', group_views.GroupListAPIView.as_view(), name='group_list'), TODO@saas
    url(r'^group/(?P<uid>[\w|-]+)/$', group_views.GroupDetailAPIView.as_view(), name='group_detail'),
    # url(r'^group/(?P<uid>[\w|-]+)/list/$', group_views.GroupScopeListAPIView.as_view(), name='group_scope_list'), TODO@saas
    url(r'^group/(?P<uid>[\w|-]+)/tree/$', group_views.ManagerGroupTreeAPIView.as_view(), name='group_tree'),
    url(r'^group/(?P<uid>[\w|-]+)/group/$', group_views.GroupChildGroupAPIView.as_view(), name='group_child_group'),
    url(r'^group/(?P<uid>[\w|-]+)/user/$', group_views.GroupChildUserAPIView.as_view(), name='group_child_user'),
    # app group
    # url(r'^app-group/(?P<uid>[\w|-]+)/app-group/$', app_group_views.AppGroupChildAppGroupAPIView.as_view(), name='app_group_child_app_group'),
    path('app-group/<str:uid>/', app_group_views.AppGroupDetailAPIView.as_view(), name='appgroup_detail'),
    path('app-group/<str:uid>/app-group/',
         app_group_views.AppGroupChildAppGroupAPIView.as_view(),
         name='appgroup_child_appgroup'),
    path('app-group/<str:uid>/app/', app_group_views.AppGroupChildAppAPIView.as_view(), name='appgroup_child_app'),
    path('app-group/<str:uid>/tree/', app_group_views.ManagerAppGroupTreeAPIView.as_view(), name='appgroup_tree'),

    # dept
    # url(r'^dept/$', dept_views.DeptListAPIView.as_view(), name='dept_list'), TODO@saas
    url(r'^dept/(?P<uid>[\w|-]+)/$', dept_views.DeptDetailAPIView.as_view(), name='dept_detail'),
    # url(r'^dept/(?P<uid>[\w|-]+)/list/$', dept_views.DeptScopeListAPIView.as_view(), name='dept_scope_list'), TODO@saas
    url(r'^dept/(?P<uid>[\w|-]+)/tree/$', dept_views.ManagerDeptTreeAPIView.as_view(), name='dept_tree'),
    url(r'^dept/(?P<uid>[\w|-]+)/dept/$', dept_views.DeptChildDeptAPIView.as_view(), name='dept_child_dept'),
    url(r'^dept/(?P<uid>[\w|-]+)/user/$', dept_views.DeptChildUserAPIView.as_view(), name='dept_child_user'),
    # org
    url(r'^ucenter/org/$', org_views.UcenterCurrentOrgAPIView.as_view(), name='ucenter_org'),
    url(r'^org/$', org_views.OrgListCreateAPIView.as_view(), name='org_list'),
    url(r'^org/(?P<oid>[\w|-]+)/$', org_views.OrgDetailAPIView.as_view(), name='org_detail'),
    url(r'^org/(?P<oid>[\w|-]+)/user/$', org_views.OrgUserListUpdateAPIView.as_view(), name='org_user_list'),
    url(r'^org/(?P<oid>[\w|-]+)/user/(?P<username>[\w]+)/$',
        org_views.OrgUserDetailAPIView.as_view(),
        name='org_user_detail'),
    path('org/<uuid:oid>/user/<str:username>/node/',
         org_views.OrgUserNodeListUpdateAPIView.as_view(),
         name='org_user_node_detail'),
    # perm
    url(r'^perm/$', perm_views.PermListCreateAPIView.as_view(), name='perm_list'),
    url(r'^perm/(?P<uid>[\w|-]+)/$', perm_views.PermDetailAPIView.as_view(), name='perm_detail'),
    url(r'^perm/(?P<uid>[\w|-]+)/owner/$', perm_views.PermOwnerAPIView.as_view(), name='perm_owner'),
    url(r'^perm/user/(?P<username>[\w]+)/$', perm_views.UserPermView.as_view(), name='user_perm'),
    url(r'^perm/dept/(?P<uid>[\w|-]+)/$', perm_views.DeptPermView.as_view(), name='dept_perm'),
    url(r'^perm/group/(?P<uid>[\w|-]+)/$', perm_views.GroupPermView.as_view(), name='group_perm'),
    url(r'^perm/node/(?P<uid>[\w|-]+)/$', node_views.NodePermAPIView.as_view(), name='node_perm'),
    # task
    url(r'^task/import/ding/$', ImportDingAPIView.as_view(), name='import_ding'),
    url(r'^task/override/ding/$', OverrideDingAPIView.as_view(), name='override_ding'),
    url(r'^task/init/noah/$', InitNoahAPIView.as_view(), name='init_noah'),
    url(r'^task/(?P<task_id>[\w|-]+)/result/', TaskResultAPIView.as_view(), name='task_result'),
    # auth
    url(r'^auth/token/$', ucenter_views.TokenPermAuthView.as_view(), name='token_perm_auth'),
    url(r'^auth/invitation_key/$', ucenter_views.InvitationKeyAuthView.as_view(), name='invitation_key_auth'),
    url(r'^revoke/token/$', ucenter_views.RevokeTokenView.as_view(), name='revoke_token'),
    # dingding
    url(r'^ding/qr/callback/$', qr_views.DingQrCallbackView.as_view(), name='ding_qr_callback'),
    url(r'^ding/bind/$', qr_views.DingBindAPIView.as_view(), name='ding_bind'),
    url(r'^ding/register/bind/$', qr_views.DingRegisterAndBindView.as_view(), name='ding_register_bind'),
    url(r'^qr/query/user/$', qr_views.QrQueryUserAPIView.as_view(), name='qr_query_user'),
    # alipay
    url(r'^alipay/qr/callback/$', qr_views.AlipayQrCallbackView.as_view(), name='alipay_qr_callback'),
    url(r'^alipay/bind/$', qr_views.AlipayBindAPIView.as_view(), name='alipay_bind'),
    url(r'^alipay/register/bind/$', qr_views.AlipayRegisterAndBindView.as_view(), name='alipay_register_bind'),
    # qq
    url(r'^qq/qr/callback/$', qr_views.QQQrCallbackView.as_view(), name='qq_qr_callback'),
    url(r'^qq/bind/$', qr_views.QQBindAPIView.as_view(), name='qq_bind'),
    url(r'^qq/register/bind/$', qr_views.QQRegisterAndBindView.as_view(), name='qq_register_bind'),
    # work_wechat
    url(r'^work_wechat/qr/callback/$', qr_views.WorkWechatQrCallbackView.as_view(), name='work_wechat_qr_callback'),
    url(r'^work_wechat/bind/$', qr_views.WorkWechatBindAPIView.as_view(), name='work_wechat_bind'),
    url(r'^work_wechat/register/bind/$',
        qr_views.WorkWechatRegisterAndBindView.as_view(),
        name='work_wechat_register_bind'),
    # wechat
    url(r'^wechat/qr/callback/$', qr_views.WechatQrCallbackView.as_view(), name='wechat_qr_callback'),
    url(r'^wechat/bind/$', qr_views.WechatBindAPIView.as_view(), name='wechat_bind'),
    url(r'^wechat/register/bind/$', qr_views.WechatRegisterAndBindView.as_view(), name='wechat_register_bind'),
    # shortcut
    url(r'^slice/$', shortcut_views.ObjSliceAPIView.as_view(), name='shortcut_slice'),
    url(r'^slice/delete/$', shortcut_views.ObjSliceDeleteAPIView.as_view(), name='shortcut_slice_delete'),
    # ucenter
    url(r'^ucenter/sub_account/$', ucenter_views.UcenterSubAccountListView.as_view(), name='ucenter_sub_account_list'),
    url(r'^ucenter/password/$', ucenter_views.SetPasswordAPIView.as_view(), name='ucenter_password'),
    url(r'^ucenter/contact/$', ucenter_views.UserContactAPIView.as_view(), name='update_user_contact'),
    url(r'^ucenter/perm/$', perm_views.UserSelfPermView.as_view(), name='user_self_perm'),
    url(r'^ucenter/login/$', ucenter_views.UserLoginAPIView.as_view(), name='user_login'),
    url(r'^ucenter/register/$', ucenter_views.UserRegisterAPIView.as_view(), name='user_register'),
    url(r'^ucenter/ding/login/$', ucenter_views.DingLoginAPIView.as_view(), name='ding_login'),
    url(r'^ucenter/profile/$', ucenter_views.UcenterProfileAPIView.as_view(), name='ucenter_profile'),
    url(r'^ucenter/org/(?P<oid>[\w|-]+)/profile/$',
        ucenter_views.UcenterOrgProfileAPIView.as_view(),
        name='ucenter_org_profile'),
    url(r'^ucenter/mobile/$', ucenter_views.UcenterMobileAPIView.as_view(), name='ucenter_mobile'),
    url(r'^ucenter/profile/invited/$',
        ucenter_views.UcenterProfileInvitedAPIView.as_view(),
        name='ucenter_profile_invited'),
    # ucenter node
    url(r'^ucenter/node/(?P<uid>[\w|-]+)/$', node_views.UcenterNodeDetailAPIView.as_view(), name='ucenter_node_detail'),
    url(r'^ucenter/node/(?P<uid>[\w|-]+)/tree/$', node_views.UcenterNodeTreeAPIView.as_view(),
        name='ucenter_node_tree'),

    # ucenter app
    url(r'^ucenter/apps/$', app_views.UcenterAPPListAPIView.as_view(), name='ucenter_app_list'),
    # ucenter user
    url(r'^ucenter/user/(?P<username>[\w]+)/$',
        user_views.UcenterUserDetailAPIView.as_view(),
        name='ucenter_user_detail'),
    # service
    url(r'^service/', include(('infrastructure.urls', 'infrastructure'), namespace='infra')),
    # config
    url(r'^config/$', ConfigAPIView.as_view(), name='config'),
    url(r'^org/(?P<oid>[\w|-]+)/config/$', OrgConfigAPIView.as_view(), name='org_config'),
    url(r'^config/admin/$', AdminAPIView.as_view(), name='alter_admin'),
    url(r'^config/storage/$', StorageConfigAPIView.as_view(), name='storage_config'),
    url(r'^org/(?P<oid>[\w|-]+)/config/custom/field/(?P<field_subject>[a-z_]+)/$',
        CustomFieldListCreateAPIView.as_view(),
        name='custom_field_list'),
    url(r'^org/(?P<oid>[\w|-]+)/config/custom/field/(?P<field_subject>[a-z_]+)/(?P<uuid>[\w]+)/$',
        CustomFieldDetailAPIView.as_view(),
        name='custom_field_detail'),
    url(r'^config/native/field/(?P<field_subject>[a-z_]+)/$',
        NativeFieldListAPIView.as_view(),
        name='native_field_list'),
    url(r'^config/native/field/(?P<field_subject>[a-z_]+)/(?P<uuid>[\w]+)/$',
        NativeFieldDetailAPIView.as_view(),
        name='native_field_detail'),

    # log
    url(r'^log/$', log_views.LogListAPIView.as_view(), name='log_list_all'),
    url(r'^org/(?P<oid>[\w|-]+)/log/$', log_views.OrgLogListAPIView.as_view(), name='log_list'),
    url(r'^log/(?P<uuid>[\w|-]+)', log_views.LogDetailAPIView.as_view(), name='log_detail'),

    # meta
    url(r'^meta/$', MetaConfigAPIView.as_view(), name='meta'),
    url(r'^meta/log/$', log_views.MetaLogAPIView.as_view(), name='meta_log'),
    url(r'^meta/perm/$', perm_views.MetaPermAPIView.as_view(), name='meta_perm'),
    url(r'^org/(?P<oid>[\w|-]+)/meta/$', OrgMetaConfigAPIView.as_view(), name='meta_org'),
    url(r'^org/(?P<oid>[\w|-]+)/meta/node/$', node_views.MetaNodeAPIView.as_view(), name='meta_node'),
    url(r'^org/(?P<oid>[\w|-]+)/meta/perm/$', perm_views.MetaOrgPermAPIView.as_view(), name='meta_org_perm'),

    # app
    url(r'^org/(?P<oid>[\w|-]+)/app/$', app_views.APPListCreateAPIView.as_view(), name='app_list'),
    url(r'^org/(?P<oid>[\w|-]+)/app/(?P<uid>[\w|-]+)/$', app_views.APPDetailAPIView.as_view(), name='app_detail'),
    url(r'^org/(?P<oid>[\w|-]+)/app/(?P<uid>[\w|-]+)/oauth/$',
        app_views.APPOAuthRegisterAPIView.as_view(),
        name='app_register_oauth'),

    # migrate
    url(r'^migration/user/csv/export/$', migrate_views.UserCSVExportView.as_view(), name='export_user'),
    # url(r'^migration/user/csv/import/$', migrate_views.UserCSVImportView.as_view(), name='import_user'),

    # events
    url(r'^invitation/user/(?P<username>[\w]+)/$', event_views.InviteUserCreateAPIView.as_view(), name='invite_user'),
    url(r'^org/(?P<oid>[\w|-]+)/invitation/$', org_views.OrgInvitationLinkAPIView.as_view(), name='org_invite_link'),
    url(r'^org/(?P<oid>[\w|-]+)/invitation/(?P<key>[\w|-]+)/$',
        org_views.OrgInvitationLinkDetailAPIView.as_view(),
        name='org_invite_link_detail'),
    # statistics
    url(r'^statistics/user_statistic/$', UserStatisticView.as_view(), name='user_statistic'),
]
