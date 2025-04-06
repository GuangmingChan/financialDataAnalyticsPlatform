import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import Lasso
from pathlib import Path

from credit_risk_exploration import load_credit_data
from credit_risk_cleaning import data_cleaning
import matplotlib as mpl
mpl.rcParams['font.family'] = 'DejaVu Sans'

def calculate_technical_indicators(df):
    """
    计算技术指标
    虽然MACD、RSI、OBV通常用于时间序列分析，这里我们将其应用于信用卡特征中
    """
    print("开始计算技术指标...")
    
    df_features = df.copy()
    
    # 提取时间顺序的账单和支付金额
    bill_cols = ['BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6']
    pay_cols = ['PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6']
    
    # 1. 计算MACD（指数平滑异同平均线）
    print("计算MACD指标...")
    
    # 短期和长期指数移动平均值
    for i, col in enumerate(bill_cols):
        # 只能为每个客户计算一个MACD值，而不是时间序列
        # 这里我们用短期(近期)和长期(远期)账单的EMA代替
        if i < 3:  # 用前3个月作为短期
            df_features[f'EMA_short_{i+1}'] = df[bill_cols[i]]
        else:  # 用后3个月作为长期
            df_features[f'EMA_long_{i-2}'] = df[bill_cols[i]]
    
    # 计算MACD值
    for i in range(1, 4):
        df_features[f'MACD_{i}'] = df_features[f'EMA_short_{i}'] - df_features[f'EMA_long_{i}']
    
    # 2. 计算RSI（相对强弱指标）
    print("计算RSI指标...")
    
    # 计算账单变化
    for i in range(len(bill_cols)-1):
        df_features[f'bill_change_{i+1}'] = df[bill_cols[i]] - df[bill_cols[i+1]]
    
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
    
    # 3. 计算OBV（能量潮指标）
    print("计算OBV指标...")
    
    # 初始化OBV为第一个月的账单金额
    df_features['OBV'] = df['BILL_AMT1']
    
    # 计算OBV
    for i in range(1, len(bill_cols)):
        # 如果账单增加，OBV加上支付金额；如果账单减少，OBV减去支付金额
        df_features['OBV'] += np.where(df[bill_cols[i-1]] > df[bill_cols[i]], 
                                     df[pay_cols[i-1]], 
                                     -df[pay_cols[i-1]])
    
    # 移除中间计算列
    drop_cols = [col for col in df_features.columns if any(x in col for x in ['EMA_', 'bill_change_', 'positive_change_', 'negative_change_'])]
    df_features.drop(columns=drop_cols, inplace=True)
    
    print("技术指标计算完成！")
    
    return df_features

def extract_features(df, n_components=10, alpha=0.01):
    """
    使用PCA和Lasso进行特征提取
    """
    print("\n开始特征提取...")
    
    # 分离特征和标签
    X = df.drop('DEFAULT', axis=1)
    y = df['DEFAULT']
    
    # 1. PCA降维
    print("执行PCA降维...")
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X)
    
    explained_variance = pca.explained_variance_ratio_
    cumulative_variance = np.cumsum(explained_variance)
    
    print(f"使用{n_components}个主成分，解释的总方差比例: {cumulative_variance[-1]:.4f}")
    
    # 将PCA结果转换回DataFrame
    pca_cols = [f'PC{i+1}' for i in range(n_components)]
    X_pca_df = pd.DataFrame(X_pca, columns=pca_cols)
    
    # 可视化PCA主成分贡献
    plt.figure(figsize=(10, 6))
    plt.bar(range(1, n_components+1), explained_variance)
    plt.plot(range(1, n_components+1), cumulative_variance, 'r-')
    plt.xlabel('主成分')
    plt.ylabel('解释方差比例')
    plt.title('PCA主成分解释方差')
    plt.savefig('credit_risk_pca.png')
    
    # 2. Lasso特征选择
    print("\n执行Lasso特征选择...")
    lasso = Lasso(alpha=alpha)
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
    plt.savefig('credit_risk_lasso_importance.png')
    
    # 3. 组合PCA和原始特征
    X_selected = X[selected_features]
    X_combined = pd.concat([X_selected, X_pca_df], axis=1)
    
    # 将标签加回
    final_df = pd.concat([X_combined, y], axis=1)
    
    print("\n特征提取完成！")
    print(f"原始特征数: {X.shape[1]}")
    print(f"Lasso选择的特征数: {len(selected_features)}")
    print(f"PCA主成分数: {n_components}")
    print(f"最终特征数: {X_combined.shape[1]}")
    
    return final_df, selected_features, pca_cols

if __name__ == "__main__":
    # 加载原始数据
    df = load_credit_data()
    
    # 数据清洗
    df_cleaned = data_cleaning(df)
    
    # 计算技术指标
    df_with_indicators = calculate_technical_indicators(df_cleaned)
    
    # 特征提取
    df_final, selected_features, pca_cols = extract_features(df_with_indicators)
    
    print("\n最终数据集预览:")
    print(df_final.head())
    
    # 保存处理后的数据
    output_path = Path(__file__).parent / "credit_risk_processed.csv"
    df_final.to_csv(output_path, index=False)
    print(f"\n处理后的数据已保存至: {output_path}") 