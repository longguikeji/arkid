# 用于 Python 的 ArkID Client

该 SDK 为 ArkID APIs 提供了便捷的 Pythonic 接口 。

## 基本用法

### 安装 

- pip install arkid-client

### 基本使用

- 您可以从 arkid_client 导入 ArkID 客户端。例如：


    from arkid_client.auth import ConfidentialAppAuthClient
    from arkid_client.client import ArkIDClient
    
    # 设置 ArkID 服务根地址
    url = 'https://arkid.longguikeji.com/'
    
    # 初始化 ArkID 认证客户端
    caac = ConfidentialAppAuthClient(base_url=url)
    
    # 初始化 ArkID 服务客户端
    ac = ArkIDClient(
        authorizer=caac.get_authorizer('admin', 'admin'), 
        base_url=url
    )
    
    # 查询用户列表
    users = ac.query_user()

## 链接

### 完整文档：
...

### 源代码：
https://github.com/longguikeji/arkid-core.git

### API文档：
https://arkid.docs.apiary.io/
