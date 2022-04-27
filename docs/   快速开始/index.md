# 快速开始

## 官方SaaS
如果希望快速的了解系统的基本使用，可以访问 [https://saas.akid.cc](https://saas.arkid.cc)

注册后，创建自己的租户，即可使用系统的大部分功能

!!! 提示
    如果希望体验**超级管理员**，**安装配置插件**等，推荐使用 **[私有化部署](#私有化部署)** 的方式

## 私有化部署

### 命令行工具arkos一键部署
#### （1）准备运维操作机器：

> 需要准备一台机器来运行docker，用容器来部署arkid
> 一台centos7+或者ubuntu18+，安装有docker
>
> 以下docker环境也可以：
>
> - mac安装docker desktop
> - pc安装docker desktop
> - pc WSL 2.0 子系统中安装docker

```shell
## 安装docker

curl -sSL https://get.daocloud.io/docker | sh

```

#### （2）准备部署arkid的机器

##### 2.1、只有一台机器
> 需要准备的文件
> - hosts
```shell
## hosts 文件格式
## 只需修改ip地址和端口，还有用户名和密码
## 将hosts文件放到运维操作机器中的某个目录
[arkos-masters]
arkos-master01 hostname=arkos-master01 ansible_ssh_host=x.x.x.x ansible_ssh_port=22

[all:vars]
ansible_connection=ssh
ansible_user=root
ansible_password=xxxx

```
运行部署命令：
```shell
## 在运维操作机器执行
## 进入到hosts文件所在目录，执行命令来安装arkid
docker run --rm --mount type=bind,source="$(pwd)"/hosts,target=/etc/ansible/hosts harbor.longguikeji.com/ark-releases/arkos one

```


##### 2.2、有多台机器

> 需要准备的文件
> - hosts
```shell
## hosts 文件格式
## 只需修改ip地址和端口，还有用户名和密码
## 在[arkos-nodes] 下添加或删减机器，记得递增序号
## 将hosts文件放到运维操作机器中的某个目录
[arkos-masters]
arkos-master01 hostname=arkos-master01 ansible_ssh_host=x.x.x.x ansible_ssh_port=22

[arkos-nodes]
arkos-node01 hostname=arkos-node01   ansible_ssh_host=x.x.x.x ansible_ssh_port=22
arkos-node02 hostname=arkos-node02   ansible_ssh_host=x.x.x.x ansible_ssh_port=22

[all:vars]
ansible_connection=ssh
ansible_user=root
ansible_password=xxxx


```

运行部署命令：

```shell
## 在运维操作机器执行
## 进入到hosts文件所在目录，执行命令来安装arkid
docker run --rm --mount type=bind,source="$(pwd)"/hosts,target=/etc/ansible/hosts harbor.longguikeji.com/ark-releases/arkos two

```

### helm/charts 方式部署

#### 环境

* Kubernetes 1.12+
* Helm 3.1.0
* PV provisioner support in the underlying infrastructure
* ReadWriteMany volumes for deployment scaling

#### 安装
``` py
## 下载arkid 的chart
git clone --branch v2-dev --depth 1  https://github.com/longguikeji/arkid-charts.git

cd arkid-charts/chart

# 安装
helm install arkidv2 . \
--set persistence.init=true \
--set ingress.cert=false \
--set ingress.tls=false \
--set ingress.host.name=arkid.yourcompany.com

# 暴露端口访问
kubectl port-forward svc/arkid-portal  8989:80

Forwarding from 127.0.0.1:8989 -> 80
Handling connection for 8989

```

#### 更多配置

##### 公共配置
| NAME | Description | DEFAULT VALUE |
| --- | --- | --- |
| imagePullSecrets | 拉取镜像的secret名字 | nil |
| persistence.init | 是否新创建pvc，如果设置为false则claimName的pvc必须存在 | true |
| persistence.storageClass | storageclass名字 | nil |
| persistence.accessMode | pvc访问模式 | ReadWriteOnce |
| persistence.size | 默认8GB | 8Gi |


##### arkid配置
| NAME | DESCRIPTION | DEFAULT VALUE |
| --- | --- | --- |
| fe.image | arkid前端的镜像 | longguikeji/arkid-fe:v2dev |
| fe.pullPolicy | IfNotPresent, Always | IfNotPresent |
| fe.resources.requests | arkid前端的requests | {"cpu": "800m","memory": "1024Mi"} |
| fe.resources.limits | arkid前端的limits | {} |
| be.image | arkid后端的镜像 | longguikeji/arkid:v2dev |
| be.pullPolicy |  |  |
| be.resources.requests | arkid后端的requests | {"cpu": "800m","memory": "1024Mi"} |
| be.resources.limits | arkid后端的limits | {} |


##### mysql数据库配置
| NAME | Description | DEFAULT VALUE |
| --- | --- | --- |
| mysql.enabled | true会部署一个mysql，如果是false则需要设置externalDatabase下的配置 | true |
| mysql.image | mysql镜像 | mysql:5.7 |
| mysql.pullPolicy | IfNotPresent, Always | IfNotPresent |
| mysql.rootPassword | root密码 | root |
| mysql.database | db名字 | arkid |
| externalDatabase.host | 外部mysql数据库的host | "" |
| externalDatabase.port | 外部mysql数据库的port | 3306 |
| externalDatabase.database | 外部mysql数据库的库名 | "" |
| externalDatabase.user | 外部mysql数据库的user | "" |
| externalDatabase.password | 外部mysql数据库的password | "" |


##### redis配置
| NaME | Description | DEFAULT VALUE |
| --- | --- | --- |
| redis.enabled | true会部署一个redis，如果是false则需要设置externalRedis下的配置 | true |
| redis.image | redis镜像 | redis:5.0.3 |
| redis.pullPolicy | IfNotPresent, Always | IfNotPresent |
| externalRedis.host | 外部redis的host | "" |
| externalRedis.port | 外部redis的port | 6379 |
| externalRedis.db | 外部redis的db | 0 |


##### ingress配置
| name | DEscription | default value |
| --- | --- | --- |
| ingress.enabled | 添加ingress记录 | true |
| ingress.cert | 使用cert-manager生成证书 | false |
| ingress.annotations | ingress的注释 | {"kubernetes.io/ingress.class": "nginx","certmanager.k8s.io/cluster-issuer": "letsencrypt-prod"} |
| ingress.host.name | ingress记录的域名 | "" |
| ingress.tls | 如果没有 cert-manager，tls为true则helm会生成一个自签名的证书存到secret | false |


### docker-compose 方式部署

``` py
# 下载 arkid v2.0 部署文件
git clone --branch v2-dev --depth 1  https://github.com/longguikeji/arkid-charts.git

cd arkid-charts/docker-compose

# 修改 .env 文件、settings_local.py、arkid.local.toml 文件
# 默认的访问地址是 http://localhost:8989
# 如果是其他地址访问，则需要更改 arkid.local.toml 文件
# 例如：http://192.168.184.133:8989, 修改arkid.local.toml文件如下
# 
# name = "arkid v2"
# host = '192.168.184.133:8989'
# frontend_host = '192.168.184.133:8989'
# https_enabled = 0


# 启动
docker-compose up -d

# 打开 http://localhost:8989 (具体端口视 .env 中 HTTP_PORT 而定)
# 内置账号 admin / admin 登录。

```
### 部署完成

浏览器打开[http://localhost:8989](http://localhost:8989)，探索ArkID的完整功能
