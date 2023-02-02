## k3s部署

> k3s只推荐单节点使用，自带的组件已经足够用了

- 存储：local-storage（只能单机使用）
- 网关：traefik（ = ingress + cert-manager + alidns webhook）
- helm-controller：管理helm包

### k3s安装：

```shell
curl -sfL https://rancher-mirror.oss-cn-beijing.aliyuncs.com/k3s/k3s-install.sh | INSTALL_K3S_MIRROR=cn sh -
```

### 配置阿里云dns域名解析：

- arkid.xxx.xxx ==> k3s ip
- *.arkid.xxx.xxx  ==>  k3s ip

### 配置traefik 

> cert-manager的域名认证，必须验证签署证书的域名是属于你，才能正常签发TLS证书。
>
> 在阿里云账户下生成accesskey和accesssecret（赋予域名相关的权限）

```shell
## 在 kube-system 中创建secret
kubectl -n kube-system create secret alidns-secret \
--from-literal=ALICLOUD_ACCESS_KEY=youraccesskey \
--from-literal=ALICLOUD_SECRET_KEY=youraccesssecret


## k3s自带组件的配置在 /var/lib/rancher/k3s/server/manifests
vi /var/lib/rancher/k3s/server/manifests/traefik-config.yaml
## email地址改为自己的，保存退出之后稍等就会自动更新成功

apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    persistence:
      enabled: true
    additionalArguments:
    - "--certificatesResolvers.ali.acme.dnsChallenge.provider=alidns"
    - "--certificatesResolvers.ali.acme.email=youremail@xxxx"
    - "--certificatesResolvers.ali.acme.storage=/data/acme.json"
    envFrom:
    - secretRef:
        name: alidns-secret

```





### 部署arkid

> 推荐使用k3s自带的helm-controller来部署chart

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
      host:
        name: arkid.xxxx.xxx ## 填正确的域名
      annotations:
        kubernetes.io/ingress.class: traefik
        traefik.ingress.kubernetes.io/router.entrypoints: websecure
        traefik.ingress.kubernetes.io/router.tls.certresolver: ali
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