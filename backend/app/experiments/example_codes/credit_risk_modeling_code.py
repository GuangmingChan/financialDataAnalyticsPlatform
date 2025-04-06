import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns
from app.services.bank_analysis import bank_service
import matplotlib as mpl
mpl.rcParams['font.family'] = 'DejaVu Sans'
# 加载预处理后的数据
df = bank_service.load_credit_data()

# 简单数据清洗
df_cleaned = df.copy()

# 分离特征和标签
X = df_cleaned.drop('DEFAULT', axis=1)
y = df_cleaned['DEFAULT']

print(f"特征数量: {X.shape[1]}")
print(f"样本数量: {X.shape[0]}")
print(f"违约样本比例: {y.mean():.4f}")

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

print(f"训练集大小: {X_train.shape[0]}")
print(f"测试集大小: {X_test.shape[0]}")

# 处理类别不平衡问题
print("使用SMOTE处理类别不平衡...")
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
print(f"SMOTE后训练集大小: {X_train_resampled.shape[0]}")
print(f"SMOTE后违约样本比例: {y_train_resampled.mean():.4f}")

# 可视化SMOTE前后的目标变量分布
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
sns.countplot(x=y_train)
plt.title('重采样前的目标变量分布')
plt.xlabel('违约状态')
plt.ylabel('样本数量')

plt.subplot(1, 2, 2)
sns.countplot(x=y_train_resampled)
plt.title('SMOTE重采样后的目标变量分布')
plt.xlabel('违约状态')
plt.ylabel('样本数量')

plt.tight_layout()
plt.show()

# 创建随机森林模型
model = RandomForestClassifier(
    n_estimators=100, 
    max_depth=10, 
    min_samples_split=5,
    min_samples_leaf=2, 
    random_state=42
)

# 创建包含标准化的管道
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', model)
])

# 训练模型
print("训练模型...")
pipeline.fit(X_train_resampled, y_train_resampled)

# 预测
print("模型预测...")
y_pred = pipeline.predict(X_test)
y_prob = pipeline.predict_proba(X_test)[:, 1]

# 计算评估指标
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_prob)

# 打印评估结果
print("\n===== 模型评估结果 =====")
print(f"准确率 (Accuracy): {accuracy:.4f}")
print(f"精确率 (Precision): {precision:.4f}")
print(f"召回率 (Recall): {recall:.4f}")
print(f"F1分数: {f1:.4f}")
print(f"ROC AUC: {roc_auc:.4f}")

# 特征重要性
feature_importance = pipeline.named_steps['model'].feature_importances_
feature_names = X.columns

# 绘制特征重要性
indices = np.argsort(feature_importance)[::-1]
top_n = 10

plt.figure(figsize=(10, 6))
plt.title("特征重要性")
plt.bar(range(top_n), feature_importance[indices][:top_n], align="center")
plt.xticks(range(top_n), feature_names[indices][:top_n], rotation=90)
plt.xlim([-1, top_n])
plt.tight_layout()
plt.show()

# 打印前10个最重要的特征
print("\n前10个最重要的特征:")
for i in range(top_n):
    print(f"{feature_names[indices[i]]}: {feature_importance[indices[i]]:.4f}")

# 保存模型（在实际环境中可用，这里仅做示例）
import joblib
# joblib.dump(pipeline, 'credit_risk_model.pkl') 