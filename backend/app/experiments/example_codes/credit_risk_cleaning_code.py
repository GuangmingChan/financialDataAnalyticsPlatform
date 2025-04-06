import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from app.services.bank_analysis import bank_service
import matplotlib as mpl
mpl.rcParams['font.family'] = 'DejaVu Sans'
# 加载数据
df = bank_service.load_credit_data()
print("原始数据形状:", df.shape)

# 创建原始数据的副本
df_cleaned = df.copy()

# 1. 检查并处理重复值
duplicates = df_cleaned.duplicated().sum()
if duplicates > 0:
    print(f"发现 {duplicates} 个重复行，正在移除...")
    df_cleaned = df_cleaned.drop_duplicates()

# 2. 处理缺失值
missing_values = df_cleaned.isnull().sum()
if missing_values.sum() > 0:
    print(f"发现 {missing_values.sum()} 个缺失值，正在处理...")
    # 对数值型变量用中位数填充
    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df_cleaned[col].isnull().sum() > 0:
            median_value = df_cleaned[col].median()
            df_cleaned[col].fillna(median_value, inplace=True)
else:
    print("数据集中没有缺失值")

# 3. 处理异常值
print("\n开始处理异常值...")
numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols.remove('DEFAULT')  # 不处理目标变量

for col in numeric_cols:
    Q1 = df_cleaned[col].quantile(0.25)
    Q3 = df_cleaned[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # 统计异常值
    outliers = df_cleaned[(df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)][col]
    
    if len(outliers) > 0:
        print(f"  - {col}列有 {len(outliers)} 个异常值 ({len(outliers)/len(df_cleaned)*100:.2f}%)")
        
        # 将异常值替换为边界值
        df_cleaned.loc[df_cleaned[col] < lower_bound, col] = lower_bound
        df_cleaned.loc[df_cleaned[col] > upper_bound, col] = upper_bound

# 4. 数据标准化
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
df_standardized = pd.concat([X_scaled, y], axis=1)

# 对比标准化前后的描述性统计
print("\n标准化前的统计量:")
print(df_cleaned[numeric_cols].describe())
print("\n标准化后的统计量:")
print(df_standardized[numeric_cols].describe())

print(f"\n清洗完成！原始数据: {df.shape}，清洗后: {df_standardized.shape}")

# 可视化标准化前后
plt.figure(figsize=(15, 6))

# 标准化前
plt.subplot(1, 2, 1)
plt.boxplot(df_cleaned[['LIMIT_BAL', 'AGE', 'BILL_AMT1']])
plt.title('标准化前')
plt.xticks([1, 2, 3], ['LIMIT_BAL', 'AGE', 'BILL_AMT1'])

# 标准化后
plt.subplot(1, 2, 2)
plt.boxplot(df_standardized[['LIMIT_BAL', 'AGE', 'BILL_AMT1']])
plt.title('标准化后')
plt.xticks([1, 2, 3], ['LIMIT_BAL', 'AGE', 'BILL_AMT1'])

plt.tight_layout()
plt.show() 