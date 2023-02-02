## Features

Message middleware plug -in for platform introduction message middle parts（Such as Artemis,KAFKA etc.）Communication with a third -party system（If the notification data）

## Implementation
When developing a message in the middleware plug -in，Only inherit the message of the message intercding and complete the data writing process，The platform has provided message storage model（Scalable）,And provide message storage methods in the base class：

## Foundation definition

::: arkid.core.extension.message.MessageExtension
    rendering:
        show_source: true
