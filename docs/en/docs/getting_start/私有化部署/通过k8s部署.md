## K8s deployment

> Relatively pure clusters, manually installed k8s clusters generally do not have additional components
>
> At least three machines

### 0. Configure Alibaba Cloud DNS domain name resolution:

- Arkid. XXX. XXX = = > k8s master IP or load balancing IP
- *. Arkid. XXX. XXX = = > k8s master IP or load balancing IP

### 1. Storage: Recommend Rook-Ceph or longhorn

> The choice of storage must be very careful, Rook-Ceph and longhorn are relatively stable and very powerful, but the deployment is more complex and demanding
>
> Please install the document operation on the official website. Longhorn best Ubuntu + ext4; Rook-Ceph also recommends Ubuntu, which is best for cloud native.

### 2. Gateway: recommend ingress-nginx or traefik

> If you install traefik as the gateway, you do not need to deploy the cert-manager and alidns web hook separately
>
> https://kubernetes.github.io/ingress-nginx/deploy/
>
> The following documentation uses ingress-nginx as an example, and the traefik documentation is the same as `k3s部署` in

```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.5.1/deploy/static/provider/cloud/deploy.yaml
```

### 3. Certificate management: cert-manager + alidns webhook

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

### 4. Package management: helm-controller is recommended

```shell
CHARTCRD=`kubectl get crd|grep helmcharts.helm.cattle.io`
if [ -z "$CHARTCRD" ];then
    kubectl create -f https://gitee.com/longguikeji/arkid-charts/raw/main/helmchartscrd.yaml
fi
```

### 5. Deploy arkid

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





## Upgrade arkid chart version
```shell
kubectl -n arkid edit helmcharts arkid

## 修改版本号，保存退出, 会自动更新
spec:
  chart: arkid
  version: 3.2.14
```

## More configurations
> https://github.com/longguikeji/arkid-charts.git
### Common configuration
| NAME | Description |DEFAULT VALUE|
| --- | --- | --- |
|imagePullSecrets| 拉取镜像的secret名字 | nil |
| persistence.init |Whether to create a new PVC. If set to false, the PVC for claimName must exist| true |
|persistence.storageClass| storageclass名字 | nil |
|persistence.accessMode| pvc访问模式 | ReadWriteOnce |
|persistence.size| 默认8GB | 8Gi |


### Arkid configuration
| NAME | DESCRIPTION |DEFAULT VALUE|
| --- | --- | --- |
| fe.image | arkid前端的镜像 |harbor.longguikeji.com/ark-releases/arkid-fe-vue3:2.5.0|
| fe.pullPolicy |IfNotPresent, Always| IfNotPresent |
| fe.resources.requests | arkid前端的requests |{"cpu": "800m","memory": "1024Mi"}|
|fe.resources.limits| arkid前端的limits | {} |
| be.image | arkid后端的镜像 |harbor.longguikeji.com/ark-releases/arkid:2.5.0|
|be.pullPolicy|  |  |
| be.resources.requests | arkid后端的requests |{"cpu": "800m","memory": "1024Mi"}|
|be.resources.limits| arkid后端的limits | {} |


### The MySQL database configuration
| NAME | Description |DEFAULT VALUE|
| --- | --- | --- |
| mysql.enabled |If it is true, a MySQL will be deployed. If it is false, the configuration under externalDatabase needs to be set| true |
|externalDatabase.host| 外部mysql数据库的host | "" |
|externalDatabase.port| 外部mysql数据库的port | 3306 |
|externalDatabase.database| 外部mysql数据库的库名 | "" |
|externalDatabase.user| 外部mysql数据库的user | "" |
|externalDatabase.password| 外部mysql数据库的password | "" |


### The redis configuration
| NaME | Description |DEFAULT VALUE|
| --- | --- | --- |
| redis.enabled |If it is true, a redis will be deployed. If it is false, the configuration under externalredis needs to be set| true |
|externalRedis.host| 外部redis的host | "" |
|externalRedis.port| 外部redis的port | 6379 |
|externalRedis.db| 外部redis的db | 0 |


### Ingress configuration
| name | DEscription |default value|
| --- | --- | --- |
|ingress.enabled| 添加ingress记录 | false |
| ingress.cert |Generate a certificate using cert-manager| false |
| ingress.annotations | ingress的注释 |{"kubernetes.io/ingress.class": "nginx","certmanager.k8s.io/cluster-issuer": "letsencrypt-prod"}|
|ingress.host.name| ingress记录的域名 | "" |
| ingress.tls |If there is no cert-manager and TLS is true, helm generates a self-signed certificate to be stored in secret| false |

