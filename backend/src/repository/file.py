from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from model.file import FileUpload
from model.day_price import DayPrice
from repository.base import BaseData


class FileUploadData(BaseData):
    def __init__(self, session: AsyncSession):
        super().__init__(model=FileUpload, session=session)

    async def delete(self, id: int) -> bool:
        obj = await self.get_one(id)
        day_price_slct = delete(DayPrice).where(DayPrice.file_upload_id == id)
        await self.session.execute(day_price_slct)
        await self.session.delete(obj)
        await self.session.commit()
        return True
