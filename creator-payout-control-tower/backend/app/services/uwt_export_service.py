from io import BytesIO
from openpyxl import Workbook
from ..services.uwt_import_service import fixed_uwt_rows,FIXED

def build_uwt_workbook(period=None,status=None):
    rows=fixed_uwt_rows(period,status)
    wb=Workbook();ws=wb.active;ws.title="uwt final"
    ws.append(FIXED)
    for r in rows:ws.append([r.get(k,"") for k in FIXED])
    for cell in ws[1]:cell.font=cell.font.copy(bold=True)
    for col,width in {"A":18,"B":28,"C":30,"D":18,"E":12,"F":18,"G":16,"H":24,"I":10,"J":22,"K":18,"L":12,"M":45}.items():ws.column_dimensions[col].width=width
    buf=BytesIO();wb.save(buf);buf.seek(0);return buf
