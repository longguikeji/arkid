from PIL import Image, ImageDraw, ImageFont, ImageFilter
from common.provider import AuthCodeProvider
from django.http import HttpResponse
from .constants import KEY
from io import BytesIO

import random
import string


class AuthCodeIdpProvider(AuthCodeProvider):


    def __init__(self) -> None:
        super().__init__()

        from extension.models import Extension
        o = Extension.active_objects.filter(
            type=KEY,
        ).first()

        assert o is not None

    def get_random_char(self):
        '''
        获取随机4个字符组合
        '''
        chr_all = string.ascii_letters + string.digits
        chr_4 = ''.join(random.sample(chr_all, 4))
        return chr_4

    def get_random_color(self, low, high):
        '''
        获取随机颜色
        '''
        return (random.randint(low, high), random.randint(low, high), random.randint(low, high))

    def get_authcode_picture(self, request):
        '''
        制作验证码图片
        '''
        width, height = 180, 60
        # 创建空白画布
        image = Image.new('RGB', (width, height), self.get_random_color(20, 100))
        # 验证码的字体
        font = ImageFont.truetype('./extension_root/authcode/assess/stxinwei.ttf', 40)
        # 创建画笔
        draw = ImageDraw.Draw(image)
        # 获取验证码
        char_4 = self.get_random_char()
        # 向画布上填写验证码
        for i in range(4):
            draw.text((40 * i + 10, 0), char_4[i], font=font, fill=self.get_random_color(100, 200))
        # 绘制干扰点
        for x in range(random.randint(200, 600)):
            x = random.randint(1, width - 1)
            y = random.randint(1, height - 1)
            draw.point((x, y), fill=self.get_random_color(50, 150))
        # 模糊处理
        image = image.filter(ImageFilter.BLUR)
        # 存入session,用于做进一步的验证
        request.session['verification_code'] = char_4
        buf = BytesIO()
        # 将图片保存在内存中，文件类型为png
        image.save(buf, 'png')
        return HttpResponse(buf.getvalue(), 'image/png')
