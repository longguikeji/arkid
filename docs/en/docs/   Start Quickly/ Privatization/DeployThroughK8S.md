## k8sdeploy

> Pure cluster，The manually installed K8S cluster generally does not have additional components
>
> At least three machines

### 0、Configure Alibaba Cloud DNS domain name analysis：

- arkid.xxx.xxx  ==>  k8s master ip or Load balancing ip
- *.arkid.xxx.xxx ==> k8s master ip or Load balancing ip

### 1、storage：recommend Rook-Ceph or longhorn

> The choice of storage must be very cautious，Rook-Ceph and longhorn Both are relatively stable，The function is also very powerful，But the deployment is more complicated，The requirements are also relatively high
>
> Please install the document operation of the official website。Longhorn is best ubuntu+ext4; Rook-Ceph also recommends Ubuntu，The best at Yunyun is the best Ubuntu。

### 2、Gateway：Recommend Ingress-nginx or traefik

> If TrapeiK is installed as a gateway，There is no need to deploy CERT alone-manager and alidns webhook
>
> https://kubernetes.github.io/ingress-nginx/deploy/
>
> The following documents are in Ingress-Nginx as an example，TrayFik documentation and`K3S deployment`In the same way

```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.5.1/deploy/static/provider/cloud/deploy.yaml
```

### 3、Certificate management：cert-manager + alidns webhook

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
## Modify Bundle.in yaml acme.yourcompany.com change into acme.xxxx.com（The domain name of its own company）！
## The clusterissuer behind this group name is the same
kubectl apply -f bundle.yaml

# 2、 Create secret containing Alidns credentials
## Generate ACCESSKEY and Accesssecret under the Alibaba Cloud account（Given the domain name -related permissions）
## exist cert-manager Create secret in China
kubectl -n cert-manager create secret alidns-secret \
--from-literal=access-key=youraccesskey \
--from-literal=secret-key=youraccesssecret

# 3、create ClusterIssuer
## groupNameAlso changed to the same as above，email writes yourself，No need to change other
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

### 4、Pack management：Recommended helm-controller

```shell
CHARTCRD=`kubectl get crd|grep helmcharts.helm.cattle.io`
if [ -z "$CHARTCRD" ];then
    kubectl create -f https://gitee.com/longguikeji/arkid-charts/raw/main/helmchartscrd.yaml
fi
```

### 5、Deploy Arkid

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
      tls: true
      host:
        name: arkid.xxxx.xxx ## Fill in the correct domain name
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

## Install arkid
kubectl apply -f arkid.yaml

## Check
kubectl -n arkid get pods

## Wait a moment，Browser access：
https://arkid.xxx.xxx

## Notice：Open Arkid for the first time，There will be an input box for confirmation address，After the confirmation is confirmed, you can’t change it anymore！

```





## upgrade arkid chart version
```shell
kubectl -n arkid edit helmcharts arkid

## Modified version number，Save exit, Will update automatically
spec:
  chart: arkid
  version: 3.2.14
```

## More configuration
> https://github.com/longguikeji/arkid-charts.git
### Public configuration
| NAME | Description | DEFAULT VALUE |
| --- | --- | --- |
| imagePullSecrets | SECRET name of pulling the image | nil |
| persistence.init | Whether to create a new PVC，If it is set to false, the PVC of Claimname must exist | true |
| persistence.storageClass | storageclassname | nil |
| persistence.accessMode | pvcAccess mode | ReadWriteOnce |
| persistence.size | By default 8GB | 8GI |


### arkidConfiguration
| NAME | DESCRIPTION | DEFAULT VALUE |
| --- | --- | --- |
| fe.image | arkidFront -end mirror |  harbor.longguikeji.com/ark-releases/arkid-fe-In view of view:2.5.0 |
| fe.pullPolicy | IfNotPresent, Always | IfNotPresent |
| fe.resources.requests | arkidRequests at the front end | {"cpu": "800m","memory": "1024Mi"} |
| fe.resources.limits | arkidLimits at the front end | {} |
| be.image | arkidBack -end mirror |  harbor.longguikeji.com/ark-releases/arkid:2.5.0  |
| be.pullPolicy |  |  |
| be.resources.requests | arkidRequests at the back end | {"cpu": "800m","memory": "1024Mi"} |
| be.resources.limits | arkidLimits at the back end | {} |


### mysqlDatabase configuration
| NAME | Description | DEFAULT VALUE |
| --- | --- | --- |
| mysql.enabled | trueWill deploy a MySQL，If it is false, you need to set up the configuration under ExternalDataBase | true |
| externalDatabase.host | External MySQL database host | "" |
| externalDatabase.port | Port of the external MySQL database | 3306 |
| externalDatabase.database | The name of the outer MySQL database | "" |
| externalDatabase.user | User of external MySQL database | "" |
| externalDatabase.password | Password of external MySQL database | "" |


### redisConfiguration
| NaME | Description | DEFAULT VALUE |
| --- | --- | --- |
| redis.enabled | trueWill deploy a redis，If it is false, you need to set the configuration under Externalredis | true |
| externalRedis.host | Host of external redis | "" |
| externalRedis.port | External redis port | 6379 |
| externalRedis.db | DB of external redis | 0 |


### ingressConfiguration
| name | DEscription | default value |
| --- | --- | --- |
| ingress.enabled | Add Ingress record | false |
| ingress.cert | Use Cert-Manager generating certificate | false |
| ingress.annotations | ingressAnnotation | {"kubernetes.io/ingress.class": "nginx","certmanager.k8s.io/cluster-issuer": "Letsencrypt-prod"} |
| ingress.host.name | ingressRecorded domain name | "" |
| ingress.tls | if there is not cert-manager，TLS is True, and HELM will generate a self -signed certificate to the Secret | false |

