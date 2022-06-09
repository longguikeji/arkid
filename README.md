# ArkID - v2

产品介绍：https://arkid.cc

产品试用：https://saas.arkid.cc/ 先注册用户，再登录使用

**DO NOT USE THIS VRESION IN PRODUCTION (请勿在生产环境中使用)**

# QuickStart

## docker-compose 启动

## arkid v2.0

    git clone --branch v2-dev --depth 1  https://github.com/longguikeji/arkid-charts.git

    cd arkid-charts/docker-compose

    docker-compose up -d


Open your browser and visit http://localhost:8989

default admin account

username: **admin**

password: **admin**

## Helm Charts 方式部署
请查看详细文档：https://github.com/longguikeji/arkid-charts/tree/v2-dev/chart


## 开发环境
https://www.yuque.com/longguikeji/arkid2/nr77mt

1. 用git clone下代码，切换到 v2-dev分支
2. 安装依赖库，本项目使用了pipenv。
pipenv install
注意：pipenv在pipfile中默认使用的是python 3.6，可根据各自情况安装或更改python的版本。

3. 启动服务
python manager.py runserver
