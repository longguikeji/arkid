import os
import uuid
import django
import collections

# 导入settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arkid.settings")
# 安装django
django.setup()

def update_url():
    print(123)


if __name__ == "__main__":
    update_url()