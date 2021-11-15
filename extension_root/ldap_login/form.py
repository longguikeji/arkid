from common.loginpage import BaseForm, FormItem


class LdapLoginForm(BaseForm):
    form_label = 'LDAP 登录'
    form_items = [
        FormItem('username', 'text', '用户名'),
        FormItem('password', 'password', '密码'),
    ]

    def set_form_item_placeholder(self, login_form_item):
        if login_form_item['name'] == 'username':
            placeholders = []
            placeholders.append('用户名')
            login_form_item['placeholder'] = '/'.join(placeholders)
