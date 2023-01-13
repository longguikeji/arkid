# A quick start

## Quick start

After cloning the ArkID's warehouse to the local

Start celery first (requires redis service, port 6379)
```
    celery -A arkid.core.tasks.celery worker -l debug
```
Start Django server after celery has finished starting
```
    python manage.py runserver 0.0.0.0:8000
```
Start directly through the source code, because there is no nginx and other environments, some functions can not work properly.

It is recommended to **[私有化部署](#_3)** experience the product through.

## Official IDaaS
If you want to quickly understand the basic use of the system, you can visit

Once registered, you can create your own tenant and use most of the system's features.

If you want to experience ** Super Admin **, ** Install the configuration plug-in ** etc., the recommended way to use **[私有化部署](#_3)**

## Privatization deployment

[ Deploy with ArkOS (recommended) ](./%20私有化部署/通过ArkOS部署/){.md-button}
[通过docker部署](./%20私有化部署/通过Docker部署/){.md-button}
[通过k8s部署](./%20私有化部署/通过k8s部署/){.md-button}