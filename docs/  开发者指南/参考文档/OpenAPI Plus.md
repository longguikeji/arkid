# OpenAPI Plus

OpenAPI-Plus 使用[`django-ninja`](https://github.com/vitalik/django-ninja)和[`pydantic`](https://github.com/samuelcolvin/pydantic)进行功能扩展，以达到适配 ArkID 一账通项目前端生成的目的。

OpenAPI-Plus 主要讲述对其进行了哪些扩展，而这些扩展又有什么样的含义存在呢？请继续阅读文档。

## 扩展一: 路由（routers）

其主要声明前端路由信息，通过读取解析 routers 中内容，生成前端侧边栏等内容。一共可以分为两种类别：

- 有 Children 的路由
- 无 Children 的路由

| 关键字 | 含义                                                                   | 类型            |
| ------ | ---------------------------------------------------------------------- | --------------- |
| path   | 前端访问路径，使用/字符进行叠加                                        | string          |
| name   | 侧边栏路由名称                                                         | string          |
| icon   | 侧边栏路由图标，需与前端配合声明                                       | string          |
| hidden | 是否隐藏，如果为 true，则不展示在前端侧边栏中                          | boolean         |
| page   | 该路由需要渲染的页面，具体信息指向 [pages](#pages) 扩展                | string          |
| url    | 直接访问该URL接口，默认为GET，接口返回新的url地址，放入iframe中显示      | string          |
| web    | 是否为电脑端侧边栏，可以含有顺序                                       | number, boolean |
| mobile | 是否为手机端底边栏，并含有顺序                                         | number, boolean |

!!! attention "重要声明" 
    01. path 不能使用 `.` 等特殊字符。 
    02. page 不能使用 `[ ] { }` 等特殊字符。

```json title='有Children路由示例'
{
  "path": "mine",
  "name": "我的",
  "icon": "mine",
  "hidden": true,
  "children": [
    {
      "path": "profile",
      "name": "个人管理",
      "page": "mine_profile",
      "icon": "profile"
    },
    {
      "path": "logout",
      "name": "退出登录",
      "page": "mine_logout",
      "icon": "logout"
    }
  ]
}
```

```json title='无Children路由示例'
{
  "path": "mine",
  "name": "我的",
  "icon": "mine",
  "hidden": true,
  "page": "mine"
}
```

## 扩展二: 页面配置（pages）

声明前端页面生成所需要的配置信息，前端将会根据OpenAPI返回的该项内容进行解析处理，从而生成前端各种类型的页面。下面将详细说明每一项配置的含义以及对应怎么表达和展示在前端。

!!! info "问题"
    01. 生成一个表格或表单页面，需要那些配置信息呢？
    02. 生成一个树结构页面呢？
    03. 页面之间有什么区别呢？

### 页面类型

针对以上问题，先给出我们目前`已支持 ✔`或`待支持 ✘`的页面类型。

| 类型 | 名称 | 支持性 |
| --- | --- | --- |
| table | 表格型页面 | ✔ |
| form | 表单型页面 | ✔ |
| tree | 树状性页面 | ✔ |
| tabs | 切换型页面 | ✔ |
| description | 描述型页面 | ✔ |
| cards | 卡片型页面 | ✔ |
| grid | 网格型页面 | ✘ |
| list | 列表型页面 | ✘ |
| step | 步骤型页面 | ✔ |

### 页面配置

对页面中所需的配置进行说明，以支持上述各类型页面的生成情形。

| 关键字 | 含义 | 功能 | 附加说明 |
| --- | --- | --- | --- |
| type | 页面类型 | 生成前端页面模板 | 具体参考下面的页面类型说明 |
| tag | 页面标识符 | 匹配唯一页面配置 | 页面唯一标签 |
| name | 页面名称 | 对应显示前端页面标题 | 需支持中英文 |
| init_action | [页面初始化操作](#_6) | 获取schema和数据 | 具体参考init_action详细说明 |
| init_data | 初始化数据 | 初始化后的赋值操作 | 默认从父级数据池开始查找 |
| global_action | [页面全局操作](#_7) | 生成全局按钮操作 | 具体参考global_action详细说明 |
| local_action | [页面局部操作](#_8) | 生成局部按钮操作 | 具体参考local_action详细说明 |
| node_action | [页面节点操作](#_9) | 生成节点点击操作 | 可能存在于tree/cards等页面中，具体参考node_action详细说明 |
| select | 是否为可选页面 | 生成可选页面 | form页面中无需该字段 |
| pages | tabs/step多页面指向 | 生成tabs/step多页面 | 只存在于tabs/step页面中 |

!!! attention "重要提示"
    1. tag 不能只有`[ ] { }`等特殊字符
    2. tag 同一个页面下不要重复声明一个页签


### 页面操作

  页面主要配置就是有多个操作组成的。包含初始化数据获取操作，增删改查等点击操作。所以操作配置有着极为重要的含义和详细配置声明。

##### 操作类型

| 关键字 | 名称 | 详情说明 | 支持性 |
| --- | --- | --- | --- |
| direct | 直接型 | 常见于确认编辑或删除以及树节点点击获取Children等操作 | ✔ |
| open | 弹框型 | 打开对话框，展示新的一个类型页面，常见于创建或编辑等操作 | ✔ |
| cascade | 级联型 | 常见于树状型页面的级联页面使用，当点击某个节点时, 出现与之并列的数据展示页面 |  ✔ |
| import | 导入型 | 导入文件或数据时使用 | ✘ |
| export | 导出型 | 导出文件或数据时使用，分为全导出或部分导出 | ✘ |
| next | 步骤型 | 点击继续下一步操作，根据情况自动添加上一步按钮 | ✔ |
| url | 地址型 | 直接更改当前浏览器地址栏地址 | ✔ |


##### 操作配置

| 关键字 | 含义 | 功能 |
| --- | --- | --- |
| tag | 操作标签 | 可用于前端操作名称 |
| path | API接口 | 用于匹配schema描述和获取数据 |
| method | API接口方法 | 同上 |
| type | [操作类型](#_4) | 方便识别操作，见上方具体说明 |
| page | 页面tag | 当操作类型为open时，指向打开页面的tag |
| name | 操作名称 | 前端页面按钮名，node_action无需包含该内容 |
| icon | 图标 | 可选，目前暂未支持 |
| close | 关闭条件 | 开关型按钮操作的关闭条件 |
| open | 打开条件 | 开关型按钮操作的打开条件 |


!!! attention "提示"
    01. 上述字段均为可选字段，需要根据具体情况进行声明
    02. tag或page均不能包含特殊字符
    03. close/open仅支持bool说明，其他条件在计划开发中
        close=True; (✔)
        open=False; (✔)
        close=is_system; (✘)
        open=!is_admin; (✘)
        close=is_system&!is_admin; (✘)


##### 初始化操作

  init_action的目的是为了获取某个页面Schema结构和初始数据。也就是当你打开或看到某个页面时，该操作就会自动发起，然后将获取到的数据填入页面中。

  其主要包含`path`和`method`，且操作类型为`direct`类型，目前也没有其他类型的初始化操作出现。

```json
{
  "init_action": {
    "path": "/api/v1/xxx",
    "method": "get",
    "tag": "",
    "type": "direct",
  }
}
```

##### 全局操作

  global_action主要完成页面全局按钮的生成，并根据配置完成其对应操作的初始化工作。比如创建/导入等操作。
  
  其配置需要完全按照[操作配置](#_5)的说明来完成。

```json
{
  "global_action": {
    "create": {
      "name": "新建",
      "path": "/api/v1/xxx",
      "method": "post",
      "type": "open",
      "page": "user_create",
      "tag": "",
    },
    "import": {
      "name": "导入",
      "path": "/api/v1/xxx",
      "method": "post",
      "type": "import",
      "tag": "",
    },
    "export": {
      "name": "导出",
      "path": "/api/v1/xxx",
      "method": "post",
      "type": "export",
      "tag": "",
    },
  }
}
```

##### 局部操作

  local_action主要完成页面局部按钮的生成，以及对应其操作的初始化。比如删除/编辑等操作。

  其配置需要完全按照[操作配置](#_5)的说明来完成。

```json title='示例'
{
  "local_action": {
    "edit": {
      "name": "编辑",
      "type": "open",
      "page": "user_edit",
      "tag": "",
    },
    "delete": {
      "name": "删除",
      "type": "direct",
      "path": "/api/v1/xxx/{id}/",
      "method": "delete",
      "tag": "",
    }
  }
}
```

##### 节点操作

  node_action主要完成页面节点的操作的生成，不会有对应按钮的显示。
  
  功能主要为获取子节点和级联页面的数据，在Cards类型的页面中可以作为点击Cards的操作声明。

!!! info "提示"
    1. node_action为数组类型配置
    2. 若node_action中有什么`direct`类型的操作时，且当前为树页面，默认认为存在子节点
    3. 若node_action中有`cascade`类型的操作时，将在该页面执行完init_action之后使用第一个节点数据触发级联页面的init_action


```json title='示例'
{
  "node_action": [
    {
      "path": "/api/v1/xxx",
      "method": "get",
      "type": "direct",
      "tag": "",
    },
    {
      "type": "cascade",
      "page": "user_list",
      "tag": "",
    },
  ]
}
```

### 配置举例

##### 表格型页面

```json
{
  "name": "用户列表",
  "type": "table",
  "tag": "user_list",
  "init_action": {
    "path": "/api/v1/xxx",
    "method": "get",
    "type": "direct",
    "tag": "",
  },
  "local_action": {
    "edit": {
      "name": "编辑",
      "page": "user_edit",
      "tag": "",
      "type": "open",
      "icon": "edit",
    },
    "delete": {
      "name": "删除",
      "tag": "",
      "type": "direct",
      "path": "/api/v1/xxx/{id}/",
      "method": "delete",
    }
  },
  "global_action": {
    "create": {
      "name": "创建",
      "path": "/api/v1/xxx",
      "method": "post",
      "type": "open",
      "tag": "",
    }
  },
}
```

!!! 提示
    1. 配置中的全局和局部操作都包含type=open类型的操作，但描述却有所差异
    2. 全局‘创建’操作页面只有一个接口描述，故不再需要page字段，前端将会自行处理
    3. 局部‘编辑’操作页面将会有两个接口（get和post）描述，故需要page字段

##### 表单型页面

  表单页面一般情况没有local_action的声明。global_action声明一般为提交表单操作。

```json
{
  "name": "编辑用户",
  "type": "form",
  "tag": "user_edit",
  "init_action": {
    "path": "/api/v1/xxx/{id}/",
    "method": "get",
    "type": "direct",
    "tag": "",
  },
  "global_action": {
    "confirm": {
      "name": "确认",
      "path": "/api/v1/xxx/{id}/",
      "method": "post",
      "type": "direct",
      "tag": "",
    }
  }
}
```

##### 树状型页面

  树型页面一般需要配合select或cascade进行联合使用，单独使用的情况较少。

```json
{
  "name": "用户分组",
  "type": "tree",
  "tag": "user_group",
  "init_action": {

  },
}
```

##### 描述型页面

  描述型页面配置如下所示：

```json
{
  "name": "个人资料",
  "type": "description",
  "tag": "",
  "init_action": {
    "path": "/api/v1/xxx",
    "method": "get",
    "tag": "",
    "type": "direct",
  },
  "global_action": {
    "edit": {
      "name": "编辑",
      "type": "open",
      "page": "edit_login_user",
      "tag": "",
    },
  },
}
```

##### 卡片型页面

  卡片型页面配置如下所示：

```json
{
  "name": "本地应用",
  "type": "cards",
  "tag": "",
  "init_action": {
    "path": "/api/v1/xxx",
    "method": "get",
    "type": "direct",
    "tag": "",
  },
  "global_action": {
    "create": {
      "name": "创建",
      "path": "/api/v1/xxx",
      "method": "post",
      "tag": "",
      "type": "open",
    }
  },
  "local_action": {
    "eidt": {
      "name": "编辑",
      "page": "edit_this_app",
      "type": "open",
      "tag": "",
    },
    "delete": {
      "name": "删除",
      "path": "/api/v1/xxx",
      "method": "delete",
      "type": "direct",
      "tag": "",
    }
  }
}
```

##### 步骤型页面

```json
{
  "name": "订单",
  "type": "step",
  "tag": "",
  "pages": [
    "first_step",
    "second_step",
    "third_step"
  ],
}
```

##### 切换型页面

```json
{
  "name": "应用列表",
  "type": "tabs",
  "tag": "",
  "pages": [
    "my_app_list",
    "app_store_list",
    "purchased_app_list"
  ],
}
```

## 扩展三：Schema

  OpenAPI-Plus中使用`pydantic`中提供的`Field`方法进行Schema字段的扩展。下面将详细说明扩展了哪些字段并解释说明这些字段在前端界面中的使用情况。

### 类型/格式 type/format

| type | 信息 | 页面展示 |
| --- | --- | --- |
| integer | 数字类型 | 数字输入框 |
| string | 字符串类型 | 字符串输入框 |
| boolean | 布尔类型 | 开关按钮 |
| array | 数组类型 | 下拉选框 |
| object | 对象类型 | 主要为多个表单项 |

| format | 信息 | 页面展示 |
| --- | --- | --- |
| textarea | 长文本 | 可调节长文本输入框 |
| link | 链接类型 | 使用a标签展示 |
| date-time | 时间 | 时间选择器 |
| auto | 自动填充 | 下拉时触发选项，配合option_action使用 |
| dynamic | 动态表单 | 可以添加多个和删除以某个单元为基础的表单 |
| binary | 二进制文件 | 输入框加上传按钮 |
| qrcode | 二维码 | 展示二维码 |
| markdown | MD文档 | 展示MD文档 |
| badges | 多标签 | 展示多个标签内容 |


除此之外，还存在其他的一些Schema描述，也影响着前端页面的展示情况。比如：

* 枚举(enum) - 使用下拉单选框
* allOf - 使用FormObject
* oneOf - 使用FormObject
* $ref - 使用FormObject

!!! info "附加说明"
    1. 当声明deprecated=True或hidden=True时，前端界面不展示
    2. 当声明readonly=True时，前端界面禁止编辑

### 操作 *_action

  该模块的操作主要对Schema描述中的部分属性进行单一化的操作。主要包含以下三种情形，该模块可以进行扩展，需要根据实际情况和需求而定。每一项内容比较类似于上面所描述的页面配置操作。

| 关键字 | 类型 |
| --- | --- |
| item_action | [元素项操作](#item_action) |
| suffix_action | [后缀项操作](#suffix_action) |
| option_action | [选择项操作](#option_action) |

##### item_action
  
  元素项操作主要用于开关按钮类型的元素中，也就是type=bool的元素。

```json title="示例"
{
  "path": "/api/v1/xxx",
  "method": "post",
  "close": false,
}
```

##### suffix_action

  后缀项操作主要用于像`发送校验码`等类似的表单项操作。通过suffix_action的描述，前端将读取识别，并在input输入框后挂载上点击按钮操作，发起suffix_action。

```json title="示例"
{
  "path": "/api/v1/xxx",
  "method": "post",
  "name": "发送校验码",
  "delay": 60,
}
```

##### option_action

  选择项操作主要用于获取下拉选框数据。通过option_action的描述，当用户鼠标移入到对应的前端页面select元素上时，触发该操作。该操作需要注意返回数据的格式。

```json title="示例"
{
  "path": "/api/v1/xxx",
  "method": "post",
}
```

### 对话框 page

!!! 提示
    > 想一想: 为什么会需要弹出新的对话框呢？
    
    1. 当需要选择某个页面中的某个或多个数据并进行统一添加时
    2. 当需要选择某个页面中的某个或多个数据并进行统一回传时

  当某个元素描述上使用Field添加了page属性，则代表当点击该页面元素时，需要打开page属性指向的对话框页面。
  page属性指向的内容需要在[`pages`](#pages)中进行提供和声明。除此之外，还需要声明该数据是多选还是单选，单选使用`string`，多选使用`array`。

  当数据添加或回传只需要id值时，不要再进行其他的声明。否则需要声明回传的Schema内容。举例如下:

```python
class UserGroupCreateParentIn(Schema):
  """hidden=True意味着不需要在前端展示，但是需要在接口中回传"""
  id:UUID = Field(hidden=True)
  name:str

class UserGroupCreateIn(ModalSchema): 

  parent: Optional[UserGroupCreateParentIn] = Field(
    title=_("上级用户分组"),
    page="",
  )
```

## 扩展四：接口（paths）

  OpenAPI-Plus对Paths模块做了一些必要的扩展。比如operationId等内容。

  通过这些内容用于接口API权限的设置和匹配。

## 扩展五：权限（permissions）

  OpenAPI-Plus添加了权限相关模块。

  通过权限的匹配来实现API接口和页面的控制。

## 扩展六：国际化（translation）

  OpenAPI-Plus添加了国际化模块。

  主要包含了在OpenAPI描述中需要进行翻译的字段的中英文信息。
