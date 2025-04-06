import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple, Optional, Any
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

class BankAnalysisService:
    """银行信贷分析服务，提供信贷风险控制和违约分析功能"""
    
    def __init__(self, data_dir: str = "./data"):
        """初始化银行分析服务
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # 预训练模型
        self.models = {}
    
    def load_credit_data(self, dataset: str = "taiwan_credit") -> pd.DataFrame:
        """加载信用卡客户数据
        
        Args:
            dataset: 数据集名称，默认为 "taiwan_credit"
            
        Returns:
            信用卡客户数据 DataFrame
        """
        # 检查本地是否有缓存
        cache_file = os.path.join(self.data_dir, f"{dataset}.csv")
        
        if os.path.exists(cache_file):
            return pd.read_csv(cache_file)
        
        # 否则生成模拟数据
        df = self._generate_mock_credit_data(10000)
        
        # 保存到缓存
        df.to_csv(cache_file, index=False)
        
        return df
    
    def _generate_mock_credit_data(self, n_samples: int) -> pd.DataFrame:
        """生成模拟信用卡数据
        
        Args:
            n_samples: 样本数量
            
        Returns:
            模拟的信用卡数据 DataFrame
        """
        np.random.seed(42)
        
        # 创建特征
        data = {
            'LIMIT_BAL': np.random.randint(10000, 1000000, n_samples),
            'AGE': np.random.randint(20, 80, n_samples),
            'EDUCATION': np.random.randint(1, 5, n_samples),
            'MARRIAGE': np.random.randint(1, 4, n_samples),
            'SEX': np.random.randint(1, 3, n_samples),
            'PAY_1': np.random.randint(-2, 10, n_samples),
            'PAY_2': np.random.randint(-2, 10, n_samples),
            'PAY_3': np.random.randint(-2, 10, n_samples),
            'PAY_4': np.random.randint(-2, 10, n_samples),
            'PAY_5': np.random.randint(-2, 10, n_samples),
            'PAY_6': np.random.randint(-2, 10, n_samples),
            'BILL_AMT1': np.random.randint(-100000, 1000000, n_samples),
            'BILL_AMT2': np.random.randint(-100000, 1000000, n_samples),
            'BILL_AMT3': np.random.randint(-100000, 1000000, n_samples),
            'BILL_AMT4': np.random.randint(-100000, 1000000, n_samples),
            'BILL_AMT5': np.random.randint(-100000, 1000000, n_samples),
            'BILL_AMT6': np.random.randint(-100000, 1000000, n_samples),
            'PAY_AMT1': np.random.randint(0, 100000, n_samples),
            'PAY_AMT2': np.random.randint(0, 100000, n_samples),
            'PAY_AMT3': np.random.randint(0, 100000, n_samples),
            'PAY_AMT4': np.random.randint(0, 100000, n_samples),
            'PAY_AMT5': np.random.randint(0, 100000, n_samples),
            'PAY_AMT6': np.random.randint(0, 100000, n_samples),
        }
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 生成目标变量 - 违约概率与PAY_X、BILL_AMT和额度的关系
        probs = (df['PAY_1'] + df['PAY_2'] + df['PAY_3']) / 30.0
        probs += (df['BILL_AMT1'] / df['LIMIT_BAL']) * 0.2
        probs = 1 / (1 + np.exp(-probs))  # Sigmoid函数
        probs = np.clip(probs, 0.01, 0.99)  # 裁剪到合理范围
        
        # 生成二元目标变量
        df['DEFAULT'] = np.random.binomial(1, probs)
        
        return df
    
    def split_data(self, data: pd.DataFrame, target: str = 'DEFAULT', test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """将数据分为训练集和测试集
        
        Args:
            data: 数据
            target: 目标变量列名
            test_size: 测试集比例
            
        Returns:
            训练特征，测试特征，训练标签，测试标签
        """
        X = data.drop(target, axis=1)
        y = data[target]
        return train_test_split(X, y, test_size=test_size, random_state=42)
    
    def train_credit_default_model(self, data: pd.DataFrame, model_type: str = "random_forest") -> Dict[str, Any]:
        """训练信用卡违约预测模型
        
        Args:
            data: 数据
            model_type: 模型类型，支持 "random_forest" 和 "logistic_regression"
            
        Returns:
            包含模型训练结果的字典
        """
        # 分割数据
        X_train, X_test, y_train, y_test = self.split_data(data)
        
        # 定义预处理步骤
        numeric_features = X_train.select_dtypes(include=['int64', 'float64']).columns
        categorical_features = X_train.select_dtypes(include=['object']).columns
        
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features)
            ]
        )
        
        # 选择模型
        if model_type == "random_forest":
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            model = LogisticRegression(random_state=42, max_iter=1000)
        
        # 创建并训练管道
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('model', model)
        ])
        
        pipeline.fit(X_train, y_train)
        
        # 预测
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]
        
        # 评估模型
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_prob),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
        
        # 保存模型
        self.models[model_type] = pipeline
        
        return {
            'model_type': model_type,
            'metrics': metrics,
            'feature_importance': self._get_feature_importance(pipeline, X_train.columns),
            'test_predictions': y_prob.tolist()[:10]  # 返回前10个预测样本的概率
        }
    
    def _get_feature_importance(self, pipeline, feature_names):
        """获取特征重要性
        
        Args:
            pipeline: 训练好的模型管道
            feature_names: 特征名称
            
        Returns:
            特征重要性字典
        """
        model = pipeline.named_steps['model']
        
        if hasattr(model, 'feature_importances_'):
            # 对于随机森林等基于树的模型
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            # 对于线性模型
            importances = np.abs(model.coef_[0])
        else:
            return {}
        
        # 返回前10个最重要的特征
        indices = np.argsort(importances)[::-1][:10]
        return {str(feature_names[i]): float(importances[i]) for i in indices}
    
    def predict_default_probability(self, customer_data: Dict[str, Any], model_type: str = "random_forest") -> Dict[str, Any]:
        """预测客户违约概率
        
        Args:
            customer_data: 客户数据字典
            model_type: 模型类型
            
        Returns:
            包含预测结果的字典
        """
        if model_type not in self.models:
            raise ValueError(f"Model {model_type} not trained. Call train_credit_default_model first.")
        
        # 将输入转换为DataFrame
        df = pd.DataFrame([customer_data])
        
        # 预测
        pipeline = self.models[model_type]
        prob = pipeline.predict_proba(df)[0, 1]
        prediction = 1 if prob >= 0.5 else 0
        
        return {
            'customer_id': customer_data.get('id', 'unknown'),
            'default_probability': float(prob),
            'predicted_default': int(prediction),
            'risk_level': self._get_risk_level(prob)
        }
    
    def _get_risk_level(self, probability: float) -> str:
        """根据违约概率确定风险等级
        
        Args:
            probability: 违约概率
            
        Returns:
            风险等级
        """
        if probability < 0.2:
            return "低风险"
        elif probability < 0.4:
            return "中低风险"
        elif probability < 0.6:
            return "中风险"
        elif probability < 0.8:
            return "中高风险"
        else:
            return "高风险"
    
    def analyze_credit_factors(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析影响信用评分的因素
        
        Args:
            data: 信用卡数据
            
        Returns:
            包含分析结果的字典
        """
        # 计算各个特征与违约的相关性
        corr = data.corr()['DEFAULT'].sort_values(ascending=False)
        
        # 计算各个特征的统计信息
        stats = {}
        for col in data.columns:
            if col != 'DEFAULT':
                stats[col] = {
                    'mean': data[col].mean(),
                    'median': data[col].median(),
                    'std': data[col].std(),
                    'min': data[col].min(),
                    'max': data[col].max()
                }
        
        # 计算违约与非违约客户的特征差异
        default_data = data[data['DEFAULT'] == 1]
        non_default_data = data[data['DEFAULT'] == 0]
        
        diff = {}
        for col in data.columns:
            if col != 'DEFAULT':
                diff[col] = {
                    'default_mean': default_data[col].mean(),
                    'non_default_mean': non_default_data[col].mean(),
                    'diff_percentage': (default_data[col].mean() - non_default_data[col].mean()) / non_default_data[col].mean() * 100 if non_default_data[col].mean() != 0 else 0
                }
        
        return {
            'correlations': {k: v for k, v in corr.items() if k != 'DEFAULT'},
            'statistics': stats,
            'group_differences': diff
        }

# 创建服务实例
bank_service = BankAnalysisService() 