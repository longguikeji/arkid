'''
认证后端
'''

from oneid_meta.models import User
from executer.utils.password import verify_password


class OneIDBasicAuthBackend:
    '''
    针对oneid.User
    检查以下三项：
    - 账号密码
    - 是否删除
    - 是否可用
    '''
    def authenticate(self, request, username=None, password=None):    # pylint: disable=no-self-use,unused-argument
        '''
        return user if success else None
        '''
        user = User.active_objects.filter(username=username).first()
        if not user:
            return None

        ciphertext = user.password
        plaintext = password
        if verify_password(plaintext, ciphertext):
            if request:
                request.user = user    # 注意这里替换的是OneID.User，可能会与其他backend记录的user不一样
            return user
        return None

    def get_user(self, user_id):    # pylint: disable=no-self-use
        '''
        TODO
        '''
        return User.objects.filter(pk=user_id).first()
