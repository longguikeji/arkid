## k3sdeploy

> k3sOnly recommend single nodes to use，The own component is enough

- storage：local-storage（Can only be used by a single machine）
- Gateway：traventual（ = ingress + cert-manager + alidns webhook）
- helm-controller：Manage the helm package

### k3sInstall：

```shell
curl -sfL https://rancher-mirror.oss-cn-beijing.aliyuncs.com/k3s/k3s-install.sh | INSTALL_K3S_MIRROR=cn sh -
```

### Configure Alibaba Cloud DNS domain name analysis：

- arkid.xxx.xxx ==> k3s ip
- *.arkid.xxx.xxx  ==>  k3s ip

### Configure TrayFik 

> cert-managerDomain name authentication，The domain name of the signing certificate must be you，In order to issue a TLS certificate normally。
>
> Generate ACCESSKEY and Accesssecret under the Alibaba Cloud account（Given the domain name -related permissions）

```shell
## exist be-system Create secret in China
kubectl -n kube-system create secret alidns-secret \
--from-literal=ALICLOUD_ACCESS_KEY=youraccesskey \
--from-literal=ALICLOUD_SECRET_KEY=youraccesssecret


## k3sThe configuration of its own component is in /was/lib/rancher/Stick/server/manifests
vi /var/lib/rancher/k3s/server/manifests/traefik-config.yaml
## emailThe address is changed to your own，After saving and exiting, it will be updated automatically

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





### Deploy Arkid

> Recommended helm with K3S comes with-Controller to deploy Chart

```shell
## Create naming space
kubectl create ns arkid

## Editing file arkid.yaml
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
        name: arkid.xxxx.xxx ## Fill in the correct domain name
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

## Install arkid
kubectl apply -f arkid.yaml

## Check
kubectl -n arkid get pods

## Wait a moment，Browser access：
https://arkid.xxx.xxx

## Notice：Open Arkid for the first time，There will be an input box for confirmation address，After the confirmation is confirmed, you can’t change it anymore！

```
