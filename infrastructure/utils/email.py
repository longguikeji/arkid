'''
邮件
'''
from common.Email.email_manager import EmailManager
from oneid_meta.models.config import EmailConfig


def send_email(addrs, subject, content):
    '''
    发送邮件
    '''
    email_config = EmailConfig.get_current()
    emailer = EmailManager(
        user=email_config.access_key,
        pwd=email_config.access_secret,
        host=email_config.host,
        port=email_config.port,
        nickname=email_config.nickname,
    )
    emailer.send_html_mail(addrs, subject, content)
