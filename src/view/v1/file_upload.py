from io import BytesIO

from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File

from settings.database import get_session
from schema.file_upload import FileUploadSchema
from service.upload_file import file_upload_handle


router = APIRouter(prefix='/file_upload', tags=['FileUpload'])


@router.post('/', status_code=status.HTTP_201_CREATED)
async def file_upload(
                        parameters: FileUploadSchema = Depends(),
                        file: UploadFile = File(),
                        session=Depends(get_session)):
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Только файлы Excel (.xlsx, .xls) разрешены")
        contents = await file.read()
        file_stream = BytesIO(contents)
        await file_upload_handle(file_stream)
        return {"filename": file.filename}
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка загрузки файла")
