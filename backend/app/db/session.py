from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 创建数据库引擎
logger.info(f"正在连接数据库: {settings.SQLALCHEMY_DATABASE_URI}")
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化数据库表结构"""
    from app.models.base import Base
    
    logger.info("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成")

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 