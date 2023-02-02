# Application access


## Business system

Before starting to access，To figure out the general situation of the company's business system：

1. What systems are there
2. All systems are supported by what protocols are supported by single -point login or unified accounts
3. There are several users' data sources，What are the retention and abandonment
4. What is the synchronization relationship between data sources

etc.

## system structure

After dealing with these problems，You can start designing the system architecture，The figure below shows a typical system architecture diagram example：

[![v8sYRA.jpg](https://s1.ax1x.com/2022/08/11/v8sYRA.jpg)](https://imgtu.com/i/v8sYRA)

After the user data enters the EHR system，Synchronize to AD domain via SCIM data，Use AD domain as the standard data source，Microsoft systems or systems that support ADs can directly connect with AD domain（Notice，AD domain is a unified account dense，Not single -point login），Other systems such as OA can be connected to ARKID through single -point login protocols such as OIDC or SAML2。

There can also be another architecture design，As shown in the figure：

[![v8ywlR.jpg](https://s1.ax1x.com/2022/08/11/v8ywlR.jpg)](https://imgtu.com/i/v8ywlR)

In this architecture，Arkid can be used as LDAP Server provides unified account secret services outside，The system that has supported AD domain can be directly accessible。Such as flying books，Three -party systems such as Office365 can be accepted through the SAML2 protocol to complete the single point login。

## Application access

### sign in

ArkID Support for different protocols，So as to support a variety of single -point login protocols

### Unified authority

In addition to the inlet authority that can be controlled by a single point and corresponding to the single -point login，Arkid also provides a technical solution for uniformly controlling permissions in the application。

### Unified approval

ArkIDProvides all technical solutions for all requests that need to be approved within the application，And support these approval requests to push to different approval systems。
