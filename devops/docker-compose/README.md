# develop ArkID by docker-compose

1. docker-compose up -d

2. 打开 http://localhost:8989，以内置账号 admin / admin 登录。

3. 打开vscode，点击Remote-Containers插件，点击 **Remote-Containers: Attach to Running Container**，选择 **arkid-be**

4. 这样就进入了容器内部了，第一次可能还需要打开文件夹，项目文件在/root/workspace/arkid，现在就可以在容器内部开发了。

5、暴露端口到本机，点击Remote-Containers插件，点击 **Remote-Containers: Forward Port from Container**，选择暴露的端口，就可以测试接口了

更详细文档请看
