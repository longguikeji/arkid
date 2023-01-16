# Plug -in development

## What is the plug -in？

The main purpose of the plug -in is to meet the user's personality needs as much as possible，And prevent ARKID's own products from being too high and too high。

The plug -in is an independent Python module。

## What can I do in my plug -in？

The plug -in can use Django and Django-Except for the complete function used by Ninja framework，

ArkIDDefine or provide the following functions for plug -in：

* Custom new API，Or update the kernel API
* Custom new back -end routing，Front -end routing，Front -end page
* Custom new Django Model，Or expand the niche original Model
* Customize new events (Event)，Or listen to the kernel event
* Custom PIP dependencies
* Custom configuration
* Custom document
* Custom language package

## How to develop plug -in？

CLONE of Arkid's warehouse to locally，exist**extension_root**Add a folder in the directory，This folder is the main catalog of the plug -in。
Add in this directory **\_\_init\_\_.py** document，Plug -in**main**document。

exist **extension_root** In the directory，Officially provided multiple default plugins，They are all good examples。

More teaching，reference **[Novice Tutorial：Develop the first plug -in] (%20 Develop the first plug -in/)**

## Want to share or sell your plug -in？

Officially provided a plug -in store，Developers can put the plug -in **github private warehouse link** or**zip package**Upload，You can share or sell your plug -in。

Specific tutorial reference：**[Plug -in release] (%20 Test and release/release/)**

## need help？

You need any help，You can contact us at any time by mail，email address：**support@longguikeji.com**

Can also be below**Comment**or **[github forum] (https://github.com/longguikeji/arkid/discussions)** Ask us to ask us questions or leave a message。
