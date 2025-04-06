import logging
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.experiment import Experiment, ExperimentStep, ExperimentSubmission
from app.api.v1.endpoints.experiments import experiments, submissions
from datetime import datetime

logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """初始化数据库，迁移现有实验和提交数据"""
    logger.info("开始初始化数据库")
    
    try:
        # 迁移实验数据
        migrate_experiments(db)
        
        # 迁移提交数据
        migrate_submissions(db)
        
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化过程中出错: {str(e)}")
        # 回滚事务以避免数据库锁定
        db.rollback()

def migrate_experiments(db: Session) -> None:
    """迁移内存中的实验数据到数据库"""
    logger.info(f"开始迁移实验数据，共 {len(experiments)} 个实验")
    
    # 检查数据库中是否已有实验数据
    existing_experiments = db.query(Experiment).count()
    if existing_experiments > 0:
        logger.info(f"数据库中已存在 {existing_experiments} 个实验，跳过迁移")
        return
    
    # 获取当前最大步骤ID
    max_step_id = db.query(ExperimentStep.id).order_by(ExperimentStep.id.desc()).first()
    next_step_id = 1 if max_step_id is None else max_step_id[0] + 1
    
    # 遍历内存中的实验数据
    for exp_data in experiments:
        try:
            # 创建实验
            experiment = Experiment(
                id=exp_data["id"],
                title=exp_data["title"],
                description=exp_data["description"],
                category=exp_data["category"],
                difficulty_level=exp_data["difficulty_level"],
                estimated_duration=exp_data["estimated_duration"],
                prerequisites=exp_data["prerequisites"],
                data_source=exp_data["data_source"]
            )
            db.add(experiment)
            db.flush()  # 确保获取 ID
            
            # 创建实验步骤，使用动态生成的ID而非原始ID
            for idx, step_data in enumerate(exp_data.get("steps", [])):
                step = ExperimentStep(
                    id=next_step_id,  # 使用新的ID
                    experiment_id=experiment.id,
                    title=step_data["title"],
                    description=step_data["description"],
                    order=idx+1
                )
                db.add(step)
                next_step_id += 1
                
            logger.info(f"创建实验 ID {experiment.id} 成功")
            # 每个实验提交一次事务，避免全部失败
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"迁移实验 ID {exp_data['id']} 失败: {str(e)}")

def migrate_submissions(db: Session) -> None:
    """迁移内存中的提交数据到数据库"""
    logger.info(f"开始迁移提交数据，共 {len(submissions)} 个提交")
    
    # 检查数据库中是否已有提交数据
    existing_submissions = db.query(ExperimentSubmission).count()
    if existing_submissions > 0:
        logger.info(f"数据库中已存在 {existing_submissions} 个提交，跳过迁移")
        return
    
    # 遍历内存中的提交数据
    for sub_data in submissions:
        try:
            # 从原始数据中提取代码提交
            submission_data = sub_data.get("data", {})
            report_content = submission_data.get("report_content", "")
            code_submissions = submission_data.get("code_submissions", {})
            
            # 如果未提供提交时间，使用当前时间
            submitted_at = None
            if "submitted_at" in sub_data:
                try:
                    submitted_at = datetime.fromisoformat(sub_data["submitted_at"])
                except (ValueError, TypeError):
                    submitted_at = datetime.utcnow()
            else:
                submitted_at = datetime.utcnow()
            
            # 创建提交记录
            submission = ExperimentSubmission(
                id=sub_data["id"],
                experiment_id=sub_data["experiment_id"],
                user_id=sub_data["user_id"],
                status=sub_data["status"],
                score=sub_data.get("score"),
                feedback=sub_data.get("feedback"),
                submitted_at=submitted_at,
                report_content=report_content,
                code_submissions=code_submissions
            )
            db.add(submission)
            logger.info(f"创建提交 ID {submission.id} 成功")
            # 每个提交提交一次事务，避免全部失败
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"迁移提交 ID {sub_data['id']} 失败: {str(e)}") 