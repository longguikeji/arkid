## Foreword
To facilitate the configuration of the development environment, ArkID only supports containerized development.

## I. Required tools
- The latest version of vscode
- Docker Desktop latest version and install plugins remote-containers, python
- docker-compose

## 2. Clone arkid code

```shell

## 可以先fork此仓库，然后clone下来fork后的仓库
git clone https://github.com/longguikeji/arkid.git
```

## 3. Start docker-compose

```shell
cd arkid/docker-compose
docker-compose up -d

## 需要等所有容器启动完成，首次启动可能需要几分钟
```

## 4. Vscode opens the environment in the container for development

- 1. Open vscode, click "Attach to Running Container" and select arkid-be
[![Z6nNNv.png](https://www.helloimg.com/images/2022/09/16/Z6nNNv.png)](https://www.helloimg.com/image/Z6nNNv)[![Z6nQuE.png](https://www.helloimg.com/images/2022/09/16/Z6nQuE.png)](https://www.helloimg.com/image/Z6nQuE)

- 2. After opening for the first time, you need to click to open the folder. The project file is in/arkid
> Ignore git changes in the container environment, because git commands cannot be used in the container for the time being, and you need to use git tools outside the container to pull, push, and so on

[![ Z6nzEY.md.png ](https://www.helloimg.com/images/2022/09/16/Z6nzEY.md.png)](https://www.helloimg.com/image/Z6nzEY)

- 4. Open the terminal of the container environment to view the process.

```shell
# 默认后端启动命令为 supervisord
# 查看进程状态：
supervisorctl status
# 关闭所有进程：
supervisorctl stop all
# 启动所有进程：
supervisorctl start all
```

- 5. Open the browser
> To open for the first time, you need to fill in the access address. Click OK d.
[![ Z6HMS6.md.png ](https://www.helloimg.com/images/2022/09/17/Z6HMS6.md.png)](https://www.helloimg.com/image/Z6HMS6)