from typing import Dict
from common.provider import AppTypeProvider


class AutoFormFillAppTypeProvider(AppTypeProvider):
    def create(self, app, data: Dict) -> Dict:

        username_css = data.get('username_css')
        password_css = data.get('password_css')
        submit_css = data.get('submit_css')
        auto_login = data.get('auto_login')

        return {
            'username_css': username_css,
            'password_css': password_css,
            'submit_css': submit_css,
            'auto_login': auto_login,
        }

    def update(self, app, data: Dict) -> Dict:

        username_css = data.get('username_css')
        password_css = data.get('password_css')
        submit_css = data.get('submit_css')
        auto_login = data.get('auto_login')

        return {
            'username_css': username_css,
            'password_css': password_css,
            'submit_css': submit_css,
            'auto_login': auto_login,
        }
