import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report, 
    roc_curve, precision_recall_curve, average_precision_score
)
import joblib
from app.services.bank_analysis import bank_service

import matplotlib as mpl
mpl.rcParams['font.family'] = 'DejaVu Sans'

# 加载测试集和预测结果（示例，实际情况中这些变量应该已经存在）
# 这里仅为演示，请根据实际情况修改
df = bank_service.load_credit_data()
X = df.drop('DEFAULT', axis=1)
y = df['DEFAULT']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

# 加载前一步训练好的模型（或重新训练一个）
# 如果有保存的模型，可以使用：pipeline = joblib.load('credit_risk_model.pkl')
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE

# 重新训练模型
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42))
])

pipeline.fit(X_train_resampled, y_train_resampled)

# 使用模型进行预测
y_pred = pipeline.predict(X_test)
y_prob = pipeline.predict_proba(X_test)[:, 1]

# 1. 计算各种评估指标
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_prob)
avg_precision = average_precision_score(y_test, y_prob)

# 打印评估结果
print("\n===== 详细模型评估结果 =====")
print(f"准确率 (Accuracy): {accuracy:.4f}")
print(f"精确率 (Precision): {precision:.4f}")
print(f"召回率 (Recall): {recall:.4f}")
print(f"F1分数: {f1:.4f}")
print(f"ROC AUC: {roc_auc:.4f}")
print(f"平均精确率 (Average Precision): {avg_precision:.4f}")

# 2. 打印分类报告
print("\n分类报告:")
print(classification_report(y_test, y_pred))

# 3. 混淆矩阵
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('混淆矩阵')
plt.ylabel('真实标签')
plt.xlabel('预测标签')
plt.tight_layout()
plt.show()

# 4. ROC曲线
plt.figure(figsize=(8, 6))
fpr, tpr, _ = roc_curve(y_test, y_prob)
plt.plot(fpr, tpr, color='blue', lw=2, label=f'ROC曲线 (AUC = {roc_auc:.4f})')
plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('假阳性率 (False Positive Rate)')
plt.ylabel('真阳性率 (True Positive Rate)')
plt.title('ROC曲线')
plt.legend(loc="lower right")
plt.show()

# 5. PR曲线
plt.figure(figsize=(8, 6))
precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_prob)
plt.plot(recall_curve, precision_curve, color='green', lw=2, 
         label=f'PR曲线 (AP = {avg_precision:.4f})')
plt.axhline(y=y_test.mean(), color='gray', linestyle='--', 
           label=f'基准 (违约率 = {y_test.mean():.4f})')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('召回率 (Recall)')
plt.ylabel('精确率 (Precision)')
plt.title('精确率-召回率曲线')
plt.legend(loc="lower left")
plt.show()

# 6. 计算不同阈值下的性能
thresholds = np.arange(0.1, 1.0, 0.1)
threshold_metrics = []

for threshold in thresholds:
    y_pred_threshold = (y_prob >= threshold).astype(int)
    threshold_metrics.append({
        'threshold': threshold,
        'accuracy': accuracy_score(y_test, y_pred_threshold),
        'precision': precision_score(y_test, y_pred_threshold),
        'recall': recall_score(y_test, y_pred_threshold),
        'f1': f1_score(y_test, y_pred_threshold)
    })

threshold_df = pd.DataFrame(threshold_metrics)
print("\n不同阈值下的模型性能:")
print(threshold_df)

# 绘制不同阈值下的指标变化
plt.figure(figsize=(10, 6))
plt.plot(threshold_df['threshold'], threshold_df['accuracy'], marker='o', label='准确率')
plt.plot(threshold_df['threshold'], threshold_df['precision'], marker='s', label='精确率')
plt.plot(threshold_df['threshold'], threshold_df['recall'], marker='^', label='召回率')
plt.plot(threshold_df['threshold'], threshold_df['f1'], marker='*', label='F1分数')
plt.xlabel('阈值')
plt.ylabel('指标值')
plt.title('不同阈值下的模型性能')
plt.legend()
plt.grid(True)
plt.show()

# 7. 特征重要性分析（如果模型支持）
if hasattr(pipeline.named_steps['model'], 'feature_importances_'):
    importances = pipeline.named_steps['model'].feature_importances_
    indices = np.argsort(importances)[::-1]
    
    plt.figure(figsize=(10, 6))
    plt.title('特征重要性')
    plt.bar(range(X.shape[1]), importances[indices], align='center')
    plt.xticks(range(X.shape[1]), X.columns[indices], rotation=90)
    plt.tight_layout()
    plt.show()
    
    print("\n特征重要性排名:")
    for i in range(10):  # 只打印前10个
        print(f"{i+1}. {X.columns[indices[i]]}: {importances[indices[i]]:.4f}") 