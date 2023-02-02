# CasServer

CASIt's Central Authentication Abbreviation of service，Central Certification Service。When a user visits the CAS authentication server，Request authentication。CAS certification service will check whether the user logs in。Go to log in if you don't log in，If you have logged in，CAS will issue a short -term TGT bill，And regatt it to the service address provided by developers。Then，The application connects CAS through a secure connection，And provide your own service logo and verification ticket。After that, CAS gave identity information about specific users

The entire certification process is shown in the figure:

``` mermaid
graph LR
  A[start] --> B [Visit Login Page] --> C {Whether to log in}--> |Yes| D [Bring the bills jump to the service address]--> E [Use bills to obtain user information] --> F [End];
  C ---->|No| G[Log in!];
  G --> |login successful| D;
```

## CasCertification

### Create an application

=== "Open the application list"
    [![jxpxtP.md.jpg](https://s1.ax1x.com/2022/07/25/jxpxtP.md.jpg)](https://imgtu.com/i/jxpxtP)
=== "New CAS application"
    [![jx9Fmj.md.jpg](https://s1.ax1x.com/2022/07/25/jx9Fmj.md.jpg)](https://imgtu.com/i/jx9Fmj)
=== "Click the protocol configuration in the list"
    [![jx9Zt0.md.jpg](https://s1.ax1x.com/2022/07/25/jx9Zt0.md.jpg)](https://imgtu.com/i/jx9Zt0)
=== "Select the type as CAS and confirm"
    [![jx9MX4.md.jpg](https://s1.ax1x.com/2022/07/25/jx9MX4.md.jpg)](https://imgtu.com/i/jx9MX4)
=== "Click the protocol configuration again in the list"
    [![jx9TNq.md.jpg](https://s1.ax1x.com/2022/07/25/jx9TNq.md.jpg)](https://imgtu.com/i/jx9TNq)
=== "Save login and check address"
    [![jxCi8K.md.jpg](https://s1.ax1x.com/2022/07/25/jxCi8K.md.jpg)](https://imgtu.com/i/jxCi8K)


### use Cas application
1.  Place the login link on a third -party page that needs to be logged in

    Here you need to allow users to access the unified authentication of Arkid on the side。The service parameter is a callback address after Arkid certification。

    http://localhost:9528/api/v1/tenant/4da114ce-e115-44a0-823b-d372114425d0/app/e78f117b-1632-42c9-8e3c-ec4fd796c89e/cas/login/?service=http://www.baidu.com

    The page will automatically jump to log in

    http://localhost:9528/login?next=/api/v1/tenant/4da114ce-e115-44a0-823b-d372114425d0/app/e78f117b-1632-42c9-8e3c-ec4fd796c89e/cas/login/%3Fservice%3Dhttp%3A//www.baidu.com&tenant_id=4da114ce-e115-44a0-823b-d372114425d0

2. After the login is successful, you will get a bill

    https://www.baidu.com/?ticket=ST-1658743424-pvotuhaInoW1UGQlIlD1eLU6tZoMppu6

3. Obtain user information through the verification address

    A bill can only be used once，Service is the same as the previous login，If you succeed, you can get user information

    [![jxCIMD.md.jpg](https://s1.ax1x.com/2022/07/25/jxCIMD.md.jpg)](https://imgtu.com/i/jxCIMD)

    If you try to use the notes you have used

    [![jxCHZd.md.jpg](https://s1.ax1x.com/2022/07/25/jxCHZd.md.jpg)](https://imgtu.com/i/jxCHZd)

    You need to log in each time you get the bill and then use the bill to exchange for user information
