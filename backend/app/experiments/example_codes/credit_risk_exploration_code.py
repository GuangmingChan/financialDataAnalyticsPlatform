import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from app.services.bank_analysis import bank_service
import matplotlib as mpl
mpl.rcParams['font.family'] = 'DejaVu Sans'

# 加载数据
df = bank_service.load_credit_data()

# 1. 基本统计量
print("=== 基本统计量 ===")
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

# 违约率与年龄的关系
plt.subplot(2, 3, 3)
sns.boxplot(x='DEFAULT', y='AGE', data=df)
plt.title('违约率与年龄关系')

# 相关性分析
plt.figure(figsize=(12, 10))
correlation_matrix = df.corr()
sns.heatmap(correlation_matrix, annot=False, cmap='coolwarm', linewidths=0.5)
plt.title('特征相关性热力图')
plt.show() 