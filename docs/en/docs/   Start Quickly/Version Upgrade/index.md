

## Use Arkos deployment upgrade method

- arkid
> - View the new version number in github
> - `https://github.com/longguikeji/arkid-charts/releases`
> - Modify the deployment file version number，Log in arches-Master01 operation
> - Path of deployment files：
>   - The location of the first two deployment：/was/lib/rancher/Stick/server/manifests/arkid.yaml
>   - The last high available deployment file location：/was/lib/rancher/Stick/server/manifests/arkid.yaml
>   - After saving, it will be updated automatically

```yaml
## Revise version field，Save exit，Will complete the update later

apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: arkid
  namespace: kube-system
spec:
  chart: arkid
  version: 3.0.13
  repo: https://harbor.longguikeji.com/chartrepo/public
  targetNamespace: arkid

```


- kubeapps
> - View the new version number in Artifacthub
> - `https://artifacthub.io/packages/helm/bitnami/kubeapps`
> - Modify the deployment file version number，Log in arches-Master01 operation
> - Path of deployment files：
>   - The location of the first two deployment：/was/lib/rancher/Stick/server/manifests/kubeapps.yaml
>   - The last high available deployment file location：/was/lib/rancher/Stick/server/manifests/kubeapps.yaml
>   - After saving, it will be updated automatically

```yaml
## Revise version field，Save exit，Will complete the update later

apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: kubeapps
  namespace: kube-system
spec:
  chart: kubeapps
  version: 10.3.1
  repo: https://harbor.longguikeji.com/chartrepo/public
  targetNamespace: kubeapps

```


## Using docker deployment upgrade method

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

## The upgrade method deployed with K8S

```shell
helm repo update

helm -n arkid upgrade arkid lgkj/arkid \
--set persistence.init=true
```
