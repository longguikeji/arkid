# 代码结构

本文档旨在介绍 arkid-core 的代码结构

```
├── Dockerfile
├── LICENSE.md
├── Makefile
├── Pipfile
├── Pipfile.lock
├── README.md
├── celery_app.py              // 异步任务由 celery 实现
├── common                     // 通用类工具
├── devops                     // 主要为 jenkinsfile，用于内部的自动集成与部署
├── djangosaml2idp             // SAML Server 实现代码，基于第三方库二次开发
├── docker-compose             // 以 docker-compose 方式运行 ArkID 所需的配置
├── docs
├── drf_expiring_authtoken     // token 生成与校验，基于第三方库二次开发
├── executer                   // 人员、组织架构调整的底层接口
│   ├── Ding
│   ├── LDAP
│   ├── RDB
│   ├── cache
│   ├── core.py
│   ├── log
│   ├── tests
│   └── utils
├── infrastructure             // 基础服务，例如短信服务、图片验证码服务
├── ldap                       // LDAP server 构建所需文件，以及必要的数据库兼容性迁移声明
├── locale                     // 国际化
├── manage.py
├── oauth2_provider            // OAuth2.0 Server、OIDC Server 实现代码，基于第三方库二次开发
├── oneid
│   ├── __init__.py
│   ├── auth_backend.py        // 自定义的认证后端，关于登陆时如何判断一份凭证是否正确
│   ├── authentication.py      // 自定义的接口认证方式，关于如何判断一个请求的发起者的身份
│   ├── permissions.py         // 自定义的权限
│   ├── settings.py            // Django 核心配置文件
│   ├── settings_example.py    // 对`本地运行时如何修改配置文件`作出的示例
│   ├── settings_test.py       // 仅用于单元测试的配置文件
│   ├── settings_test_with_data.py  // 仅用于功能测试、回归测试的配置文件
│   ├── statistics.py          // 用户统计，类似于中间件
│   ├── urls.py                // Django 路由入口
│   ├── utils.py               // 项目全局变量
│   └── wsgi.py                // WSGI 配置
├── oneid_meta
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   └── models                  // 表结构设计
│       ├── __init__.py
│       ├── app.py              // 应用
│       ├── config.py           // 配置
│       ├── dept.py             // 部门
│       ├── event.py            // 事件
│       ├── group.py            // 组
│       ├── log.py              // 日志
│       ├── mixin.py            // 部分通用属性的抽象
│       ├── perm.py             // 权限
│       └── user.py             // 人员
├── requirements-dev.txt
├── requirements.txt
├── scripts
├── siteadmin
├── siteapi
│   ├── __init__.py
│   └── v1                      // 接口实现
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── blueprint.md        // 接口文档
│       ├── serializers         // 序列化定义
│       ├── tests               // 单元测试
│       ├── ucenter.md          // 对于如何用一批接口实现复杂功能的说明
│       ├── urls.py
│       └── views               // 接口核心实现
├── supervisord.conf            // docker 容器中由 supervisord 管理进程
├── tasksapp                    // 周期性任务由 django_celery_beat 实现
│   ├── README.md
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   ├── models.py
│   └── tasks.py
├── test                         // 功能测试所用数据，以及复杂数据背景下的部分接口测试
├── thirdparty_data_sdk          // 第三方 SDK
│   ├── __init__.py
│   ├── alipay_api
│   ├── dingding
│   ├── error_utils.py
│   ├── qq_sdk
│   ├── wechat_sdk
│   └── work_wechat_sdk
└── uwsgi.ini                    // WSGI 配置
```

## 建议源码阅读顺序

1. 设计文档 `docs`

2. 表结构设计 `oneid_meta/models`

3. 接口路由 `siteapi/v1/urls.py`

4. 接口实现 `siteapi/v1/views`

## 错误排查顺序

1. 接口路由 `siteapi/v1/urls.py`

2. 接口实现 `siteapi/v1/views`

3. 接口序列化 `siteapi/v1/serializers`

认证、权限相关则从 `oneid/settings.py` 出发，主要关注 `REST_FRAMEWORK`, `AUTHENTICATION_BACKENDS` 两项配置
