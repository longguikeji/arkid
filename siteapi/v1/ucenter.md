# 注册

## 手机注册

1. 提交手机注册申请，发送验证码
    > /service/sms/register/ [POST]
    - captcha
    - captcha_key
    - mobile

	短信中获取验证码 (code)

2. 校验短信验证码 
    > /service/sms/register/ [GET]
    - mobile
    - code

    · sms_token

3. 凭sms_token创建用户
    > /ucenter/register/ [POST]
    - sms_token
    - password
    - username

## 邮件注册

1. 提交邮件注册申请，发送邮件
    > /service/email/register/ [POST]
    - email
 
 	邮件中获取验证码( email_token )

2. 校验邮件验证码，获取邮箱用于展示
    > /service/email/register/ [GET]
    - email_token

    · email

3. 凭email_token创建用户
    > /ucenter/register/ [POST]
    - email_token
    - password
    - username

# 重置密码

## 短信重置密码
1. 提交手机重置密码申请，发送验证码
    > /service/sms/reset_password/ [POST]
    - captcha
    - captcha_key
    - mobile
    - username

	短信中获取验证码 (code)

2. 校验短信验证码 
    > /service/sms/reset_password/ [GET]
    - mobile
    - code

    · sms_token

3. 凭sms_token重置密码 
    > /ucenter/password/ [PATCH]
    - mobile
    - sms_token
    - new_password
    

## 邮件重置密码
1. 提交邮件重置密码申请，发送验证邮件
    > /service/email/reset_password/ [POST]
    - email
    - username

    邮件中获取验证码 (email_token)

2. 校验邮件验证码，获取用户名用于展示
    > /service/email/reset_password/ [GET]
    - email_token

    · email  
    · username  
    · name  

3. 凭 email_token 重置密码
    > /ucenter/password/ [PATCH]
    - email
    - email_token
    - new_password

## 旧密码重置密码

1. 凭旧密码重置密码 
    > /ucenter/password/ [PATCH]
    - username
    - old_password
    - new_password

# 激活

1. 管理员在后台添加新用户，并生成邀请码
    > /invitation/user/{username}/ [POST]

    · key

2. 解析邀请码，获得token等信息
    > /ucenter/profile/invited/ [GET]
    - key

    · private_email - 从该字段中获取`private_email`，作为后续步骤的`email`，注意不要直接使用`email`  
    · mobile
    · name


## 短信激活

1. 提交短信激活申请，发送验证码
    > /service/sms/activate_user/ [POST]
    - key

    短信中获取验证码 (code)

2. 校验短信验证码
    > /service/sms/activate_user/ [GET]
    - mobile
    - code

    · sms_token

3. 凭邀请码、sms_token 设置账号密码
    > /ucenter/profile/invited/ [PATCH]
    - key
    - sms_token
    - username
    - password

## 邮件激活

1. 提交邮件激活申请，发送验证邮件
    > /service/email/activate_user/ [POST]
    - key

    邮件中获取验证码 (email_token)

2. 校验邮件验证码，获取用户邮箱展示
    > /service/email/activate_user/ [GET]
    - email_token

    · email  
    · username  
    · name  
    · key  

3. 凭邀请码、email_token 设置账号密码
    > /ucenter/profile/invited/ [PATCH]

    - key
    - email_token
    - username
    - password



# 修改联系方式

## 修改手机
整个流程均需登录

1. 提交修改手机申请，发送验证码
    > /service/sms/update_mobile/ [POST]
    - mobile
    - password

    短信中获取验证码 (code)

2. 校验短信验证码
    > /service/sms/update_mobile/ [GET]
    - mobile
    - code

    · sms_token

3. 凭密码、sms_token 重置手机
    > /ucenter/contact/ [PATCH]
    - sms_token


## 修改私人邮箱
整个流程均需登录

1. 提交修改私人邮件申请，发送验证邮件
    > /service/email/update_email/ [POST]
    - email
    - password

    邮件中获取验证码 (email_token)

2. 校验邮件验证码，获取用户名用于展示
    > /service/email/update_email/ [GET]
    - email_token

    · email (这里为希望改成的私人邮箱)  
    · username  
    · name  

3. 凭密码、email_token 重置私人邮箱
    > /ucenter/contact/ [PATCH]
    - email_token


* 在换取到sms_token后，code随即失效。
* 凭sms_token、email_token进行操作时(指步骤3，不包括纯粹的验证token)，一旦token验证成功，随即失效，不管其他验证是否通过、目的是否达成。
* 本文中的`email`均为私人邮箱，内部均按`private_email`存储和查询。