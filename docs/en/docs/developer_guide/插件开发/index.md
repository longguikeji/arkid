# Plug-in development

## What is the plug-in?

The main purpose of the plug-in is to meet the individual needs of users as much as possible and to prevent the complexity of ArkID's own products from being too high.

A plug-in is a standalone python module.

## What can a plug-in do?

Plugins can use the full functionality of Django and the django-ninja framework,

ArkID defines or provides the following functions for the plug-in:

* Customize the new API, or update the kernel API
* Customize new backend routing, frontend routing, frontend pages
* Customize the new Django Model, or extend the original Model in the kernel
* Customize a new Event, or listen for kernel events
* Custom pip dependencies
* Custom configuration
* Customize the document
* Customize the language pack

## How to develop plug-ins?

Clone the ArkID repository to the local directory, and ** extension_root ** add a folder under the directory, which is the home directory of the plug-in. Add ** \_\_init\_\_.py ** the files in this directory, which are the files for the plug-in ** main **.

In the ** extension_root ** table of contents, there are several default plug-ins, which are good examples.

More teaching, reference

## Want to share or sell your plugin?

There is an official plugin store, and developers can share or sell your plugin by ** Zip package ** ** Link to github private repository ** uploading or uploading the plugin.

Specific tutorial reference: **[插件发布](%20测试与发布/发布/)**

## Need help?

If you need any help, you can contact us by email at any time, email address: **support@longguikeji.com**

You can also ask us a question or leave us a message below ** Comment ** or **[github论坛](https://github.com/longguikeji/arkid/discussions)** in.