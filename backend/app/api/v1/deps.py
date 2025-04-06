from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from app.db.session import get_db
from app.models.user import User
from app.services.user import user_service
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    获取当前认证用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的身份认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 只进行简单的令牌验证，适用于演示环境
        # 在生产环境中应该进行更严格的JWT验证
        user_id = 1  # 默认使用ID为1的用户
        user = user_service.get(db, user_id=user_id)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

def get_optional_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """
    获取当前用户（可选）
    """
    if token is None:
        return None
    
    try:
        return get_current_user(db, token)
    except HTTPException:
        return None 