## Features
Authorization rules，As a system of certification, supplementation，It can support more fine -grained permissions given。
It can support the given authority for different attributes of users，For example user name、Nick name、gender、Mobile phone number waiting。
You can also give the permissions of the different attributes of the grouping。
You can also according to the development of the developer，The structure of the data storage，Realize the authority of permission in specific scenarios。
## Implementation
arkidThe system has assumed the permissions of the user attributes by default，Convenient developer for reference

``` mermaid
graph LR
  A[start] --> B {Design SCHEMA} --> C {Register the front -end page}--> D {register SCHEMA}--> E {Implementing the authorization function} --> F [End];
```

Let's make a brief introduction to the realization of ideas:

1. Need developers want to know the attributes that need to be screened if they develop plugins，Is the user attribute，Still packet attributes，Or other attributes。And those applications need to be filtered，And those permissions。
To design schema，Used to store data structure。If there are some application lists in SCHEMA，Permission list，User lists, etc.，Need to use the front -end page used，Use the parent class [register_front_pages](#arkid.core.extension.impower_rule.ImpowerRuleBaseExtension.register_front_PAGES) registered separately。

2. Different authorization rules are divided through different SCHEMA，So when the developer designed the SCHEMA，Need to pass [register_impowerrule_schema](#arkid.core.extension.impower_rule.ImpowerRuleBaseExtension.register_impowerrule_schema)，Register。

3. After the registration is completed，Page green Type fields that create authorized rules will have one more authorized rules，As shown below:

    [![jqhUld.md.jpg](https://s1.ax1x.com/2022/07/21/jqhUld.md.jpg)](https://imgtu.com/i/jqhUld)

    If we choose different authorization rules，The red part will show different content，The display content is determined by the SCHEMA structure。

    Create editing and deletion of authorization rules，They are all processed in advance by Arkid，Developers only need to pay attention to the method of power。
    
    Let's introduce the use of the method of empowerment:

    Need developers to implement [GET_auth_result(event, **Kwargs)] (#arkid.core.extension.impower_rule.ImpowerRuleBaseExtension.get_auth_Result) method

    1. parameter: This method`Kwargs`，`event` Two parameters，We focus on`event`parameter，This parameter contains`data`and`tenant`Two attributes，in`event.tenant`You can get the current tenant；`event.data`You can get the data passed over。We get the value in the data
        1. `data.user`Can get the current user；
        2. `data.app`Can get the current application，If this application is a None，It means that the application is arkid，On the contrary, it is other applications；
        3. `data.arr` You can get user permissions array (0 or 1 composition，0 is no authority，1 There is authority，SOON's sort_ID is the same)；
        4. `data.config` You can get the current authorization rules
    2. use: Developers need to be based on the rules of authorization`event.config`，Combine`data.user`，According to your own needs，After screening，Return to SORT with permissions_ID array


## Abstract method
* [get_auth_result(event, **kwargs)](#arkid.core.extension.impower_rule.ImpowerRuleBaseExtension.get_auth_result)

## Foundation definition

::: arkid.core.extension.impower_rule.ImpowerRuleBaseExtension
    rendering:
        show_source: true

## Exemplary

::: extension_root.com_longgui_impower_rule.ImpowerRuleExtension
    rendering:
        show_source: true
