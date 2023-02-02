## Foreword
In order to facilitate the configuration development environment，ARKID only supports development with containerization。

## one、Required tools
- vscode new
- Docker Desktop The latest version and install plug -in remote-containers、python
- docker-compose

## two、Cloning ARKID code

```shell

## You can give this warehouse first，Then the clone down fork the warehouse
git clone https://github.com/longguikeji/arkid.git
```

## three、start up docker-compose

```shell
cd arkid/docker-compose
docker-compose up -d

## Need to wait for all containers to start completed，It may take a few minutes to start for the first time
```

## Four、VSCODE opens the environment in the container，Develop

- 1、Open VSCODE，Clicked“Attach to Running Container”, Choose Arkid-be
[![Z6nNNv.png](https://www.helloimg.com/images/2022/09/16/Z6nNNv.png)](https://www.helloimg.com/image/Z6nNNv)
[![Z6nQuE.png](https://www.helloimg.com/images/2022/09/16/Z6nQuE.png)](https://www.helloimg.com/image/Z6nQuE)

- 2、You need to click after the first opening Open the folder，The project file is /arkid
> Ignore git changes in the container environment，Because the Git command cannot be used in the container，You need to use the GIT tool outside the container for pulling push and other operations

[![Z6nzEY.md.png](https://www.helloimg.com/images/2022/09/16/Z6nzEY.md.png)](https://www.helloimg.com/image/Z6nzEY)

- 4、Open the terminal of the container environment，View process

```shell
# The default rear start command is supervisord
# View process status：
supervisorctl status
# Turn off all processes：
supervisorctl stop all
# Start all processes：
supervisorctl start all
```

- 5、Open the browser `http://localhost:8989`
> You need to fill in the access address for the first time，Click OK D
[![Z6HMS6.md.png](https://www.helloimg.com/images/2022/09/17/Z6HMS6.md.png)](https://www.helloimg.com/image/Z6HMS6)
