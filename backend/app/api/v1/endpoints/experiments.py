from fastapi import APIRouter, Depends, HTTPException, Query, Body, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from app.db.session import get_db
from app.services.stock_analysis import stock_service
from app.services.bank_analysis import bank_service
from app.services.insurance_analysis import insurance_service
from app.crud.experiment import experiment_crud
from app.models.user import User
from ..deps import get_current_user, get_optional_current_user

router = APIRouter()

# 模拟实验数据存储
experiments = [
    {
        "id": 1,
        "title": "银行信贷风险控制",
        "description": "使用机器学习模型预测信用卡客户违约风险",
        "category": "bank",
        "difficulty_level": 3,
        "estimated_duration": 120,
        "prerequisites": "基本的数据分析和机器学习知识",
        "data_source": "台湾信用卡数据集",
        "steps": [
            {"id": 1, "title": "数据探索", "description": "探索信用卡数据集，了解特征和目标变量"},
            {"id": 2, "title": "数据预处理", "description": "处理缺失值和异常值，标准化特征"},
            {"id": 3, "title": "特征工程", "description": "特征选择和转换，提高模型性能"},
            {"id": 4, "title": "模型训练", "description": "训练信用卡违约预测模型"},
            {"id": 5, "title": "模型评估", "description": "使用多种指标评估模型性能"},
            {"id": 6, "title": "风险控制策略", "description": "基于模型结果制定风险控制策略"}
        ]
    },
    {
        "id": 2,
        "title": "银行客户流失预警模型",
        "description": "使用机器学习方法预测和分析银行客户流失风险因素",
        "category": "bank",
        "difficulty_level": 4,
        "estimated_duration": 120,
        "prerequisites": "统计分析基础和数据挖掘知识",
        "data_source": "银行客户交易与行为数据",
        "steps": [
            {"id": 1, "title": "客户行为分析", "description": "分析客户交易频率、金额和渠道偏好等行为特征"},
            {"id": 2, "title": "流失指标定义", "description": "确定客户流失的定义和关键指标"},
            {"id": 3, "title": "预警变量筛选", "description": "识别和筛选有预测价值的客户特征变量"},
            {"id": 4, "title": "预警模型构建", "description": "使用随机森林、逻辑回归等算法构建流失预警模型"},
            {"id": 5, "title": "模型验证", "description": "使用ROC曲线、混淆矩阵等方法评估模型效果"},
            {"id": 6, "title": "客户挽留策略", "description": "基于模型结果设计针对性的客户挽留方案"}
        ]
    },
    {
        "id": 3,
        "title": "银行信用欺诈数据分析",
        "description": "分析并检测银行信用卡交易中的欺诈行为",
        "category": "bank",
        "difficulty_level": 3,
        "estimated_duration": 130,
        "prerequisites": "数据挖掘和异常检测基础知识",
        "data_source": "银行信用卡交易数据",
        "steps": [
            {"id": 1, "title": "欺诈类型分析", "description": "了解不同类型的银行信用欺诈手段和特征"},
            {"id": 2, "title": "交易数据处理", "description": "清洗和准备交易数据，处理时间特征"},
            {"id": 3, "title": "异常特征提取", "description": "提取能够识别欺诈交易的关键特征"},
            {"id": 4, "title": "欺诈检测建模", "description": "构建欺诈检测模型，解决不平衡数据问题"},
            {"id": 5, "title": "模型调优与评估", "description": "使用精确率-召回率和AUC评估模型性能"},
            {"id": 6, "title": "欺诈预警系统", "description": "设计实时欺诈交易监控与预警系统架构"}
        ]
    },
    {
        "id": 4,
        "title": "股票技术指标分析",
        "description": "计算和分析股票技术指标，包括移动平均线、MACD、RSI等",
        "category": "security",
        "difficulty_level": 2,
        "estimated_duration": 90,
        "prerequisites": "基本的金融和股票知识",
        "data_source": "股票历史价格数据",
        "steps": [
            {"id": 1, "title": "数据获取", "description": "获取股票历史价格数据"},
            {"id": 2, "title": "趋势指标计算", "description": "计算移动平均线、MACD等趋势指标"},
            {"id": 3, "title": "摆动指标计算", "description": "计算RSI、KDJ等摆动指标"},
            {"id": 4, "title": "指标可视化", "description": "绘制技术指标和价格图表"},
            {"id": 5, "title": "交易信号分析", "description": "分析指标产生的交易信号"},
            {"id": 6, "title": "回测策略", "description": "回测基于技术指标的交易策略"}
        ]
    },
    {
        "id": 5,
        "title": "投资组合优化",
        "description": "使用马科维茨模型和夏普比率优化股票投资组合",
        "category": "security",
        "difficulty_level": 4,
        "estimated_duration": 150,
        "prerequisites": "投资理论和基础统计知识",
        "data_source": "多只股票历史收益率数据",
        "steps": [
            {"id": 1, "title": "数据准备", "description": "获取多只股票的历史价格和收益率"},
            {"id": 2, "title": "风险和收益计算", "description": "计算各股票的预期收益和风险"},
            {"id": 3, "title": "相关性分析", "description": "分析股票间的相关性"},
            {"id": 4, "title": "效率前沿构建", "description": "构建投资组合的效率前沿"},
            {"id": 5, "title": "最优组合确定", "description": "确定最优夏普比率的投资组合"},
            {"id": 6, "title": "投资组合评估", "description": "评估最优投资组合的表现"}
        ]
    },
    {
        "id": 6,
        "title": "车险索赔率影响因素分析",
        "description": "分析影响车险索赔率的因素，建立预测模型",
        "category": "insurance",
        "difficulty_level": 3,
        "estimated_duration": 120,
        "prerequisites": "基本的统计分析和机器学习知识",
        "data_source": "车险客户和索赔数据",
        "steps": [
            {"id": 1, "title": "数据探索", "description": "探索车险客户和索赔数据"},
            {"id": 2, "title": "索赔率计算", "description": "计算不同因素下的索赔率"},
            {"id": 3, "title": "特征重要性分析", "description": "分析影响索赔率的重要因素"},
            {"id": 4, "title": "预测模型构建", "description": "构建索赔金额预测模型"},
            {"id": 5, "title": "风险分群", "description": "对客户进行风险分群"},
            {"id": 6, "title": "保险定价策略", "description": "基于分析结果制定保险定价策略"}
        ]
    },
    {
        "id": 7,
        "title": "医疗保险精准营销分析",
        "description": "使用客户分群和预测模型进行医疗保险精准营销",
        "category": "insurance",
        "difficulty_level": 3,
        "estimated_duration": 120,
        "prerequisites": "基本的数据分析和机器学习知识",
        "data_source": "医疗保险客户数据",
        "steps": [
            {"id": 1, "title": "数据探索", "description": "探索医疗保险客户数据"},
            {"id": 2, "title": "客户分群", "description": "使用K-means对客户进行分群"},
            {"id": 3, "title": "购买意向预测", "description": "构建购买意向预测模型"},
            {"id": 4, "title": "分群特征分析", "description": "分析各群体的特征和行为"},
            {"id": 5, "title": "营销建议生成", "description": "为各客户群体生成营销建议"},
            {"id": 6, "title": "营销效果评估", "description": "评估针对不同群体的营销策略效果"}
        ]
    }
]

# 模拟实验提交数据
submissions = [
    {
        "id": 1,
        "experiment_id": 1,
        "user_id": 1,
        "status": "graded",
        "score": 85,
        "feedback": "分析全面，模型选择合适，但风险控制策略可以更具体。",
        "submitted_at": "2023-04-01T10:30:00"
    },
    {
        "id": 2,
        "experiment_id": 2,
        "user_id": 1,
        "status": "submitted",
        "submitted_at": "2023-04-10T14:20:00"
    }
]

@router.get("")
async def get_experiments(
    category: Optional[str] = Query(None, description="实验类别：bank, security, insurance"),
    difficulty: Optional[int] = Query(None, description="难度级别：1-5"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    获取实验列表，可以按类别和难度过滤
    """
    # 强制使用内存中的数据而不查询数据库
    filtered_experiments = experiments
    
    if category:
        filtered_experiments = [exp for exp in filtered_experiments if exp["category"] == category]
    
    if difficulty:
        filtered_experiments = [exp for exp in filtered_experiments if exp["difficulty_level"] == difficulty]
    
    return filtered_experiments[skip:skip+limit]

# 保留原有路由以兼容
@router.get("/")
async def get_experiments_slash(
    category: Optional[str] = Query(None, description="实验类别：bank, security, insurance"),
    difficulty: Optional[int] = Query(None, description="难度级别：1-5"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    获取实验列表，可以按类别和难度过滤（带斜杠版本）
    """
    # 调用主函数以保持行为一致
    return await get_experiments(category, difficulty, skip, limit, db)

@router.get("/{experiment_id}")
async def get_experiment(
    experiment_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取特定实验的详细信息
    """
    # 首先尝试从数据库获取
    db_experiment = experiment_crud.get_experiment(db, experiment_id)
    if db_experiment:
        return db_experiment.as_dict()
    
    # 尝试从实验数据文件获取信息（包括示例代码）
    try:
        import json
        from pathlib import Path
        
        # 获取experiments_data.json文件路径
        data_path = Path(__file__).parent.parent.parent.parent / "db" / "experiments_data.json"
        
        # 读取文件内容
        if data_path.exists():
            with open(data_path, 'r', encoding='utf-8') as f:
                experiments_data = json.load(f)
                
            # 查找指定实验
            if "experiments" in experiments_data:
                for exp in experiments_data["experiments"]:
                    if exp.get("id") == experiment_id:
                        print(f"从JSON文件获取实验{experiment_id}的完整信息")
                        return exp
    except Exception as e:
        print(f"尝试从JSON文件获取实验信息时出错: {str(e)}")
    
    # 如果数据库中不存在，尝试从内存列表获取（兼容旧代码）
    experiment = next((exp for exp in experiments if exp["id"] == experiment_id), None)
    if not experiment:
        raise HTTPException(status_code=404, detail=f"实验 ID {experiment_id} 不存在")
    
    return experiment

@router.get("/{experiment_id}/steps")
async def get_experiment_steps(
    experiment_id: int,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    获取特定实验的步骤
    """
    # 首先尝试从数据库获取
    db_steps = experiment_crud.get_experiment_steps(db, experiment_id)
    if db_steps:
        return [step.as_dict() for step in db_steps]
    
    # 如果数据库中不存在，尝试从内存列表获取（兼容旧代码）
    experiment = next((exp for exp in experiments if exp["id"] == experiment_id), None)
    if not experiment:
        raise HTTPException(status_code=404, detail=f"实验 ID {experiment_id} 不存在")
    
    return experiment.get("steps", [])

@router.get("/{experiment_id}/steps_with_code")
async def get_experiment_steps_with_code(
    experiment_id: int,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    获取特定实验的步骤，包括示例代码
    """
    # 尝试从实验数据文件获取信息（包括示例代码）
    try:
        import json
        from pathlib import Path
        
        # 获取experiments_data.json文件路径
        data_path = Path(__file__).parent.parent.parent.parent / "db" / "experiments_data.json"
        
        # 读取文件内容
        if data_path.exists():
            with open(data_path, 'r', encoding='utf-8') as f:
                experiments_data = json.load(f)
                
            # 查找指定实验的步骤
            if "experiments" in experiments_data:
                for exp in experiments_data["experiments"]:
                    if exp.get("id") == experiment_id and "steps" in exp:
                        print(f"从JSON文件获取实验{experiment_id}的步骤信息，包含示例代码")
                        return exp["steps"]
    except Exception as e:
        print(f"尝试从JSON文件获取实验步骤时出错: {str(e)}")
    
    # 如果无法从文件获取，使用内存中的步骤（不含示例代码）
    experiment = next((exp for exp in experiments if exp["id"] == experiment_id), None)
    if not experiment:
        raise HTTPException(status_code=404, detail=f"实验 ID {experiment_id} 不存在")
    
    return experiment.get("steps", [])

@router.get("/{experiment_id}/steps/{step_id}")
async def get_experiment_step(
    experiment_id: int,
    step_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取特定实验步骤的详细信息
    """
    # 首先尝试从数据库获取
    db_step = experiment_crud.get_experiment_step(db, experiment_id, step_id)
    if db_step:
        return db_step.as_dict()
    
    # 尝试从实验数据文件获取信息（包括示例代码）
    try:
        import json
        from pathlib import Path
        
        # 获取experiments_data.json文件路径
        data_path = Path(__file__).parent.parent.parent.parent / "db" / "experiments_data.json"
        
        # 读取文件内容
        if data_path.exists():
            with open(data_path, 'r', encoding='utf-8') as f:
                experiments_data = json.load(f)
                
            # 查找指定实验和步骤
            if "experiments" in experiments_data:
                for exp in experiments_data["experiments"]:
                    if exp.get("id") == experiment_id and "steps" in exp:
                        for step in exp["steps"]:
                            if step.get("id") == step_id:
                                print(f"从JSON文件获取实验{experiment_id}步骤{step_id}的信息")
                                return step
    except Exception as e:
        print(f"尝试从JSON文件获取实验步骤时出错: {str(e)}")
    
    # 如果以上方法都失败，尝试从内存数据获取（兼容旧代码）
    experiment = next((exp for exp in experiments if exp["id"] == experiment_id), None)
    
    if not experiment:
        raise HTTPException(status_code=404, detail=f"实验 ID {experiment_id} 不存在")
    
    step = next((step for step in experiment.get("steps", []) if step["id"] == step_id), None)
    
    if not step:
        raise HTTPException(status_code=404, detail=f"步骤 ID {step_id} 不存在")
    
    return step

@router.get("/{experiment_id}/data")
async def get_experiment_data(
    experiment_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取特定实验的示例数据
    """
    experiment = next((exp for exp in experiments if exp["id"] == experiment_id), None)
    
    if not experiment:
        raise HTTPException(status_code=404, detail=f"实验 ID {experiment_id} 不存在")
    
    # 根据实验类别返回不同的数据
    if experiment["category"] == "bank":
        df = bank_service.load_credit_data()
        return {
            "data": df.head(100).to_dict(orient="records"),
            "total_records": len(df),
            "columns": df.columns.tolist()
        }
    elif experiment["category"] == "security":
        df = stock_service.get_stock_data("AAPL", "2020-01-01", "2020-12-31")
        return {
            "data": df.reset_index().to_dict(orient="records"),
            "total_records": len(df),
            "columns": df.reset_index().columns.tolist()
        }
    elif experiment["category"] == "insurance":
        if "索赔率" in experiment["title"]:
            df = insurance_service.load_car_insurance_data()
        else:
            df = insurance_service.load_health_insurance_data()
        return {
            "data": df.head(100).to_dict(orient="records"),
            "total_records": len(df),
            "columns": df.columns.tolist()
        }
    
    return {"message": "无可用数据"}

@router.post("/{experiment_id}/submit")
async def submit_experiment(
    experiment_id: int,
    request: Request,
    user_id: int = Query(1, description="用户ID"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    提交实验结果
    """
    try:
        print(f"收到提交请求: experiment_id={experiment_id}, user_id={user_id}")
        
        # 获取Content-Type
        content_type = request.headers.get("content-type", "")
        print(f"Content-Type: {content_type}")
        
        # 读取原始请求体
        raw_body = await request.body()
        print(f"原始请求体: {raw_body}")
        
        try:
            # 尝试解析请求体
            if "application/json" in content_type.lower():
                try:
                    body_data = await request.json()
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {str(e)}")
                    body_data = {}
            else:
                print(f"不支持的Content-Type: {content_type}")
                body_data = {}
            
            print(f"解析后的请求体: {body_data}")
            
            # 从请求体中提取数据，如果没有则使用默认值
            report_content = body_data.get("report_content", "简单报告内容")
            code_submissions = body_data.get("code_submissions", {"1": "# 示例代码"})
            
            # 确保code_submissions是字典类型
            if not isinstance(code_submissions, dict):
                print(f"警告: code_submissions不是字典类型，使用默认值")
                code_submissions = {"1": "# 示例代码"}
            
        except Exception as e:
            print(f"请求体解析错误: {str(e)}")
            report_content = "简单报告内容"
            code_submissions = {"1": "# 示例代码"}
        
        # 获取用户信息（用于管理员视图）
        user_info = {"id": user_id, "username": f"用户{user_id}"}
        try:
            # 尝试从数据库获取真实用户信息
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user_info = {"id": user.id, "username": user.username}
        except Exception as e:
            print(f"获取用户信息失败: {str(e)}")
        
        # 检查实验是否存在
        db_experiment = experiment_crud.get_experiment(db, experiment_id)
        memory_experiment = None
        
        if not db_experiment:
            memory_experiment = next((exp for exp in experiments if exp["id"] == experiment_id), None)
            if not memory_experiment:
                raise HTTPException(status_code=404, detail=f"实验 ID {experiment_id} 不存在")
        
        print(f"使用的提交数据: report_content={report_content}, code_submissions={code_submissions}")
            
        if db_experiment:
            submission = experiment_crud.create_submission(
                db,
                experiment_id=experiment_id,
                user_id=user_id,
                report_content=report_content,
                code_submissions=code_submissions
            )
            
            if background_tasks:
                background_tasks.add_task(grade_submission_db, db, submission.id)
            
            return {
                "id": submission.id,
                "status": "submitted",
                "message": "实验已提交，正在评分中"
            }
        else:
            simplified_data = {
                "report_content": report_content,
                "code_submissions": code_submissions
            }
            
            new_submission = {
                "id": len(submissions) + 1,
                "experiment_id": experiment_id,
                "user_id": user_id,
                "user_info": user_info,  # 添加用户信息
                "status": "submitted",
                "submitted_at": datetime.now().isoformat(),
                "data": simplified_data
            }
            
            submissions.append(new_submission)
            
            if background_tasks:
                background_tasks.add_task(grade_submission, new_submission["id"])
            
            return {
                "id": new_submission["id"],
                "status": "submitted",
                "message": "实验已提交，正在评分中"
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"提交处理错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理提交时发生错误: {str(e)}")

@router.get("/submissions/{submission_id}")
async def get_submission(
    submission_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取特定提交的详细信息
    """
    # 首先尝试从数据库获取
    db_submission = experiment_crud.get_submission(db, submission_id)
    if db_submission:
        return db_submission.as_dict()
    
    # 如果数据库中不存在，尝试从内存列表获取（兼容旧代码）
    submission = next((sub for sub in submissions if sub["id"] == submission_id), None)
    if not submission:
        raise HTTPException(status_code=404, detail=f"提交 ID {submission_id} 不存在")
    
    return submission

@router.get("/users/{user_id}/submissions")
async def get_user_submissions(
    user_id: int,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    获取特定用户的所有实验提交记录
    """
    print(f"获取用户 {user_id} 的提交记录")
    
    # 从内存列表获取（兼容旧代码）
    memory_submissions = [sub for sub in submissions if sub["user_id"] == user_id]
    print(f"内存中找到 {len(memory_submissions)} 条记录")
    
    # 尝试从数据库获取用户提交
    db_submissions = experiment_crud.get_user_submissions(db, user_id)
    db_submissions_list = []
    if db_submissions:
        db_submissions_list = [sub.as_dict() for sub in db_submissions]
        print(f"数据库中找到 {len(db_submissions_list)} 条记录")
    
    # 合并提交记录
    all_submissions = memory_submissions + db_submissions_list
    
    # 按提交时间降序排序
    all_submissions.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
    
    print(f"总共返回 {len(all_submissions)} 条提交记录")
    return all_submissions

async def grade_submission_db(db: Session, submission_id: int):
    """
    后台任务，为数据库中的提交评分
    """
    import time
    import random
    
    # 模拟评分过程
    time.sleep(5)  # 模拟评分需要时间
    
    # 更新提交状态
    score = random.randint(60, 100)
    experiment_crud.update_submission_status(
        db, 
        submission_id=submission_id,
        status="graded",
        score=score,
        feedback="自动评分完成。"
    )

async def grade_submission(submission_id: int):
    """
    后台任务，为提交评分
    """
    submission = next((sub for sub in submissions if sub["id"] == submission_id), None)
    
    if not submission:
        return
    
    # 模拟评分过程
    import time
    import random
    time.sleep(5)  # 模拟评分需要时间
    
    # 更新提交状态
    submission["status"] = "graded"
    submission["score"] = random.randint(60, 100)
    submission["feedback"] = "自动评分完成。"
    
    return submission

@router.delete("/submissions/{submission_id}")
async def delete_submission(
    submission_id: int,
    user_id: int = Query(..., description="用户ID"),
    is_admin: bool = Query(False, description="是否为管理员"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    删除特定的实验提交记录
    """
    # 首先尝试从数据库获取
    db_submission = experiment_crud.get_submission(db, submission_id)
    
    if db_submission:
        # 检查权限：只有提交者本人或管理员才能删除
        if db_submission.user_id != user_id and not is_admin:
            raise HTTPException(status_code=403, detail="没有权限删除此提交")
        
        experiment_crud.delete_submission(db, submission_id)
        return {"message": "提交记录已成功删除"}
    
    # 如果数据库中不存在，尝试从内存列表获取（兼容旧代码）
    submission_index = next((i for i, sub in enumerate(submissions) if sub["id"] == submission_id), None)
    
    if submission_index is None:
        raise HTTPException(status_code=404, detail=f"提交 ID {submission_id} 不存在")
    
    # 检查权限：只有提交者本人或管理员才能删除
    if submissions[submission_index]["user_id"] != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="没有权限删除此提交")
    
    # 删除提交
    deleted_submission = submissions.pop(submission_index)
    
    return {"message": "提交记录已成功删除"}

@router.get("/submissions")
async def get_all_submissions(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
) -> List[Dict[str, Any]]:
    """
    获取所有实验提交记录（仅管理员可用）
    """
    try:
        # 添加详细调试日志
        user_id = getattr(current_user, "id", "unknown") if current_user else "unknown"
        print(f"获取所有提交记录请求: 用户ID={user_id}")
        
        # 权限检查 - 暂时注释掉
        # if current_user and not (getattr(current_user, "is_superuser", False) or getattr(current_user, "role", "") == "admin"):
        #    raise HTTPException(status_code=403, detail="需要管理员权限")
        
        # 添加提交源数据调试
        print(f"内存中的submissions列表长度: {len(submissions)}")
        for idx, sub in enumerate(submissions[:3]):  # 只打印前3条记录
            print(f"提交记录 {idx+1}: id={sub.get('id')}, user_id={sub.get('user_id')}, experiment_id={sub.get('experiment_id')}")
        
        # 首先尝试从数据库获取
        db_submissions = experiment_crud.get_all_submissions(db)
        db_submissions_list = []
        if db_submissions:
            db_submissions_list = [sub.as_dict() for sub in db_submissions]
            print(f"从数据库中获取到 {len(db_submissions_list)} 条提交记录")
        
        # 合并内存列表中的提交记录（兼容旧代码）
        all_submissions = submissions + db_submissions_list
        
        # 按提交时间降序排序
        all_submissions.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
        
        print(f"总共返回 {len(all_submissions)} 条提交记录")
        return all_submissions
    except Exception as e:
        print(f"获取所有提交记录时出错: {str(e)}")
        # 这里添加详细的错误堆栈跟踪
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        # 返回空列表而不是抛出错误
        return []

@router.put("/submissions/{submission_id}/grade")
async def grade_submission_manually(
    submission_id: int,
    grade: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    手动为提交评分（仅管理员可用）
    """
    # 首先尝试从数据库获取
    db_submission = experiment_crud.get_submission(db, submission_id)
    
    if db_submission:
        # 更新提交状态和分数
        updated_submission = experiment_crud.update_submission_status(
            db, 
            submission_id=submission_id,
            status="graded",
            score=grade.get("score"),
            feedback=grade.get("feedback")
        )
        return updated_submission.as_dict()
    
    # 如果数据库中不存在，尝试从内存列表获取（兼容旧代码）
    submission = next((sub for sub in submissions if sub["id"] == submission_id), None)
    
    if not submission:
        raise HTTPException(status_code=404, detail=f"提交 ID {submission_id} 不存在")
    
    # 更新提交状态
    submission["status"] = "graded"
    submission["score"] = grade.get("score")
    submission["feedback"] = grade.get("feedback")
    
    return submission 