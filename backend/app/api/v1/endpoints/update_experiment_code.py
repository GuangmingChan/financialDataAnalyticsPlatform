#!/usr/bin/env python3
"""
此脚本用于更新银行信贷风险控制实验的示例代码
"""

import os
import sys
import json
from pathlib import Path

# 获取示例代码
def get_example_code(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件 {filename} 失败: {e}")
        return ""

# 获取实验数据
def get_experiments_data():
    try:
        data_path = Path(__file__).parent.parent.parent.parent / "db" / "experiments_data.json"
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取实验数据失败: {e}")
        return {"experiments": []}

# 更新实验代码
def update_experiment_code():
    # 加载示例代码
    example_codes_dir = Path(__file__).parent.parent.parent.parent / "experiments" / "example_codes"
    
    code_files = [
        "credit_risk_exploration_code.py",
        "credit_risk_cleaning_code.py",
        "credit_risk_feature_engineering_code.py",
        "credit_risk_modeling_code.py",
        "credit_risk_evaluation_code.py",
        "credit_risk_strategy_code.py"
    ]
    
    example_codes = []
    for file in code_files:
        code = get_example_code(example_codes_dir / file)
        if code:
            example_codes.append(code)
        else:
            print(f"警告: {file} 为空")
    
    if len(example_codes) != 6:
        print(f"错误: 应该有6个示例代码，但实际有 {len(example_codes)}")
        return
    
    # 获取实验数据
    data = get_experiments_data()
    if not data or "experiments" not in data:
        print("错误: 无法获取实验数据")
        return
    
    experiments = data["experiments"]
    
    # 查找银行信贷风险控制实验
    credit_risk_exp = None
    for i, exp in enumerate(experiments):
        if exp.get("title") == "银行信贷风险控制":
            credit_risk_exp = exp
            credit_risk_exp_index = i
            break
    
    if not credit_risk_exp:
        print("错误: 找不到银行信贷风险控制实验")
        return
    
    # 检查步骤数量
    steps = credit_risk_exp.get("steps", [])
    if len(steps) != 6:
        print(f"警告: 实验应该有6个步骤，但实际有 {len(steps)}")
    
    # 更新每个步骤的示例代码
    for i, step in enumerate(steps):
        if i < len(example_codes):
            step["example_code"] = example_codes[i]
    
    # 更新实验数据
    data["experiments"][credit_risk_exp_index] = credit_risk_exp
    
    # 保存更新后的实验数据
    data_path = Path(__file__).parent.parent.parent.parent / "db" / "experiments_data.json"
    try:
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("成功更新实验示例代码")
    except Exception as e:
        print(f"保存实验数据失败: {e}")

if __name__ == "__main__":
    update_experiment_code() 