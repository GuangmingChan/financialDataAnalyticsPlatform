import matplotlib
import os
from pathlib import Path

def configure_matplotlib_fonts():
    """
    配置matplotlib字体设置，确保能够正确显示中文字符
    
    这个函数会按照以下顺序尝试设置字体：
    1. 尝试使用常见的CJK字体 (Noto Sans CJK, WenQuanYi等)
    2. 如果找不到中文字体，默认使用DejaVu Sans (基本不支持中文，但不会报错)
    
    在Docker环境中尤其有用，因为它解决了常见的"无法找到适当中文字体"的问题。
    """
    # 首先创建字体缓存目录
    font_dir = "/tmp/font-cache"
    os.makedirs(font_dir, exist_ok=True)
    
    # 设置字体缓存目录
    matplotlib.rcParams['font.cachedir'] = font_dir
    
    # 尝试设置中文字体
    # 先尝试使用系统中可能存在的中文字体列表
    chinese_fonts = [
        'Noto Sans CJK SC',  # 思源黑体简体中文版
        'Noto Sans CJK TC',  # 思源黑体繁体中文版
        'Noto Sans CJK JP',  # 思源黑体日文版
        'WenQuanYi Micro Hei',  # 文泉驿微米黑
        'WenQuanYi Zen Hei',  # 文泉驿正黑
        'SimHei',  # 中文黑体
        'SimSun',  # 中文宋体
        'Microsoft YaHei',  # 微软雅黑
        'DejaVu Sans'  # 默认无中文支持的字体
    ]
    
    # 设置字体参数
    matplotlib.rcParams['font.family'] = chinese_fonts
    matplotlib.rcParams['axes.unicode_minus'] = False  # 正确显示负号
    
    print(f"Matplotlib字体配置完成，字体列表: {chinese_fonts}")
    
    return True 