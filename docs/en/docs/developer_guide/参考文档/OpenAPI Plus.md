# OpenAPI Plus

OpenAPI-Plus  Use [ `django-ninja`] (https://github.com/vitalik/django-ninja) and [ `pydantic`] (https://github.com/samuelcolvin/pydantic) for feature expansion. In order to achieve the purpose of adapting to the front-end generation of ArkID One Account Project.

OpenAPI-Plus mainly talks about what extensions have been made to it, and what are the implications of these extensions? Read on for the documentation.

## Extension 1: routers

It mainly declares the front-end routing information, and generates the front-end sidebar and other contents by reading and parsing the contents in routers. It can be divided into two categories:

- Routes with Children
- Routing without Children

| 关键字 |Meaning| 类型            |
| ------ | ---------------------------------------------------------------------- | --------------- |
| path   |Front-end access path, overlaid with/character| string          |
| name   |Sidebar Route Name| string          |
| icon   |Sidebar routing icon, to be declared in conjunction with the front end| string          |
| hidden |Whether to hide, if true, it will not be displayed in the front sidebar| boolean         |
| page   |The route needs to render the page, and the specific information points to [pages](#pages) the extension.| string          |
| url    |Directly access the URL interface. The default is GET. The interface returns a new URL address, which is displayed in the iframe.| string          |
| web    |Is it a computer side sidebar, which can contain order| number, boolean |
| mobile |Whether it is the bottom sidebar of the mobile phone and contains the order| number, boolean |

!!! Attention "important statement"
    01. The path cannot use `.` special characters such as.
    02. Special characters such as page cannot be used `[] {}`.

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

## Extension 2: page configuration (pages)

Declare the configuration information required for front-end page generation. The front-end will parse the content returned by OpenAPI to generate various types of front-end pages. The meaning of each configuration and how it is expressed and displayed in the front end will be explained in detail below.

!!! Info "Problem"
    01. What configuration information is required to generate a table or form page?
    02. Generate a tree structure page?
    03. What's the difference between pages?

### Page type

In response to the above questions, we first give our current `已支持 ✔` or `待支持 ✘` page types.

| 类型 | 名称 |Supportive|
| --- | --- | --- |
|table| 表格型页面 | ✔ |
| form |Form type page| ✔ |
| tree |Tree-based page| ✔ |
| tabs |Switched page| ✔ |
|description| 描述型页面 | ✔ |
|cards| 卡片型页面 | ✔ |
| grid |Grid type page| ✘ |
| list |List table type page| ✘ |
| step |Step type page| ✔ |

### Page configuration

Describe the configuration required in the page to support the generation scenario for each of these types of pages.

| 关键字 | 含义 | 功能 |Additional notes|
| --- | --- | --- | --- |
| type | 页面类型 | 生成前端页面模板 |Refer to the page type description below for details.|
| tag | 页面标识符 |Match unique page configuration| 页面唯一标签 |
| name | 页面名称 |The front-end page title is displayed accordingly.| 需支持中英文 |
| init_action | [页面初始化操作](#_6) | 获取schema和数据 |Please refer to the init _ action for details.|
| init_data | 初始化数据 | 初始化后的赋值操作 |By default, the lookup starts at the parent data pool|
| global_action | [页面全局操作](#_7) | 生成全局按钮操作 |Please refer to global _ action for details.|
| local_action | [页面局部操作](#_8) | 生成局部按钮操作 |Please refer to local _ action for details.|
| node_action | [页面节点操作](#_9) | 生成节点点击操作 |It may exist in tree/cards and other pages. For details, please refer to node _ action.|
| select | 是否为可选页面 | 生成可选页面 |This field is not required in the form page|
| pages | tabs/step多页面指向 | 生成tabs/step多页面 |Only in the tabs/step page|

!!! Attention "Important"
    1. Special characters such as tag cannot be used only `[] {}`
    2. Do not declare a tab repeatedly on the same page


### Page operation

  The main configuration of the page is composed of multiple operations. It includes the operation of initializing data acquisition, adding, deleting, modifying and querying, etc. Therefore, the operation configuration has extremely important meanings and detailed configuration statements.

##### Type of operation

| 关键字 | 名称 |A detailed description| 支持性 |
| --- | --- | --- | --- |
| direct | 直接型 |Common operations such as confirming editing or deleting and clicking on the tree node to get Children| ✔ |
| open | 弹框型 |Opens a dialog box showing a new type page, common for operations such as creating or editing| ✔ |
| cascade | 级联型 |It is commonly used in the cascading pages of tree-type pages. When a node is clicked, a data display page appears in parallel with it.|  ✔ |
| import | 导入型 |Use when importing files or data| ✘ |
| export | 导出型 |Used when exporting files or data, either fully or partially| ✘ |
| next | 步骤型 |Click to proceed to the next step, and add the previous step button automatically according to the situation| ✔ |
| url | 地址型 |Directly change the address of the current browser address bar| ✔ |


##### Operational configuration

|Keyword| 含义 | 功能 |
| --- | --- | --- |
| tag | 操作标签 |The name that can be use for that front-end operation|
| path | API接口 |Used to match schema descriptions and get data|
| method |API interface method| 同上 |
| type | [操作类型](#_4) |For easy identification and operation, see the specific instructions above.|
| page | 页面tag |When the operation type is open, point to the tag of the open page|
| name | 操作名称 |Front-end page button name, node _ action does not need to include this content|
| icon | 图标 |Optional, not currently supported|
| close | 关闭条件 |Close condition of switch type push-button operation|
| open | 打开条件 |On condition of switch type push-button operation|


!!! Attention "tip"
    01. The above fields are optional and need to be declared according to the specific situation.
    02. Neither tag nor page can contain special characters
    03. Only bool description is supported for close/open, and close = True for other conditions in plan development; (✔)open=False; (✔)close=is_system; (✘)open=!is_admin; (✘)close=is_system&!is_admin; (✘)


##### Initialize the operation

  The purpose of init _ action is to get the Schema structure and initial data of a page. That is, when you open or see a page, the operation will be automatically initiated, and then the data obtained will be filled into the page.

  It mainly contains `path` and `method`, and the operation type is `direct` type. At present, there is no initialization operation of other types.

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

##### Global operation

  The global _ action is mainly used to generate the global button on the page and complete the initialization of the corresponding operation according to the configuration. Uch as create/import.
  
  The configuration needs to be done exactly as [操作配置](#_5) described in.

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

##### Local operation

  The local _ action is mainly used to generate the local button on the page and initialize the corresponding operation. Uch as delete/edit.

  The configuration needs to be done exactly as [操作配置](#_5) described in.

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

##### Node operation

  The node _ action is mainly used to generate the operation of the page node, and the corresponding button will not be displayed.
  
  The main function is to obtain the data of child nodes and cascading pages, which can be used as the operation statement of clicking Cards in the Cards type page.

!!! Info "Prompt"
    1. Node _ action configuration for array type
    2. If there is any type of operation in `direct` node _ action, and the current page is a tree page, it is considered that there is a child node by default
    3. If there is an `cascade` operation of type in the node _ action, the init _ action of the cascaded page will be triggered by the first node data after the page executes the init _ action.


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

### Configuration example

##### Tabular page

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

!!! Hint
    1. Both global and local operations in the configuration contain operations of type = open, but the descriptions are different
    2. The global'Create 'action page has only one interface description, so the page field is no longer needed, and the front end will handle it by itself
    3. The local'edit 'action page will have two interface (get and post) descriptions, so the page field is required

##### Form type page

  The form page generally has no declaration of local _ action. The global _ action declaration is typically a submit form action.

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

##### Tree-type page

  Tree pages generally need to be used in conjunction with select or cascade, and rarely used alone.

```json
{
  "name": "用户分组",
  "type": "tree",
  "tag": "user_group",
  "init_action": {

  },
}
```

##### Descriptive page

  Descriptive page configuration is as follows:

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

##### Card type page

  The card type page is configured as follows:

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

##### Step type page

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

##### Switched page

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

## Extension 3: Schema

  In OpenAPI-Plus, the method provided `Field` in is used `pydantic` to extend the Schema field. The following section details which fields are extended and explains how they are used in the front-end interface.

### Type/format type/format

|type| 信息 | 页面展示 |
| --- | --- | --- |
|integer| 数字类型 | 数字输入框 |
|string| 字符串类型 | 字符串输入框 |
|boolean| 布尔类型 | 开关按钮 |
|array| 数组类型 | 下拉选框 |
| object | 对象类型 |Primarily multiple form item|

|format| 信息 | 页面展示 |
| --- | --- | --- |
| textarea | 长文本 |Adjustable long text entry box|
| link | 链接类型 |Use a label to display|
|date-time| 时间 | 时间选择器 |
| auto | 自动填充 |Trigger option when pulled down, used with option _ action|
| dynamic | 动态表单 |You can add multiple and delete forms based on a cell.|
| binary | 二进制文件 |Input box plus pass button|
|qrcode| 二维码 | 展示二维码 |
|markdown| MD文档 | 展示MD文档 |
| badges | 多标签 |Display multiple label content|


In addition, there are other Schema descriptions that also affect the presentation of the front-end page. For example

* Enumeration (enum) — Use the drop-down radio box
* All Of-Use FormObject
* One Of-Use FormObject
* $Ref-Use FormObject

!!! Info "Additional Notes"
    1. When deprecated = True or hidden = True is declared, the front-end interface is not displayed
    2. When readonly = True is declared, the front-end interface is not editable

### Action * _ action

  The operation of this module is mainly to simplify some attributes in the Schema description. It mainly includes the following three situations. The module can be extended according to the actual situation and requirements. Each content comparison is similar to the page configuration operations described above.

|Keyword| 类型 |
| --- | --- |
| item_action |[元素项操作](#item_action)|
| suffix_action |[后缀项操作](#suffix_action)|
| option_action |[选择项操作](#option_action)|

##### item_action
  
  The element item action is primarily used in elements of the switch button type, that is, elements with type = bool.

```json title="示例"
{
  "path": "/api/v1/xxx",
  "method": "post",
  "close": false,
}
```

##### suffix_action

  Suffix item operations are primarily used for `发送校验码` form item operations such as. Through the description of the suffix _ action, the front end will read and identify it, and click the button on the mount behind the input box to initiate the suffix _ action.

```json title="示例"
{
  "path": "/api/v1/xxx",
  "method": "post",
  "name": "发送校验码",
  "delay": 60,
}
```

##### option_action

  The selection operation is mainly used to obtain the data of the drop-down box. With the description of option _ action, the action is triggered when the user moves the mouse over the corresponding front-end page select element. This operation requires attention to the format of the returned data.

```json title="示例"
{
  "path": "/api/v1/xxx",
  "method": "post",
}
```

### Dialog box page

!!! Hint
    
    1. When you need to select one or more data in a page and add them uniformly
    2. When one or more pieces of data in a page need to be selected and returned uniformly

  When the Page attribute is added to an element description using Field, it means that when the page element is clicked, the dialog box page pointed by the Page attribute needs to be opened. The content pointed to by the page attribute needs to be provided and declared in [ `pages`] (# pages). In addition, you also need to declare whether the data is multi-choice or single-choice, single-choice use `string`, and multi-choice use `array`.

  When only the ID value is needed for data addition or postback, no other declarations should be made. Otherwise, the returned Schema content needs to be declared. Examples are as follows:

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

## Extension 4: interface (paths)

  OpenAPI-Plus makes some necessary extensions to the Paths module. Such as operationId.

  These contents are used for setting and matching API permissions of the interface.

## Extension 5: permissions

  OpenAPI-Plus adds permissions-related modules.

  The control of API interface and page is realized through the matching of permissions.

## Extension 6: Internationalization (translation)

  OpenAPI-Plus adds an internationalization module.

  It mainly contains the Chinese and English information of the fields that need to be translated in the OpenAPI description.
