## k8s部署

> 比较纯净的集群，手动安装的k8s集群一般没有附加组件
>
> 至少三台以上的机器

### 0、配置阿里云dns域名解析：

- arkid.xxx.xxx  ==>  k8s master ip 或者 负载均衡 ip
- *.arkid.xxx.xxx ==> k8s master ip 或者 负载均衡 ip

### 1、存储：推荐 Rook-Ceph或者longhorn

> 存储的选择必须很谨慎，Rook-Ceph 和 longhorn 都比较稳定，功能也非常强大，但是部署比较复杂，要求也比较高
>
> 请安装官网的文档操作。longhorn最好ubuntu+ext4; Rook-Ceph也推荐ubuntu，云原生最好ubuntu。

### 2、网关：推荐ingress-nginx或者traefik

> 如果安装traefik作为网关，就不需要再单独部署cert-manager和alidns webhook了
>
> https://kubernetes.github.io/ingress-nginx/deploy/
>
> 以下文档以ingress-nginx为例，traefik文档和`k3s部署`中的一样

```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.5.1/deploy/static/provider/cloud/deploy.yaml
```

### 3、证书管理：cert-manager + alidns webhook

> https://artifacthub.io/packages/helm/cert-manager/cert-manager

```shell
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.10.1/cert-manager.crds.yaml

helm repo add jetstack https://charts.jetstack.io

kubectl create namespace cert-manager
helm install cert-manager --namespace cert-manager --version v1.10.1 jetstack/cert-manager
```
> https://github.com/pragkent/alidns-webhook
```shell
# 1、Install alidns-webhook
curl -O https://raw.githubusercontent.com/pragkent/alidns-webhook/master/deploy/bundle.yaml
## 修改bundle.yaml中 acme.yourcompany.com 修改为 acme.xxxx.com（自己公司的域名）！
## 这个group名字后边的clusterissuer也要是相同的
kubectl apply -f bundle.yaml

# 2、 创建secret包含 alidns的凭据
## 在阿里云账户下生成accesskey和accesssecret（赋予域名相关的权限）
## 在 cert-manager 中创建secret
kubectl -n cert-manager create secret alidns-secret \
--from-literal=access-key=youraccesskey \
--from-literal=secret-key=youraccesssecret

# 3、创建 ClusterIssuer
## groupName也要改成和上边一致的，email写自己的，其他不用改
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    email: xxxx@xxx.com
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - dns01:
        webhook:
          groupName: acme.xxxxx.com
          solverName: alidns
          config:
            region: ""
            accessKeySecretRef:
              name: alidns-secret
              key: access-key
            secretKeySecretRef:
              name: alidns-secret
              key: secret-key
```

### 4、包管理：推荐helm-controller

```shell
CHARTCRD=`kubectl get crd|grep helmcharts.helm.cattle.io`
if [ -z "$CHARTCRD" ];then
    kubectl create -f https://gitee.com/longguikeji/arkid-charts/raw/main/helmchartscrd.yaml
fi
```

### 5、部署arkid

```shell
## 创建命名空间
kubectl create ns arkid

## 编辑文件 arkid.yaml
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: arkid
  namespace: arkid
spec:
  chart: arkid
  version: 3.2.14
  repo: https://harbor.longguikeji.com/chartrepo/public
  targetNamespace: arkid
  valuesContent: |-
    ingress:
      enabled: true
      tls: true
      host:
        name: arkid.xxxx.xxx ## 填正确的域名
      annotations:
        kubernetes.io/ingress.class: "nginx"    
        cert-manager.io/clusterissuer: "letsencrypt-prod"
    persistence:
      init: true
      accessMode: ReadWriteMany
      size: 8Gi
    mysql:
      auth:
        rootPassword: root
        database: arkid
        username: arkid
        password: arkid

## 安装 arkid
kubectl apply -f arkid.yaml

## 查看
kubectl -n arkid get pods

## 稍等片刻，浏览器访问：
https://arkid.xxx.xxx

## 注意：首次打开arkid，会有一个确认地址的输入框，在点完确认之后就不能再更改了！

```





## 升级 arkid chart版本
```shell
kubectl -n arkid edit helmcharts arkid

## 修改版本号，保存退出, 会自动更新
spec:
  chart: arkid
  version: 3.2.14
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

