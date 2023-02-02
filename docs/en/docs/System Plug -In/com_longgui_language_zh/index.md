# Multi -language package plugin：Simplified Chinese

## Configuration guide

=== "Plug -in lease"
    Enter through the menu bar on the left【Tenant management】->【Plug -in management】，Find a Chinese language package plug -in card in the plug -in lease page，Click to rent
    [![vEqtlq.png](https://s1.ax1x.com/2022/08/02/vEqtlq.png)](https://imgtu.com/i/vEqtlq)

=== "Language package data update"
    * The system provides language package data online update capabilities，Priority User update language package data > Language package plug -in data > System default language translation<br/>
    + Enter through the menu bar on the left【Platform management】->【Language Package Management】，Enter the language package page page<br/>
    [![vEqohd.md.png](https://s1.ax1x.com/2022/08/02/vEqohd.md.png)](https://imgtu.com/i/vEqohd)
    + Click on the editor button on the right side of the language bag，Enter the language package data details page<br/>
    [![vEqqjP.md.png](https://s1.ax1x.com/2022/08/02/vEqqjP.md.png)](https://imgtu.com/i/vEqqjP)
    + Click the new button in the upper right corner，Enter the new translation page，The original phrase here refers to the phrase to be translated in the system，Translation sentences are translated words<br/>
    [![vEL99s.md.png](https://s1.ax1x.com/2022/08/02/vEL99s.md.png)](https://imgtu.com/i/vEL99s)

## Abstract method implementation
* [language_type](#extension_root.com_longgui_language_zh.TranslationZhExtension.language_type)
* [language_data](#extension_root.com_longgui_sms_aliyun.TranslationZhExtension.language_data)

## Code

::: extension_root.com_longgui_language_zh.TranslationZhExtension
    rendering:
        show_source: true
