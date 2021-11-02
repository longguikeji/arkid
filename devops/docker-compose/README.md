# develop ArkID by docker-compose

```shell
docker-compose up -d
```

## vscode 进入容器arkid-be，开发后端
> 查看进程状态：
> supervisorctl status
> 关闭所有进程：
> supervisorctl stop all
> 启动所有进程：
> supervisorctl start all


## vscode 进入容器arkid-fe，开发前端
> 安装依赖：
> npm install
> 启动进程：
> npm run dev


查看效果：http://localhost:8989