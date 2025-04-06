from sqlalchemy.orm import Session
from app.models.experiment import Experiment, ExperimentStep, ExperimentSubmission
from typing import List, Dict, Any, Optional

class ExperimentCRUD:
    @staticmethod
    def get_experiments(db: Session, *, skip: int = 0, limit: int = 100, 
                        category: Optional[str] = None, difficulty: Optional[int] = None) -> List[Experiment]:
        query = db.query(Experiment)
        if category:
            query = query.filter(Experiment.category == category)
        if difficulty:
            query = query.filter(Experiment.difficulty_level == difficulty)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_experiment(db: Session, experiment_id: int) -> Optional[Experiment]:
        return db.query(Experiment).filter(Experiment.id == experiment_id).first()
    
    @staticmethod
    def get_experiment_steps(db: Session, experiment_id: int) -> List[ExperimentStep]:
        return db.query(ExperimentStep).filter(
            ExperimentStep.experiment_id == experiment_id
        ).order_by(ExperimentStep.order).all()
    
    @staticmethod
    def get_experiment_step(db: Session, experiment_id: int, step_id: int) -> Optional[ExperimentStep]:
        return db.query(ExperimentStep).filter(
            ExperimentStep.experiment_id == experiment_id,
            ExperimentStep.id == step_id
        ).first()
    
    @staticmethod
    def create_submission(db: Session, *, experiment_id: int, user_id: int, 
                         report_content: str, code_submissions: Dict[str, str]) -> ExperimentSubmission:
        submission = ExperimentSubmission(
            experiment_id=experiment_id,
            user_id=user_id,
            report_content=report_content,
            code_submissions=code_submissions
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        return submission
    
    @staticmethod
    def get_submission(db: Session, submission_id: int) -> Optional[ExperimentSubmission]:
        return db.query(ExperimentSubmission).filter(
            ExperimentSubmission.id == submission_id
        ).first()
    
    @staticmethod
    def get_user_submissions(db: Session, user_id: int) -> List[ExperimentSubmission]:
        return db.query(ExperimentSubmission).filter(
            ExperimentSubmission.user_id == user_id
        ).all()
    
    @staticmethod
    def update_submission_status(db: Session, submission_id: int, status: str,
                               score: Optional[int] = None, feedback: Optional[str] = None) -> Optional[ExperimentSubmission]:
        submission = db.query(ExperimentSubmission).filter(
            ExperimentSubmission.id == submission_id
        ).first()
        
        if not submission:
            return None
            
        submission.status = status
        if score is not None:
            submission.score = score
        if feedback is not None:
            submission.feedback = feedback
            
        db.commit()
        db.refresh(submission)
        return submission

    @staticmethod
    def get_all_submissions(db: Session) -> List[ExperimentSubmission]:
        """获取所有提交记录"""
        return db.query(ExperimentSubmission).order_by(ExperimentSubmission.submitted_at.desc()).all()
        
    @staticmethod
    def delete_submission(db: Session, submission_id: int) -> bool:
        """删除提交记录"""
        submission = db.query(ExperimentSubmission).filter(
            ExperimentSubmission.id == submission_id
        ).first()
        
        if not submission:
            return False
            
        db.delete(submission)
        db.commit()
        return True

experiment_crud = ExperimentCRUD() 