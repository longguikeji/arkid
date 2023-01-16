# ArkIDOperator

If you want to operate your independent IDAAS site，Your user uses Arkid directly as a tenant，Then you can expose Arkid on the public website，Configure the domain name。

## Operator conditions

* Public network server (any cloud service is available)
* Deploy private ARKID and set domain names
* Open ARKID's multi -tenant switch

## Operating rules

### Plug -in lease

Practitioner paid to use operator's Arkid service。Arkid's plug -in supports lease。That is, tenants need lease to use these plug -ins。

The operator is regarded as a kind of agent，Related settings are exactly the same as the agent。

Also**Agent level**，Set up**Agent discount**

Similar to proxy，All tenants regard the operator as their agents。The relevant calculations are as follows：

* Tenture rental price
  
    ```Tenture rental price = Developer rental market guidance price * Operator agent discount + Operator takes the price```

* Operator takes the price

    ```Operator takes the price = Developer rental market guidance price * Maximum（Developer rental cost discount，Operator agent level discount）+ ArkStore platform commission```

* ArkStorePlatform commission
    
    ```ArkStorePlatform commission = Minimum（Developer rental market guidance price * 0.1 ， Developer rental market guidance price * Developer rental cost discount * 0.3）```

* Operator level discount
    
    ```Operator level discount rules，See```[Agent level discount rules] (../%20 agent/#_4)

### Application purchase

The operator will be regarded as the agent of its tenant，That is, tenants purchase application，The operator will also get the corresponding division。

## Operating expenses

In addition to the operator needs to purchase plug -in or apps directly from a plug -in or app store，In principle, Long Gui will not have any additional charges to operators，It does not rule out that the operator needs additional hosting，Operation and maintenance，Development service，This part can be sent to [BD@Dragon Turtle Technology.com] (Mailto:bd@Dragon Turtle Technology.com)，Inform your needs，We will contact you。

## Order and withdrawal

You can check the agent order or initiate a withdrawal application in the ARKSTORE expense center。
