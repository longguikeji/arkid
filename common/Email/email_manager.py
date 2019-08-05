# coding: utf-8

import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr


class EmailManager(object):
    """send email"""

    def __init__(self, user, pwd, host, port, nickname='', retry=1):
        """
        :param str user: 账号
        :param str pwd: 密码
        :param str host: 邮件服务器
        :param str nickname: 发件人昵称
        :param int retry: 重试次数
        """
        self.server = smtplib.SMTP()
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.nickname = nickname
        self.retry = retry

    def connect(self, retry=1):
        """
        连接

        :param int retry: 重试次数
        """
        try:
            self.server.connect(self.host, self.port)
            self.server.starttls()
            self.server.login(self.user, self.pwd)
        except Exception as e:
            self.quit()
            if retry:
                self.connect(retry - 1)
            else:
                raise e

    def quit(self):
        """
        断开连接
        """
        self.server.quit()

    def _format_addr(self, s):
        """
        地址格式化
        """
        name, addr = parseaddr(s)
        # addr = addr.encode('utf-8') if isinstance(addr, unicode) else addr
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def send_mail(self, addrs, msg, one_by_one=True):
        """
        发送邮件

        :param str/list addrs: 收件人地址
        :param MIME msg: 信件
        :param bool one_by_one: 当存在多个收件地址时逐个发送还是群发,默认逐个发送
        """
        try:
            if type(addrs) == str:
                msg['To'] = addrs
                self.server.sendmail(self.user, [addrs], msg.as_string())
            if type(addrs) == list:
                if one_by_one:
                    for addr in addrs:
                        if 'To' in msg:
                            del msg['To']
                        msg['To'] = addr
                        self.server.sendmail(self.user, [addr], msg.as_string())
                else:
                    msg['To'] = ';'.join(addrs)
                    self.server.sendmail(self.user, addrs, msg.as_string())
        except Exception:
            if 'To' in msg:
                del msg['To']
            self.connect(self.retry)
            self.send_mail(addrs, msg, one_by_one)

    def gen_msg(self, content, type='plain', charset='utf-8'):
        """
        生成信件

        :param str content: 内容
        :param str type: 类型, plain:文本, html:HTML, multi:复合
        :param str charset: 编码

        :rtype: MIME
        """

        msg = None
        if type == 'plain':
            msg = MIMEText(content, 'plain', charset)
        if type == 'html':
            msg = MIMEText(content, 'html', charset)
        if type == 'multi':
            msg = MIMEMultipart()
        # ...
        return msg

    def send_text_mail(self, addrs, subject, text, one_by_one=True):
        """
        发送文本信件

        :param str/list addrs: 收件人地址
        :param str subject: 信件标题
        :param str text: 文本内容
        :param bool one_by_one: 当存在多个收件地址时逐个发送还是群发,默认逐个发送
        """
        msg = self.gen_msg(text, type='plain')
        msg['Subject'] = Header(subject, 'utf-8').encode()
        msg['From'] = self._format_addr('{} <{}>'.format(self.nickname, self.user))
        self.send_mail(addrs, msg, one_by_one)

    def send_html_mail(self, addrs, subject, html, one_by_one=True):
        """
        发送文本信件

        :param str/list addrs: 收件人地址
        :param str subject: 信件标题
        :param str html: HTML内容
        :param bool one_by_one: 当存在多个收件地址时逐个发送还是群发,默认逐个发送
        """
        msg = self.gen_msg(html, type='html')
        msg['Subject'] = Header(subject, 'utf-8').encode()
        msg['From'] = self._format_addr('{} <{}>'.format(self.nickname, self.user))
        self.send_mail(addrs, msg, one_by_one)

    def send_multi_mail(self, addrs, subject, msgs, one_by_one=True):
        """
        发送复合信件,可混合文本,html,附件等

        :param str/list addrs: 收件人地址
        :param str subject: 信件标题
        :param [MIME] msgs: 信件内容
        :param bool one_by_one: 当存在多个收件地址时逐个发送还是群发,默认逐个发送
        """
        main_msg = self.gen_msg('_', type='multi')
        main_msg['Subject'] = Header(subject, 'utf-8').encode()
        main_msg['From'] = self._format_addr('{} <{}>'.format(self.nickname, self.user))
        for msg in msgs:
            main_msg.attach(msg)
        self.send_mail(addrs, main_msg, one_by_one)
