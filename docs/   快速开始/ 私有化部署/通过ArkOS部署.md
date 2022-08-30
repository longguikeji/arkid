# 通过ArkOS部署

ArkOS是用来安装K8s和ArkID的命令行工具。

部署时会预装一些应用：

* ArkID
* kuboard
* kubeapps

## 环境准备

### 准备运维操作机器：
> 需要准备一台机器来运行docker，用容器来部署arkid
> 一台centos7+或者ubuntu18+，安装有docker

以下docker环境也可以：

- mac安装docker desktop
- pc安装docker desktop
- pc WSL 2.0 子系统中安装docker

```shell
## linux系统快速安装docker

curl -sSL https://get.daocloud.io/docker | sh

```

### 准备部署arkid的机器
#### 一、单台机器部署
需要准备的文件
- hosts

```shell
## hosts 文件格式
## 只需修改ip地址和端口，还有用户名和密码
## 将hosts文件放到运维操作机器中的某个目录
[arkos-masters]
arkos-master01 hostname=arkos-master01 ansible_ssh_host=x.x.x.x ansible_ssh_port=22

[all:vars]
ansible_connection=ssh
ansible_user=root
ansible_password=xxxx

```
运行部署命令：
```shell
## 在运维操作机器执行
## 进入到hosts文件所在目录，执行命令来安装arkid
docker run --rm --mount type=bind,source="$(pwd)"/hosts,target=/etc/ansible/hosts harbor.longguikeji.com/ark-releases/arkos one

```


#### 二、多台机器部署(如5,6台)

需要准备的文件

- hosts

```shell
## hosts 文件格式
## 只需修改ip地址和端口，还有用户名和密码
## 在[arkos-nodes] 下添加或删减机器，记得递增序号
## 将hosts文件放到运维操作机器中的某个目录
[arkos-masters]
arkos-master01 hostname=arkos-master01 ansible_ssh_host=x.x.x.x ansible_ssh_port=22

[arkos-nodes]
arkos-node01 hostname=arkos-node01   ansible_ssh_host=x.x.x.x ansible_ssh_port=22
arkos-node02 hostname=arkos-node02   ansible_ssh_host=x.x.x.x ansible_ssh_port=22

[all:vars]
ansible_connection=ssh
ansible_user=root
ansible_password=xxxx


```

运行部署命令：

```shell
## 在运维操作机器执行
## 进入到hosts文件所在目录，执行命令来安装arkid
docker run --rm --mount type=bind,source="$(pwd)"/hosts,target=/etc/ansible/hosts harbor.longguikeji.com/ark-releases/arkos two

```



### 三、生产高可用部署(10+台机器)

> 两台机器用来部署 haproxy
> 三台机器作k8s master
> 其他机器作k8s node

> 需要准备的文件
> - hosts
```shell
## hosts 文件格式
## 只需修改ip地址和端口，还有用户名和密码
## 在[arkos-nodes] 下可以添加或删减机器，记得递增序号
## 将hosts文件放到运维操作机器中的某个目录
[arkos-has]
arkos-halb01 hostname=arkos-halb01 ansible_ssh_host=xx.xx.xx.xx ansible_ssh_port=22
arkos-halb02 hostname=arkos-halb02 ansible_ssh_host=xx.xx.xx.xx ansible_ssh_port=22

[arkos-masters]
arkos-master01 hostname=arkos-master01 ansible_ssh_host=xx.xx.xx.xx ansible_ssh_port=22
arkos-master02 hostname=arkos-master02 ansible_ssh_host=xx.xx.xx.xx ansible_ssh_port=22
arkos-master03 hostname=arkos-master03 ansible_ssh_host=xx.xx.xx.xx ansible_ssh_port=22

[arkos-nodes]
arkos-node01 hostname=arkos-node01 ansible_ssh_host=xx.xx.xx.xx ansible_ssh_port=22
arkos-node02 hostname=arkos-node02 ansible_ssh_host=xx.xx.xx.xx ansible_ssh_port=22

[all:vars]
ansible_connection=ssh
ansible_user=root
ansible_password=root
## 需要准备两个vip，ha_vip是用来给masters的apiserver做负载均衡的；lb_vip是用来给集群中的ingress做负载均衡的，也是需要外部DNS解析到的ip。
arkos_ha_vip=x.x.x.x
arkos_lb_vip=x.x.x.x


```

运行部署命令：

```shell
## 在运维操作机器执行
## 进入到hosts文件所在目录，执行命令来安装arkid
docker run --rm --mount type=bind,source="$(pwd)"/hosts,target=/etc/ansible/hosts harbor.longguikeji.com/ark-releases/arkos three

```

## 访问初始化arkid

浏览器打开网址：`http://{arkos-master01-ip}:32580`

首次打开arkid，需要输入访问url，此url只能输入这一次，需要慎重！！！

如果生产环境需要域名访问，那请配置好一切之后再填这个url！！！

初始化用户名：admin/admin

## 访问kuboard

浏览器打开网址：`http://{arkos-master01-ip}:32567`

token获取：

```
## 在 arkos-master01机器上执行
## 复制到 kuboard 登录页面上即可访问
echo $(kubectl -n kube-system get secret $(kubectl -n kube-system get secret | grep ^kuboard-user | awk '{print $1}') -o go-template='{{.data.token}}' | base64 -d)

```

## 访问kubeapps

浏览器打开网址：`http://{arkos-master01-ip}:32581`

token获取：

```
## 在 arkos-master01机器上执行
## 复制到 kubeapps 登录页面上即可访问
echo $(kubectl -n kube-system get secret $(kubectl -n kube-system get secret | grep ^kuboard-user | awk '{print $1}') -o go-template='{{.data.token}}' | base64 -d)

```

## 更新组件版本

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



