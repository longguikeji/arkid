# Default approval system plug -in

## Features
After the default approval system plug -in installation，Will be at**Approval management**Add below the menu**Default request processing**page，Used to handle approval requests assigned to the current approval system

### Create approval action
=== "Open the approval action page，Click to create button"
    [![X7nDTH.png](https://s1.ax1x.com/2022/06/16/X7nDTH.png)](https://imgtu.com/i/X7nDTH)

=== "Fill in form parameters"
    [![X45oyq.png](https://s1.ax1x.com/2022/06/14/X45oyq.png)](https://imgtu.com/i/X45oyq)


### Generate approval request

=== "Open the account life cycle，Click to create button"
    [![X7nulV.png](https://s1.ax1x.com/2022/06/16/X7nulV.png)](https://imgtu.com/i/X7nulV)

=== "Configuration form parameter，Click to create button"
    Since the previous step has been configured for approval action for creating a life cycle configuration，So the request should return 403
    [![X59seS.png](https://s1.ax1x.com/2022/06/14/X59seS.png)](https://imgtu.com/i/X59seS)


### Check the approval request

=== "Open**Approval management->Approval request**page"
    [![X5Pr5Q.png](https://s1.ax1x.com/2022/06/14/X5Pr5Q.png)](https://imgtu.com/i/X5Pr5Q)


=== "Open**profile picture->Approval request**page"
    [![X5PDUg.png](https://s1.ax1x.com/2022/06/14/X5PDUg.png)](https://imgtu.com/i/X5PDUg)


### Process approval request

=== "Open**Approval management->Default request processing**page， Click to pass the button"
    [![X5nksH.png](https://s1.ax1x.com/2022/06/14/X5nksH.png)](https://imgtu.com/i/X5nksH)


=== "Open**Audited**bookmark， Confirmation status has changed"
    [![X5nFQe.png](https://s1.ax1x.com/2022/06/14/X5nFQe.png)](https://imgtu.com/i/X5nFQe)


=== "Open**Account life cycle**page， Confirm that the request to be reviewed is re -executed"
    [![X5nPzD.png](https://s1.ax1x.com/2022/06/14/X5nPzD.png)](https://imgtu.com/i/X5nPzD)

    

## Implementation
- exist**approve_requests_page**Add**Default request processing**page
- **Default request processing** Call on the page /approve_requests/{{request_id}}/pass/ Agree with approval request
- **Default request processing** Call on the page /approve_requests/{{request_id}}/deny/ Reject approval request
- accomplish [pass_approve_request](#extension_root.com_Dragon turtle_approve_system_arkid.ApproveSystemArkIDExtension.pass_approve_request) Abstract method Agree with approval request
- accomplish [deny_approve_request](#extension_root.com_Dragon turtle_approve_system_arkid.ApproveSystemArkIDExtension.deny_approve_request) Abstract method Reject approval request
- Since this plug -in does not need to send the approval request to a third party, there is no abstract method of covering [Create_approve_request](#extension_root.com_Dragon turtle_approve_system_arkid.ApproveSystemArkIDExtension.create_approve_request)
- See [ARKID.core.extension.approve_system.ApproveSystemExtension](../../%20%20 Developer Guide/%20 plug -in development/%20 plug -in classification/Approval system/)

## Abstract method implementation:
* [pass_approve_request](#extension_root.com_longgui_approve_system_arkid.ApproveSystemArkIDExtension.pass_approve_request)
* [deny_approve_request](#extension_root.com_longgui_approve_system_arkid.ApproveSystemArkIDExtension.deny_approve_request)
* [create_approve_request](#extension_root.com_longgui_approve_system_arkid.ApproveSystemArkIDExtension.create_approve_request)



## Code

::: extension_root.com_longgui_approve_system_arkid.ApproveSystemArkIDExtension
    rendering:
        show_source: true
