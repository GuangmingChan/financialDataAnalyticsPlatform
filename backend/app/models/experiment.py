from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime

class Experiment(BaseModel):
    __tablename__ = "experiments"
    
    title = Column(String(200), index=True)
    description = Column(Text)
    category = Column(String(50), index=True)
    difficulty_level = Column(Integer)
    estimated_duration = Column(Integer)
    prerequisites = Column(Text)
    data_source = Column(String(200))
    
    # 关联
    steps = relationship("ExperimentStep", back_populates="experiment", cascade="all, delete-orphan")
    submissions = relationship("ExperimentSubmission", back_populates="experiment")
    
    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "difficulty_level": self.difficulty_level,
            "estimated_duration": self.estimated_duration,
            "prerequisites": self.prerequisites,
            "data_source": self.data_source,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ExperimentStep(BaseModel):
    __tablename__ = "experiment_steps"
    
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    title = Column(String(200))
    description = Column(Text)
    order = Column(Integer)
    
    # 关联
    experiment = relationship("Experiment", back_populates="steps")
    
    def as_dict(self):
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "title": self.title,
            "description": self.description,
            "order": self.order
        }

class ExperimentSubmission(BaseModel):
    __tablename__ = "experiment_submissions"
    
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(50), default="submitted")
    score = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    report_content = Column(Text)
    code_submissions = Column(JSON) # 或者创建单独的代码提交表
    
    # 关联
    experiment = relationship("Experiment", back_populates="submissions")
    user = relationship("User", back_populates="submissions")
    
    def as_dict(self):
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "user_id": self.user_id,
            "status": self.status,
            "score": self.score,
            "feedback": self.feedback,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "report_content": self.report_content,
            "code_submissions": self.code_submissions
        } 