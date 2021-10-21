# Provisoning 预设

通过本功能可以快速同步当前ArkID的账号信息数据到第三方应用中，常见的为SaaS厂商应用，如： Github等


## 协议支持

1. SCIM V2.0


## Privisoning 策略

1. SCIM Information
2. Model Mapping ( ArkID User -> Your App User)
3. Scope(all users & groups / assgined users & groups)
4. Notification Settings


### SCIM Configuration Information

1. EndPoint, 如: http://scimdemoapp.dev.attackt.com/scim/v2/
2. Secret Token(Optional)

### Model Mapping

ArkID Users
ArkID Groups