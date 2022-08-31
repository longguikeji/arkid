
# 通过docker-compose部署

```shell
# 下载 arkid 部署文件
git clone https://github.com/longguikeji/arkid-charts.git

cd arkid-charts/docker-compose

# 启动
docker-compose up -d

# 打开 http://localhost:8989 (具体端口视 .env 中 HTTP_PORT 而定)

```

## 部署完成，初始化访问


> 浏览器打开[http://localhost:8989](http://localhost:8989)，
> 
> 首次打开arkid，需要输入访问url，此url只能输入这一次，需要慎重！！！
> 
> 如果生产环境需要域名访问，那请配置好一切之后再填这个url！！！
> 
> 内置账号 admin / admin 登录，探索ArkID的完整功能。




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
