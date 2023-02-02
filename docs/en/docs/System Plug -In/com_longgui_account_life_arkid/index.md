# Default life cycle plug -in

## Features
Set the user expiration time，The timing task will regularly compare the user's expiration time and the current time，If the current time is greater than the user expiration time，The user is disabled

### Configure the life cycle timing task

=== "Open the account life cycle page"
    Clicked**Edit life cycle timing task**Button
    [![X7mszV.png](https://s1.ax1x.com/2022/06/16/X7mszV.png)](https://imgtu.com/i/X7mszV)

=== "Configure timing task form parameters"
    Among them, timing running time grammar reference**linux Crontab**Command grammar，The following figure is an example：Run once every day at 8 o'clock，If it fails, try it again every 30 seconds at intervals
    [![X4Jmsf.png](https://s1.ax1x.com/2022/06/14/X4Jmsf.png)](https://imgtu.com/i/X4Jmsf)


### Configure user expiration time


=== "Click to create button"
    [![X7nulV.png](https://s1.ax1x.com/2022/06/16/X7nulV.png)](https://imgtu.com/i/X7nulV)

=== "Click Config"
    [![X7nGk9.png](https://s1.ax1x.com/2022/06/16/X7nGk9.png)](https://imgtu.com/i/X7nGk9)

=== "Configure users and expiration time"
    [![X4ye4P.png](https://s1.ax1x.com/2022/06/14/X4ye4P.png)](https://imgtu.com/i/X4ye4P)

=== "After the configuration is complete，Click to create button"
    [![X4yn9f.png](https://s1.ax1x.com/2022/06/14/X4yn9f.png)](https://imgtu.com/i/X4yn9f)

## Implementation
Time tasks compare the user's expiration time and current time，If the user has expired，Then set the user attribute is_Active is false，The user will be prohibited from logging in to ARKID</br>
Abstract methods to cover the base class of plug -in，See [ARKID.core.extension.account_life.AccountLifeExtension](../../%20%20 Developer Guide/%20 plug -in classification/Account life cycle/)

## Abstract method implementation:
* [periodic_task](#extension_root.com_longgui_account_life_arkid.AccountLifeArkIDExtension.periodic_task)


## Code

::: extension_root.com_longgui_account_life_arkid.AccountLifeArkIDExtension
    rendering:
        show_source: true
