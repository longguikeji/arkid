
# 通过k8s部署

## 环境准备

* Kubernetes 1.12+
* Helm 3.1.0
* PV provisioner support in the underlying infrastructure
* ReadWriteMany volumes for deployment scaling

## 安装
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

## 更多配置

### 公共配置
| NAME | Description | DEFAULT VALUE |
| --- | --- | --- |
| imagePullSecrets | 拉取镜像的secret名字 | nil |
| persistence.init | 是否新创建pvc，如果设置为false则claimName的pvc必须存在 | true |
| persistence.storageClass | storageclass名字 | nil |
| persistence.accessMode | pvc访问模式 | ReadWriteOnce |
| persistence.size | 默认8GB | 8Gi |


### arkid配置
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


### mysql数据库配置
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


### redis配置
| NaME | Description | DEFAULT VALUE |
| --- | --- | --- |
| redis.enabled | true会部署一个redis，如果是false则需要设置externalRedis下的配置 | true |
| redis.image | redis镜像 | redis:5.0.3 |
| redis.pullPolicy | IfNotPresent, Always | IfNotPresent |
| externalRedis.host | 外部redis的host | "" |
| externalRedis.port | 外部redis的port | 6379 |
| externalRedis.db | 外部redis的db | 0 |


### ingress配置
| name | DEscription | default value |
| --- | --- | --- |
| ingress.enabled | 添加ingress记录 | true |
| ingress.cert | 使用cert-manager生成证书 | false |
| ingress.annotations | ingress的注释 | {"kubernetes.io/ingress.class": "nginx","certmanager.k8s.io/cluster-issuer": "letsencrypt-prod"} |
| ingress.host.name | ingress记录的域名 | "" |
| ingress.tls | 如果没有 cert-manager，tls为true则helm会生成一个自签名的证书存到secret | false |

