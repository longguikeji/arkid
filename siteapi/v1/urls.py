'''
urls of apis
'''
# pylint: disable=invalid-name

from django.conf.urls import url, include
from django.urls import path

from siteapi.v1.views.task import (
    ImportDingAPIView,
    OverrideDingAPIView,
    InitNoahAPIView,
    TaskResultAPIView,
)

from siteapi.v1.views.config import (
    ConfigAPIView,
    AdminAPIView,
    MetaConfigAPIView,
    CustomFieldListCreateAPIView,
    CustomFieldDetailAPIView,
    NativeFieldListAPIView,
    NativeFieldDetailAPIView,
    StorageConfigAPIView,
    I18NMobileListCreateAPIView,
    I18NMobileDetailAPIView,
)

from siteapi.v1.views import (event as event_views, node as node_views, migrate as migrate_views, log as log_views,
                              group as group_views, dept as dept_views, user as user_views, app as app_views, shortcut
                              as shortcut_views, perm as perm_views, ucenter as ucenter_views, qr as qr_views, advance
                              as advance_views, third_party as third_party_views)

from siteapi.v1.views.statistics import UserStatisticView

urlpatterns = [
    # user
    url(r'^user/$', user_views.UserListCreateAPIView.as_view(), name='user_list'),
    url(r'^user/isolated/$', user_views.UserIsolatedAPIView.as_view(), name='isolated_user_list'),    # FIX
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
    url(r'^user/(?P<username>[\w]+)/perm/$', perm_views.UserPermListView.as_view(), name='user_perm_list'),
    url(r'^user/(?P<username>[\w]+)/perm/(?P<perm_uid>[\w|-]+)/$',
        perm_views.UserPermDetailView.as_view(),
        name='user_perm_detail'),
    url(r'^user/(?P<username>[\w]+)/perm/(?P<perm_uid>[\w|-]+)/result/$',
        perm_views.UserPermResultView.as_view(),
        name='user_perm_result'),
    # node
    url(r'^node/(?P<uid>[\w|-]+)/list/$', node_views.NodeListAPIView.as_view(), name='node_list'),
    url(r'^node/(?P<uid>[\w|-]+)/$', node_views.NodeDetailAPIView.as_view(), name='node_detail'),
    url(r'^node/(?P<uid>[\w|-]+)/tree/$', node_views.ManagerNodeTreeAPIView.as_view(), name='node_tree'),
    url(r'^node/(?P<uid>[\w|-]+)/node/$', node_views.NodeChildNodeAPIView.as_view(), name='node_child_node'),
    url(r'^node/(?P<uid>[\w|-]+)/user/$', node_views.NodeChildUserAPIView.as_view(), name='node_child_user'),
    # group
    url(r'^group/$', group_views.GroupListAPIView.as_view(), name='group_list'),
    url(r'^group/(?P<uid>[\w|-]+)/$', group_views.GroupDetailAPIView.as_view(), name='group_detail'),
    url(r'^group/(?P<uid>[\w|-]+)/list/$', group_views.GroupScopeListAPIView.as_view(), name='group_scope_list'),
    url(r'^group/(?P<uid>[\w|-]+)/tree/$', group_views.ManagerGroupTreeAPIView.as_view(), name='group_tree'),
    url(r'^group/(?P<uid>[\w|-]+)/group/$', group_views.GroupChildGroupAPIView.as_view(), name='group_child_group'),
    url(r'^group/(?P<uid>[\w|-]+)/user/$', group_views.GroupChildUserAPIView.as_view(), name='group_child_user'),
    # dept
    url(r'^dept/$', dept_views.DeptListAPIView.as_view(), name='dept_list'),
    url(r'^dept/(?P<uid>[\w|-]+)/$', dept_views.DeptDetailAPIView.as_view(), name='dept_detail'),
    url(r'^dept/(?P<uid>[\w|-]+)/list/$', dept_views.DeptScopeListAPIView.as_view(), name='dept_scope_list'),
    url(r'^dept/(?P<uid>[\w|-]+)/tree/$', dept_views.ManagerDeptTreeAPIView.as_view(), name='dept_tree'),
    url(r'^dept/(?P<uid>[\w|-]+)/dept/$', dept_views.DeptChildDeptAPIView.as_view(), name='dept_child_dept'),
    url(r'^dept/(?P<uid>[\w|-]+)/user/$', dept_views.DeptChildUserAPIView.as_view(), name='dept_child_user'),
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
    url(r'^work_wechat/register/bind/$', qr_views.WorkWechatRegisterAndBindView.as_view(),\
        name='work_wechat_register_bind'),
    # wechat
    url(r'^wechat/qr/callback/$', qr_views.WechatQrCallbackView.as_view(), name='wechat_qr_callback'),
    url(r'^wechat/bind/$', qr_views.WechatBindAPIView.as_view(), name='wechat_bind'),
    url(r'^wechat/register/bind/$', qr_views.WechatRegisterAndBindView.as_view(),\
        name='wechat_register_bind'),
    # github
    path('github/callback/', third_party_views.GithubCallbackView.as_view(), name='github_callback'),
    path('github/bind/', third_party_views.GithubBindAPIView.as_view(), name='github_bind'),
    path('github/register/bind/', third_party_views.GithubRegisterAndBindView.as_view(), name='github_register_bind'),
    # shortcut
    url(r'^slice/$', shortcut_views.ObjSliceAPIView.as_view(), name='shortcut_slice'),
    url(r'^slice/delete/$', shortcut_views.ObjSliceDeleteAPIView.as_view(), name='shortcut_slice_delete'),
    # ucenter
    url(r'^ucenter/sub_account/$', ucenter_views.UcenterSubAccountListView.as_view(),
        name='ucenter_sub_account_list'),
    url(r'^ucenter/password/$', ucenter_views.SetPasswordAPIView.as_view(), name='ucenter_password'),
    url(r'^ucenter/contact/$', ucenter_views.UserContactAPIView.as_view(), name='update_user_contact'),
    url(r'^ucenter/perm/$', perm_views.UserSelfPermView.as_view(), name='user_self_perm'),
    url(r'^ucenter/login/$', ucenter_views.UserLoginAPIView.as_view(), name='user_login'),
    url(r'^ucenter/register/$', ucenter_views.UserRegisterAPIView.as_view(), name='user_register'),
    url(r'^ucenter/ding/login/$', ucenter_views.DingLoginAPIView.as_view(), name='ding_login'),
    url(r'^ucenter/profile/$', ucenter_views.UcenterProfileAPIView.as_view(), name='ucenter_profile'),
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
    url(r'^config/admin/$', AdminAPIView.as_view(), name='alter_admin'),
    url(r'^config/storage/$', StorageConfigAPIView.as_view(), name='storage_config'),
    url(r'^config/custom/field/(?P<field_subject>[a-z_]+)/$',
        CustomFieldListCreateAPIView.as_view(),
        name='custom_field_list'),
    url(r'^config/custom/field/(?P<field_subject>[a-z_]+)/(?P<uuid>[\w]+)/$',
        CustomFieldDetailAPIView.as_view(),
        name='custom_field_detail'),
    url(r'^config/native/field/(?P<field_subject>[a-z_]+)/$',
        NativeFieldListAPIView.as_view(),
        name='native_field_list'),
    url(r'^config/native/field/(?P<field_subject>[a-z_]+)/(?P<uuid>[\w]+)/$',
        NativeFieldDetailAPIView.as_view(),
        name='native_field_detail'),
    path('config/i18n_mobile/', I18NMobileListCreateAPIView.as_view(), name='i18n_mobile_config_list'),
    path('config/i18n_mobile/<uuid>/', I18NMobileDetailAPIView.as_view(), name='i18n_mobile_config_detail'),

    # log
    url(r'^log/$', log_views.LogListAPIView.as_view(), name='log_list'),
    url(r'^log/(?P<uuid>[\w|-]+)', log_views.LogDetailAPIView.as_view(), name='log_detail'),
    # meta
    url(r'^meta/$', MetaConfigAPIView.as_view(), name='meta'),
    url(r'^meta/node/$', node_views.MetaNodeAPIView.as_view(), name='meta_node'),
    url(r'^meta/log/$', log_views.MetaLogAPIView.as_view(), name='meta_log'),
    url(r'^meta/perm/$', perm_views.MetaPermAPIView.as_view(), name='meta_perm'),
    # app
    url(r'^app/$', app_views.APPListCreateAPIView.as_view(), name='app_list'),
    url(r'^app/(?P<uid>[\w|-]+)/$', app_views.APPDetailAPIView.as_view(), name='app_detail'),
    url(r'^app/(?P<uid>[\w|-]+)/oauth/$', app_views.APPOAuthRegisterAPIView.as_view(), name='app_register_oauth'),
    # migrate
    url(r'^migration/user/csv/export/$', migrate_views.UserCSVExportView.as_view(), name='export_user'),
    url(r'^migration/user/csv/import/$', migrate_views.UserCSVImportView.as_view(), name='import_user'),

    # events
    url(r'^invitation/user/(?P<username>[\w]+)/', event_views.InviteUserCreateAPIView.as_view(), name='invite_user'),
    # statistics
    url(r'^statistics/user_statistic/$', UserStatisticView.as_view(), name='user_statistic'),

    # advance
    url(r'^plugin/crontab/$', advance_views.CrontabPluginListAPIView.as_view(),
        name='crontab_plugin_list'),
    url(r'^plugin/crontab/(?P<uuid>[\w]+)/$', advance_views.CrontabPluginDetailAPIView.as_view(),
        name='crontab_plugin_detail'),
    url(r'^plugin/middleware/$', advance_views.MiddlewarePluginListAPIView.as_view(),
        name='middleware_plugin_list'),
    url(r'^plugin/middleware/(?P<uuid>[\w]+)/$', advance_views.MiddlewarePluginDetailAPIView.as_view(),
        name='middleware_plugin_detail'),
]
