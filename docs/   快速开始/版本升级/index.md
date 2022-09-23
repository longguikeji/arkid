

## 使用ArkOS部署的升级方法

- arkid
> - 在github查看新版本号
> - `https://github.com/longguikeji/arkid-charts/releases`
> - 修改部署文件版本号，登录 arkos-master01操作
> - 部署文件的路径：
>   - 前两种部署的文件位置：/var/lib/rancher/k3s/server/manifests/arkid.yaml
>   - 最后一种高可用的部署文件位置：/var/lib/rancher/k3s/server/manifests/arkid.yaml
>   - 保存之后会自动更新

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
> - 在ArtifactHUB查看新版本号
> - `https://artifacthub.io/packages/helm/bitnami/kubeapps`
> - 修改部署文件版本号，登录 arkos-master01操作
> - 部署文件的路径：
>   - 前两种部署的文件位置：/var/lib/rancher/k3s/server/manifests/kubeapps.yaml
>   - 最后一种高可用的部署文件位置：/var/lib/rancher/k3s/server/manifests/kubeapps.yaml
>   - 保存之后会自动更新

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


## 使用Docker部署的升级方法

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

## 使用K8S部署的升级方法

```shell
helm repo update

helm -n arkid upgrade arkid lgkj/arkid \
--set persistence.init=true
```
