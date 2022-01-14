from django.db import models
from django.utils.translation import ugettext_lazy as _

from common.model import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Article(BaseModel):
    """
    文章
    """

    title = models.CharField(
        max_length=200,
        verbose_name=_("标题")
    )

    content = models.TextField(
        verbose_name=_("内容")
    )

    author = models.ForeignKey(
        User,
        related_name="articles",
        on_delete=models.PROTECT,
        verbose_name=_("作者")
    )

    readers = models.ManyToManyField(
        User,
        related_name="readed_articles",
        verbose_name=_("阅读用户"),
    )

    readed_times = models.IntegerField(
        default=0,
        verbose_name=_("阅读次数")
    )

    def read_record(self, reader: User):
        """
        记录阅读次数和人
        """
        self.readers.add(reader)
        self.readed_times += 1
        self.save()
