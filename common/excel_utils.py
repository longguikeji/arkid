import os
from sys import _getframe
import time

from ..common.setup_utils import NotConfiguredException, validate_attr


def export_excel(headers, records):
    import xlwt
    from django.conf import settings
    ts = int(time.time())
    key_file = 'excel_{}.{}'.format(ts, 'xls')

    validate_attr(_getframe().f_code.co_filename, _getframe().f_code.co_name, _getframe().f_lineno, 'UPLOAD_DIR')

    file_name = os.path.join(settings.UPLOAD_DIR, key_file)
    xls = xlwt.Workbook(encoding='utf-8')
    sheet = xls.add_sheet("sheet1")

    for idx, header in enumerate(headers):
        sheet.write(0, idx, header)

    for index1, i in enumerate(records):
        for index2, key in enumerate(i):
            value = i[key]
            sheet.write(index1+1, index2, value)

    xls.save(file_name)
    return file_name