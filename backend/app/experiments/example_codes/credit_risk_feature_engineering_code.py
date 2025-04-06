import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import Lasso
import matplotlib.pyplot as plt
from app.services.bank_analysis import bank_service
import matplotlib as mpl
mpl.rcParams['font.family'] = 'DejaVu Sans'
# 加载数据
df = bank_service.load_credit_data()

# 清洗过的数据
df_cleaned = df.copy()

# 1. 计算技术指标
print("开始计算技术指标...")
df_features = df_cleaned.copy()

# 提取时间顺序的账单和支付金额
bill_cols = ['BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6']
pay_cols = ['PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6']

# 计算MACD（指数平滑异同平均线）
print("计算MACD指标...")
# 短期和长期指数移动平均值
for i, col in enumerate(bill_cols):
    if i < 3:  # 用前3个月作为短期
        df_features[f'EMA_short_{i+1}'] = df_cleaned[bill_cols[i]]
    else:  # 用后3个月作为长期
        df_features[f'EMA_long_{i-2}'] = df_cleaned[bill_cols[i]]

# 计算MACD值
for i in range(1, 4):
    df_features[f'MACD_{i}'] = df_features[f'EMA_short_{i}'] - df_features[f'EMA_long_{i}']

# 计算RSI（相对强弱指标）
print("计算RSI指标...")
# 计算账单变化
for i in range(len(bill_cols)-1):
    df_features[f'bill_change_{i+1}'] = df_cleaned[bill_cols[i]] - df_cleaned[bill_cols[i+1]]

# 对于每个客户，计算其正面和负面的账单变化
for i in range(1, len(bill_cols)):
    # 正面变化（账单减少）
    df_features[f'positive_change_{i}'] = df_features[f'bill_change_{i}'].apply(lambda x: max(x, 0))
    # 负面变化（账单增加）
    df_features[f'negative_change_{i}'] = df_features[f'bill_change_{i}'].apply(lambda x: abs(min(x, 0)))

# 计算平均正面和负面变化
df_features['avg_positive_change'] = df_features[[col for col in df_features.columns if 'positive_change' in col]].mean(axis=1)
df_features['avg_negative_change'] = df_features[[col for col in df_features.columns if 'negative_change' in col]].mean(axis=1)

# 计算RSI
df_features['RSI'] = 100 - (100 / (1 + df_features['avg_positive_change'] / (df_features['avg_negative_change'] + 1e-10)))

# 计算OBV（能量潮指标）
print("计算OBV指标...")
# 初始化OBV为第一个月的账单金额
df_features['OBV'] = df_cleaned['BILL_AMT1']

# 计算OBV
for i in range(1, len(bill_cols)):
    # 如果账单增加，OBV加上支付金额；如果账单减少，OBV减去支付金额
    df_features['OBV'] += np.where(df_cleaned[bill_cols[i-1]] > df_cleaned[bill_cols[i]], 
                                 df_cleaned[pay_cols[i-1]], 
                                 -df_cleaned[pay_cols[i-1]])

# 2. 使用PCA和Lasso进行特征提取
print("\n开始特征提取...")
# 分离特征和标签
X = df_features.drop('DEFAULT', axis=1)
y = df_features['DEFAULT']

# PCA降维
print("执行PCA降维...")
n_components = 10
pca = PCA(n_components=n_components)
X_pca = pca.fit_transform(X)

explained_variance = pca.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance)

print(f"使用{n_components}个主成分，解释的总方差比例: {cumulative_variance[-1]:.4f}")

# 将PCA结果转换回DataFrame
pca_cols = [f'PC{i+1}' for i in range(n_components)]
X_pca_df = pd.DataFrame(X_pca, columns=pca_cols)

# 可视化PCA
plt.figure(figsize=(10, 6))
plt.bar(range(1, n_components+1), explained_variance)
plt.plot(range(1, n_components+1), cumulative_variance, 'r-')
plt.xlabel('主成分数量')
plt.ylabel('解释方差比例')
plt.title('PCA主成分解释方差')
plt.show()

# Lasso特征选择
print("\n执行Lasso特征选择...")
lasso = Lasso(alpha=0.01)
sfm = SelectFromModel(lasso)
sfm.fit(X, y)

# 获取被选择的特征
feature_names = X.columns
selected_features = feature_names[sfm.get_support()]

print(f"Lasso选择了{len(selected_features)}个特征:")
for feature in selected_features:
    print(f"  - {feature}")

# 特征重要性
feature_importance = pd.Series(np.abs(lasso.coef_), index=feature_names)
top_features = feature_importance.sort_values(ascending=False).head(15)

plt.figure(figsize=(12, 6))
top_features.plot(kind='bar')
plt.title('Lasso特征重要性')
plt.xlabel('特征')
plt.ylabel('重要性')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# 组合PCA和原始特征
X_selected = X[selected_features]
X_combined = pd.concat([X_selected, X_pca_df], axis=1)

# 将标签加回
final_df = pd.concat([X_combined, y], axis=1)

print("\n特征工程完成！")
print(f"原始特征数: {df.shape[1]}")
print(f"构建的技术指标: MACD, RSI, OBV")
print(f"Lasso选择的特征数: {len(selected_features)}")
print(f"PCA主成分数: {n_components}")
print(f"最终特征数: {X_combined.shape[1]}")

print("\n最终数据集预览:")
print(final_df.head()) 