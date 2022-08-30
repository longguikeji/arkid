
# 通过k8s部署

## 环境准备

* Kubernetes 1.12+
* Helm 3.1.0
* PV provisioner support in the underlying infrastructure
* ReadWriteMany volumes for deployment scaling

## 通过helm安装

> !!! 生产环境推荐使用 gitops工具（如argoCD）来部署和管理
> chart源码仓库地址： https://github.com/longguikeji/arkid-charts.git

### 添加helm仓库
```shell
helm repo add lgkj https://harbor.longguikeji.com/chartrepo/public

helm repo update
```

### helm 查找 arkid 的 charts
```shell
helm search repo arkid -l
```

### 安装 arkid chart


```shell
kubectl create ns arkid

helm --namespace arkid install arkid lgkj/arkid \
--set persistence.init=true
```

## nodeport 端口访问 arkid

```shell

打开浏览器访问: `http://{任意节点ip}:32580/`

首次打开arkid，需要输入访问url，此url只能输入这一次，需要慎重！！！

如果生产环境需要域名访问，那请配置好一切之后再填这个url！！！

初始密码：`admin/admin`
```



## 升级 arkid chart版本
```shell
helm repo update

helm -n arkid upgrade arkid lgkj/arkid \
--set persistence.init=true
```



## 更多配置
> https://github.com/longguikeji/arkid-charts.git
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
| fe.image | arkid前端的镜像 |  harbor.longguikeji.com/ark-releases/arkid-fe-vue3:2.5.0 |
| fe.pullPolicy | IfNotPresent, Always | IfNotPresent |
| fe.resources.requests | arkid前端的requests | {"cpu": "800m","memory": "1024Mi"} |
| fe.resources.limits | arkid前端的limits | {} |
| be.image | arkid后端的镜像 |  harbor.longguikeji.com/ark-releases/arkid:2.5.0  |
| be.pullPolicy |  |  |
| be.resources.requests | arkid后端的requests | {"cpu": "800m","memory": "1024Mi"} |
| be.resources.limits | arkid后端的limits | {} |


### mysql数据库配置
| NAME | Description | DEFAULT VALUE |
| --- | --- | --- |
| mysql.enabled | true会部署一个mysql，如果是false则需要设置externalDatabase下的配置 | true |
| externalDatabase.host | 外部mysql数据库的host | "" |
| externalDatabase.port | 外部mysql数据库的port | 3306 |
| externalDatabase.database | 外部mysql数据库的库名 | "" |
| externalDatabase.user | 外部mysql数据库的user | "" |
| externalDatabase.password | 外部mysql数据库的password | "" |


### redis配置
| NaME | Description | DEFAULT VALUE |
| --- | --- | --- |
| redis.enabled | true会部署一个redis，如果是false则需要设置externalRedis下的配置 | true |
| externalRedis.host | 外部redis的host | "" |
| externalRedis.port | 外部redis的port | 6379 |
| externalRedis.db | 外部redis的db | 0 |


### ingress配置
| name | DEscription | default value |
| --- | --- | --- |
| ingress.enabled | 添加ingress记录 | false |
| ingress.cert | 使用cert-manager生成证书 | false |
| ingress.annotations | ingress的注释 | {"kubernetes.io/ingress.class": "nginx","certmanager.k8s.io/cluster-issuer": "letsencrypt-prod"} |
| ingress.host.name | ingress记录的域名 | "" |
| ingress.tls | 如果没有 cert-manager，tls为true则helm会生成一个自签名的证书存到secret | false |

