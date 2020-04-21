# 一账通UI自动化测试脚本运行              
本文描述如何运行一账通测试脚本。             
1、使用`git clone`将一账通源码克隆到本地。               
2、切换到测试脚本所在目录。                                   
3、`docker pull longguikeji/arkid-test:0.1.0`拉取镜像。                  
4、使用下面的命令运行镜像。                   
```
（1）make container
（2）docker exec -it arkid-test sh
（3）npm run test
```
注意：脚本运行时需要有一个已经搭建好并处于运行状态的ArkID实例，测试脚本会对该实例进行操作。
