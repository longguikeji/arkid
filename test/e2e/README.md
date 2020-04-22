# 一账通UI自动化测试脚本运行              
本文描述如何运行一账通测试脚本。  
           
1、使用`git clone`将一账通源码克隆到本地，在本地通过[docker](https://www.docker.com/)部署一个一账通实例并使用`docker-compose`启动。               
2、将测试脚本src目录下`config.js`文件中的`url`改为本地部署的一账通地址。          
3、切换到测试脚本所在目录。                
4、`docker pull longguikeji/arkid-test:0.1.0`拉取镜像。                             
5、使用下面的命令运行镜像。                              
```
（1）make container
（2）docker exec -it arkid-test sh
（3）npm run test
```
>注意：启动的一账通实例需要与测试脚本在同一台宿主机。
