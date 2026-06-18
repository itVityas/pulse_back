from sqlalchemy.ext.asyncio import AsyncSession

from model.file import FileUpload
from repository.base import BaseData


class FileUploadData(BaseData):
    def __init__(self, session: AsyncSession):
        super().__init__(model=FileUpload, session=session)
