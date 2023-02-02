# 快速开始

## 快速启动

将ArkID的仓库clone到本地后

先启动celery（需要redis服务，端口6379）
```
    celery -A arkid.core.tasks.celery worker -l debug
```
celery启动完毕后再启动 Django server
```
    python manage.py runserver 0.0.0.0:8000
```
通过源码直接启动，由于没有nginx等环境，部分功能无法正常工作。

建议通过 **[私有化部署](#_3)** 来体验产品。

## 官方IDaaS
如果希望快速的了解系统的基本使用，可以访问 [https://idaas.akid.cc](https://idaas.arkid.cc)

注册后，创建自己的租户，即可使用系统的大部分功能。

如果希望体验**超级管理员**，**安装配置插件**等，推荐使用 **[私有化部署](#_3)** 的方式

## 私有化部署

[通过ArkOS部署(推荐)](./%20私有化部署/通过ArkOS部署/){.md-button}
[通过docker部署](./%20私有化部署/通过Docker部署/){.md-button}
[通过k8s部署](./%20私有化部署/通过k8s部署/){.md-button}