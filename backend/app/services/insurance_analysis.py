import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple, Optional, Any
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.cluster import KMeans

class InsuranceAnalysisService:
    """保险分析服务，提供车险索赔率和医疗保险营销分析功能"""
    
    def __init__(self, data_dir: str = "./data"):
        """初始化保险分析服务
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # 预训练模型
        self.models = {}
    
    def load_car_insurance_data(self) -> pd.DataFrame:
        """加载车险数据
        
        Returns:
            车险数据 DataFrame
        """
        # 检查本地是否有缓存
        cache_file = os.path.join(self.data_dir, "car_insurance.csv")
        
        if os.path.exists(cache_file):
            return pd.read_csv(cache_file)
        
        # 否则生成模拟数据
        df = self._generate_mock_car_insurance_data(5000)
        
        # 保存到缓存
        df.to_csv(cache_file, index=False)
        
        return df
    
    def _generate_mock_car_insurance_data(self, n_samples: int) -> pd.DataFrame:
        """生成模拟车险数据
        
        Args:
            n_samples: 样本数量
            
        Returns:
            模拟的车险数据 DataFrame
        """
        np.random.seed(42)
        
        # 创建特征
        data = {
            'age': np.random.randint(18, 80, n_samples),
            'gender': np.random.choice(['male', 'female'], n_samples),
            'driving_experience': np.random.randint(0, 50, n_samples),
            'car_age': np.random.randint(0, 20, n_samples),
            'car_value': np.random.randint(5000, 100000, n_samples),
            'car_category': np.random.choice(['sedan', 'SUV', 'truck', 'sports'], n_samples),
            'annual_mileage': np.random.randint(1000, 50000, n_samples),
            'traffic_violations': np.random.poisson(0.5, n_samples),
            'previous_accidents': np.random.poisson(0.3, n_samples),
            'urban_driving_percent': np.random.randint(0, 100, n_samples),
            'night_driving_percent': np.random.randint(0, 100, n_samples),
            'credit_score': np.random.randint(300, 850, n_samples),
            'married': np.random.choice([0, 1], n_samples),
            'children': np.random.poisson(1, n_samples),
            'has_garage': np.random.choice([0, 1], n_samples),
            'education_level': np.random.choice(['high_school', 'bachelors', 'masters', 'phd'], n_samples),
            'income_level': np.random.randint(20000, 200000, n_samples),
        }
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 生成索赔率 - 与年龄、驾驶经验、交通违规、之前事故等相关
        claim_rate = 0.05
        claim_rate += (50 - df['age']) / 500  # 年龄越小，索赔率越高
        claim_rate += (10 - df['driving_experience']) / 200  # 驾驶经验越少，索赔率越高
        claim_rate += df['traffic_violations'] * 0.02  # 交通违规次数越多，索赔率越高
        claim_rate += df['previous_accidents'] * 0.03  # 之前事故次数越多，索赔率越高
        claim_rate += df['night_driving_percent'] / 1000  # 夜间驾驶比例越高，索赔率越高
        
        # 确保索赔率在合理范围内
        claim_rate = np.clip(claim_rate, 0.01, 0.5)
        
        # 生成索赔金额
        claim_amount = np.zeros(n_samples)
        claims = np.random.binomial(1, claim_rate)
        claim_amount[claims == 1] = np.random.gamma(2, 2000, size=sum(claims))
        
        df['claim_occurred'] = claims
        df['claim_amount'] = claim_amount
        
        return df
    
    def load_health_insurance_data(self) -> pd.DataFrame:
        """加载医疗保险数据
        
        Returns:
            医疗保险数据 DataFrame
        """
        # 检查本地是否有缓存
        cache_file = os.path.join(self.data_dir, "health_insurance.csv")
        
        if os.path.exists(cache_file):
            return pd.read_csv(cache_file)
        
        # 否则生成模拟数据
        df = self._generate_mock_health_insurance_data(8000)
        
        # 保存到缓存
        df.to_csv(cache_file, index=False)
        
        return df
    
    def _generate_mock_health_insurance_data(self, n_samples: int) -> pd.DataFrame:
        """生成模拟医疗保险数据
        
        Args:
            n_samples: 样本数量
            
        Returns:
            模拟的医疗保险数据 DataFrame
        """
        np.random.seed(42)
        
        # 创建特征
        data = {
            'age': np.random.randint(18, 80, n_samples),
            'gender': np.random.choice(['male', 'female'], n_samples),
            'bmi': np.random.normal(26, 5, n_samples),
            'children': np.random.poisson(1, n_samples),
            'smoker': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
            'region': np.random.choice(['northeast', 'northwest', 'southeast', 'southwest'], n_samples),
            'income': np.random.normal(50000, 20000, n_samples),
            'employment_status': np.random.choice(['employed', 'self-employed', 'unemployed', 'retired'], n_samples),
            'exercise_frequency': np.random.choice(['never', 'rarely', 'sometimes', 'regularly'], n_samples),
            'alcohol_consumption': np.random.choice(['none', 'light', 'moderate', 'heavy'], n_samples),
            'chronic_disease': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
            'family_history': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
            'past_claims': np.random.poisson(1, n_samples),
            'coverage_level': np.random.choice(['basic', 'standard', 'premium'], n_samples),
            'deductible': np.random.choice([500, 1000, 1500, 2000], n_samples),
            'has_dental': np.random.choice([0, 1], n_samples),
            'has_vision': np.random.choice([0, 1], n_samples),
        }
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 固定BMI范围
        df['bmi'] = np.clip(df['bmi'], 15, 45)
        
        # 固定收入范围
        df['income'] = np.clip(df['income'], 10000, 150000)
        
        # 生成保费
        df['premium'] = 5000
        df['premium'] += df['age'] * 50  # 年龄越大，保费越高
        df['premium'] += (df['bmi'] - 25) * 200  # BMI偏离正常值，保费越高
        df['premium'] += df['children'] * 500  # 孩子越多，保费越高
        df['premium'] += df['smoker'] * 5000  # 吸烟者保费大幅增加
        df['premium'] += df['chronic_disease'] * 3000  # 慢性病患者保费增加
        df['premium'] += df['past_claims'] * 1000  # 过去理赔次数增加保费
        
        # 添加一些随机波动
        df['premium'] *= np.random.normal(1, 0.1, n_samples)
        
        # 确保保费在合理范围内
        df['premium'] = np.clip(df['premium'], 1000, 20000)
        df['premium'] = np.round(df['premium'], -2)  # 取整到百位
        
        # 生成购买标志
        purchase_prob = 0.5
        purchase_prob -= df['premium'] / 50000  # 保费越高，购买概率越低
        purchase_prob += df['age'] / 200  # 年龄越大，购买概率略高
        purchase_prob += df['chronic_disease'] * 0.1  # 有慢性病，购买概率高
        purchase_prob += df['family_history'] * 0.05  # 有家族病史，购买概率高
        
        # 确保概率在合理范围内
        purchase_prob = np.clip(purchase_prob, 0.1, 0.9)
        
        df['purchased'] = np.random.binomial(1, purchase_prob)
        
        return df
    
    def analyze_car_insurance_claims(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析车险索赔影响因素
        
        Args:
            data: 车险数据
            
        Returns:
            包含分析结果的字典
        """
        # 计算总体索赔率
        total_claim_rate = data['claim_occurred'].mean()
        
        # 按不同特征分组分析索赔率
        age_groups = pd.cut(data['age'], bins=[18, 25, 35, 45, 55, 65, 100], labels=['18-25', '26-35', '36-45', '46-55', '56-65', '65+'])
        age_claim_rates = data.groupby(age_groups)['claim_occurred'].mean()
        
        gender_claim_rates = data.groupby('gender')['claim_occurred'].mean()
        
        experience_groups = pd.cut(data['driving_experience'], bins=[-1, 2, 5, 10, 20, 50], labels=['0-2', '3-5', '6-10', '11-20', '20+'])
        experience_claim_rates = data.groupby(experience_groups)['claim_occurred'].mean()
        
        violation_claim_rates = data.groupby('traffic_violations')['claim_occurred'].mean()
        
        car_category_claim_rates = data.groupby('car_category')['claim_occurred'].mean()
        
        # 计算索赔金额统计
        claim_amount_stats = {
            'mean': data['claim_amount'].mean(),
            'median': data[data['claim_amount'] > 0]['claim_amount'].median(),
            'max': data['claim_amount'].max(),
            'total': data['claim_amount'].sum()
        }
        
        # 训练一个简单的回归模型预测索赔金额
        X = data.drop(['claim_occurred', 'claim_amount'], axis=1)
        X = pd.get_dummies(X, drop_first=True)
        y = data['claim_amount']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        
        self.models['car_claim_amount'] = model
        
        # 获取特征重要性
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1][:10]
        feature_importance = {X.columns[i]: float(importances[i]) for i in indices}
        
        return {
            'total_claim_rate': total_claim_rate,
            'age_claim_rates': dict(age_claim_rates),
            'gender_claim_rates': dict(gender_claim_rates),
            'experience_claim_rates': dict(experience_claim_rates),
            'violation_claim_rates': dict(violation_claim_rates),
            'car_category_claim_rates': dict(car_category_claim_rates),
            'claim_amount_stats': claim_amount_stats,
            'model_metrics': {
                'r2': r2_score(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred))
            },
            'feature_importance': feature_importance
        }
    
    def predict_car_claim_amount(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """预测车险客户的预期索赔金额
        
        Args:
            customer_data: 客户数据字典
            
        Returns:
            包含预测结果的字典
        """
        if 'car_claim_amount' not in self.models:
            raise ValueError("Model not trained. Call analyze_car_insurance_claims first.")
        
        # 将输入转换为DataFrame并进行编码
        df = pd.DataFrame([customer_data])
        df = pd.get_dummies(df, drop_first=True)
        
        # 确保与训练数据有相同的列
        model = self.models['car_claim_amount']
        expected_features = model.feature_names_in_
        
        # 处理缺失特征
        for feature in expected_features:
            if feature not in df.columns:
                df[feature] = 0
        
        # 只保留模型期望的特征，并按照正确顺序排列
        df = df[expected_features]
        
        # 预测
        predicted_amount = model.predict(df)[0]
        
        return {
            'customer_id': customer_data.get('id', 'unknown'),
            'predicted_claim_amount': float(predicted_amount),
            'risk_level': self._get_car_risk_level(predicted_amount)
        }
    
    def _get_car_risk_level(self, amount: float) -> str:
        """根据预期索赔金额确定风险等级
        
        Args:
            amount: 预期索赔金额
            
        Returns:
            风险等级
        """
        if amount < 1000:
            return "低风险"
        elif amount < 3000:
            return "中低风险"
        elif amount < 6000:
            return "中风险"
        elif amount < 10000:
            return "中高风险"
        else:
            return "高风险"
    
    def health_insurance_customer_segmentation(self, data: pd.DataFrame, n_clusters: int = 5) -> Dict[str, Any]:
        """对医疗保险客户进行分群，用于精准营销
        
        Args:
            data: 医疗保险数据
            n_clusters: 分群数量
            
        Returns:
            包含分群结果的字典
        """
        # 选取用于分群的特征
        features = ['age', 'bmi', 'income', 'children', 'smoker', 'chronic_disease', 'past_claims', 'premium']
        X = data[features].copy()
        
        # 处理分类特征
        X['smoker'] = X['smoker'].astype(int)
        X['chronic_disease'] = X['chronic_disease'].astype(int)
        
        # 标准化数值特征
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # K均值聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        # 将分群结果添加回原数据
        data_with_clusters = data.copy()
        data_with_clusters['cluster'] = clusters
        
        # 分析每个群体的特征
        cluster_profiles = data_with_clusters.groupby('cluster').agg({
            'age': 'mean',
            'bmi': 'mean',
            'income': 'mean',
            'children': 'mean',
            'smoker': 'mean',
            'chronic_disease': 'mean',
            'past_claims': 'mean',
            'premium': 'mean',
            'purchased': 'mean',
        }).reset_index()
        
        # 计算每个群体的大小
        cluster_sizes = data_with_clusters['cluster'].value_counts().sort_index().to_dict()
        
        # 为每个群体生成营销建议
        marketing_recommendations = {}
        for i in range(n_clusters):
            profile = cluster_profiles[cluster_profiles['cluster'] == i].iloc[0]
            
            recommendations = []
            
            # 根据特征生成建议
            if profile['smoker'] > 0.5:
                recommendations.append("强调戒烟的健康保险福利")
            
            if profile['chronic_disease'] > 0.5:
                recommendations.append("提供慢性病管理计划")
            
            if profile['age'] > 55:
                recommendations.append("关注老年人特殊需求的保险计划")
            
            if profile['income'] > 70000:
                recommendations.append("提供高端保险产品")
            else:
                recommendations.append("提供经济实惠的基础保险计划")
            
            if profile['children'] > 1:
                recommendations.append("强调家庭保险计划的优势")
            
            if profile['purchased'] < 0.3:
                recommendations.append("制定特别促销活动以提高转化率")
            
            marketing_recommendations[i] = recommendations
        
        return {
            'cluster_profiles': cluster_profiles.to_dict('records'),
            'cluster_sizes': cluster_sizes,
            'marketing_recommendations': marketing_recommendations,
            'purchase_rate_by_cluster': cluster_profiles[['cluster', 'purchased']].to_dict('records')
        }
    
    def predict_health_insurance_purchase(self, data: pd.DataFrame) -> Dict[str, Any]:
        """预测医疗保险购买概率，用于精准营销
        
        Args:
            data: 医疗保险数据
            
        Returns:
            包含预测结果的字典
        """
        # 准备数据
        X = data.drop('purchased', axis=1)
        y = data['purchased']
        
        # 处理分类特征
        categorical_features = X.select_dtypes(include=['object']).columns
        numerical_features = X.select_dtypes(exclude=['object']).columns
        
        # 定义预处理管道
        numerical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, numerical_features),
                ('cat', categorical_transformer, categorical_features)
            ]
        )
        
        # 建立模型管道
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', GradientBoostingClassifier(random_state=42))
        ])
        
        # 分割数据
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 训练模型
        pipeline.fit(X_train, y_train)
        
        # 预测
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]
        
        # 保存模型
        self.models['health_purchase'] = pipeline
        
        # 评估模型
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_prob)
        }
        
        # 获取特征重要性
        # 这里使用了一个简化方法，因为管道中的特征转换使得直接获取特征重要性变得复杂
        feature_importance = {}
        
        return {
            'model_metrics': metrics,
            'feature_importance': feature_importance,
            'test_predictions': y_prob[:10].tolist()
        }
    
    def recommend_insurance_products(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """根据客户特征推荐保险产品
        
        Args:
            customer_data: 客户数据字典
            
        Returns:
            包含推荐结果的字典
        """
        if 'health_purchase' not in self.models:
            raise ValueError("Model not trained. Call predict_health_insurance_purchase first.")
        
        # 将输入转换为DataFrame
        df = pd.DataFrame([customer_data])
        
        # 预测购买概率
        pipeline = self.models['health_purchase']
        purchase_prob = pipeline.predict_proba(df)[0, 1]
        
        # 根据客户特征和购买概率制定推荐
        recommendations = []
        
        # 基于购买概率的推荐
        if purchase_prob > 0.7:
            recommendations.append("高购买意向客户，可提供全面的保险产品套餐")
        elif purchase_prob > 0.4:
            recommendations.append("中等购买意向客户，可提供基础产品并适当推荐附加服务")
        else:
            recommendations.append("低购买意向客户，需要更多营销努力，可提供试用或特别优惠")
        
        # 基于年龄的推荐
        age = customer_data.get('age', 0)
        if age > 60:
            recommendations.append("老年保健计划，包括处方药和慢性病管理")
        elif age > 35:
            recommendations.append("家庭保险计划，兼顾个人与家庭需求")
        else:
            recommendations.append("青年健康计划，强调预防保健和运动意外保障")
        
        # 基于健康状况的推荐
        if customer_data.get('smoker', 0) == 1:
            recommendations.append("戒烟支持计划，提供额外的呼吸系统保障")
        
        if customer_data.get('bmi', 25) > 30:
            recommendations.append("体重管理计划，提供营养咨询和健身服务")
        
        if customer_data.get('chronic_disease', 0) == 1:
            recommendations.append("慢性病管理计划，包括药物报销和定期检查")
        
        return {
            'customer_id': customer_data.get('id', 'unknown'),
            'purchase_probability': float(purchase_prob),
            'customer_segment': self._get_customer_segment(purchase_prob),
            'product_recommendations': recommendations
        }
    
    def _get_customer_segment(self, purchase_prob: float) -> str:
        """根据购买概率确定客户分群
        
        Args:
            purchase_prob: 购买概率
            
        Returns:
            客户分群
        """
        if purchase_prob < 0.3:
            return "难以转化"
        elif purchase_prob < 0.5:
            return "需要推动"
        elif purchase_prob < 0.7:
            return "有意向"
        else:
            return "高度意向"

# 创建服务实例
insurance_service = InsuranceAnalysisService() 