## 前言
为了方便配置开发环境，ArkID仅支持用容器化的方式开发。

## 一、所需工具
- vscode 最新版
- Docker Desktop 最新版并安装插件 remote-containers、python
- docker-compose

## 二、克隆arkid代码

```shell

## 可以先fork此仓库，然后clone下来fork后的仓库
git clone https://github.com/longguikeji/arkid.git
```

## 三、启动 docker-compose

```shell
cd arkid/docker-compose
docker-compose up -d

## 需要等所有容器启动完成，首次启动可能需要几分钟
```

## 四、vscode打开容器中的环境，进行开发

- 1、打开vscode，点击“Attach to Running Container”, 选择arkid-be
[![Z6nNNv.png](https://www.helloimg.com/images/2022/09/16/Z6nNNv.png)](https://www.helloimg.com/image/Z6nNNv)
[![Z6nQuE.png](https://www.helloimg.com/images/2022/09/16/Z6nQuE.png)](https://www.helloimg.com/image/Z6nQuE)

- 2、第一次打开之后需要点击 打开文件夹，项目文件在 /arkid
> 忽略容器环境中的git变更，因为暂时在容器中无法使用git命令，需要使用容器外的git工具来进行拉取推送等操作

[![Z6nzEY.md.png](https://www.helloimg.com/images/2022/09/16/Z6nzEY.md.png)](https://www.helloimg.com/image/Z6nzEY)

- 4、打开容器环境的终端，查看进程

```shell
# 默认后端启动命令为 supervisord
# 查看进程状态：
supervisorctl status
# 关闭所有进程：
supervisorctl stop all
# 启动所有进程：
supervisorctl start all
```

- 5、打开浏览器 `http://localhost:8989`
> 首次打开需要填访问地址，点确定d
[![Z6HMS6.md.png](https://www.helloimg.com/images/2022/09/17/Z6HMS6.md.png)](https://www.helloimg.com/image/Z6HMS6)