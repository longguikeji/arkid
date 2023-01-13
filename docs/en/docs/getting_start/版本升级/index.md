## Upgrade method using ArkOS deployment

- arkid
> - Check the new version number on github
> - `https://github.com/longguikeji/arkid-charts/releases`
> - Modify the version number of the deployment file and log in to arkos-master01
> - Path to deployment file:
>   - File location for the first two deployments:/var/lib/rancher/k3s/server/manifests/arkid. Yaml
>   - The last highly available deployment file location is/var/lib/rancher/k3s/server/manifests/arkid. Yaml.
>   - Automatically updated after saved

```yaml
## 修改 version字段，保存退出，稍后会完成更新

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
> - Check the new version number at ArtifactHUB
> - `https://artifacthub.io/packages/helm/bitnami/kubeapps`
> - Modify the version number of the deployment file and log in to arkos-master01
> - Path to deployment file:
>   - File location for the first two deployments:/var/lib/rancher/k3s/server/manifests/kubeapps. Yaml
>   - The last highly available deployment file location is/var/lib/rancher/k3s/server/manifests/kubeapps. Yaml.
>   - Automatically updated after saved

```yaml
## 修改 version字段，保存退出，稍后会完成更新

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


## Upgrade method using Docker deployment

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

## Upgrade method using K8S deployment

```shell
helm repo update

helm -n arkid upgrade arkid lgkj/arkid \
--set persistence.init=true
```
