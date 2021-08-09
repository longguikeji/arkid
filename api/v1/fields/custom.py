from drf_spectacular.drainage import set_override, get_override
from drf_spectacular.utils import extend_schema_field


def create_foreign_field(field_cls):
    @extend_schema_field(
        field={
            'format': 'foreign',
        }
    )
    class ForeignField(field_cls):
        _field_meta = {}

        def __init__(self, model_cls, field_name, page, **kwargs):
            field = get_override(self, 'field', {})
            field['model'] = model_cls.__name__
            field['field'] = field_name
            field['page'] = page
            if 'source' in kwargs:
                field['source'] = kwargs['source']
            if 'link' in kwargs:
                field['link'] = kwargs['link']
                kwargs.pop('link')

            for k, v in kwargs.items():
                if isinstance(v, (str, int, list, bool, dict, float)):
                    field[k] = v

            set_override(self, 'field', field)
            super().__init__(**kwargs)

    return ForeignField

def create_foreign_key_field(field_cls):
    @extend_schema_field(
        field={
            'format': 'foreign_key',
        }
    )
    class ForeignKeyField(create_foreign_field(field_cls)):
        def __init__(self, model_cls, field_name, **kwargs):
            print(kwargs)
            super().__init__(model_cls, field_name, **kwargs)

    return ForeignKeyField

def create_hint_field(field_cls):
    class HintField(field_cls):
        _field_meta = {}

        def __init__(self, hint, **kwargs):
            field = get_override(self, 'field', {})
            field['hint'] = hint

            for k, v in kwargs.items():
                if isinstance(v, (str, int, list, bool, dict, float)):
                    field[k] = v

            set_override(self, 'field', field)
            super().__init__(**kwargs)

    return HintField

def create_mobile_field(field_cls):
    @extend_schema_field(
        field={
            'format': 'mobile',
        }
    )
    class MobileField(field_cls):
        _field_meta = {}

        def __init__(self, hint, **kwargs):
            field = get_override(self, 'field', {})
            field['hint'] = hint

            for k, v in kwargs.items():
                if isinstance(v, (str, int, list, bool, dict, float)):
                    field[k] = v

            set_override(self, 'field', field)
            super().__init__(**kwargs)

    return MobileField

def create_password_field(field_cls):
    @extend_schema_field(
        field={
            'format': 'password',
        }
    )
    class PasswordField(field_cls):
        _field_meta = {}

        def __init__(self, hint, **kwargs):
            field = get_override(self, 'field', {})
            field['hint'] = hint

            for k, v in kwargs.items():
                if isinstance(v, (str, int, list, bool, dict, float)):
                    field[k] = v

            set_override(self, 'field', field)
            super().__init__(**kwargs)

    return PasswordField

def create_enum_field(field_cls):
    class EnumField(field_cls):
        _field_meta = {}

        def __init__(self, enum, **kwargs):
            field = get_override(self, 'field', {})
            field['enum'] = enum

            for k, v in kwargs.items():
                if isinstance(v, (str, int, list, bool, dict, float)):
                    field[k] = v

            set_override(self, 'field', field)
            super().__init__(**kwargs)

    return EnumField

def create_dowload_url_field(field_cls):
    """
    通过url下载数据
    """

    @extend_schema_field(
        field={
            'format': 'download_url',
        }
    )
    class DownloadUrlField(field_cls):
        """
        下载字段
        """

        _field_meta = {}

        def __init__(self, hint, **kwargs):
            field = get_override(self, 'field', {})
            field['hint'] = hint

            for k, v in kwargs.items():
                if isinstance(v, (str, int, list, bool, dict, float)):
                    field[k] = v

            set_override(self, 'field', field)
            super().__init__(**kwargs)

    return DownloadUrlField

def create_upload_file_field(field_cls):
    """
    文件上传字段
    """

    @extend_schema_field(
        field={
            'format': 'upload_file',
        }
    )
    class UploadFileField(field_cls):
        """
        文件上传字段
        """

        _field_meta = {}

        def __init__(self, hint, **kwargs):
            field = get_override(self, 'field', {})
            field['hint'] = hint

            for k, v in kwargs.items():
                if isinstance(v, (str, int, list, bool, dict, float)):
                    field[k] = v

            set_override(self, 'field', field)
            super().__init__(**kwargs)

    return UploadFileField

def create_upload_url_field(field_cls):
    """
    文件上传字段(前端上传并写入返回结果中的url)
    """

    @extend_schema_field(
        field={
            'format': 'upload_url',
        }
    )
    class UploadUrlField(field_cls):
        """
        文件上传字段
        """

        _field_meta = {}

        def __init__(self, hint, **kwargs):
            field = get_override(self, 'field', {})
            field['hint'] = hint

            for k, v in kwargs.items():
                if isinstance(v, (str, int, list, bool, dict, float)):
                    field[k] = v

            set_override(self, 'field', field)
            super().__init__(**kwargs)

    return UploadUrlField

def create_custom_dict_field(field_cls):
    """
    自定义字典字段
    """

    @extend_schema_field(
        field={
            'format': 'custom_dict',
        }
    )
    class CustomDictField(field_cls):
        """
        自定义字典字段
        """

        _field_meta = {}

        def __init__(self, hint, **kwargs):
            field = get_override(self, 'field', {})
            field['hint'] = hint

            for k, v in kwargs.items():
                if isinstance(v, (str, int, list, bool, dict, float)):
                    field[k] = v

            set_override(self, 'field', field)
            super().__init__(**kwargs)

    return CustomDictField

def create_html_field(field_cls):
    """
    自定义字典字段
    """

    @extend_schema_field(
        field={
            'format': 'html',
        }
    )
    class HtmlField(field_cls):
        """
        自定义字典字段
        """

        _field_meta = {}

        def __init__(self, hint, **kwargs):
            field = get_override(self, 'field', {})
            field['hint'] = hint

            for k, v in kwargs.items():
                if isinstance(v, (str, int, list, bool, dict, float)):
                    field[k] = v

            set_override(self, 'field', field)
            super().__init__(**kwargs)

    return HtmlField

