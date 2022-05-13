# 通过ArkOS部署

ArkOS是以K8s及其生态为基础，使用ArkID作为其核心来构建的一套类PaaS系统。

系统预装了下列系统并默认使用OIDC协议联通：

* ArkID
* kuboards

## 环境准备

需要准备一台机器来运行docker，用容器来部署arkid
一台centos7+或者ubuntu18+，安装有docker

以下docker环境也可以：

- mac安装docker desktop
- pc安装docker desktop
- pc WSL 2.0 子系统中安装docker

```shell
## 安装docker

curl -sSL https://get.daocloud.io/docker | sh

```

## 单台机器部署
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


## 多台机器部署

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