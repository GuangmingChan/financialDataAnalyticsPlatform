import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns

from credit_risk_exploration import load_credit_data
import matplotlib as mpl
mpl.rcParams['font.family'] = 'DejaVu Sans'

def data_cleaning(df, return_preprocessed=True):
    """
    数据清洗流程
    """
    print("开始数据清洗...")
    
    # 创建原始数据的副本
    df_cleaned = df.copy()
    
    # 1. 检查并处理重复值
    duplicates = df_cleaned.duplicated().sum()
    if duplicates > 0:
        print(f"发现 {duplicates} 个重复行，正在移除...")
        df_cleaned = df_cleaned.drop_duplicates()
    
    # 2. 处理缺失值（如果有的话）
    missing_values = df_cleaned.isnull().sum()
    if missing_values.sum() > 0:
        print(f"发现 {missing_values.sum()} 个缺失值，正在处理...")
        # 对数值型变量用中位数填充
        numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df_cleaned[col].isnull().sum() > 0:
                median_value = df_cleaned[col].median()
                df_cleaned[col].fillna(median_value, inplace=True)
                print(f"  - 已用中位数 {median_value} 填充 {col} 列")
                
        # 对分类变量用众数填充
        cat_cols = df_cleaned.select_dtypes(exclude=[np.number]).columns
        for col in cat_cols:
            if df_cleaned[col].isnull().sum() > 0:
                mode_value = df_cleaned[col].mode()[0]
                df_cleaned[col].fillna(mode_value, inplace=True)
                print(f"  - 已用众数 {mode_value} 填充 {col} 列")
    else:
        print("数据集中没有缺失值")

    # 3. 处理异常值
    print("\n开始处理异常值...")
    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols.remove('DEFAULT')  # 不处理目标变量
    
    outliers_summary = {}
    
    for col in numeric_cols:
        Q1 = df_cleaned[col].quantile(0.25)
        Q3 = df_cleaned[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 统计异常值
        outliers = df_cleaned[(df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)][col]
        outliers_summary[col] = len(outliers)
        
        if len(outliers) > 0:
            print(f"  - {col}列有 {len(outliers)} 个异常值 ({len(outliers)/len(df_cleaned)*100:.2f}%)")
            
            # 将异常值替换为边界值
            df_cleaned.loc[df_cleaned[col] < lower_bound, col] = lower_bound
            df_cleaned.loc[df_cleaned[col] > upper_bound, col] = upper_bound
            
            print(f"    已将异常值替换为边界值: [{lower_bound}, {upper_bound}]")
    
    print("\n异常值处理完成!")
    
    # 4. 数据标准化/归一化
    if return_preprocessed:
        print("\n开始数据标准化...")
        
        # 分离特征和标签
        X = df_cleaned.drop('DEFAULT', axis=1)
        y = df_cleaned['DEFAULT']
        
        # 对数值类型的特征进行标准化
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        
        # 使用StandardScaler进行标准化
        scaler = StandardScaler()
        X_scaled = X.copy()
        X_scaled[numeric_cols] = scaler.fit_transform(X[numeric_cols])
        
        print(f"已对 {len(numeric_cols)} 个数值特征进行标准化")
        
        # 合并回DataFrame
        df_preprocessed = pd.concat([X_scaled, y], axis=1)
        
        # 展示标准化前后对比的直方图(选择几个主要特征)
        main_features = ['LIMIT_BAL', 'AGE', 'BILL_AMT1', 'PAY_AMT1']
        plt.figure(figsize=(15, 10))
        
        for i, feature in enumerate(main_features):
            # 原始数据分布
            plt.subplot(2, 4, i+1)
            sns.histplot(df_cleaned[feature], kde=True)
            plt.title(f'原始 {feature}')
            
            # 标准化后的分布
            plt.subplot(2, 4, i+5)
            sns.histplot(df_preprocessed[feature], kde=True)
            plt.title(f'标准化后 {feature}')
        
        plt.tight_layout()
        plt.savefig('credit_risk_standardization.png')
        print("标准化前后对比可视化已保存")
        
        return df_preprocessed
    
    return df_cleaned

if __name__ == "__main__":
    # 加载数据
    df = load_credit_data()
    
    # 数据清洗
    df_cleaned = data_cleaning(df)
    
    print(f"\n清洗完成！原始数据: {df.shape}，清洗后: {df_cleaned.shape}")
    print("\n清洗后数据预览:")
    print(df_cleaned.head()) 