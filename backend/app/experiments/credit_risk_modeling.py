import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import joblib

# 导入机器学习模型和工具
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report, 
    roc_curve, precision_recall_curve, average_precision_score
)
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE

from credit_risk_exploration import load_credit_data
from credit_risk_cleaning import data_cleaning
from credit_risk_feature_engineering import calculate_technical_indicators, extract_features
import matplotlib as mpl
from app.services.docker_matplotlib_fix import configure_matplotlib_fonts

# 配置字体以支持中文显示
configure_matplotlib_fonts()

def train_credit_risk_model(df, model_type="random_forest", balance_data=True, test_size=0.25, random_state=42):
    """
    训练信用卡违约预测模型
    """
    print(f"\n开始训练{model_type}模型...")
    
    # 分离特征和标签
    X = df.drop('DEFAULT', axis=1)
    y = df['DEFAULT']
    
    print(f"特征数量: {X.shape[1]}")
    print(f"样本数量: {X.shape[0]}")
    print(f"违约样本比例: {y.mean():.4f}")
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    print(f"训练集大小: {X_train.shape[0]}")
    print(f"测试集大小: {X_test.shape[0]}")
    
    # 处理类别不平衡问题
    if balance_data:
        print("使用SMOTE处理类别不平衡...")
        smote = SMOTE(random_state=random_state)
        X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
        print(f"SMOTE后训练集大小: {X_train_resampled.shape[0]}")
        print(f"SMOTE后违约样本比例: {y_train_resampled.mean():.4f}")
    else:
        X_train_resampled, y_train_resampled = X_train, y_train
    
    # 选择并训练模型
    if model_type == "logistic_regression":
        model = LogisticRegression(C=1.0, max_iter=1000, random_state=random_state)
    elif model_type == "random_forest":
        model = RandomForestClassifier(
            n_estimators=100, max_depth=10, min_samples_split=5, 
            min_samples_leaf=2, random_state=random_state
        )
    elif model_type == "gradient_boosting":
        model = GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=5,
            random_state=random_state
        )
    else:
        raise ValueError("不支持的模型类型")
    
    # 创建包含标准化的管道
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', model)
    ])
    
    # 训练模型
    print("训练模型...")
    pipeline.fit(X_train_resampled, y_train_resampled)
    
    # 预测并评估
    print("模型评估...")
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    
    # 计算各种评估指标
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    avg_precision = average_precision_score(y_test, y_prob)
    
    # 打印评估结果
    print("\n===== 模型评估结果 =====")
    print(f"准确率 (Accuracy): {accuracy:.4f}")
    print(f"精确率 (Precision): {precision:.4f}")
    print(f"召回率 (Recall): {recall:.4f}")
    print(f"F1分数: {f1:.4f}")
    print(f"ROC AUC: {roc_auc:.4f}")
    print(f"平均精确率 (Average Precision): {avg_precision:.4f}")
    
    # 打印分类报告
    print("\n分类报告:")
    print(classification_report(y_test, y_pred))
    
    # 混淆矩阵
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('混淆矩阵')
    plt.ylabel('真实标签')
    plt.xlabel('预测标签')
    plt.tight_layout()
    plt.savefig('credit_risk_confusion_matrix.png')
    
    # ROC曲线
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
    plt.savefig('credit_risk_roc_curve.png')
    
    # PR曲线
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
    plt.savefig('credit_risk_pr_curve.png')
    
    # 如果是树模型，可视化特征重要性
    if model_type in ["random_forest", "gradient_boosting"]:
        feature_importance = pipeline.named_steps['model'].feature_importances_
        feature_names = X.columns
        
        # 按重要性排序
        indices = np.argsort(feature_importance)[::-1]
        top_n = 15  # 只显示前15个重要特征
        
        plt.figure(figsize=(10, 6))
        plt.title(f"{model_type} 特征重要性")
        plt.bar(range(top_n), feature_importance[indices][:top_n], align="center")
        plt.xticks(range(top_n), feature_names[indices][:top_n], rotation=90)
        plt.tight_layout()
        plt.savefig('credit_risk_feature_importance.png')
    
    # 保存模型
    model_path = Path(__file__).parent / f"credit_risk_{model_type}.pkl"
    joblib.dump(pipeline, model_path)
    print(f"\n模型已保存至: {model_path}")
    
    # 返回评估结果和模型
    eval_results = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "avg_precision": avg_precision,
        "confusion_matrix": cm,
        "classification_report": classification_report(y_test, y_pred)
    }
    
    return pipeline, eval_results

def evaluate_multiple_models(df):
    """
    评估多个模型并比较性能
    """
    models = {
        "logistic_regression": "逻辑回归",
        "random_forest": "随机森林",
        "gradient_boosting": "梯度提升树"
    }
    
    results = {}
    
    for model_key, model_name in models.items():
        print(f"\n{'='*20} 训练{model_name}模型 {'='*20}")
        _, eval_results = train_credit_risk_model(df, model_type=model_key)
        results[model_key] = eval_results
    
    # 比较不同模型的性能
    plt.figure(figsize=(12, 8))
    metrics = ["accuracy", "precision", "recall", "f1", "roc_auc", "avg_precision"]
    metric_names = ["准确率", "精确率", "召回率", "F1分数", "ROC AUC", "平均精确率"]
    
    for i, metric in enumerate(metrics):
        plt.subplot(2, 3, i+1)
        values = [results[model][metric] for model in models.keys()]
        model_names = [models[model] for model in models.keys()]
        
        sns.barplot(x=model_names, y=values)
        plt.title(metric_names[i])
        plt.xticks(rotation=45)
        plt.ylim([0, 1])
    
    plt.tight_layout()
    plt.savefig('credit_risk_model_comparison.png')
    print("\n模型比较图已保存!")
    
    # 返回结果
    return results

if __name__ == "__main__":
    # 加载原始数据
    df = load_credit_data()
    
    # 数据清洗
    df_cleaned = data_cleaning(df)
    
    # 计算技术指标
    df_with_indicators = calculate_technical_indicators(df_cleaned)
    
    # 特征提取
    df_final, _, _ = extract_features(df_with_indicators)
    
    # 评估多个模型
    model_results = evaluate_multiple_models(df_final)
    
    # 选择性能最佳的模型（这里以ROC AUC为标准）
    best_model = max(model_results.items(), key=lambda x: x[1]['roc_auc'])
    print(f"\n根据ROC AUC指标，性能最佳的模型是: {best_model[0]}")
    
    # 保存最终的处理后数据集
    output_path = Path(__file__).parent / "credit_risk_final.csv"
    df_final.to_csv(output_path, index=False)
    print(f"\n最终处理后的数据已保存至: {output_path}") 