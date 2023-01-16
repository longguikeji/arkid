## Features
Account life cycle，Used to handle account creation，change，Disable the logic of account attributes in the process of division，Plug -in developers can flexibly add their own logic as needed

## Implementation

- ArkIDCore provides the timing task of interface creation and update life cycle: **arkid.core.tasks.tasks.account_life_periodic_task**
- Timing task**account_life_periodic_task**Will send it at running**ACCOUNT_LIFE_PERIODIC_TASK**event
- This incident will be monitored in the plug -in base class，In the event processing function [Periodic_task_event_handler](#arkid.core.extension.account_life.AccountLifeExtension.periodic_task_event_Handler) Call the abstract method of abstraction [periodic_task](#arkid.core.extension.account_life.AccountLifeExtension.periodic_task)
- Cover abstract method in the specific plug -in [PERIODIC_task](#arkid.core.extension.account_life.AccountLifeExtension.periodic_task) to implement specific logic

## Abstract method
* [periodic_task](#arkid.core.extension.account_life.AccountLifeExtension.periodic_task)
## Foundation definition

::: arkid.core.extension.account_life.AccountLifeExtension
    rendering:
        show_source: true
    
## Exemplary

::: extension_root.com_longgui_account_life_arkid.AccountLifeArkIDExtension
    rendering:
        show_source: true
        
