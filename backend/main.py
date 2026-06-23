from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from settings.config import server_config, project_config
from view.v1.v1 import v1_router
from share.my_exception import MyHttpException
from settings.loguru_conf import setup_logger
from middleware.logs_middleware import LogMiddleware


setup_logger()


app = FastAPI(
    title=project_config.project_name,
    version=project_config.project_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.add_middleware(LogMiddleware)


@app.exception_handler(MyHttpException)
async def my_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={'title': exc.title, 'detail': exc.detail}
    )

app.include_router(prefix='/v1', router=v1_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=server_config.host,
        port=server_config.port,
        reload=server_config.reload)
