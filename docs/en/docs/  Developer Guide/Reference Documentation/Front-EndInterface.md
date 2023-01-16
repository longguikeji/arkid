# Front -end interface

!!! info "Kind tips"
    1. Before reading the document，I hope you have read Openapi-Plus documentation
    2. You have used or browsed the front -end interface of the ARKID

  The front -end interface mainly contains the following modules：

* [login interface](#_2)

* [Front -end address interface](#_5)

* [Functional interface](#_6)

## login interface

  The login interface is mainly passed`/api/v1/tenant/{tenant_id}/login_page/`Page described by the interface to describe information generation。

  Login interface configuration interface Return content includes two items，As shown in the table below。For example, as shown in the figure below。

| Keyword | name | Detail description |
| --- | --- | --- |
| data | [Page surface configuration] (#_3) | Rendering/Different page forms such as registration |
| tenant | [Practitioner Information] (#_4) | Rendering tenants icons and names, etc. |

[![vVLQyt.png](https://s1.ax1x.com/2022/08/03/vVLQyt.png)](https://imgtu.com/i/vVLQyt)

### Page surface configuration

  Page surface configuration information can be caused by it`Authentication`Module dynamic additional income。There is information such as the user name and password login page configuration and other information。As shown in FIG，Page surface configuration generates all different forms and buttons in the login module。The main page items include the login page、Register page and forget the password page。Since the rendering process of three pages items is consistent，Here we only introduce the generation process and precautions of the login page item。

  dataThe value corresponding to the keyword is the description information of the respective page of the page item，Each item contains`forms bottoms extend name`Field information。

| Keyword | name |
| --- | --- |
| name | Page configuration item name |
| forms | Forms in different ways |
| bottoms | Found operation of the table |
| extend | worth mentioning |

**Table item forms**

  formsUsed to render different ways form items。For example, login can exist ① Username password login method；② SMS verification code login method Wait。And it contains`label items submit`Field information。

| Keyword | Detail |
| --- | --- |
| label | Table title name |
| items | Detailed expression of each form item |
| submit | Submitting operation expression of the form item |


  itemsForm items are used to display and enter user names、password、Mobile phone number and other information，And with functional operations such as sending verification codes。

| Keyword | meaning | Detail |
| --- | --- | --- |
| name | Field key | Key returned when submitted |
| type | Table type type | ① text ② password ③ hidden |
| placeholder | Tables shareholding | - |
| readonly | Table item read only | - |
| append | Suffering | See the submit operation instructions， Generally used for'Send the verification code'and'Graphical Code'Wait |

  submitTo submit the Items information entered by the user。

| Keyword | Detail |
| --- | --- |
| http | Button operation content，Including URL/path/Params and other content |
| title | Button operation name |
| redirect | Click the redirection to the address after clicking |
| agreement | Registration agreement description |
| delay | time delay， Used to send verification codes and other operations |
| gopage | Page name，Used to a page in Data |
| img | The map's address，Icon display for third -party login |
| long | Boolean value，Long type button, Control of the length of the button |
| prepend | Button prefix text，Commonly used for the bottom button at the bottom of the form |
| tooltip | The button move into the prompt information description，Commonly used for third -party login buttons |


**Bottom operation bottoms**

  bottomsUsed to switch between different pages configuration items。

  In the front -end page display，Common`No account yet，Sign up now`and`Forgot password`Waiting for the button。The operation attributes of this type generally include in the above description`prepend gopage`Equal attribute。

**worth mentioning extend**

  extendOnly in the login page configuration item，Used to display different third -party login items。It is expressed in the above picture as the multiple icons below。

  extendDepend on`title buttons`Two items。Title is the title；Buttons configures for the button for each third party login。

  buttonsThe operating attributes in it generally include`img redirect tooltip`Equity information。

**Configuration Example**

  The information returned in the interface is as described as described below：

```json
{
  "data": {
    "login": {
      "name": "login",
      "forms": [
        {
          "label": "Username password login",
          "items": [
            {
              "value": "",
              "type": "text",
              "name": "username",
              "placeholder": "username",
            },
            {
              "value": "",
              "type": "password",
              "name": "password",
              "placeholder": "password",
            },
          ],
          "submit": {
            "http": {
              "url": "/api/v1/xxx",
              "method": "post",
              "params": null,
            },
            "title": "Log in",
            "long": true,
          },
        }
      ],
      "bottoms": [
        {
          "prepend": "No account yet，",
          "gopage": "register",
          "title": "Sign up now",
        },
        {
          "prepend": null,
          "gopage": "password",
          "title": "Forgot password",
        },
      ],
      "extend": {
        "title": "worth mentioning",
        "buttons": [
          {
            "img": "xxx.png",
            "redirect": {
              "url": "xxx",
              "params": null,
            },
            "tooltip": "Github",
          },
          {
            "img": "xxx.png",
            "redirect": {
              "url": "xxx",
              "params": null,
            },
            "tooltip": "Gitee",
          }
        ],
      },
    },
    "register": {},
    "password": {},
  }
}
```

### Tenant information

  Ten information mainly returns the current login tenant information。Rendering the tenants icon and tenant name above the form in the figure above。

!!! Login prompt
    1. Login page By default, use platform tenants to log in
    2. If you want to use other existing tenants to log in，Please fill in the suffix information in the address bar
       For example：`/login?tenant_id=123`


## Front -end address interface

  The existence of this page is just to match the possible tenant SLUG。

  The front -end address interface is shown in the figure below：

  [![v1AlJf.png](https://s1.ax1x.com/2022/08/09/v1AlJf.png)](https://imgtu.com/i/v1AlJf)


!!! attention "Instructions for use"
    1. The address must contain protocols、Domain name and port。for example`https://Ark.dev.Dragon Turtle Technology.com`
    2. If the input address contains space at both ends，Will automatically remove。
    3. If the at the end of the input address is`/`character，It will also be removed automatically。
    4. If there is a space in the middle of the input address or a non -site string，Will not submit success。

## Functional interface

  Main description how to pass Openapi-Plus expansion interface`/api/v1/openapi.json`The returned information evolved into each interface displayed by the front end。By described by the evolution of the generation process of the front -end interface，It makes it easier for those who read the front -end project of the ARKID to recommend or use。

  The functional interface mainly includes other functional pages except login page，That is, you can read data and add deletion to the content page of the data information information.。The content and operation of the specific page need to have the foundation of the front -end knowledge，For example, TypeScript、Vue3 and bootstrap5, etc.。This document will avoid the basic knowledge required by any front end，And just for you to penetrate the front end and the back end，So as to understand the general operation of its operation。

### Overview

  How did these pages come from?？The generation of the function page is generally passed by the following steps。

1. According to routes（routers）Generate front -end route
2. According to the page provided by the routing（page）Find page configuration（pages）Corresponding configuration details
3. Generate type page according to the page configuration，And look for the bomb box page、Level United Page and Sub -page，And the corresponding operations（paths）
4. Find the corresponding description according to the operation information（components）content，And generate page attributes according to the description
5. Mount the operation to the page or button，So as to complete the rendering of the page and the operation of the button

!!! hint
    1. Bouncing page：The dialog box page of the operation of the button type is Open
    2. Level joint page：Generally a tree page node_Cascade type operation in the Action description of the point of the cascade type operation
    3. Subpages：Definition as tabs/Pages declared in STEP and other types of pages point to the page

### OpenAPI-Plus

OpenAPI-PlusPass the interface`/api/v1/openapi.json`Introduction to the information and functions returned as follows。For more detailed content, please refer to Openapi-Plus documentation。

| Module | name | Detail description | Whether to use the front end |
| --- | --- | --- | :---: |
| routers | Routing set | Used for front -end generating route information | ✔ |
| pages | Page set | Used to generate different page types and page operations in the front end | ✔ |
| paths | Interface set | Used to find Components and permissions certification | ✔ |
| components | Description | Used for front -end generation page element information | ✔ |
| permissions | Authority set | Used for authority management | ✔ |
| translation | globalization | Used for international voice switch | ✔ |
| info | information | Openapi description | ✘ |
| openapi | Version | version number | ✘ |

### routing routers

  Routing information is obitated by Openapi-Plus interface provides。The front end will read the content of this module directly，And based on routing description to generate front -end routing table。

  During the generating front -end routing table, you need to process and mount some information on the routing page and some information。Routes are divided into Children and no Children。

!!! info "hint"
    1. Sub -routing children quantity is greater than or equal to 2 o'clock，It will produce a father -son sidebar
    2. Sub -routing children is empty or quantity is 1，Display the page directly on the sidebar

```json title='No Children Routing Example'
{
  "path": "mine",
  "name": "mine",
  "icon": "mine",
  "hidden": true,
  "page": "mine",
}
```


**Routing authority**

  If some Openapi-Plus routing table provided`page`information，It means that this routing table needs to display a page，You need to judge whether the page has authority。The permissions set will not directly provide the permissions of the page，And the front end needs to find the initialization interface of the page，The authority of the routing page is indirectly judged by the interface。

  Route permission search step（The above example is an example）：

1. In the above example`page`Point to the MINE page，It will be configured on [page] (#Check in pages)_action。If it is a level connection page and sub -page (TABS/STEP) type，Then look for the first sub -page of the level connection page [page configuration] (page configuration] (#pages)
2. Through init_Action look for [interface information] (interface information] (#Paths) corresponding interface Operationid
3. Go to [permissions set] through Operationid#Find the corresponding SORT in Permissions)_ID value
4. According to sort_The ID value determines whether it has permissions through the string information returned by the permission interface
5. If you have this routing permission，It is displayed；Otherwise it will not be displayed


**Display attribute**

  In addition to the routing permissions need front -end attention，Openapi-Provided by Plus`mobile web`Two display attributes also require the front end for corresponding treatment。

  These two attributes determine which routing pages are displayed on the mobile and web side。If the mobile attribute is indicated，The corresponding routing information will be displayed on the bottom of the mobile page。

[![vZArBF.png](https://s1.ax1x.com/2022/08/03/vZArBF.png)](https://imgtu.com/i/vZArBF)


### Page configuration pages

  Page configuration items are mainly used to render the type and operation of the page。By reading the content in the analysis page configuration item，Complete the complete rendering of the routing page。What are the contents of the page configuration items，Already in Openapi-Plus document explains in detail，I won't go into details here。

A certain homepage generated as shown in the figure below：

[![vZZlX6.png](https://s1.ax1x.com/2022/08/03/vZZlX6.png)](https://imgtu.com/i/vZZlX6)

The pages of a pop -up box generated are shown in the figure below：

[![vZZYAe.png](https://s1.ax1x.com/2022/08/03/vZZYAe.png)](https://imgtu.com/i/vZZYAe)


!!! info "Reading prompt"
    1. If the routing statement page and its level pages are the homepage
    2. Homepage and other sub -pages (TABS/STEP) use CARD without MODAL
    3. The first sub -page of the homepage and the homepage is required to initialize the data when the route is opened

Page configuration item reading steps：

1. Read the page configuration name，Mount it to the front page page，If it is the main page and not a level joint page, the name is hidden
2. Read init_ACTION Information，According to init_Interface acquisition interface description in the action information information
3. Read the rest information，And generate the corresponding operation or button in the page
4. Use the ACTION information in the above two steps，Complete the mounting of the page operation
5. Repeat the reading step，Complete the configuration reading of all specified pages

### Interface information paths

  Interface information is for the front end，Except for Operationid，Mainly used for the reading of interface Responses or requestbody content and mounting of operating content。

  When [page configuration] (page configuration] (#Action description in pages)`method=get`Read responses when you read；Otherwise, read Requestbody。

**Two read routes**

1. responses => 200 => content => application/json => schema => $ref
2. requestBody => content => application/json => schema => $ref

  
  And read the one further$Ref Direction。For example`$ref=#/components/schemas/Mineapppsout`Time，Will be based on it`Mineapppsout`Go [Properties Description] (#further operation description in components)。

[![vZQA2Q.png](https://s1.ax1x.com/2022/08/03/vZQA2Q.png)](https://imgtu.com/i/vZQA2Q)


### Attribute description components

  Attribute description`components => schema => Mineapppsout`Analysis and processing of detailed information described by way。

  In the detailed information`properties`Wuling in the contents of different types of pages。

  tableThe table type page is mounted to the table column；Form table model page is mounted to the form item。

[![vZQZKs.png](https://s1.ax1x.com/2022/08/03/vZQZKs.png)](https://imgtu.com/i/vZQZKs)

### Authority set permissions

  Permanent set is mainly used for the control of the front -end routing and the API button.。

  When there is no route or button permission information，The page will not display the corresponding content。

### globalization translation

  Page example picture：

[![vZQrxH.png](https://s1.ax1x.com/2022/08/03/vZQrxH.png)](https://imgtu.com/i/vZQrxH)

  Internationalization is mainly used to switch between users' choice between language，After switching, the page will be refreshed and updated，Use Openapi-The translation text provided by PLUS for the global replacement of the location used by the page。
