import os
import time


def export_excel(headers, records):
    import xlwt
    from django.conf import settings
    ts = int(time.time())
    key_file = 'excel_{}.{}'.format(ts, 'xls')
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