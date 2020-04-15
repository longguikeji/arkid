# 一账通UI自动化测试脚本运行              
本文描述如何运行一账通测试脚本。             
1、使用`git clone`将一账通源码克隆到本地。               
2、切换到测试脚本所在目录。                 
3、使用`npm install`安装依赖。                   
4、`docker pull longguikeji/arkid-test:0.1.0`拉取镜像。                  
5、运行镜像。                   
```
make container
docker exec -it arkid-test sh
npm run test
```
