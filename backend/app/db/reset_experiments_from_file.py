import logging
import json
import os
from sqlalchemy.orm import Session
from app.models.experiment import Experiment, ExperimentStep

logger = logging.getLogger(__name__)

def reset_experiments_from_file(db: Session, file_path: str) -> None:
    """
    从JSON文件加载实验数据，并重置数据库中的实验
    """
    if not os.path.exists(file_path):
        logger.error(f"文件 {file_path} 不存在")
        return
    
    try:
        # 加载实验数据
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        experiments = data.get('experiments', [])
        logger.info(f"从文件加载了 {len(experiments)} 个实验")
        
        # 清除现有数据
        logger.info("开始清除实验步骤数据...")
        db.query(ExperimentStep).delete()
        db.commit()
        logger.info("实验步骤数据已清除")
        
        logger.info("开始清除实验数据...")
        db.query(Experiment).delete()
        db.commit()
        logger.info("实验数据已清除")
        
        # 重新插入实验数据
        logger.info(f"开始导入 {len(experiments)} 个实验")
        
        # 跟踪步骤ID
        next_step_id = 1
        
        # 遍历实验数据
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
    import sys
    import os
    
    # 将当前目录添加到路径中，以便导入app模块
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from app.db.session import SessionLocal
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建数据库会话
    db = SessionLocal()
    
    # 默认文件路径
    file_path = '/app/app/db/experiments_data.json'
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    # 重置实验数据
    reset_experiments_from_file(db, file_path)
    
    # 关闭数据库会话
    db.close() 