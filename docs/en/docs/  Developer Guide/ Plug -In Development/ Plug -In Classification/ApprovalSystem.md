## Features
The approval system is mainly used to handle approval requests，Plug -in developers can be in processing approval request logic，Send the approval request to different third -party systems，After the third -party system has processed the approval request，You can send the processing results back

## Implementation
* First create approval action，Specify the interface PATH, Method and the approval system plug -in responsible for processing

* In the middle part**arkid.core.approve_request_middleware**According to the scanning approval action，Intercept http Request，
    1. If an approval action does not create an approval request，Then create approval requests，distribution**CREATE_APPROVE_REQUEST**event，HTTP Request stored in the approval request, Interrupt http Request
    2. If an approval action has been created for approval request，Determine the approval request status，If the state is passed，Continue to execute HTTP Request，If the status is rejected，Interrupt http Request

* Supervise in the approval system plug -in**CREATE_APPROVE_REQUEST**event，Through [Create_approve_request](#arkid.core.extension.approve_system.ApproveSystemExtension.create_approve_Request) Send the approval request to other third -party system processing

* After other third -party approval systems process the approval request，You can return the approval results through the interface

    - agree**Approval request**interface

        - path：/approve_requests/{{request_id}}/pass/
        - method: PUT
        - Processing function：pass_approve_request_handler
        - Need to implement abstract methods: [pass_approve_request](#arkid.core.extension.approve_system.ApproveSystemExtension.pass_approve_request)

    - reject**Approval request**interface

        - path：/approve_requests/{{request_id}}/deny/'
        - method: PUT
        - Processing function：deny_approve_request_handler
        - Need to implement abstract methods: [deny_approve_request](#arkid.core.extension.approve_system.ApproveSystemExtension.deny_approve_request)

## Abstract method
* [create_approve_request](#arkid.core.extension.approve_system.ApproveSystemExtension.create_approve_request)
* [deny_approve_request](#arkid.core.extension.approve_system.ApproveSystemExtension.deny_approve_request)
* [pass_approve_request](#arkid.core.extension.approve_system.ApproveSystemExtension.pass_approve_request)

## Foundation definition

::: arkid.core.extension.approve_system.ApproveSystemExtension
    rendering:
        show_source: true
    
## Exemplary

::: extension_root.com_longgui_approve_system_arkid.ApproveSystemArkIDExtension
    rendering:
        show_source: true
