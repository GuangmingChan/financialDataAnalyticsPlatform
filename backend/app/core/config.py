from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "金融大数据虚拟仿真实验平台"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    # 默认使用SQLite作为数据库，避免对PostgreSQL的依赖
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")  # 可以是 sqlite 或 postgres
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "finance_platform")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "bZG-CLz4EMDVleS3NVr-WZOf7uRTnXDqUfGpTkJLcu8")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 实验环境配置
    PYTHON_ENV_PATH: str = os.getenv("PYTHON_ENV_PATH", "/usr/local/bin/python")
    MAX_CONCURRENT_EXPERIMENTS: int = 60
    
    def __init__(self):
        if self.DB_TYPE.lower() == "postgres":
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            )
        else:
            # 使用SQLite作为数据库，数据存储在/app/data目录下
            sqlite_path = os.path.abspath(os.path.join("data", "finance_platform.db"))
            # 确保数据目录存在
            os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
            self.SQLALCHEMY_DATABASE_URI = f"sqlite:///{sqlite_path}"
            print(f"使用SQLite数据库: {self.SQLALCHEMY_DATABASE_URI}")

settings = Settings() 