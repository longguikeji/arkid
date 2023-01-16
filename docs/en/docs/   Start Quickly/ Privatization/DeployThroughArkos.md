# Deploy through ARKOS

ArkOSIt is a command line tool used to install K8S and Arkid。

Some applications will be pre -installed when deploying：

* ArkID
* kuboard
* kubeapps

## Environmental preparation

### Prepare operation and maintenance operation machine：
> Need to prepare a machine to run docker，Use a container to deploy ARKID
> One CentOS7+Or ubuntu18+，Install docker

The following docker environment is also fine：

- macInstall docker desktop
- pcInstall docker desktop
- pc WSL 2.0 Install docker in the subsystem

```shell
## linuxThe system quickly installs docker

curl -sSL https://get.daocloud.io/docker | sh

```

### Prepare to deploy ARKID machines
#### one、Single machine deployment
Documents that need to be prepared
- hosts

```shell
## hosts file format
## Just modify the IP address and port，There are also usernames and passwords
## Put the hosts file into a directory in the operation and maintenance operation machine
[arkos-masters]
arkos-master01 hostname=arkos-master01 ansible_ssh_host=x.x.x.x ansible_ssh_port=22

[all:vars]
ansible_connection=ssh
ansible_user=root
ansible_password=xxxx

```
Operating deployment command：
```shell
## Execute the machine in operation and maintenance operation
## Enter the directory where the hosts file is located，Execute the command to install ARKID
docker run --rm --mount type=bind,source="$(pwd)"/hosts,target=/etc/ansible/hosts harbor.longguikeji.com/ark-releases/arkos one

```


#### two、Multiple machine deployment (such as 5,6)

Documents that need to be prepared

- hosts

```shell
## hosts file format
## Just modify the IP address and port，There are also usernames and passwords
## In [Arkos-nodes] Add or delete the machine，Remember to increase the serial number
## Put the hosts file into a directory in the operation and maintenance operation machine
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

Operating deployment command：

```shell
## Execute the machine in operation and maintenance operation
## Enter the directory where the hosts file is located，Execute the command to install ARKID
docker run --rm --mount type=bind,source="$(pwd)"/hosts,target=/etc/ansible/hosts harbor.longguikeji.com/ark-releases/arkos two

```



### three、Production high available deployment (10+Taiwan machine)

> Two machines are used to deploy haproxy
> Three machines as K8S master
> Other machines as K8S node

> Documents that need to be prepared
> - hosts
```shell
## hosts file format
## Just modify the IP address and port，There are also usernames and passwords
## In [Arkos-nodes] You can add or delete the machine，Remember to increase the serial number
## Put the hosts file into a directory in the operation and maintenance operation machine
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
## Need to prepare two VIPs，ha_VIP is used to make a load balancing for the APISERVER of Masters；lb_VIP is used to make a load balancing for the Ingress in the cluster，It is also an IP that needs external DNS parsing。
arkos_ha_vip=x.x.x.x
arkos_lb_vip=x.x.x.x


```

Operating deployment command：

```shell
## Execute the machine in operation and maintenance operation
## Enter the directory where the hosts file is located，Execute the command to install ARKID
docker run --rm --mount type=bind,source="$(pwd)"/hosts,target=/etc/ansible/hosts harbor.longguikeji.com/ark-releases/arkos three

```

## Visit initial ARKID

Browser open URL：`http://{arches-master01-ip}:32580`

Open Arkid for the first time，Need to enter access URL，This url can only enter this time，Need to be cautious！！！

If the production environment requires domain name access，Please configure everything before filling this url！！！

Initialized username：admin/admin

## Visit Kuboard

Browser open URL：`http://{arches-master01-ip}:32567`

tokenObtain：

```
## exist arches-execute on the master01 machine
## copy to kuboard You can access it on the login page
echo $(kubectl -n kube-system get secret $(kubectl -n kube-system get secret | grep ^kuboard-user | awk '{print $1}') -o go-template='{{.data.token}}' | base64 -d)

```

## Visit Kubeapps

Browser open URL：`http://{arches-master01-ip}:32581`

tokenObtain：

```
## exist arches-execute on the master01 machine
## copy to kubeapps You can access it on the login page
echo $(kubectl -n kube-system get secret $(kubectl -n kube-system get secret | grep ^kuboard-user | awk '{print $1}') -o go-template='{{.data.token}}' | base64 -d)

```

## Update component version

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



