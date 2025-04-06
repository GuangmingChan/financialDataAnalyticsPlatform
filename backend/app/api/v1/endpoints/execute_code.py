from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import base64
import traceback
import io
import sys
import contextlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from app.db.session import get_db
from app.kernel_manager import KernelManager
import matplotlib
from app.services.docker_matplotlib_fix import configure_matplotlib_fonts

# 配置字体以支持中文显示
configure_matplotlib_fonts()

router = APIRouter()
kernel_manager = KernelManager()

class ExecutionRequest:
    def __init__(self, code: str, experiment_id: int, step_id: int):
        self.code = code
        self.experiment_id = experiment_id
        self.step_id = step_id

@router.post("", response_model=Dict[str, Any])
async def execute_code_root(
    request_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    执行代码并返回结果 (根路径版本)
    """
    return await execute_code(request_data, db)

@router.post("/execute-code", response_model=Dict[str, Any])
async def execute_code(
    request_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    执行代码并返回结果
    """
    try:
        # 从请求体中提取代码和元数据
        code = request_data.get("code", "")
        experiment_id = request_data.get("experiment_id")
        step_id = request_data.get("step_id")
        
        if not code:
            raise HTTPException(status_code=400, detail="代码不能为空")
        if not experiment_id:
            raise HTTPException(status_code=400, detail="必须提供实验ID")
        
        # 创建执行请求对象
        execution_request = ExecutionRequest(code, experiment_id, step_id)
        
        # 重定向标准输出来捕获打印输出
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        charts = []
        
        # 捕获可能的matplotlib绘图
        plt.figure()
        
        # 使用上下文管理器捕获标准输出和错误
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            try:
                # 创建安全的局部变量环境
                local_vars = {
                    'pd': pd,
                    'np': np,
                    'plt': plt
                }
                
                # 执行代码
                exec(code, local_vars)
                
                # 检查是否有图形输出
                if plt.get_fignums():
                    for i in plt.get_fignums():
                        fig = plt.figure(i)
                        img_data = io.BytesIO()
                        fig.savefig(img_data, format='png')
                        img_data.seek(0)
                        chart_base64 = base64.b64encode(img_data.read()).decode('utf-8')
                        charts.append(chart_base64)
                    plt.close('all')
                
                # 获取标准输出和错误
                stdout = stdout_capture.getvalue()
                stderr = stderr_capture.getvalue()
                
                # 组合输出信息
                output = stdout
                if stderr:
                    output += f"\nError: {stderr}"
                
                # 获取执行结果
                result = {
                    "output": output,
                    "charts": charts,
                    "success": True if not stderr else False
                }
                
                return result
            
            except Exception as e:
                # 记录错误堆栈并返回错误信息
                error_trace = traceback.format_exc()
                return {
                    "output": f"Error: {str(e)}\n\n{error_trace}",
                    "charts": [],
                    "success": False
                }
            finally:
                # 确保关闭所有图表
                plt.close('all')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute", response_model=Dict[str, Any])
async def execute_custom_code(
    request_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    执行自定义代码并返回结果
    """
    try:
        # 从请求体中提取代码
        code = request_data.get("code", "")
        
        if not code:
            raise HTTPException(status_code=400, detail="代码不能为空")
        
        # 重定向标准输出来捕获打印输出
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # 捕获可能的matplotlib绘图
        visualization_data = None
        
        # 使用上下文管理器捕获标准输出和错误
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            try:
                # 创建安全的局部变量环境 - 导入常用的数据分析库
                local_vars = {
                    'pd': pd,
                    'np': np,
                    'plt': plt,
                }
                
                # 执行代码
                exec(code, local_vars)
                
                # 检查是否有图形输出
                if plt.get_fignums():
                    fig = plt.gcf()  # 获取当前图形
                    img_data = io.BytesIO()
                    fig.savefig(img_data, format='png', bbox_inches='tight')
                    img_data.seek(0)
                    visualization_data = base64.b64encode(img_data.read()).decode('utf-8')
                    plt.close('all')
                
                # 获取标准输出和错误
                stdout = stdout_capture.getvalue()
                stderr = stderr_capture.getvalue()
                
                # 组合输出信息
                output = stdout
                if stderr:
                    output += f"\nError: {stderr}"
                
                return {
                    "output": output,
                    "visualization": visualization_data,
                    "success": True if not stderr else False
                }
            
            except Exception as e:
                # 记录错误堆栈并返回错误信息
                error_trace = traceback.format_exc()
                return {
                    "output": f"Error: {str(e)}\n\n{error_trace}",
                    "visualization": None,
                    "success": False
                }
            finally:
                # 确保关闭所有图表
                plt.close('all')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user_codes", response_model=Dict[str, Any])
async def save_user_code(
    request_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    保存用户自定义代码
    """
    try:
        # 从请求体中提取数据
        name = request_data.get("name", "")
        description = request_data.get("description", "")
        tags = request_data.get("tags", "")
        code = request_data.get("code", "")
        
        if not name or not code:
            raise HTTPException(status_code=400, detail="名称和代码不能为空")
        
        # TODO: 实际项目中应将代码保存到数据库
        # 这里使用模拟返回
        return {
            "id": 123,  # 模拟ID
            "name": name,
            "description": description,
            "tags": tags,
            "created_at": "2023-06-15T12:00:00Z",
            "success": True
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 