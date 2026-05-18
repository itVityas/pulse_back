from datetime import date as idate

from sqlalchemy.ext.asyncio import AsyncSession
from openpyxl import load_workbook


async def file_upload_handle(file, currency_id: int, shop_id: int, date: idate, session: AsyncSession):
    print(file)
    wb = load_workbook(file)
    print(wb)
    for sheet in wb.worksheets:
        for row in sheet.iter_rows(min_row=2, values_only=True):
            print(row)
