# 通过ArkOS部署

ArkOS是用来安装K8s和ArkID的命令行工具。

可以在部署时选装一些应用：

* ArkID `--arkid true(默认是true）`
* kuboard `--kuboard true(默认是false）`
* kubeapps `--kubeapps true（默认是false）`
* prometheus `--prometheus true （默认是false）`
* grafana LOKI `--loki true（默认是false）`
* 

## 环境准备

### 准备运维操作机器：
> 需要准备一台机器来运行docker，用容器来部署arkid
> 一台centos7+或者ubuntu18+，安装有docker

以下docker环境也可以：

- mac安装docker desktop
- pc安装docker desktop
- pc WSL 2.0 子系统中安装docker

```shell
## 安装docker

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


#### 二、多台机器部署

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

### 更新集群中的arkid

> !!! 生产环境推荐使用 gitops工具（如argoCD）来部署和管理
> chart源码仓库地址： https://github.com/longguikeji/arkid-charts.git

```shell
helm repo update

helm -n arkid upgrade arkid lgkj/arkid \
--set persistence.init=true
```