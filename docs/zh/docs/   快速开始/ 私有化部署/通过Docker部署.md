# docker-compose部署

### 配置阿里云dns域名解析：

- arkid.xxx.xxx ==> docker-compose机器 ip

### 部署arkid

```shell
git clone --branch main --depth 1  https://github.com/longguikeji/arkid-charts.git

##无法访问github的话，可以使用gitee仓库：https://gitee.com/longguikeji/arkid-charts.git

cd arkid-charts/docker-compose

## 1、修改 traefik.yml中 'certificatesResolvers: ali: acme: email:' 为你的邮件地址
## 2、修改 .env 中 ALICLOUD_ACCESS_KEY 和 ALICLOUD_SECRET_KEY
##    在阿里云账户下生成accesskey和accesssecret（赋予域名相关的权限，用于自动生成证书）
## 3、修改 .env 中 MY_HOSTNAME，设置为阿里云dns中配置的域名

## 之后启动

sudo docker-compose up -d

## 稍等片刻，浏览器访问：
https://arkid.xxx.xxx

## 注意：首次打开arkid，会有一个确认地址的输入框，在点完确认之后就不能再更改了！


```

# 更新docker-compose部署版本
```shell
## 进入 docker-compose 目录
cd arkid-charts/docker-compose

## 停止
docker-compose down

## 拉取更新 git仓库
git pull

## 再次执行启动命令，就会拉取新的镜像更新版本
docker-compose up -d

```
