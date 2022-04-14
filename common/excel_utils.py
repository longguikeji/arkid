import os
import io
import time


def export_excel(headers, records, name="", generate_name=""):
    import xlwt
    ts = int(time.time())
    if generate_name == "":
        key_file = '{}_{}.{}'.format(name, ts, 'xls') if name else 'excel_{}.{}'.format(ts, 'xls')
    else:
        key_file = generate_name

    xls = xlwt.Workbook(encoding='utf-8')
    sheet = xls.add_sheet("sheet1")

    for idx, header in enumerate(headers):
        sheet.write(0, idx, header)

    for index1, i in enumerate(records):
        for index2, key in enumerate(i):
            value = i[key]
            if value == None or value == 'None':
                value = ''
            sheet.write(index1 + 1, index2, value)

    output = io.BytesIO()
    xls.save(output)
    output.seek(0)

    contents = output.getvalue()
    return contents

# 导入excel
def import_excel(file):
    import xlrd
    data = xlrd.open_workbook(file_contents=file.read())
    table = data.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    colnames = table.row_values(0)
    list = []
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        if row:
            app = {}
            for i in range(len(colnames)):
                app[colnames[i]] = row[i]
            list.append(app)
    return list