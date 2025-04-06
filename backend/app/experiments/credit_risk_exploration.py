import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import matplotlib as mpl
from app.services.docker_matplotlib_fix import configure_matplotlib_fonts

# 配置字体以支持中文显示
configure_matplotlib_fonts()

def load_credit_data():
    """
    加载台湾信用卡违约数据集
    """
    data_path = Path(__file__).parent.parent / "data" / "taiwan_credit.csv"
    df = pd.read_csv(data_path)
    print(f"数据集成功加载，共有 {df.shape[0]} 行，{df.shape[1]} 列")
    return df

def exploratory_analysis(df):
    """
    对数据进行探索性分析
    """
    # 1. 基本统计量
    print("\n=== 基本统计量 ===")
    print(df.describe())
    
    # 2. 数据类型和基本信息
    print("\n=== 数据类型 ===")
    print(df.info())
    
    # 3. 目标变量分布
    target_counts = df['DEFAULT'].value_counts()
    print("\n=== 目标变量分布 ===")
    print(f"未违约: {target_counts[0]} ({target_counts[0]/len(df)*100:.2f}%)")
    print(f"已违约: {target_counts[1]} ({target_counts[1]/len(df)*100:.2f}%)")
    
    # 4. 异常值统计
    print("\n=== 异常值统计 ===")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
        
        if not outliers.empty:
            print(f"{col}列有 {len(outliers)} 个异常值 ({len(outliers)/len(df)*100:.2f}%)")
    
    # 5. 重复值统计
    duplicates = df.duplicated().sum()
    print(f"\n=== 重复值统计 ===")
    print(f"数据集中有 {duplicates} 个重复行 ({duplicates/len(df)*100:.2f}%)")
    
    # 6. 缺失值统计
    missing_values = df.isnull().sum()
    print("\n=== 缺失值统计 ===")
    if missing_values.sum() == 0:
        print("数据集中没有缺失值")
    else:
        print(missing_values[missing_values > 0])
    
    # 7. 可视化部分特征分布
    plt.figure(figsize=(15, 10))
    
    # 年龄分布
    plt.subplot(2, 3, 1)
    sns.histplot(df['AGE'], kde=True)
    plt.title('年龄分布')
    
    # 信用额度分布
    plt.subplot(2, 3, 2)
    sns.histplot(df['LIMIT_BAL'], kde=True)
    plt.title('信用额度分布')
    
    # 教育程度分布
    plt.subplot(2, 3, 3)
    sns.countplot(x='EDUCATION', data=df)
    plt.title('教育程度分布')
    
    # 婚姻状况分布
    plt.subplot(2, 3, 4)
    sns.countplot(x='MARRIAGE', data=df)
    plt.title('婚姻状况分布')
    
    # 性别分布
    plt.subplot(2, 3, 5)
    sns.countplot(x='SEX', data=df)
    plt.title('性别分布')
    
    # 违约率与年龄的关系
    plt.subplot(2, 3, 6)
    sns.boxplot(x='DEFAULT', y='AGE', data=df)
    plt.title('违约率与年龄关系')
    
    plt.tight_layout()
    plt.savefig('credit_risk_eda.png')
    
    # 8. 相关性分析
    plt.figure(figsize=(12, 10))
    correlation_matrix = df.corr()
    sns.heatmap(correlation_matrix, annot=False, cmap='coolwarm', linewidths=0.5)
    plt.title('特征相关性热力图')
    plt.tight_layout()
    plt.savefig('credit_risk_correlation.png')
    
    return {
        "basic_stats": df.describe(),
        "target_distribution": df['DEFAULT'].value_counts().to_dict(),
        "duplicates": duplicates,
        "missing_values": missing_values.sum(),
        "correlation_matrix": correlation_matrix
    }

if __name__ == "__main__":
    df = load_credit_data()
    results = exploratory_analysis(df)
    print("\n探索性分析完成！") 