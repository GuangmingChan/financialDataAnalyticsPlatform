import os
import argparse
from pathlib import Path
import time

from credit_risk_exploration import load_credit_data, exploratory_analysis
from credit_risk_cleaning import data_cleaning
from credit_risk_feature_engineering import calculate_technical_indicators, extract_features
from credit_risk_modeling import train_credit_risk_model, evaluate_multiple_models
from credit_risk_strategy import analyze_feature_importance, develop_risk_strategy
import matplotlib as mpl
from app.services.docker_matplotlib_fix import configure_matplotlib_fonts

# 配置字体以支持中文显示
configure_matplotlib_fonts()

def create_output_dir():
    """创建输出目录"""
    output_dir = Path(__file__).parent / "output"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def run_full_workflow(args):
    """运行完整的信用卡违约风险分析流程"""
    start_time = time.time()
    
    print("\n" + "="*50)
    print("信用卡风险控制分析流程")
    print("="*50)
    
    # 创建输出目录
    output_dir = create_output_dir()
    os.chdir(output_dir)
    print(f"输出文件将保存至: {output_dir}")
    
    # 第1步：数据探索
    print("\n" + "="*50)
    print("步骤1: 数据探索")
    print("="*50)
    df = load_credit_data()
    results = exploratory_analysis(df)
    
    # 第2步：数据清洗
    print("\n" + "="*50)
    print("步骤2: 数据清洗")
    print("="*50)
    df_cleaned = data_cleaning(df)
    
    # 第3步：特征工程
    print("\n" + "="*50)
    print("步骤3: 特征工程")
    print("="*50)
    df_with_indicators = calculate_technical_indicators(df_cleaned)
    df_final, selected_features, pca_cols = extract_features(df_with_indicators, 
                                                        n_components=args.pca_components,
                                                        alpha=args.lasso_alpha)
    
    # 保存处理后的数据集
    processed_data_path = Path(__file__).parent / "output" / "credit_risk_processed.csv"
    df_final.to_csv(processed_data_path, index=False)
    print(f"\n处理后的数据已保存至: {processed_data_path}")
    
    # 第4步：模型训练
    print("\n" + "="*50)
    print("步骤4: 模型训练")
    print("="*50)
    
    if args.all_models:
        # 评估多个模型
        model_results = evaluate_multiple_models(df_final)
        
        # 选择性能最佳的模型（以ROC AUC为标准）
        best_model_name = max(model_results.items(), key=lambda x: x[1]['roc_auc'])[0]
        print(f"\n根据ROC AUC指标，性能最佳的模型是: {best_model_name}")
        
        # 加载最佳模型
        from joblib import load
        best_model_path = Path(__file__).parent / "output" / f"credit_risk_{best_model_name}.pkl"
        pipeline = load(best_model_path)
    else:
        # 只训练指定模型
        pipeline, _ = train_credit_risk_model(df_final, 
                                          model_type=args.model,
                                          balance_data=args.balance_data)
    
    # 第5步：风险控制策略制定
    print("\n" + "="*50)
    print("步骤5: 风险控制策略开发")
    print("="*50)
    
    # 提取模型
    model = pipeline.named_steps['model']
    
    # 分离特征和标签
    X = df_final.drop('DEFAULT', axis=1)
    y = df_final['DEFAULT']
    
    # 分析特征重要性
    top_features = analyze_feature_importance(model, X)
    
    # 开发风险控制策略
    strategy_results = develop_risk_strategy(model, X, y, top_features)
    
    # 计算总耗时
    total_time = time.time() - start_time
    print(f"\n完整分析流程完成！总耗时: {total_time:.2f} 秒 ({total_time/60:.2f} 分钟)")
    print(f"所有输出文件已保存至: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='信用卡风险控制分析工具')
    
    parser.add_argument('--model', type=str, default='random_forest',
                       choices=['logistic_regression', 'random_forest', 'gradient_boosting'],
                       help='指定要训练的模型类型')
    
    parser.add_argument('--all-models', action='store_true',
                       help='是否训练和评估所有模型')
    
    parser.add_argument('--balance-data', action='store_true',
                       help='是否使用SMOTE处理类别不平衡')
    
    parser.add_argument('--pca-components', type=int, default=10,
                       help='PCA降维时保留的主成分数量')
    
    parser.add_argument('--lasso-alpha', type=float, default=0.01,
                       help='Lasso特征选择的正则化参数')
    
    args = parser.parse_args()
    
    run_full_workflow(args)

if __name__ == "__main__":
    main() 