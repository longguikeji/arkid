# Register and log in
A total of four types of pages: Log in,register,reset Password，Binding account
Each page determines its function based on the operating plug -in and its configuration。

The basic structure of each page is as follows：

1. Practitioner icon and name
2. Subject form: Support multiple forms, Each form corresponds to a submit button, Trigger the corresponding API
3. Form extension: Used to jump to other pages
4. The extension of the login window: 
      1. Third -party login entrance
      2. Other tips

* register"
[![BK5XVb.jpg](https://v1.ax1x.com/2022/10/14/BK5XVb.jpg)](https://x.imgtu.com/i/BK5XVb)

* Log in"
[![BK5jJe.jpg](https://v1.ax1x.com/2022/10/14/BK5jJe.jpg)](https://x.imgtu.com/i/BK5jJe)
## Practitioner icon and name

exist [Practice configuration] () Change


## Log in, register, reset Password

The contents of these three pages are mainly consistent [Certification factor] () Configuration decision，Configure by administrator，So as to have SMS verification，Various functions of mailbox registration and other functions。

## Binding account

!!! hint

    The content of the binding account page is always consistent with the content of the login page。

After you enter the system through a third party login，If the account does not bind the account of ARKID，**Binded account page**Will open。

Binded account window，Will clearly remind users to complete the login through which third -party account number，And display its avatar and name。The content of this part，Directly displayed in“The extension of the login window”To。Text：“Your WeChat account（WeChat name）No ARKID account。If you already have an arkid account，Log in through this window to complete the binding。If you have no，You can enter the registration page to create a new account。”



## worth mentioning

The administrator can be [worth mentioning]() Manage all third parties login。

Click on the third party to log in，There will be two cases。

   * This three -party account has been bound to the ARKID account，Then there is no need to bind，Directly enter the system。
   * The second is that the account is not bound to ARKID account，It is required to be binding，Enter the binding window
