# 用于 Python 的 ArkID Client

该 SDK 为 ArkID APIs 提供了便捷的 Pythonic 接口 。

## 基本用法

### 安装 

- pip install arkid-client

### 基本使用

- 您可以从 arkid_client 导入 ArkID 客户端。例如：


    from arkid_client.auth.client import ConfidentialAppAuthClient
    from arkid_client.authorizers import BasicAuthorizer
    from arkid_client.client import ArkIDClient
    from arkid_client.config import set_config_path
    
    set_config_path('/usr/home/oneid.cfg')
    cc = ConfidentialAppAuthClient()
    ba = BasicAuthorizer(ac.auth_to_get_token('admin', 'admin'))
    ac = ArkIDClient(authorizer=ba)
    users = ac.query_user()

## 链接

### 完整文档：
...

### 源代码：
https://github.com/longguikeji/arkid-core.git

### API文档：
https://arkid.docs.apiary.io/
