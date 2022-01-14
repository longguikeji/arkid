# develop ArkID by docker-compose

详细文档：https://www.yuque.com/longguikeji/arkid2/zunn5q

请仔细阅读以上文档！
需要把arkid和arkid-frontend放在同级目录下！

```shell
docker-compose up -d
```

## vscode 进入容器arkid-be，开发后端
```shell
# 查看进程状态：
supervisorctl status
# 关闭所有进程：
supervisorctl stop all
# 启动所有进程：
supervisorctl start all
```

## vscode 进入容器arkid-fe，开发前端
```shell
# 安装依赖：
npm install
# 启动进程：
npm run dev


查看效果：http://localhost:8989
