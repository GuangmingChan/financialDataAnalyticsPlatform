import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import joblib
from sklearn.metrics import roc_curve, precision_recall_curve
from sklearn.model_selection import train_test_split
import shap
import warnings
warnings.filterwarnings('ignore')

from credit_risk_exploration import load_credit_data
from credit_risk_cleaning import data_cleaning
from credit_risk_feature_engineering import calculate_technical_indicators, extract_features
import matplotlib as mpl
mpl.rcParams['font.family'] = 'DejaVu Sans'

def find_optimal_threshold(y_true, y_prob, strategy="f1"):
    """
    根据不同业务策略找到最优决策阈值
    """
    # 计算不同阈值下的性能指标
    precision, recall, thresholds_pr = precision_recall_curve(y_true, y_prob)
    # 添加一个阈值，使长度匹配
    thresholds_pr = np.append(thresholds_pr, 1.0)
    
    fpr, tpr, thresholds_roc = roc_curve(y_true, y_prob)
    
    # 计算每个阈值的F1分数
    f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
    
    # 计算每个阈值的Profit (假设不同代价)
    # 假设：
    # 正确拒绝违约客户收益100
    # 错误拒绝好客户代价50
    # 正确接受好客户收益10
    # 错误接受违约客户代价200
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
        return best_threshold, {"f1": best_f1}
    
    elif strategy == "profit":
        # 最大化利润
        profit = np.array(profit)
        best_idx = np.argmax(profit)
        best_threshold = thresholds_pr[best_idx]
        best_profit = profit[best_idx]
        print(f"最优利润阈值: {best_threshold:.4f}, 利润: {best_profit:.2f}")
        return best_threshold, {"profit": best_profit}
    
    elif strategy == "balanced":
        # 寻找TPR和TNR平衡点
        tpr_copy = np.copy(tpr)
        tnr = 1 - fpr
        balance_point = np.argmin(np.abs(tpr_copy - tnr))
        best_threshold = thresholds_roc[balance_point]
        print(f"平衡阈值 (TPR ≈ TNR): {best_threshold:.4f}, "
              f"TPR: {tpr[balance_point]:.4f}, TNR: {tnr[balance_point]:.4f}")
        return best_threshold, {"tpr": tpr[balance_point], "tnr": tnr[balance_point]}

def create_risk_segments(y_prob, n_segments=5):
    """
    根据违约概率将客户分成不同风险等级
    """
    # 创建分段
    labels = [f"风险{i+1}级" for i in range(n_segments)]
    risk_segments = pd.qcut(y_prob, q=n_segments, labels=labels)
    
    # 计算每个风险等级的统计信息
    risk_stats = pd.DataFrame({
        "风险等级": labels,
        "客户数量": [np.sum(risk_segments == label) for label in labels],
        "平均违约概率": [y_prob[risk_segments == label].mean() for label in labels]
    })
    
    # 绘制风险分布
    plt.figure(figsize=(12, 6))
    
    # 概率分布直方图
    plt.subplot(1, 2, 1)
    sns.histplot(y_prob, bins=50, kde=True)
    plt.title("违约概率分布")
    plt.xlabel("违约概率")
    plt.ylabel("客户数量")
    
    # 风险等级条形图
    plt.subplot(1, 2, 2)
    sns.barplot(x="风险等级", y="客户数量", data=risk_stats)
    plt.title("风险等级分布")
    plt.ylabel("客户数量")
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig("credit_risk_segments.png")
    
    return risk_segments, risk_stats

def analyze_feature_importance(model, X, shap_sample=500):
    """
    分析特征重要性，找出影响违约的关键因素
    """
    print("分析特征重要性...")
    
    # 对于树模型，直接获取特征重要性
    if hasattr(model, 'feature_importances_'):
        # 获取特征重要性
        feature_importance = model.feature_importances_
        feature_names = X.columns
        
        # 排序并展示前15个特征
        indices = np.argsort(feature_importance)[::-1]
        top_n = min(15, len(feature_importance))
        
        top_features = pd.DataFrame({
            'Feature': feature_names[indices[:top_n]],
            'Importance': feature_importance[indices[:top_n]]
        })
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Importance', y='Feature', data=top_features)
        plt.title('特征重要性')
        plt.tight_layout()
        plt.savefig('credit_risk_top_features.png')
        
        print("\n影响违约的关键因素:")
        for i, feature in enumerate(top_features['Feature']):
            print(f"{i+1}. {feature}: {top_features['Importance'].iloc[i]:.4f}")
    
    # 使用SHAP值进行解释
    try:
        # 随机抽样以加速SHAP计算
        if X.shape[0] > shap_sample:
            shap_X = X.sample(shap_sample, random_state=42)
        else:
            shap_X = X
        
        # 创建SHAP解释器
        if hasattr(model, 'predict_proba'):
            explainer = shap.Explainer(model, shap_X)
            shap_values = explainer(shap_X)
            
            # 汇总图
            plt.figure(figsize=(10, 8))
            shap.summary_plot(shap_values, shap_X, show=False)
            plt.tight_layout()
            plt.savefig('credit_risk_shap_summary.png')
            
            # 依赖图（针对最重要的特征）
            if hasattr(model, 'feature_importances_'):
                most_important_feature = feature_names[indices[0]]
                plt.figure(figsize=(10, 6))
                shap.dependence_plot(most_important_feature, shap_values.values, shap_X, show=False)
                plt.tight_layout()
                plt.savefig('credit_risk_shap_dependence.png')
                
            print("\nSHAP值可视化已保存")
    except Exception as e:
        print(f"SHAP分析出错: {e}")
    
    return top_features if hasattr(model, 'feature_importances_') else None

def develop_risk_strategy(model, X, y, top_features=None):
    """
    基于模型结果制定风险控制策略
    """
    print("\n开始制定风险控制策略...")
    
    # 1. 获取预测概率
    if hasattr(model, 'predict_proba'):
        y_prob = model.predict_proba(X)[:, 1]
    else:
        print("模型不支持概率预测，无法完全制定风险策略")
        return
    
    # 2. 寻找最优阈值（根据不同策略）
    print("\n寻找不同业务策略下的最优阈值:")
    threshold_f1, _ = find_optimal_threshold(y, y_prob, strategy="f1")
    threshold_profit, _ = find_optimal_threshold(y, y_prob, strategy="profit")
    threshold_balanced, _ = find_optimal_threshold(y, y_prob, strategy="balanced")
    
    # 3. 创建风险分段
    print("\n将客户分为不同风险等级:")
    risk_segments, risk_stats = create_risk_segments(y_prob, n_segments=5)
    print(risk_stats)
    
    # 4. 制定分级风险策略
    risk_strategies = pd.DataFrame({
        "风险等级": risk_stats["风险等级"],
        "平均违约概率": risk_stats["平均违约概率"],
        "信用审批策略": ["自动拒绝", "严格审查", "人工审核", "自动批准但限额", "自动批准全额"],
        "信用额度比例": [0, 0.3, 0.6, 0.8, 1.0],
        "利率调整": ["+10%", "+5%", "+2%", "+0%", "-1%"],
        "风险监控频率": ["不适用", "每周", "每两周", "每月", "每季度"]
    })
    
    # 5. 保存策略建议文档
    strategy_report = """
# 信用卡风险控制策略报告

## 1. 风险评分阈值建议

根据不同业务目标，我们确定了以下决策阈值：

- **最大化F1分数阈值**: {:.4f}
  - 适用场景：平衡识别违约客户与避免拒绝好客户

- **最大化利润阈值**: {:.4f}
  - 适用场景：注重银行整体利润最大化

- **平衡阈值**: {:.4f}
  - 适用场景：平等对待违约识别与客户接受率

## 2. 客户风险分级策略

我们将客户分为5个风险等级，并制定了相应的风险控制策略：

{}

## 3. 关键风险因素

以下是影响信用违约的主要因素（按重要性排序）：

{}

## 4. 风险控制建议

1. **差异化信用额度**：
   - 根据客户风险等级设置不同的信用额度上限
   - 高风险客户（1-2级）：严格限制或拒绝信用
   - 中风险客户（3级）：提供较低的信用额度，并定期审核
   - 低风险客户（4-5级）：提供完整信用额度和优惠条件

2. **动态利率调整**：
   - 根据客户风险等级调整利率
   - 高风险客户：较高利率以补偿风险
   - 低风险客户：优惠利率以提高客户黏性

3. **行为监控与预警**：
   - 对高风险客户实施更频繁的交易监控
   - 建立行为预警体系，识别潜在违约迹象
   - 当风险指标超过阈值时，触发审核流程

4. **风险缓释措施**：
   - 对高风险客户可能要求提供担保或额外抵押
   - 实施分期付款限制，减少大额交易风险
   - 设置自动还款机制，降低逾期风险

5. **客户教育与沟通**：
   - 为高风险客户提供财务管理指导
   - 通过积极沟通，提高客户还款意愿
   - 提供债务管理工具和资源

## 5. 风险控制流程实施

1. **风险评分计算**：使用模型计算每位客户的违约概率
2. **风险分级**：根据违约概率将客户分入相应风险等级
3. **策略应用**：根据风险等级应用相应的信用策略
4. **持续监控**：定期重新评估客户风险状况
5. **策略优化**：根据实际表现调整风险控制参数
    """.format(
        threshold_f1, 
        threshold_profit, 
        threshold_balanced, 
        risk_strategies.to_string(index=False),
        "\n".join([f"{i+1}. {name} (重要度: {imp:.4f})" for i, (name, imp) in 
                 enumerate(zip(top_features['Feature'], top_features['Importance']))])
                 if top_features is not None else "特征重要性信息不可用"
    )
    
    # 保存策略报告
    with open("credit_risk_strategy_report.md", "w") as f:
        f.write(strategy_report)
    
    print("\n风险控制策略报告已生成：credit_risk_strategy_report.md")
    
    return {
        "thresholds": {
            "f1": threshold_f1,
            "profit": threshold_profit,
            "balanced": threshold_balanced
        },
        "risk_segments": risk_segments,
        "risk_stats": risk_stats,
        "risk_strategies": risk_strategies
    }

if __name__ == "__main__":
    # 加载最佳模型
    try:
        # 尝试加载随机森林模型（通常表现较好）
        model_path = Path(__file__).parent / "credit_risk_random_forest.pkl"
        if not model_path.exists():
            # 如果随机森林模型不存在，尝试加载其他模型
            model_files = list(Path(__file__).parent.glob("credit_risk_*.pkl"))
            if model_files:
                model_path = model_files[0]
            else:
                raise FileNotFoundError("找不到任何模型文件")
        
        print(f"加载模型: {model_path}")
        pipeline = joblib.load(model_path)
        model = pipeline.named_steps['model']
        
        # 加载处理后的数据集
        data_path = Path(__file__).parent / "credit_risk_final.csv"
        if data_path.exists():
            print(f"加载处理后的数据集: {data_path}")
            df = pd.read_csv(data_path)
        else:
            # 如果处理后的数据不存在，重新生成
            print("处理后的数据集不存在，重新处理数据...")
            df = load_credit_data()
            df_cleaned = data_cleaning(df)
            df_with_indicators = calculate_technical_indicators(df_cleaned)
            df, _, _ = extract_features(df_with_indicators)
        
        # 分离特征和标签
        X = df.drop('DEFAULT', axis=1)
        y = df['DEFAULT']
        
        # 分析特征重要性
        top_features = analyze_feature_importance(model, X)
        
        # 开发风险控制策略
        strategy_results = develop_risk_strategy(model, X, y, top_features)
        
        print("\n风险控制策略开发完成!")
        
    except Exception as e:
        print(f"错误: {e}")
        print("\n请先运行credit_risk_modeling.py训练和保存模型") 