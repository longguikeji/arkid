from ninja import Schema
from enum import Enum
from arkid.core.translation import gettext_default as _
from typing import Optional
from pydantic import Field

class EXPORT_FORMAT(str, Enum):
    csv = _('csv', 'csv')
    xls = _('xls', 'xls')

class ExportUserConfigSchema(Schema):

    export_format: EXPORT_FORMAT = Field(default='xls', title=_('Export Format', '导出文件格式'))

class ImportFileSchemaIn(Schema):
    
    file: str = Field(title=_('file', '文件'), format='upload')