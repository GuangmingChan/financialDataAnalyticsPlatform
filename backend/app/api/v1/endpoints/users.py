from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any
from datetime import timedelta
import jwt

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.schemas.user import UserCreate, User
from app.services.user import user_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的用户认证",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户认证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_service.get(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

@router.post("/register", response_model=User)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    注册新用户
    """
    user = user_service.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册",
        )
    user = user_service.create(db, obj_in=user_in)
    return user

@router.post("/login")
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    用户登录
    """
    # 首先尝试邮箱登录
    user = user_service.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    
    # 如果邮箱登录失败，尝试用户名登录
    if not user:
        # 通过用户名查找用户
        user_by_username = user_service.get_by_username(db, username=form_data.username)
        if user_by_username and verify_password(form_data.password, user_by_username.hashed_password):
            user = user_by_username
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/me", response_model=User)
def get_user_me(
    current_user = Depends(get_current_user)
) -> Any:
    """
    获取当前登录用户信息
    """
    return current_user 

@router.get("/all", response_model=list[User])
def get_all_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """
    获取所有用户信息（仅管理员可用）
    """
    # 检查当前用户是否为管理员
    if not user_service.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    
    # 使用service方法获取所有用户
    users = user_service.get_all(db)
    return users 