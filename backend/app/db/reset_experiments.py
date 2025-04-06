import logging
from sqlalchemy.orm import Session
from app.models.experiment import Experiment, ExperimentStep
from app.api.v1.endpoints.experiments import experiments

logger = logging.getLogger(__name__)

def reset_experiments(db: Session) -> None:
    """
    清除数据库中的所有实验数据，然后从内存中的experiments变量重新导入
    警告：此操作会清除所有实验数据，包括关联的步骤，但不会影响提交记录
    """
    try:
        # 1. 清除所有实验步骤（先删除子表数据）
        logger.info("开始清除实验步骤数据...")
        db.query(ExperimentStep).delete()
        db.commit()
        logger.info("实验步骤数据已清除")
        
        # 2. 清除所有实验数据
        logger.info("开始清除实验数据...")
        db.query(Experiment).delete()
        db.commit()
        logger.info("实验数据已清除")
        
        # 3. 重新插入实验数据
        logger.info(f"开始重新导入{len(experiments)}个实验")
        
        # 跟踪步骤ID
        next_step_id = 1
        
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
                
                # 创建实验步骤
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
                    
                logger.info(f"实验 ID {experiment.id}: '{experiment.title}' 导入成功")
                # 每个实验提交一次事务，避免全部失败
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"导入实验 ID {exp_data['id']} 失败: {str(e)}")
        
        logger.info("实验数据重置完成")
        
    except Exception as e:
        db.rollback()
        logger.error(f"重置实验数据时出错: {str(e)}")
        raise e

if __name__ == "__main__":
    # 如果直接运行此脚本，则执行重置
    import sys
    import os
    
    # 将当前目录添加到路径中，以便导入app模块
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from app.db.session import SessionLocal
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建数据库会话
    db = SessionLocal()
    
    # 重置实验数据
    reset_experiments(db)
    
    # 关闭数据库会话
    db.close() 