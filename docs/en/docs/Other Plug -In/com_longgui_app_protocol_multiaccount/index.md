# Application multiple accounts

## Features

This plugin is based on the ARKID account system (OIDC application) derivative child application multi -account management，That is, one ARKID account can bind multiple sub -application accounts，Subcutors can choose the specific login account when receiving account login

``` mermaid
    sequenceDiagram
    participant U as user
    participant P as platform
    participant A as third-party usage
    
    U->>P: Access third -party application
    P->>A: Jump to third -party application entrance
    A->>P: Integrate the OIDC protocol data to launch a login request
    P->>U: Corresponding request，Jump login interface
```

### Steps


### Login interface
