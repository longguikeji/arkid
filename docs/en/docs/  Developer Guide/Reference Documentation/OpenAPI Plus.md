# OpenAPI Plus

OpenAPI-Plus use[`django-ninja`](https://github.com/Vitalik/django-ninja) and [`pydantic`](https://github.com/samuelcolvin/pydantic) function extension，To achieve adaptation ArkID The purpose of the front end of the one -account project。

OpenAPI-Plus Mainly tells what extensions it has made，And what do these expansion exist?？Please continue to read the document。

## Extended one: routing（routers）

Its main declaration front -end routing information，By reading analysis routers Middle content，Generate the front sidebar of the front end of the front end。A total of two categories can be divided into two categories：

- Have Children Routing
- none Children Routing

| Keyword | meaning                                                                   | Types of            |
| ------ | ---------------------------------------------------------------------- | --------------- |
| path   | Front -end access path，use/Characters are superimposed                                        | string          |
| name   | Name of side barn route                                                         | string          |
| icon   | Large -boring routing icon，Need to cooperate with the front -end statement                                       | string          |
| hidden | Whether to hide，If you do true，Do not show in the front sidebar of the front end                          | boolean         |
| page   | This route needs to be rendered，Specific information direction [pages](#pages) Expand                | string          |
| url    | Visit the URL interface directly，Deficiency of GET，The interface returns the new URL address，Put in iframe display      | string          |
| web    | Whether it is the sidebar of the computer end，Can contain order                                       | number, boolean |
| mobile | Whether it is the bottom bar of the mobile phone，And sequence                                         | number, boolean |

!!! attention "Important statement" 
    01. path Out of service `.` Special characters。 
    02. page Out of service `[ ] { }` Special characters。

```json title='There is a Children route example'
{
  "path": "mine",
  "name": "mine",
  "icon": "mine",
  "hidden": true,
  "children": [
    {
      "path": "profile",
      "name": "Personal management",
      "page": "mine_profile",
      "icon": "profile"
    },
    {
      "path": "logout",
      "name": "sign out",
      "page": "mine_logout",
      "icon": "logout"
    }
  ]
}
```

```json title='No Children Routing Example'
{
  "path": "mine",
  "name": "mine",
  "icon": "mine",
  "hidden": true,
  "page": "mine"
}
```

## Extended two: Page configuration（pages）

Declarize the configuration information required to generate the front end page，The front end will be parsed according to the content returned by OpenAPI，So as to generate various types of front -end pages。The following will explain the meaning of each configuration and how to express and display the corresponding expression at the front end。

!!! info "question"
    01. Generate a form or form page page，Need those configuration information？
    02. Generate a tree structure page？
    03. What are the differences between the page?？

### Page type

For the above problems，Give us the current`Support ✔`or`Be supported ✘`Page type。

| Types of | name | Support |
| --- | --- | --- |
| table | Table -type page | ✔ |
| form | Table model page | ✔ |
| tree | Tree -like page | ✔ |
| tabs | Switch page | ✔ |
| description | Descriptive page | ✔ |
| cards | Card -type page | ✔ |
| grid | Grid page | ✘ |
| list | List -type page | ✘ |
| step | Step -type page | ✔ |

### Page configuration

Explain the configuration required in the page，To support the generation situation of the above -mentioned pages。

| Keyword | meaning | Features | Additional information |
| --- | --- | --- | --- |
| type | Page type | Generate front -end page template | For details, refer to the following page type description |
| tag | Page identifier | Matching the unique page configuration | Page unique tag |
| name | Page name | Corresponding display front -end page title | Need to support Chinese and English |
| init_action | [Page initialization operation] (#_6) | Get SCHEMA and data | Specific reference to init_Action detailed description |
| init_data | Initialization data | Initialized assignment operation | Start from the parent -level data pool by default |
| global_action | [Page global operation] (#_7) | Generate global button operation | Specific reference Global_Action detailed description |
| local_action | [Page local operation] (#_8) | Generate local button operation | Specific reference Local_Action detailed description |
| node_action | [Page node operation] (#_9) | Generate nodes, click operation | It may exist in TREE/Cards and other pages，Specific reference node_Action detailed description |
| select | Whether it is an optional page | Selected page | This field is not required in the form page |
| pages | tabs/stepMulti -page pointing | Generate tabs/STEP multi -page | Only in TABS/In step page |

!!! attention "important hint"
    1. tag Cannot only`[ ] { }`Special characters
    2. tag Do not repeat a tag under the same page


### Page operation

  The main configuration of the page is composed of multiple operations。Including initialization data acquisition operation，Click, deletion, change, etc. Click to operate。So the operation configuration has extremely important meaning and detailed configuration statement。

##### Operating type

| Keyword | name | Detail description | Support |
| --- | --- | --- | --- |
| direct | Direct | Common in confirming editing or deleting, and clicking on tree nodes to get children and other operations | ✔ |
| open | Bomber | Open the dialog，Show a new type page，Common operations such as creating or editing | ✔ |
| cascade | Classification | Commonly used on the grade pages of tree -shaped pages，When clicking a certain node, The data display page that appears side by side |  ✔ |
| import | Import | Use when importing files or data | ✘ |
| export | Export type | Use when exporting files or data，Divided into full export or partial export | ✘ |
| next | Step | Click to continue the next operation，Automatically add a step button according to the situation | ✔ |
| url | Address | Change the current browser address bar address directly | ✔ |


##### Operating configuration

| Keyword | meaning | Features |
| --- | --- | --- |
| tag | Operating label | Can be used for front -end operation name |
| path | APIinterface | Used to match SCHEMA description and obtain data |
| method | APIInterface method | Above |
| type | [Operation type] (#_4) | Easy to identify operation，See the specific instructions above |
| page | Page tag | When the operation type is open，Pointing to the tag on the page |
| name | Operating name | Front -end page button name，node_Action does not need to include this content |
| icon | icon | Optional，Not supported yet |
| close | Closure condition | Turn on the switch -type button operation |
| open | Open condition | Open condition of the switch button operation |


!!! attention "hint"
    01. The above fields are optional fields，You need to declare according to the specific situation
    02. tagOr page can not include special characters
    03. close/openOnly support BOOL description，Other conditions are under plan development
        close=True; (✔)
        open=False; (✔)
        close=is_system; (✘)
        open=!is_admin; (✘)
        close=is_system&!is_admin; (✘)


##### Initialization operation

  init_actionThe purpose is to obtain a page SCHEMA structure and initial data。That is, when you open or see a page，This operation will automatically initiate，Then fill in the obtained data into the page。

  It mainly contains`path`and`method`，The operation type is`direct`Types of，There are no other types of initialization operations at present。

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

  global_actionMainly complete the generation of the pages global button，And complete the initialization of its corresponding operation according to the configuration。Such as creation/Import and other operations。
  
  Its configuration needs to be completely followed by [Operation Configuration] (#_5) Explanation to complete。

```json
{
  "global_action": {
    "create": {
      "name": "Newly built",
      "path": "/api/v1/xxx",
      "method": "post",
      "type": "open",
      "page": "user_create",
      "tag": "",
    },
    "import": {
      "name": "Import",
      "path": "/api/v1/xxx",
      "method": "post",
      "type": "import",
      "tag": "",
    },
    "export": {
      "name": "Export",
      "path": "/api/v1/xxx",
      "method": "post",
      "type": "export",
      "tag": "",
    },
  }
}
```

##### Local operation

  local_actionMainly complete the generation of page parts of the page，And the initialization of its operation。Such as deleting/Edit and other operations。

  Its configuration needs to be completely followed by [Operation Configuration] (#_5) Explanation to complete。

```json title='Exemplary'
{
  "local_action": {
    "edit": {
      "name": "edit",
      "type": "open",
      "page": "user_edit",
      "tag": "",
    },
    "delete": {
      "name": "delete",
      "type": "direct",
      "path": "/api/v1/xxx/{id}/",
      "method": "delete",
      "tag": "",
    }
  }
}
```

##### Node operation

  node_actionMainly complete the generation of the operation of the page node，There is no display of the corresponding button。
  
  The function is mainly to obtain the data of the sub -node and the level connection page，In the CARDS type page, it can be used as a click CARDS operation statement。

!!! info "hint"
    1. node_actionConfigure for array type
    2. If node_What is in Action`direct`During the operation，And the current tree page，The default is considered to be a child node
    3. If node_Action`cascade`During the operation，Will execute intit on this page_After using the first node data to trigger the initial page of the link_action


```json title='Exemplary'
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

### Configuration Example

##### Table -type page

```json
{
  "name": "user list",
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
      "name": "edit",
      "page": "user_edit",
      "tag": "",
      "type": "open",
      "icon": "edit",
    },
    "delete": {
      "name": "delete",
      "tag": "",
      "type": "direct",
      "path": "/api/v1/xxx/{id}/",
      "method": "delete",
    }
  },
  "global_action": {
    "create": {
      "name": "create",
      "path": "/api/v1/xxx",
      "method": "post",
      "type": "open",
      "tag": "",
    }
  },
}
```

!!! hint
    1. The global and local operations in the configuration include Type=Open type operation，But the description is different
    2. Global‘create’There is only one interface description on the operation page，Therefore, no Page field is needed，The front end will handle it by itself
    3. Partial‘edit’There will be two interfaces on the operation page（get and post）describe，Therefore, the page field needs

##### Table model page

  The form page pages are generally not local_Action statement。global_Action statement is generally for submitting form operation。

```json
{
  "name": "Edit user",
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
      "name": "confirm",
      "path": "/api/v1/xxx/{id}/",
      "method": "post",
      "type": "direct",
      "tag": "",
    }
  }
}
```

##### Tree page

  Tree pages generally need to cooperate with Select or Cascade for joint use，Little use alone。

```json
{
  "name": "User group",
  "type": "tree",
  "tag": "user_group",
  "init_action": {

  },
}
```

##### Descriptive page

  Description page configuration is shown below：

```json
{
  "name": "personal information",
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
      "name": "edit",
      "type": "open",
      "page": "edit_login_user",
      "tag": "",
    },
  },
}
```

##### Card -type page

  The configuration of the card type page is shown below：

```json
{
  "name": "Local application",
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
      "name": "create",
      "path": "/api/v1/xxx",
      "method": "post",
      "tag": "",
      "type": "open",
    }
  },
  "local_action": {
    "eidt": {
      "name": "edit",
      "page": "edit_this_app",
      "type": "open",
      "tag": "",
    },
    "delete": {
      "name": "delete",
      "path": "/api/v1/xxx",
      "method": "delete",
      "type": "direct",
      "tag": "",
    }
  }
}
```

##### Step -type page

```json
{
  "name": "Order",
  "type": "step",
  "tag": "",
  "pages": [
    "first_step",
    "second_step",
    "third_step"
  ],
}
```

##### Switch page

```json
{
  "name": "Application List",
  "type": "tabs",
  "tag": "",
  "pages": [
    "my_app_list",
    "app_store_list",
    "purchased_app_list"
  ],
}
```

## Expansion three：Schema

  OpenAPI-PlusUse`pydantic`Medium`Field`Methods to expand the SCHEMA field。The following will explain which fields are extended and explained to the usage of these fields in the front -end interface。

### Types of/Format type/format

| type | information | Page display |
| --- | --- | --- |
| integer | Number | Digital input box |
| string | String type | String input box |
| boolean | Boolean | Switch button |
| array | Array | Drop -down selection |
| object | Object type | Mainly multiple forms |

| format | information | Page display |
| --- | --- | --- |
| textarea | Long text | Adjustable long text input box |
| link | Link | Use A tag display |
| date-time | time | Time selector |
| auto | Automatic filling | Trigger options when dropping down，Cooperate Option_ACTION |
| dynamic | Dynamic form | You can add multiple and delete a form based on a certain unit |
| binary | binary file | Input box and upload button |
| qrcode | QR code | Display QR code |
| markdown | MDDocumentation | Display MD documentation |
| badges | Label | Display multiple label content |


besides，There are still some other schema descriptions，It also affects the display of the front -end page。for example：

* Enumeration (enum) - Use the drop -down single selection box
* allOf - Use FormObject
* oneOf - Use FormObject
* $ref - Use FormObject

!!! info "Additional information"
    1. When declared deprecated=True or Hidden=True，The front -end interface is not displayed
    2. When declared Readonly=True，The front -end interface is forbidden to edit

### operate *_action

  The operation of this module mainly performs a single operation of some attributes in the SCHEMA description。Mainly contain the following three situations，This module can be expanded，Depending on the actual situation and needs。Each content is similar to the page configuration operation described above。

| Keyword | Types of |
| --- | --- |
| item_action | [Element item operation] (#item_action) |
| suffix_action | [Discose operation] (#suffix_action) |
| option_action | [Select item operation] (#option_action) |

##### item_action
  
  Element item operation is mainly used in the element of the switch button type，That is Type=Bool's element。

```json title="Exemplary"
{
  "path": "/api/v1/xxx",
  "method": "post",
  "close": false,
}
```

##### suffix_action

  The suffix item operation is mainly used for image`Send a school code`Similar form items operation。Through Suffix_Action description，The front end will read and identify，And click the button to operate on the Input input box，Initiating Suffix_action。

```json title="Exemplary"
{
  "path": "/api/v1/xxx",
  "method": "post",
  "name": "Send a school code",
  "delay": 60,
}
```

##### option_action

  Selected items are mainly used to obtain the drop -down selection box data。Via Option_Action description，When the user mouse is moved into the corresponding front page Select element，Trigger the operation。This operation needs to pay attention to the format of returning the data。

```json title="Exemplary"
{
  "path": "/api/v1/xxx",
  "method": "post",
}
```

### Dialog page

!!! hint
    > Think about: Why do I need to pop up a new dialog box?？
    
    1. When you need to select one or more data in a page and add it uniformly
    2. When you need to select a certain or more data in a page and make a unified transmission

  When a certain element description is used to add a PAGE attribute with FIELD，Then it means when clicking the page element，You need to open the dialog box page of the page attribute direction。
  page属性指向的内容需要在[`pages`](#Provide and declare in pages)。besides，You also need to declare whether the data is multiple or single，Single optional use`string`，Choose more use`array`。

  When the data is added or passed back, only the ID value is required，Don't make another statement again。Otherwise, you need to declare the SCHEMA content of the return。As follows:

```python
class UserGroupCreateParentIn(Schema):
  """hidden=TrueIt means that you don't need to be displayed at the front end，But you need to return in the interface"""
  id:UUID = Field(hidden=True)
  name:str

class UserGroupCreateIn(ModalSchema): 

  parent: Optional[UserGroupCreateParentIn] = Field(
    title=_("Superior user group"),
    page="",
  )
```

## Extended four：interface（paths）

  OpenAPI-PlusDo some necessary extensions to the Paths module。Such as Operationid and other content。

  Use these contents to set and match the interface API permissions。

## Extended five：Authority（permissions）

  OpenAPI-PlusAdded permissions related modules。

  Implement the control of the API interface and page through the matching of permissions。

## Expand：globalization（translation）

  OpenAPI-PlusAdded an international module。

  It mainly includes Chinese and English information that needs to be translated in the OpenAPI description。
