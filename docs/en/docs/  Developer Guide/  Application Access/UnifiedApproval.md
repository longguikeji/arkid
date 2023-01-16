# Unified approval

## Features

The unified approval consists of three parts：

- **Approval**
- **Approval request**
- **Approval system**

### ArkIDCore (approval action，Approval request，Approval system plug -in base class)：

1. create**Approval**: Specify the API interface required for approval, And responsible for approving the API call**Approval system**

2. Monitor API call: When API calls occur，Do the following treatment:

    * If the API call does not create the corresponding**Approval request**，API call interrupt，create**Approval request**，pass**CREATE_APPROVE_REQUEST**The event is sent to the corresponding approval system。
    * If the API call has created the corresponding**Approval request**:

        - Should**Approval request**quilt**Approval system**Not processed，API call interrupt
        - Should**Approval request**quilt**Approval system**reject，API call interrupt
        - Should**Approval request**quilt**Approval system**agree，API calls continue to execute

3. Approval system plug -in base class
   
    * See [ARKID.core.extension.approve_system.ApproveSystemExtension](../../%20 plug -in development/%20 plug -in classification/Approval system/)
    * monitor**CREATE_APPROVE_REQUEST**event，Define abstract functions**create_approve_request**, The third -party plug -in system can implement this method，Send the approval request to the third -party system for processing
    * Create two interfaces to handle the logic of approval requests passing and rejection:
    
        - agree**Approval request**interface

            - path：/approve_requests/{{request_id}}/pass/
            - method: PUT
            - Processing function：pass_approve_request_handler
            - Need to implement abstract methods: pass_approve_request

        - reject**Approval request**interface

            - path：/approve_requests/{{request_id}}/deny/'
            - method: PUT
            - Processing function：deny_approve_request_handler
            - Need to implement abstract methods: deny_approve_request

4. ArkIDSystem default approval system

Third -party approval system plug -in can refer to the logic of the system plug -in with the default approval system plug -in， See the default approval system for [Extension_root.com_Dragon turtle_approve_system_arkid.ApproveSystemArkIDExtension](../../../%20%20 system plug -in/com_Dragon turtle_approve_system_arkid/)

