# Application access


## Find out the business system

Before starting to access, we should first find out the general situation of the company's business system:

1. What are the systems?
2. What protocol does each system use to support single sign-on or unified account encryption?
3. How many data sources are there for the user, which ones are kept and which ones are discarded
4. What is the synchronization relationship between the data sources

Wait

## System architecture

After dealing with these problems, we can start to design the system architecture. The following figure is an example of a typical system architecture diagram:

[![v8sYRA.jpg](https://s1.ax1x.com/2022/08/11/v8sYRA.jpg)](https://imgtu.com/i/v8sYRA)

After the user data is entered into the EHR system, it is synchronized to the AD domain through the SCIM data. The AD domain is used as a standard data source, and Microsoft systems or some systems supporting AD can be directly connected to the AD domain (note that the AD domain is a unified account password, not a single sign-on). Other systems such as OA can be connected with ArkID through single sign-on protocols such as OIDC or SAML2.

There can also be another architecture design, as shown in the figure:

[![v8ywlR.jpg](https://s1.ax1x.com/2022/08/11/v8ywlR.jpg)](https://imgtu.com/i/v8ywlR)

In this architecture, ArkID can be used as an LDAP Server to provide unified account security services, and systems that already support the AD domain can be directly accessed. Third-party systems such as Feishu and Office365 can be accessed through SAML2 protocol to complete single sign-on.

## Application access

### Single sign-on

ArkID supports various single sign-on protocols by supporting different protocols

### Unify permissions

In addition to unified control of entry permissions corresponding to single sign-on, ArkID also provides a technical solution for unified control of permissions within the application.

### Unified examination and approval

ArkID provides a technical solution for unified processing of all requests that need to be approved within the application, and supports pushing these approval requests to different approval systems.
