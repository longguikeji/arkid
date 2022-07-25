# CasServer

CAS是Central Authentication Service的缩写，中央认证服务。当用户访问CAS认证服务器，请求身份验证。CAS认证服务会检查用户是否登录。如果没登录就去登录，如果已经登录，CAS会发放一个一次性短时间的TGT票据，并重定向到开发者提供的service地址。然后，应用程序通过安全连接连接CAS，并提供自己的服务标识和验证票。之后CAS给出了关于特定用户的身份信息

整个认证过程如图所示:

``` mermaid
graph LR
  A[开始] --> B[访问登录页] --> C{是否登录}--> |Yes| D[带上票据跳转到service地址]--> E[使用票据获取用户信息] --> F[结束];
  C ---->|No| G[登录!];
  G --> |登录成功| D;
```

## Cas认证

### 创建应用

=== "打开应用列表"
    [![jxpxtP.md.jpg](https://s1.ax1x.com/2022/07/25/jxpxtP.md.jpg)](https://imgtu.com/i/jxpxtP)
=== "新建Cas应用"
    [![jx9Fmj.md.jpg](https://s1.ax1x.com/2022/07/25/jx9Fmj.md.jpg)](https://imgtu.com/i/jx9Fmj)
=== "在列表点击协议配置"
    [![jx9Zt0.md.jpg](https://s1.ax1x.com/2022/07/25/jx9Zt0.md.jpg)](https://imgtu.com/i/jx9Zt0)
=== "选择类型为Cas并确认"
    [![jx9MX4.md.jpg](https://s1.ax1x.com/2022/07/25/jx9MX4.md.jpg)](https://imgtu.com/i/jx9MX4)
=== "在列表再次点击协议配置"
    [![jx9TNq.md.jpg](https://s1.ax1x.com/2022/07/25/jx9TNq.md.jpg)](https://imgtu.com/i/jx9TNq)
=== "保存登录和校验地址"
    [![jxCi8K.md.jpg](https://s1.ax1x.com/2022/07/25/jxCi8K.md.jpg)](https://imgtu.com/i/jxCi8K)


### 使用 Cas 应用
1.  将登录链接放在需要登录的第三方页面

    这里需要让用户通过链接访问arkid这边的统一认证。service参数是arkid认证完后的回调地址。

    http://localhost:9528/api/v1/tenant/4da114ce-e115-44a0-823b-d372114425d0/app/e78f117b-1632-42c9-8e3c-ec4fd796c89e/cas/login/?service=http://www.baidu.com

    页面会自动跳到进行登录

    http://localhost:9528/login?next=/api/v1/tenant/4da114ce-e115-44a0-823b-d372114425d0/app/e78f117b-1632-42c9-8e3c-ec4fd796c89e/cas/login/%3Fservice%3Dhttp%3A//www.baidu.com&tenant_id=4da114ce-e115-44a0-823b-d372114425d0

2. 登录成功后会取得一个票据

    https://www.baidu.com/?ticket=ST-1658743424-pvotuhaInoW1UGQlIlD1eLU6tZoMppu6

3. 通过校验地址获取用户信息

    一个票据只能用一次，service要和前面登录的相同，如果成功可以获取到用户信息

    [![jxCIMD.md.jpg](https://s1.ax1x.com/2022/07/25/jxCIMD.md.jpg)](https://imgtu.com/i/jxCIMD)

    如果你试图用已经使用过的票据就会返回

    [![jxCHZd.md.jpg](https://s1.ax1x.com/2022/07/25/jxCHZd.md.jpg)](https://imgtu.com/i/jxCHZd)

    需要每次登录先拿票据然后用票据换取用户信息