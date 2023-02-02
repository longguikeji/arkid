# front end

According to the above configuration information structure description，We need to be on the back -end interface（/api/v1/openapi.json）The corresponding page configuration data is generated for the front -end analysis，The following is the basic code step：

## Create a page

``` python

from arkid.core import pages

user_list_tag = 'user_list'
user_list_name = 'user list'


page = pages.FrontPage(
    tag=user_list_tag,
    name=user_list_name,
    page_type=pages.FrontPageType.TABLE_PAGE,
    init_action=pages.FrontAction(
        path='/api/v1/tenant/{tenant_id}/users/',
        method=pages.FrontActionMethod.GET
    )
)

```

## Add Action to Page

``` python
...

page.add_local_action(
    [
        pages.FrontAction(
            name=_("delete"),
            method=pages.FrontActionMethod.DELETE,
            path="/api/v1/tenant/{tenant_id}/users/{id}/",
            icon="icon-delete",
            action_type=pages.FrontActionType.DIRECT_ACTION
        )
    ]
)

...

```

## Register the page to the global situation

``` python

pages.register_front_pages(page)

```

## Write the route information

``` python
from arkid.core import routers

user_list_router = routers.FrontRouter(
    path="user_list",
    name='User Management',
    icon='user',
    page=page,
)

router = routers.FrontRouter(
    path='user',
    name='User Management',
    icon='user',
    children=[
        user_list_router,
    ],
)

```

## Finally visiting/api/v1/openapi.The data can be obtained when json interface：

``` json
{
  ...
  "routers": [
      {
          "path": "user",
          "name": "User Management",
          "icon": "user",
          "children": [
              {
                  "path": "user_list",
                  "name": "User Management",
                  "icon": "user",
                  "page": "user_list"
              }
          ]
      }
  ],
  "pages": [
      {
          "tag": "user_list",
          "name": "user list",
          "type": "table",
          "init": {
              "tag": "16058e11df284ae1a58fd1220a85e501",
              "path": "/api/v1/tenant/{tenant_id}/users/",
              "method": "get"
          },
          "local": [
              {
                  "tag": "9181f711ffcb4ac5b5a793e043468595",
                  "name": "delete",
                  "path": "/api/v1/tenant/{tenant_id}/users/{id}/",
                  "method": "delete",
                  "icon": "icon-delete",
                  "type": "direct"
              }
          ],
      },
  ]
}
...
```
