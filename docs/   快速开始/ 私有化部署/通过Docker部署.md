
# 通过docker-compose部署

```shell
# 下载 arkid 部署文件
git clone https://github.com/longguikeji/arkid-charts.git

cd arkid-charts/docker-compose

# 修改 .env 文件、settings_local.py、arkid.local.toml 文件
# 默认的访问地址是 http://localhost:8989
# 如果是其他地址访问，则需要更改 arkid.local.toml 文件
# 例如：http://192.168.184.133:8989, 修改arkid.local.toml文件如下
# 
# name = "arkid v2"
# host = '192.168.184.133:8989'
# frontend_host = '192.168.184.133:8989'
# https_enabled = 0


# 启动
docker-compose up -d

# 打开 http://localhost:8989 (具体端口视 .env 中 HTTP_PORT 而定)
# 内置账号 admin / admin 登录。

```

## 部署完成

浏览器打开[http://localhost:8989](http://localhost:8989)，探索ArkID的完整功能

# 更新docker-compose部署版本
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
