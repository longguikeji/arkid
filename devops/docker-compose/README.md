# run ArkID by docker-compose

### docker-compose 方式部署
```shell
## arkid v2.0
git clone --branch v2-dev --depth 1  https://github.com/longguikeji/arkid-charts.git

cd arkid-charts/docker-compose

# 1. 按提示修改 .env 文件、settings_local.py 文件

# 2. $> docker-compose up -d

# 3. 打开 http://localhost:8989 (具体端口视 .env 中 HTTP_PORT 而定)，以内置账号 admin / admin 登录。

```