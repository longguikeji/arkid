## Features
Static storage plug -in to increase static files to ARKID（Such as pictures，Certificate）Ability to upload，Developers only need to inherit the base class and load the corresponding abstraction method。

## Implementation

When developing static storage plug -in，Only inherit the StorageExtenSion base class，And re -load Save_Abstract functions such as file。

The example is as follows：

``` py
class LocalStorageExtension(StorageExtension):

    def load(self):
        self.register_profile_schema(ProfileSchema)
        
        self.register_api(
            "/localstorage/{file_name}",
            'GET',
            self.get_file,
            tenant_path=True,
        )
        
        super().load()

    def save_file(self, file, f_key, *args, **kwargs):
        extension = self.model
        storage_path = extension.profile.get('storage_path','./storage/')
        
        p = Path(storage_path) / f_key

        if not p.parent.exists():
            p.parent.mkdir(parents=True)

        with open(p, 'wb') as fp:
            for chunk in file.chunks():
                fp.write(chunk)
                
    def resolve(self, f_key, tenant, *args, **kwargs):
        host = get_app_config().get_frontend_host()
        return f'{host}/api/v1/tenant/{tenant.id}/com_longgui_storage_local/localstorage/{f_key}'
    
    def get_file(self, request, tenant_id: str, file_name:str):
        """ Local storage plug -in to obtain files
        """
        extension = self.model
        storage_path = extension.profile.get('storage_path','./storage/')
        file_path = Path(storage_path) / file_name
        
        return FileResponse(
            open(file_path, 'rb')
        )
    
     def read(self,tenant_id,file_url,**kwargs):
        """Read file data

        Args:
            tenant_id (str): Tenant ID
            file_url (str): File link

        Returns:
            bytes: File data
        """
        host = get_app_config().get_frontend_host()
        useless_part = f'{host}/api/v1/tenant/{tenant_id}/com_longgui_storage_local/localstorage/'
        file_name = file_url.replace(useless_part, "")
        extension = self.model
        storage_path = extension.profile.get('storage_path','/data')
        file_path = Path(storage_path) / file_name
        rs = None
        
        with open(file_path,"rb") as f:
            rs = f.read()
        
        return rs
    
```

File storage and reading examples are as follows：
```python

    tenant = request.tenant
    data = {
        "file": file,
    }
    
    extension = Extension.active_objects.filter(
        type="storage"
    ).first()
    # Storage file event
    responses = dispatch_event(Event(tag=SAVE_FILE, tenant=tenant, request=request, packages=extension.package, data=data))
    if not responses:
        return ErrorDict(ErrorCode.STORAGE_NOT_EXISTS)
    useless, (data, extension) = responses[0]
    
    if not data:
        return ErrorDict(ErrorCode.STORAGE_FAILED)
    
    #Read file event
    t_responses = dispatch_event(Event(tag=READ_FILE, tenant=tenant, packages=extension.package, data={"url":data}))
    if not t_responses:
        return ErrorDict(ErrorCode.STORAGE_NOT_EXISTS)

    useless, (data, extension) = t_responses[0]
    
    if not data:
        print("Failure")

```



## Abstract function

* [save_file](#arkid.core.extension.storage.StorageExtension.save_file)
* [resolve](#arkid.core.extension.storage.StorageExtension.save_file)
* [read](#arkid.core.extension.storage.StorageExtension.read)

## Foundation definition

::: arkid.core.extension.storage.StorageExtension
    rendering:
        show_source: true
    
## Exemplary

::: extension_root.com_longgui_storage_local.LocalStorageExtension
    rendering:
        show_source: true
