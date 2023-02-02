# docker-composedeploy

### Configure Alibaba Cloud DNS domain name analysis：

- arkid.xxx.xxx ==> docker-composemachine ip

### Deploy Arkid

```shell
git clone --branch main --depth 1  https://github.com/longguikeji/arkid-charts.git

##If you can't access github，You can use a Gitee warehouse：https://gitee.com/longguikeji/arkid-charts.git

cd arkid-charts/docker-compose

## 1、Revise traventual.in YML 'certificatesResolvers: ali: acme: email:' Mail address for you
## 2、Revise .env middle ALICLOUD_ACCESS_KEY and ALICLOUD_SECRET_KEY
##    Generate ACCESSKEY and Accesssecret under the Alibaba Cloud account（Given the domain name -related permissions，Used to automatically generate certificates）
## 3、Revise .env middle MY_HOSTNAME，Set the domain name configured in Alibaba Cloud DNS

## Later

sudo docker-compose up -d

## Wait a moment，Browser access：
https://arkid.xxx.xxx

## Notice：Open Arkid for the first time，There will be an input box for confirmation address，After the confirmation is confirmed, you can’t change it anymore！


```

# Update docker-compose deployment version
```shell
## Enter docker-compose Table of contents
cd arkid-charts/docker-compose

## stop
docker-compose down

## Pull up update git warehouse
git pull

## Execute the startup command again，Will draw a new mirror update version
docker-compose up -d

```
