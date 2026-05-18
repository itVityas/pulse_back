from datetime import date as idate

from pydantic import BaseModel


class FileUploadSchema(BaseModel):
    currency_id: int
    shop_id: int
    date: idate
