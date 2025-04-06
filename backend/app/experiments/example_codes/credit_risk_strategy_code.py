import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, precision_recall_curve
from sklearn.model_selection import train_test_split
from app.services.bank_analysis import bank_service
import matplotlib as mpl
mpl.rcParams['font.family'] = 'DejaVu Sans'
# 使用前面模型评估步骤的变量
# 加载数据和训练模型（示例）
df = bank_service.load_credit_data()
X = df.drop('DEFAULT', axis=1)
y = df['DEFAULT']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

# 创建简单的随机森林模型
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE

# 重采样处理不平衡数据
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# 创建并训练模型
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42))
])
pipeline.fit(X_train_resampled, y_train_resampled)

# 预测概率
y_prob = pipeline.predict_proba(X_test)[:, 1]

# 1. 寻找最优阈值
def find_optimal_threshold(y_true, y_prob, strategy="f1"):
    """根据不同业务策略找到最优决策阈值"""
    # 计算不同阈值下的性能指标
    precision, recall, thresholds_pr = precision_recall_curve(y_true, y_prob)
    # 添加一个阈值，使长度匹配
    thresholds_pr = np.append(thresholds_pr, 1.0)
    
    fpr, tpr, thresholds_roc = roc_curve(y_true, y_prob)
    
    # 计算每个阈值的F1分数
    f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
    
    # 计算每个阈值的利润（假设不同代价）
    # 假设：正确拒绝违约客户收益100，错误拒绝好客户代价50
    # 正确接受好客户收益10，错误接受违约客户代价200
    profit = []
    
    for i, threshold in enumerate(thresholds_pr):
        # 在这个阈值下的预测
        y_pred = (y_prob >= threshold).astype(int)
        
        # 计算混淆矩阵
        tn = np.sum((y_true == 0) & (y_pred == 0))  # 真阴性
        fp = np.sum((y_true == 0) & (y_pred == 1))  # 假阳性
        fn = np.sum((y_true == 1) & (y_pred == 0))  # 假阴性
        tp = np.sum((y_true == 1) & (y_pred == 1))  # 真阳性
        
        # 计算收益
        current_profit = 100 * tp + 10 * tn - 50 * fn - 200 * fp
        profit.append(current_profit)
    
    # 根据策略选择最优阈值
    if strategy == "f1":
        # 最大化F1分数
        best_idx = np.argmax(f1_scores)
        best_threshold = thresholds_pr[best_idx]
        best_f1 = f1_scores[best_idx]
        print(f"最优F1分数阈值: {best_threshold:.4f}, F1: {best_f1:.4f}")
        return best_threshold
    
    elif strategy == "profit":
        # 最大化利润
        profit = np.array(profit)
        best_idx = np.argmax(profit)
        best_threshold = thresholds_pr[best_idx]
        best_profit = profit[best_idx]
        print(f"最优利润阈值: {best_threshold:.4f}, 利润: {best_profit:.2f}")
        return best_threshold
    
    elif strategy == "balanced":
        # 寻找TPR和TNR平衡点
        tpr_copy = np.copy(tpr)
        tnr = 1 - fpr
        balance_point = np.argmin(np.abs(tpr_copy - tnr))
        best_threshold = thresholds_roc[balance_point]
        print(f"平衡阈值 (TPR ≈ TNR): {best_threshold:.4f}, "
              f"TPR: {tpr[balance_point]:.4f}, TNR: {tnr[balance_point]:.4f}")
        return best_threshold

# 找出不同策略下的最优阈值
threshold_f1 = find_optimal_threshold(y_test, y_prob, strategy="f1")
threshold_profit = find_optimal_threshold(y_test, y_prob, strategy="profit")
threshold_balanced = find_optimal_threshold(y_test, y_prob, strategy="balanced")

# 2. 创建风险分段
def create_risk_segments(y_prob, n_segments=5):
    """根据违约概率将客户分成不同风险等级"""
    # 创建分段
    labels = [f"风险{i+1}级" for i in range(n_segments)]
    risk_segments = pd.qcut(y_prob, q=n_segments, labels=labels)
    
    # 计算每个风险等级的统计信息
    risk_stats = pd.DataFrame({
        "风险等级": labels,
        "客户数量": [np.sum(risk_segments == label) for label in labels],
        "平均违约概率": [y_prob[risk_segments == label].mean() for label in labels]
    })
    
    return risk_segments, risk_stats

# 将客户分为不同风险等级
risk_segments, risk_stats = create_risk_segments(y_prob, n_segments=5)
print("\n客户风险分级:")
print(risk_stats)

# 可视化风险分段
plt.figure(figsize=(12, 5))

# 违约概率分布
plt.subplot(1, 2, 1)
sns.histplot(y_prob, bins=50, kde=True)
plt.title('违约概率分布')
plt.xlabel('违约概率')
plt.ylabel('客户数量')

# 风险等级分布
plt.subplot(1, 2, 2)
sns.barplot(x="风险等级", y="客户数量", data=risk_stats)
plt.title('风险等级分布')
plt.ylabel('客户数量')
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

# 3. 制定分级风险策略
risk_strategies = pd.DataFrame({
    "风险等级": risk_stats["风险等级"],
    "平均违约概率": risk_stats["平均违约概率"],
    "信用审批策略": ["自动拒绝", "严格审查", "人工审核", "自动批准但限额", "自动批准全额"],
    "信用额度比例": [0, 0.3, 0.6, 0.8, 1.0],
    "利率调整": ["+10%", "+5%", "+2%", "+0%", "-1%"],
    "风险监控频率": ["不适用", "每周", "每两周", "每月", "每季度"]
})

print("\n风险控制策略:")
print(risk_strategies)

# 4. 分析特征重要性
if hasattr(pipeline.named_steps['model'], 'feature_importances_'):
    feature_importance = pipeline.named_steps['model'].feature_importances_
    feature_names = X.columns
    
    # 排序并展示前10个特征
    indices = np.argsort(feature_importance)[::-1]
    top_n = 10
    
    top_features = pd.DataFrame({
        'Feature': feature_names[indices[:top_n]],
        'Importance': feature_importance[indices[:top_n]]
    })
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Importance', y='Feature', data=top_features)
    plt.title('影响违约的关键因素')
    plt.tight_layout()
    plt.show()
    
    print("\n影响违约的关键因素:")
    for i, feature in enumerate(top_features['Feature']):
        print(f"{i+1}. {feature}: {top_features['Importance'].iloc[i]:.4f}")

# 5. 生成风险控制策略报告
print("\n===== 信用卡风险控制策略 =====")
print(f"\n1. 风险评分阈值建议:")
print(f"  - 最大化F1分数阈值: {threshold_f1:.4f} (平衡识别违约与避免拒绝)")
print(f"  - 最大化利润阈值: {threshold_profit:.4f} (注重银行利润)")
print(f"  - 平衡阈值: {threshold_balanced:.4f} (平等对待违约识别与接受率)")

print("\n2. 差异化信用额度:")
print("  - 高风险客户（1-2级）：严格限制或拒绝信用")
print("  - 中风险客户（3级）：提供较低的信用额度，并定期审核")
print("  - 低风险客户（4-5级）：提供完整信用额度和优惠条件")

print("\n3. 动态利率调整:")
print("  - 根据客户风险等级调整利率")
print("  - 高风险客户：较高利率以补偿风险")
print("  - 低风险客户：优惠利率以提高客户黏性")

print("\n4. 风险监控与预警:")
print("  - 对高风险客户实施更频繁的交易监控")
print("  - 建立行为预警体系，识别潜在违约迹象")
print("  - 当风险指标超过阈值时，触发审核流程")

print("\n5. 客户服务策略:")
print("  - 为高风险客户提供财务管理建议")
print("  - 向低风险客户提供忠诚度奖励和增值服务")
print("  - 定期检查并更新客户风险状况") 