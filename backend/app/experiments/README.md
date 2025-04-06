# 银行信贷风险控制实验

本目录包含"银行信贷风险控制"实验的完整实现，基于台湾信用卡违约数据集。

## 功能模块

- **credit_risk_exploration.py**: 数据的探索性分析，包括基本统计量、异常值统计、重复值统计和缺失值统计等
- **credit_risk_cleaning.py**: 数据清洗，包括缺失值处理、数据标准化、异常值处理等
- **credit_risk_feature_engineering.py**: 特征工程，包括构建技术指标(MACD、RSI、OBV)和使用主成分分析、Lasso进行特征提取
- **credit_risk_modeling.py**: 信用卡违约预测模型的训练和评估，支持多种模型类型和评估指标
- **credit_risk_strategy.py**: 基于模型结果制定风险控制策略
- **credit_risk_main.py**: 运行完整的信用卡风险分析流程

## 使用方法

### 1. 运行完整分析流程

```bash
python -m app.experiments.credit_risk_main
```

### 2. 运行带参数的分析流程

```bash
# 使用随机森林模型，并启用SMOTE处理类别不平衡
python -m app.experiments.credit_risk_main --model random_forest --balance-data

# 评估所有模型并选择最佳的
python -m app.experiments.credit_risk_main --all-models --balance-data

# 指定PCA和Lasso参数
python -m app.experiments.credit_risk_main --pca-components 15 --lasso-alpha 0.005
```

### 3. 逐步运行各个模块

也可以分别运行各个模块，按步骤完成分析：

```bash
# 步骤1: 数据探索
python -m app.experiments.credit_risk_exploration

# 步骤2: 数据清洗
python -m app.experiments.credit_risk_cleaning

# 步骤3: 特征工程
python -m app.experiments.credit_risk_feature_engineering

# 步骤4: 模型训练
python -m app.experiments.credit_risk_modeling

# 步骤5: 风险策略制定
python -m app.experiments.credit_risk_strategy
```

## 输出文件

所有输出文件将保存在 `output` 目录下，包括：

- 数据可视化图表（.png格式）
- 处理后的数据集（.csv格式）
- 训练好的模型（.pkl格式）
- 风险控制策略报告（.md格式）

## 数据集说明

台湾信用卡数据集包含以下字段：

- LIMIT_BAL: 信用额度
- AGE: 年龄
- EDUCATION: 教育程度
- MARRIAGE: 婚姻状况
- SEX: 性别
- PAY_1 ~ PAY_6: 过去6个月的还款状态
- BILL_AMT1 ~ BILL_AMT6: 过去6个月的账单金额
- PAY_AMT1 ~ PAY_AMT6: 过去6个月的还款金额
- DEFAULT: 是否违约 (1=是, 0=否)

## 依赖库

- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn
- imbalanced-learn
- shap
- joblib 