# Static file storage plug -in：Local file storage

## Features

Realize localized storage of static files，Storage path is default/data

* Notice： This is a platform plug -in，Need a platform administrator permissions for configuration

## Configuration guide

=== "Plug -in lease"
    Enter through the menu bar on the left【Tenant management】->【Plug -in management】，Find the local file storage plug -in card in the plug -in lease page，Click to rent<br/>
    [![Plug -in rental] (https://S1.ax1x.com/2022/08/02/vELyVS.png)](https://imgtu.com/i/vELyVS)

=== "Platform configuration"
    Enter through the menu bar on the left【Platform management】->【Platform plug -in】, Find the local file storage plug -in card on the installed page，Click the plug -in configuration，Configure file storage path<br/>
    [![Platform configuration] (https://S1.ax1x.com/2022/08/02/vELXx1.png)](https://imgtu.com/i/vELXx1)<br/>
    [![Platform configuration] (https://S1.ax1x.com/2022/08/03/widget.md.png)](https://imgtu.com/i/VVD6 and

## Implementation

When developing static file storage plug -in，Need to inherit StorageExtentance,And re -load Save_The file and resolve method can be

## Abstract method implementation

* [load](#extension_root.com_longgui_storage_local.LocalStorageExtension.load)
* [save_file](#extension_root.com_longgui_storage_local.LocalStorageExtension.save_file)
* [resolve](#extension_root.com_longgui_storage_local.LocalStorageExtension.resolve)
* [read](#extension_root.com_longgui_storage_local.LocalStorageExtension.read)

## Code

::: extension_root.com_longgui_storage_local.LocalStorageExtension
    rendering:
        show_source: true
