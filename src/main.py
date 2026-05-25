from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from settings.config import server_config, project_config
from view.v1.v1 import v1_router


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

app.include_router(prefix='/v1', router=v1_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=server_config.host,
        port=server_config.port,
        reload=server_config.reload)
