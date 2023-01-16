# Start quickly

## Quick Start

After the ARKID warehouse clone to the local area

Start Clery first（Need a redis service，Port 6379）
```
    celery -A arkid.core.tasks.celery worker -l debug
```
celeryStart after startup Django server
```
    python manage.py runserver 0.0.0.0:8000
```
Start directly through the source code，Because there is no environment such as nginx，Some functions cannot work normally。

Suggest **[Privatization deployment] (#_3)** Come to experience the product。

## Official IDAAS
If you want to quickly understand the basic use of the system，Accessible [https://idaas.arkid.cc](https://idas.arkid.cc)

After registration，Create your own tenant，You can use most of the system's function。

If you want to experience**Super administrator**，**Installation and configuration plugin**Wait，Recommended Use **[Privatization deployment] (#_3)** The way

## Privatization

[Deploy through ARKOS (recommendation)](./%20Privatization/DeployThroughArkos/){.md-button}
[Deploy through docker](./%20Privatization/DeployThroughDocker/){.md-button}
[Deploy through K8S](./%20Privatization/DeployThroughK8S/){.md-button}
