from email.policy import default
from arkid.extension.utils import load_active_extensions, find_available_extensions
from arkid.common.logger import logger
from arkid.extension.models import Extension, TenantExtension
from arkid.core.models import Tenant


class ExtensionLoader:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
            cls._instance._start()

        return cls._instance

    
    def _start(self):
        
        try:# 防止在migrate或其它命令运行时没有创建数据库而报错
            extensions = list(Extension.active_objects.filter())
            tenant_extensions = list(TenantExtension.active_objects.filter())
        except Exception:
            return
        
        exts = find_available_extensions()
        packages = []
        for ext in exts:
            logger.info(ext.package + ' is update_or_create')
            extension, is_create = Extension.objects.update_or_create(
                defaults={
                    'type': ext.type,
                    'labels': ext.labels,
                    'ext_dir': str(ext.ext_dir),
                    'name': ext.name,
                    'version': ext.version,
                    'is_del': False,
                },
                package = ext.package,
            )
            packages.append(ext.package)

            platform_tenant = Tenant.platform_tenant()
            tenant_extension, is_create = TenantExtension.objects.update_or_create(
                defaults={
                    'is_rented': True,
                },
                tenant = platform_tenant,
                extension = extension,
            )
            
        del_exts = Extension.objects.exclude(package__in=packages)
        for del_ext in del_exts:
            logger.info(del_ext.package + ' is deleted')
            del_ext.delete()
        load_active_extensions()
