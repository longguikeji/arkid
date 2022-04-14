import os
import uuid
import django
import collections

# 导入settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arkid.settings")
# 安装django
django.setup()

def update_url():
    from django.urls import include, re_path
    urls = [
        re_path(r'^o/', include('oauth2_provider.urls'))
    ]
    print(urls)


if __name__ == "__main__":
    update_url()