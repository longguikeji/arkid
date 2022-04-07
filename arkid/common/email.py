# coding: utf-8

import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr

EMAIL_PORT_MAPPER = {
    25: 'smtp',
    465: 'smtps',
    587: 'msa',
}

class EmailManager(object):
    """send email"""

    def __init__(self, user, pwd, host, port, nickname='', retry=1):
        """
        :param str user: 账号
        :param str pwd: 密码
        :param str host: 邮件服务器地址
        :param int port: 邮件服务器端口
        :param str nickname: 发件人昵称
        :param int retry: 重试次数
        """
        self.client = None
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.nickname = nickname
        self.retry = retry
        self.protocol = self.presume_protocol(port)

    def gen_client(self):
        '''
        gen client by protocl
        '''
        if self.protocol == 'smtps':
            return smtplib.SMTP_SSL(self.host, self.port)
        return smtplib.SMTP(self.host, self.port)

    @staticmethod
    def presume_protocol(port):
        '''
        根据端口判断邮件服务所用协议
        '''
        return EMAIL_PORT_MAPPER.get(port, 'smtps')

    def connect(self, retry=1):
        """
        连接

        :param int retry: 重试次数
        """
        try:
            client = self.gen_client()
            client.connect(self.host, self.port)
            if self.protocol == 'msa':
                client.starttls()

            try:
                client.ehlo(self.host)
                client.login(self.user, self.pwd)
            except smtplib.SMTPResponseException as exce:
                if exce.smtp_code == 530:    # msa(port=587) Must issue a STARTTLS command first.
                    self.protocol = 'msa'
                raise
            self.client = client

        except smtplib.SMTPException as exce:
            self.quit()
            if retry:
                self.connect(retry - 1)
            else:
                raise exce

    def quit(self):
        """
        断开连接
        """
        if self.client:
            self.client.quit()

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
            if not self.client:
                self.connect(self.retry)
            if type(addrs) == str:
                msg['To'] = addrs
                self.client.sendmail(self.user, [addrs], msg.as_string())
            if type(addrs) == list:
                if one_by_one:
                    for addr in addrs:
                        if 'To' in msg:
                            del msg['To']
                        msg['To'] = addr
                        self.client.sendmail(self.user, [addr], msg.as_string())
                else:
                    msg['To'] = ';'.join(addrs)
                    self.client.sendmail(self.user, addrs, msg.as_string())
        except Exception as exc:
            # if self.retry:
            # if 'To' in msg:
            #     del msg['To']
            # self.connect(self.retry)
            # self.send_mail(addrs, msg, one_by_one)
            raise exc

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
