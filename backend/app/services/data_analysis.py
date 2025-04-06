import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import warnings
from typing import Dict, List, Tuple, Optional, Any, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_classif, f_regression, RFE
from sklearn.decomposition import PCA
from sklearn.linear_model import Lasso, Ridge, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score
)
import matplotlib
from .docker_matplotlib_fix import configure_matplotlib_fonts

# 设置matplotlib字体，使用我们的配置函数
configure_matplotlib_fonts()

# 忽略警告
warnings.filterwarnings('ignore')

class DataAnalysisService:
    """数据分析工具服务，提供数据处理、特征工程和模型评估功能"""
    
    def __init__(self):
        """初始化数据分析服务"""
        pass
    
    # 1. 数据探索性分析
    def get_basic_stats(self, data: pd.DataFrame) -> Dict[str, Any]:
        """计算基本统计量
        
        Args:
            data: 输入数据
            
        Returns:
            包含基本统计量的字典
        """
        # 数值列统计
        numeric_cols = data.select_dtypes(include=['number']).columns
        numeric_stats = {}
        for col in numeric_cols:
            numeric_stats[col] = {
                'mean': data[col].mean(),
                'median': data[col].median(),
                'std': data[col].std(),
                'min': data[col].min(),
                'max': data[col].max(),
                'missing': data[col].isnull().sum()
            }
        
        # 分类列统计
        categorical_cols = data.select_dtypes(exclude=['number']).columns
        categorical_stats = {}
        for col in categorical_cols:
            value_counts = data[col].value_counts().to_dict()
            categorical_stats[col] = {
                'unique_values': len(value_counts),
                'most_common': data[col].value_counts().index[0] if not data[col].value_counts().empty else None,
                'missing': data[col].isnull().sum(),
                'value_counts': value_counts
            }
        
        # 整体统计
        overall_stats = {
            'rows': len(data),
            'columns': len(data.columns),
            'numeric_columns': len(numeric_cols),
            'categorical_columns': len(categorical_cols),
            'missing_values': data.isnull().sum().sum()
        }
        
        return {
            'overall': overall_stats,
            'numeric': numeric_stats,
            'categorical': categorical_stats
        }
    
    def correlation_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """计算相关性分析
        
        Args:
            data: 输入数据
            
        Returns:
            包含相关性分析结果的字典
        """
        # 只选择数值列
        numeric_data = data.select_dtypes(include=['number'])
        
        # 计算相关系数矩阵
        corr_matrix = numeric_data.corr().round(3)
        
        # 获取高相关特征对
        high_corr_features = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > 0.7:
                    high_corr_features.append({
                        'feature1': corr_matrix.columns[i],
                        'feature2': corr_matrix.columns[j],
                        'correlation': corr_matrix.iloc[i, j]
                    })
        
        # 获取与目标变量的相关性（如果提供）
        target_correlations = {}
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'high_correlation_pairs': high_corr_features
        }
    
    def generate_visualization(self, data: pd.DataFrame, viz_type: str, params: Dict[str, Any] = None) -> str:
        """生成数据可视化
        
        Args:
            data: 输入数据
            viz_type: 可视化类型，如 'histogram', 'boxplot', 'scatter', 等
            params: 可视化参数
            
        Returns:
            Base64编码的图像
        """
        if params is None:
            params = {}
        
        plt.figure(figsize=(10, 6))
        
        if viz_type == 'histogram':
            column = params.get('column')
            if column is None or column not in data.columns:
                return {"error": "必须提供有效的列名"}
            
            bins = params.get('bins', 30)
            sns.histplot(data[column], bins=bins, kde=params.get('kde', True))
            plt.title(f"{column} 的分布")
            plt.xlabel(column)
            plt.ylabel("频率")
            
        elif viz_type == 'boxplot':
            column = params.get('column')
            if column is None or column not in data.columns:
                return {"error": "必须提供有效的列名"}
            
            group_by = params.get('group_by')
            if group_by is not None and group_by in data.columns:
                sns.boxplot(x=group_by, y=column, data=data)
                plt.title(f"{column} 按 {group_by} 分组的箱线图")
            else:
                sns.boxplot(y=column, data=data)
                plt.title(f"{column} 的箱线图")
                
        elif viz_type == 'scatter':
            x = params.get('x')
            y = params.get('y')
            if x is None or x not in data.columns or y is None or y not in data.columns:
                return {"error": "必须提供有效的 x 和 y 列名"}
            
            hue = params.get('hue')
            if hue is not None and hue in data.columns:
                sns.scatterplot(x=x, y=y, hue=hue, data=data)
            else:
                sns.scatterplot(x=x, y=y, data=data)
            plt.title(f"{x} vs {y} 散点图")
            
        elif viz_type == 'correlation_heatmap':
            numeric_data = data.select_dtypes(include=['number'])
            sns.heatmap(numeric_data.corr(), annot=params.get('annot', True), cmap='coolwarm', vmin=-1, vmax=1)
            plt.title("相关性热力图")
            
        elif viz_type == 'pairplot':
            columns = params.get('columns', data.select_dtypes(include=['number']).columns[:5].tolist())
            hue = params.get('hue')
            plot_data = data[columns] if hue is None else data[columns + [hue]]
            sns.pairplot(plot_data, hue=hue)
            plt.suptitle("特征对图", y=1.02)
            
        elif viz_type == 'count':
            column = params.get('column')
            if column is None or column not in data.columns:
                return {"error": "必须提供有效的列名"}
            
            sns.countplot(y=column, data=data, order=data[column].value_counts().index)
            plt.title(f"{column} 的计数")
            
        else:
            return {"error": f"不支持的可视化类型: {viz_type}"}
        
        # 保存图像到内存
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # 转换为base64字符串
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return img_str
    
    # 2. 数据清洗和集成
    def handle_missing_values(self, data: pd.DataFrame, strategy: Dict[str, str]) -> pd.DataFrame:
        """处理缺失值
        
        Args:
            data: 输入数据
            strategy: 处理策略，格式为 {列名: 策略}，
                     策略可以是 'mean', 'median', 'most_frequent', 'constant:值'
            
        Returns:
            处理后的DataFrame
        """
        df = data.copy()
        
        for column, method in strategy.items():
            if column not in df.columns:
                continue
                
            # 检查列类型并选择合适的填充方法
            if method.startswith('constant:'):
                # 提取常量值
                constant_value = method.split(':', 1)[1]
                df[column] = df[column].fillna(constant_value)
                
            elif df[column].dtype.kind in 'ifc':  # 数值型列
                if method == 'drop':
                    df = df.dropna(subset=[column])
                elif method == 'mean':
                    df[column] = df[column].fillna(df[column].mean())
                elif method == 'median':
                    df[column] = df[column].fillna(df[column].median())
                elif method == 'most_frequent':
                    df[column] = df[column].fillna(df[column].mode()[0])
                    
            else:  # 类别型列
                if method == 'drop':
                    df = df.dropna(subset=[column])
                elif method == 'most_frequent':
                    df[column] = df[column].fillna(df[column].mode()[0])
                elif method == 'new_category':
                    df[column] = df[column].fillna('未知')
        
        return df
    
    def remove_duplicates(self, data: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
        """去除重复值
        
        Args:
            data: 输入数据
            subset: 用于判断重复的列，默认使用所有列
            
        Returns:
            去重后的DataFrame
        """
        return data.drop_duplicates(subset=subset)
    
    def detect_outliers(self, data: pd.DataFrame, method: str = 'zscore', threshold: float = 3.0) -> Dict[str, List[int]]:
        """检测异常值
        
        Args:
            data: 输入数据
            method: 检测方法，可以是 'zscore', 'iqr'
            threshold: 阈值
            
        Returns:
            包含异常值索引的字典，格式为 {列名: [异常值索引列表]}
        """
        # 仅处理数值型列
        numeric_cols = data.select_dtypes(include=['number']).columns
        outliers_dict = {}
        
        for col in numeric_cols:
            outliers = []
            
            if method == 'zscore':
                # Z-score方法
                z_scores = (data[col] - data[col].mean()) / data[col].std()
                outliers = data.index[abs(z_scores) > threshold].tolist()
                
            elif method == 'iqr':
                # IQR方法
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = data.index[(data[col] < Q1 - threshold * IQR) | (data[col] > Q3 + threshold * IQR)].tolist()
            
            if outliers:
                outliers_dict[col] = outliers
        
        return outliers_dict
    
    def handle_outliers(self, data: pd.DataFrame, outliers_dict: Dict[str, List[int]], method: str = 'clip') -> pd.DataFrame:
        """处理异常值
        
        Args:
            data: 输入数据
            outliers_dict: 包含异常值索引的字典，格式为 {列名: [异常值索引列表]}
            method: 处理方法，可以是 'clip', 'remove', 'replace'
            
        Returns:
            处理后的DataFrame
        """
        df = data.copy()
        
        for col, indices in outliers_dict.items():
            if col not in df.columns:
                continue
                
            if method == 'clip':
                # 使用分位数剪裁
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                df.loc[indices, col] = df.loc[indices, col].clip(lower=Q1 - 1.5 * IQR, upper=Q3 + 1.5 * IQR)
                
            elif method == 'remove':
                # 移除异常值
                df = df.drop(indices)
                
            elif method == 'replace':
                # 用中位数替换
                df.loc[indices, col] = df[col].median()
        
        return df
    
    def normalize_data(self, data: pd.DataFrame, method: str = 'zscore', columns: List[str] = None) -> pd.DataFrame:
        """数据规范化
        
        Args:
            data: 输入数据
            method: 规范化方法，可以是 'zscore', 'minmax', 'robust'
            columns: 需要规范化的列，默认为所有数值列
            
        Returns:
            规范化后的DataFrame
        """
        df = data.copy()
        
        # 如果未指定列，使用所有数值列
        if columns is None:
            columns = df.select_dtypes(include=['number']).columns.tolist()
        
        # 仅选择存在的列
        columns = [col for col in columns if col in df.columns]
        
        if method == 'zscore':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        elif method == 'robust':
            scaler = RobustScaler()
        else:
            raise ValueError(f"不支持的规范化方法: {method}")
        
        # 应用规范化
        if columns:
            df[columns] = scaler.fit_transform(df[columns])
        
        return df
    
    # 3. 特征工程
    def encode_categorical_features(self, data: pd.DataFrame, method: str = 'onehot', columns: List[str] = None) -> pd.DataFrame:
        """对分类特征进行编码
        
        Args:
            data: 输入数据
            method: 编码方法，可以是 'onehot', 'label'
            columns: 需要编码的列，默认为所有非数值列
            
        Returns:
            编码后的DataFrame
        """
        df = data.copy()
        
        # 如果未指定列，使用所有分类列
        if columns is None:
            columns = df.select_dtypes(exclude=['number']).columns.tolist()
        
        # 仅选择存在的列
        columns = [col for col in columns if col in df.columns]
        
        if method == 'onehot':
            # One-hot编码
            for col in columns:
                # 创建虚拟变量，保留原始列
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=False)
                df = pd.concat([df, dummies], axis=1)
            
            # 删除原始列
            df = df.drop(columns=columns)
            
        elif method == 'label':
            # 标签编码
            encoder = LabelEncoder()
            for col in columns:
                df[col] = encoder.fit_transform(df[col].astype(str))
        
        return df
    
    def bin_numeric_features(self, data: pd.DataFrame, columns: Dict[str, int]) -> pd.DataFrame:
        """对数值特征进行分箱
        
        Args:
            data: 输入数据
            columns: 分箱配置，格式为 {列名: 箱数}
            
        Returns:
            分箱后的DataFrame
        """
        df = data.copy()
        
        for col, bins in columns.items():
            if col in df.columns and df[col].dtype.kind in 'ifc':
                # 创建分箱特征，并保留原始特征
                df[f"{col}_binned"] = pd.cut(df[col], bins=bins, labels=False)
        
        return df
    
    def extract_features_with_pca(self, data: pd.DataFrame, n_components: int = 2, columns: List[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """使用PCA提取特征
        
        Args:
            data: 输入数据
            n_components: 主成分数量
            columns: 用于PCA的列，默认为所有数值列
            
        Returns:
            (带有PCA特征的DataFrame, PCA结果信息)
        """
        df = data.copy()
        
        # 如果未指定列，使用所有数值列
        if columns is None:
            columns = df.select_dtypes(include=['number']).columns.tolist()
        
        # 仅选择存在的列
        columns = [col for col in columns if col in df.columns]
        
        if len(columns) < n_components:
            raise ValueError(f"特征数量({len(columns)})必须大于或等于主成分数量({n_components})")
        
        # 标准化数据
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df[columns])
        
        # 应用PCA
        pca = PCA(n_components=n_components)
        pca_result = pca.fit_transform(scaled_data)
        
        # 将PCA结果添加到数据框
        for i in range(n_components):
            df[f'PCA_{i+1}'] = pca_result[:, i]
        
        # 准备PCA信息
        explained_variance_ratio = pca.explained_variance_ratio_
        cumulative_explained_variance = np.cumsum(explained_variance_ratio)
        loadings = pca.components_
        
        pca_info = {
            'explained_variance_ratio': explained_variance_ratio.tolist(),
            'cumulative_explained_variance': cumulative_explained_variance.tolist(),
            'loadings': {columns[i]: loadings[:, i].tolist() for i in range(len(columns))}
        }
        
        return df, pca_info
    
    def select_features(self, data: pd.DataFrame, target: str, method: str = 'kbest', k: int = 5) -> Tuple[List[str], Dict[str, float]]:
        """特征选择
        
        Args:
            data: 输入数据
            target: 目标变量
            method: 特征选择方法，可以是 'kbest', 'rfe', 'lasso', 'ridge'
            k: 选择的特征数量
            
        Returns:
            (所选特征列表, 特征重要性分数)
        """
        # 准备特征和目标
        if target not in data.columns:
            raise ValueError(f"目标变量 {target} 不在数据集中")
            
        X = data.drop(target, axis=1)
        y = data[target]
        
        # 仅选择数值特征
        numeric_cols = X.select_dtypes(include=['number']).columns
        X = X[numeric_cols]
        
        # 目标类型决定是分类还是回归
        is_classification = y.dtype == 'bool' or y.nunique() <= 10
        
        feature_scores = {}
        selected_features = []
        
        if method == 'kbest':
            # 使用KBest选择特征
            if is_classification:
                selector = SelectKBest(f_classif, k=min(k, len(numeric_cols)))
            else:
                selector = SelectKBest(f_regression, k=min(k, len(numeric_cols)))
                
            selector.fit(X, y)
            selected_mask = selector.get_support()
            
            selected_features = X.columns[selected_mask].tolist()
            feature_scores = {col: score for col, score in zip(X.columns, selector.scores_)}
            
        elif method == 'rfe':
            # 使用递归特征消除
            if is_classification:
                estimator = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                estimator = RandomForestRegressor(n_estimators=100, random_state=42)
                
            selector = RFE(estimator, n_features_to_select=min(k, len(numeric_cols)), step=1)
            selector.fit(X, y)
            
            selected_features = X.columns[selector.support_].tolist()
            feature_scores = {col: rank for col, rank in zip(X.columns, selector.ranking_)}
            
        elif method == 'lasso':
            # 使用Lasso正则化
            selector = Lasso(alpha=0.1)
            selector.fit(X, y)
            
            # 获取系数作为特征重要性
            feature_scores = {col: abs(coef) for col, coef in zip(X.columns, selector.coef_)}
            
            # 选择系数非零的前k个特征
            selected_features = [col for col, score in sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)[:k]]
            
        elif method == 'ridge':
            # 使用Ridge正则化
            selector = Ridge(alpha=1.0)
            selector.fit(X, y)
            
            # 获取系数作为特征重要性
            feature_scores = {col: abs(coef) for col, coef in zip(X.columns, selector.coef_)}
            
            # 选择最重要的前k个特征
            selected_features = [col for col, score in sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)[:k]]
        
        return selected_features, feature_scores
    
    # 4. 模型评估
    def evaluate_classification_model(self, y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, float]:
        """评估分类模型
        
        Args:
            y_true: 真实标签
            y_pred: 预测标签
            y_prob: 预测概率（如果可用）
            
        Returns:
            包含评估指标的字典
        """
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted'),
            'recall': recall_score(y_true, y_pred, average='weighted'),
            'f1': f1_score(y_true, y_pred, average='weighted')
        }
        
        # 如果提供了概率预测，计算ROC AUC
        if y_prob is not None:
            # 多类别问题，需要确保y_prob形状正确，此处简化处理
            if len(y_prob.shape) == 2 and y_prob.shape[1] > 1:
                # 多类别，使用OvR策略
                metrics['roc_auc'] = roc_auc_score(y_true, y_prob, multi_class='ovr')
            else:
                # 二分类
                metrics['roc_auc'] = roc_auc_score(y_true, y_prob)
        
        return metrics
    
    def evaluate_regression_model(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """评估回归模型
        
        Args:
            y_true: 真实值
            y_pred: 预测值
            
        Returns:
            包含评估指标的字典
        """
        metrics = {
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred)
        }
        
        return metrics

# 创建服务实例
data_analysis_service = DataAnalysisService()