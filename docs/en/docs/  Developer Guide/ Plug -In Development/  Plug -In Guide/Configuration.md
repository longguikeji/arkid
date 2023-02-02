# Configuration

## Root directory file configuration

In the root directory of the plugin，Need Config.Toml file，The basic content of this file is as follows：

``` toml title="config.toml"
package='com.longgui.case'
name="Sample plugin"
version='1.0'
labels='case'
homepage='https://www.company.com'
logo=''
author='case@company.com'
```

This file is with extension.\_\_init\_\_ The same role of the function.

When uploading the plug -in to the plug -in store，The plug -in store will also obtain the basic information of the plug -in through this configuration file。


## Database configuration

The kernel is for the convenience of the plug -in，Customized the configuration form of three plug -in。

And to generate the corresponding SCHEMA for these configurations to enable each plug -in API to dynamically adapt to the addition and deletion of the plugin。


### Plug -in configuration (Profile)
:   Define [arkid.extension.models.Extension](#arkid.extension.models.Extension) middle

    One -to -one configuration with the plug -in itself，json format

    use [arkid.core.extension.Extension.register_profile_schema](../%20 plug -in base class/#arkid.core.extension.Extension.register_profile_schema) Register its schema

    profileAdding, deletion, change inspection [self.model](../%20 plug -in base class/#arkid.core.extension.Extension.model) Complete completion

### Considuous configuration (Settings)

:   Define [arkid.extension.models.TenantExtension](#arkid.extension.models.TenantExtension) middle

    There is only one settings configuration for each plugin under each tenant，json format

    use [arkid.core.extension.Extension.register_settings_schema](../%20 plug -in base class/#arkid.core.extension.Extension.register_settings_schema) Register its schema

    settingsAdding, deletion, change inspection：

    * [self.get_tenant_settings](../%20Plug -in base class/#arkid.core.extension.Extension.get_tenant_settings)
    * [self.update_or_create_settings](../%20Plug -in base class/#arkid.core.extension.Extension.update_or_create_settings)

### Configuration (config) during runtime
:   Define [arkid.extension.models.TenantExtensionConfig](#arkid.extension.models.TenantExtension) middle

    Each plugin under each tenant has multiple configs，json format

    use [arkid.core.extension.Extension.register_config_schema](../%20 plug -in base class/#arkid.core.extension.Extension.register_config_schema) Register its schema

    use [arkid.core.extension.Extension.register_composite_config_schema](../%20 plug -in base class/#arkid.core.extension.Extension.register_composite_config_schema) Register a type of SCHEMA

    configAdding, deletion, change inspection:

    * [self.get_tenant_configs](../%20Plug -in base class/#arkid.core.extension.Extension.get_tenant_configs)
    * [self.get_config_by_id](../%20Plug -in base class/#arkid.core.extension.Extension.get_config_by_id)
    * [self.create_tenant_config](../%20Plug -in base class/#arkid.core.extension.Extension.create_tenant_config)
    * [self.update_tenant_config](../%20Plug -in base class/#arkid.core.extension.Extension.update_tenant_config)
    * [self.delete_tenant_config](../%20Plug -in base class/#arkid.core.extension.Extension.delete_tenant_config)


!!! attention "Notice"
    The schema of the plug -in should be called arkid.core.extension.create_extension_schema Methods to complete

```py title='Exemplary'
...

package = 'com.longgui.case'

Profile = create_extension_schema(
    'Profile', package,
    fields = [
        ('name', str, Field())
    ]
)

Settings = create_extension_schema(
    'Settings', package,
    fields = [
        ('name', str, Field())
    ]
)

Config = create_extension_schema(
    'Config', package,
    fields = [
        ('name', str, Field())
    ]
)

class CaseExtension(extension.Extension):
    def load(self):
        super().load()
        self.register_profile_schema(Profile)
        self.register_settings_schema(Settings)
        self.register_config_schema(Config)
        self.register_composite_config_schema(Config, 'type_name')

...
```

::: arkid.extension.models




