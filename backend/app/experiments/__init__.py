# 信用卡风险控制实验模块
# 此模块实现了台湾信用卡数据集的各种数据分析和模型训练功能

from pathlib import Path

# 确保输出目录存在
output_dir = Path(__file__).parent / "output"
output_dir.mkdir(exist_ok=True)