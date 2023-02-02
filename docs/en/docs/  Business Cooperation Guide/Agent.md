# ArkIDAgent

If you can contact customers，And conquer customers。That's very suitable to be an ARKID agent。

## Proxy condition

* Have the opportunity to contact customers
* Having ARKID account
* Visit ArkStore

## Plug -in proxy rules

1. Visit ArkStore
2. Clicked Agent-Agent details，Here you can see all the information of the current agent

    * Agent trademark
    * Total sales（Market guidance）
    * Annual sales（Market guidance）
    * Actual total sales（Trading price）
    * Actual annual sales（Trading price）
    * Initial level
    * Annual
    * Agent level
    * Level discount
    * Sales required for upgrade
    * Proxy discount（Can be changed）

Explain the meaning and role of each parameter：

```
Total sales，It shows the total cumulative sales of this agent,Calculate by the development of the developer's market guidance price。
Annual sales，Refers to this year's sales，Calculate by the development of the developer's market guidance price。

Actual total sales，Calculate with the actual transaction price，All cumulative sales。
Actual annual sales，Calculated at the actual transaction price，This year's sales。
```

### Agent trademark

When your client uses privatization deployment to install ARKID，You can be in the back office of the ARKID management：Platform management - Platform plug -in Found the upper right corner of the page “Set an agent” Button，Click and fill in the pop -up dialog box"Agent trademark"，Click to confirm。This completes the client，Agent's binding。

After the customer completes the agent binding，The price of its plug -in store and application store will display the price of the agent's agent，And all purchase behaviors will pass the agent to produce orders。

### Agent level

Total sales，Agent level（Initial level，Annual）， Agent level discount，Sales required for annual level upgrade。These parameters are part of the agent level system。

**Agent level** Pick **Initial level of agents** and **Agent year** Maximum value

Initial level of agents：Agent last year**Annual** Will become agents this year**Initial level**，The default value is 1

Agent year：Early morning on January 1st every year, it will be reset to 1，And the annual sales clearly zero

The agent level will determine the corresponding level discount，See the table below：

| Proxy | Level discount | **Annual**Upgrade requires annual sales（Yuan） |
|--------|---------|----------|
| 1（Initial level）| 0.9 |  0       |
| 2 | 0.8 | 200 |
| 3 | 0.7 | 400 |
| 4 | 0.6 | 800 |
| 5 | 0.5 | 1600 |
| 6 | 0.4 | 3200 |
| 7 | 0.3 | 6400 |
| 8 | 0.2 | 12800 |
| 9 | 0.1 | 25600 |
| 10 | 0 | 51200 |

!!! Notice
    Annual sales of annual upgrade，It is calculated based on market guidance price。

Level discount determines the minimum discount of the agent to get the goods，If the developer of this product is set up**Cost discount**Agent**Level discount**，Follow**Level discount**Calculate the price of the goods，If a developer**Cost discount**Greater than agent**Level discount**，Then press **Cost discount** Calculate the price of the goods。which is：

Agent takes the goods price = Developer market guidance price * Maximum value (developer cost discount，Agent level discount) + ArkStore platform commission

### ArkStorePlatform commission

ArkStorePlatform commission = Minimum（Developer market guidance price * 0.1 ， Developer cost price * 0.3）

This means，If the developer's market guidance price is 0，Immediately free，Users can get it for free。

If the cost of the developer is 0，That is, the cost discount of developers is 0，Then the agent can pick up the goods for free。

### Proxy discount

Set freely by agents 0-1 Number。

### The calculation rules are as follows

* Agent takes the goods price

    ```Agent takes the goods price = Developer market guidance price * Maximum value (developer cost discount，Agent level discount) + ArkStore platform commission```

* Product expected sales price

    ```Product expected sales price = Developer market guidance price * Agent agent discount + Agent takes the goods price```

* Product final sales price：It must not be higher than the market guidance price agreed

    ```Product final sales price = Minimum value (product expected sales price, Developer market guidance price)```

* Agent profit = Developer market guidance price * Agent agent discount。

    ```Agent profit = Product final sales price - Agent takes the goods price```
    

## Application proxy rules

Application proxy rules compared to Plug -in Be more complicated。Because the application access standards are different，The division ratio required by each application developer，Different accounting periods。Each application requires specific proxy rules。

Roughly divided into these categories：

1. OIDC and Store payment

    The application uses the OIDC protocol to connect with Arkid and connect to the store payment standard，The proxy rules are consistent with the plug -in。

2. In -application payment

    Application**OIDC protocol**or**Custom protocol**Access with Arkid，But use internal payment，It also means that the application is free application。The division ratio is based on the developer set。

3. sponsored links and In -application payment

    If the application only uses the promotion link，ARKID cannot obtain the mapping relationship with ARKID identity in the application，Unable to divide the agent according to the actual usage。
    
    The promotion link uses a record of clicks and calculates the clicks to the proportion，Divide the proportion through this clicks。

## Order and withdrawal

You can check the agent order or initiate a withdrawal application in the ARKSTORE expense center。

## Q&A
