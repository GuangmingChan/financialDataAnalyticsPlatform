from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db.session import init_db, get_db
from .api.v1.api import api_router
from .schemas.user import UserCreate
from .services.user import user_service
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    # 初始化数据库连接和表结构
    init_db()
    
    # 创建默认管理员账户
    db = next(get_db())
    admin_user = user_service.get_by_email(db, email="admin@example.com")
    if not admin_user:
        admin_data = UserCreate(
            username="admin",
            email="admin@example.com",
            password="admin123",
            full_name="系统管理员",
            is_active=True,
            is_superuser=True,
            role="admin"
        )
        user_service.create(db, obj_in=admin_data)
        logger.info("已创建默认管理员账户: admin@example.com / admin123")
    
    # 迁移实验和提交数据到数据库
    try:
        from .db.init_db import init_db as migrate_data
        db = next(get_db())
        migrate_data(db)
        logger.info("已完成数据迁移")
    except Exception as e:
        logger.error(f"数据迁移失败: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "欢迎使用金融大数据虚拟仿真实验平台",
        "version": settings.VERSION
    } 