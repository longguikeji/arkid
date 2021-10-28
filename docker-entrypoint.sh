#!/bin/bash
set -ex

## 正常启动用 tini启动
if [ "$1" = 'tini' -a "$(id -u)" = '0' ]; then
    /usr/local/bin/python3.8 manage.py compilemessages;
    /usr/local/bin/python3.8 manage.py migrate;
    # 无法修改configmap挂载的配置文件
    # chown -R arkid:arkid /var/arkid;
    exec gosu arkid "$0" "$@";
fi

/usr/local/bin/python3.8 manage.py compilemessages;
/usr/local/bin/python3.8 manage.py migrate;

exec "$@"