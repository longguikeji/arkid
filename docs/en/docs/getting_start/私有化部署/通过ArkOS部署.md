# Deploy via ArkOS

ArkOS is a command line tool used to install K8s and ArkID.

Some applications are pre-installed during deployment:

* ArkID
* kuboard
* kubeapps

## Environmental preparation

### Prepare the machine for operation and maintenance:
> You need to prepare a machine to run docker and use the container to deploy arkid.
> A centos 7 + or ubuntu18 + with docker

The following docker environments are also available:

- Mac install docker desktop
- PC install docker desktop
- Install docker in the WSL 2.0 subsystem

```shell
## linux系统快速安装docker

curl -sSL https://get.daocloud.io/docker | sh

```

### Prepare the machine on which arkid is deployed
#### I. Single machine deployment
Documents to be prepared
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
Run the deployment command:
```shell
## 在运维操作机器执行
## 进入到hosts文件所在目录，执行命令来安装arkid
docker run --rm --mount type=bind,source="$(pwd)"/hosts,target=/etc/ansible/hosts harbor.longguikeji.com/ark-releases/arkos one

```


#### II. Deployment of multiple machines (e.g. 5,6)

Documents to be prepared

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

Run the deployment command:

```shell
## 在运维操作机器执行
## 进入到hosts文件所在目录，执行命令来安装arkid
docker run --rm --mount type=bind,source="$(pwd)"/hosts,target=/etc/ansible/hosts harbor.longguikeji.com/ark-releases/arkos two

```



### III. Production high availability deployment (10 + machines)

> Two machines to deploy haproxy
> Three machines for k8s master
> Other machines as k8s node

> Documents to be prepared
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

Run the deployment command:

```shell
## 在运维操作机器执行
## 进入到hosts文件所在目录，执行命令来安装arkid
docker run --rm --mount type=bind,source="$(pwd)"/hosts,target=/etc/ansible/hosts harbor.longguikeji.com/ark-releases/arkos three

```

## Access initialization arkid

The browser opens the URL: `http://{arkos-master01-ip}:32580`

Open arkid for the first time, you need to enter the access URL, this URL can only be entered this time, you need to be careful!!!

If the production environment requires domain access, then please configure everything before filling in this URL!!!

Initialize user name: admin/admin

## Visit kuboard

The browser opens the URL: `http://{arkos-master01-ip}:32567`

Token acquisition:

```
## 在 arkos-master01机器上执行
## 复制到 kuboard 登录页面上即可访问
echo $(kubectl -n kube-system get secret $(kubectl -n kube-system get secret | grep ^kuboard-user | awk '{print $1}') -o go-template='{{.data.token}}' | base64 -d)

```

## Visit kubeapps

The browser opens the URL: `http://{arkos-master01-ip}:32581`

Token acquisition:

```
## 在 arkos-master01机器上执行
## 复制到 kubeapps 登录页面上即可访问
echo $(kubectl -n kube-system get secret $(kubectl -n kube-system get secret | grep ^kuboard-user | awk '{print $1}') -o go-template='{{.data.token}}' | base64 -d)

```

## Update the component version

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



