from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class UserRole(enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), nullable=False, default="student")
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # 关联
    submissions = relationship("ExperimentSubmission", back_populates="user")
    
    def as_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 