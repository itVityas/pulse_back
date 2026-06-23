import os
from typing import List

from dotenv import load_dotenv


if os.path.exists('.env'):
    load_dotenv(dotenv_path='.env')
else:
    load_dotenv(dotenv_path='../.env')


class DatabaseConfig:
    def __init__(self):
        self.db_driver = os.getenv("DATABASE_DRIVER")
        self.db_name = os.getenv("DATABASE_NAME")
        self.db_user = os.getenv("DATABASE_USER")
        self.db_password = os.getenv("DATABASE_PASSWORD")
        self.db_host = os.getenv("DATABASE_HOST")
        self.db_port = os.getenv("DATABASE_PORT")
        self.db_pool_size = 20
        self.db_max_overflow = 40

    def get_url(self):
        return f"postgresql+{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


database_config = DatabaseConfig()


class ServerConfig:
    '''
    host: str listen ip
    port: int listen port
    reload: bool reload when code changed
    '''

    def __init__(self):
        self.host = os.getenv('HOST', '0.0.0.0')
        self.port = int(os.getenv('PORT', 8000))
        self.reload = os.getenv('RELOAD', True)
        self.load_fixtures_on_startup = os.getenv('LOAD_FIXTURES_ON_STARTUP', False)


server_config = ServerConfig()


class ProjectConfig:
    '''
    project_name: str project name
    project_version: str project version
    debug: bool enable debug mode
    '''

    def __init__(self):
        self.project_name = os.getenv('PROJECT_NAME', 'FastAPI')
        self.project_version = '0.0.1'
        self.debug = True if 'True' == os.getenv('DEBUG', False) else False
        self.backend_cors_origins: List[str] = [
            "http://127.0.0.1:3000",
            "http://192.168.2.9:3000",
            "http://localhost:3000",
            "http://localhost:8000",
        ]


project_config = ProjectConfig()


class JWTConfig:
    """
    """
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY")
        self.refresh_key = os.getenv("REFRESH_SECRET_KEY")
        self.algorithm: str = "HS256"
        self.expire_access_token: int = 15
        self.expire_refresh_token: int = 60 * 24 * 7


jwt_config = JWTConfig()
