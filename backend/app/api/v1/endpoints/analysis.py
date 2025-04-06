from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
import pandas as pd
import json
from datetime import date

from app.db.session import get_db
from app.services.stock_analysis import stock_service
from app.services.bank_analysis import bank_service
from app.services.insurance_analysis import insurance_service
from app.services.data_analysis import data_analysis_service

router = APIRouter()

#---- 股票分析接口 ----#
@router.get("/stock/data")
async def get_stock_data(
    symbol: str = Query(..., description="股票代码"),
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD")
) -> Dict[str, Any]:
    """
    获取股票历史数据
    """
    try:
        df = stock_service.get_stock_data(symbol, start_date, end_date)
        return {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date or date.today().strftime('%Y-%m-%d'),
            "data": df.reset_index().to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/indicators")
async def get_stock_indicators(
    symbol: str = Query(..., description="股票代码"),
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD")
) -> Dict[str, Any]:
    """
    计算股票技术指标
    """
    try:
        # 获取股票数据
        df = stock_service.get_stock_data(symbol, start_date, end_date)
        
        # 计算指标
        df_with_indicators = stock_service.calculate_technical_indicators(df)
        
        return {
            "symbol": symbol,
            "indicators": df_with_indicators.reset_index().to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/stats")
async def get_stock_stats(
    symbol: str = Query(..., description="股票代码"),
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD")
) -> Dict[str, Any]:
    """
    计算股票基本统计量
    """
    try:
        # 获取股票数据
        df = stock_service.get_stock_data(symbol, start_date, end_date)
        
        # 计算统计量
        stats = stock_service.calculate_basic_stats(df)
        
        return {
            "symbol": symbol,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stock/portfolio")
async def optimize_portfolio(
    symbols: List[str],
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    risk_free_rate: float = Query(0.03, description="无风险利率，默认3%")
) -> Dict[str, Any]:
    """
    投资组合优化
    """
    try:
        # 获取所有股票数据
        stock_data = {}
        for symbol in symbols:
            df = stock_service.get_stock_data(symbol, start_date, end_date)
            stock_data[symbol] = df
        
        # 优化投资组合
        result = stock_service.portfolio_optimization(stock_data, risk_free_rate)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#---- 银行分析接口 ----#
@router.get("/bank/credit-data")
async def get_credit_data() -> Dict[str, Any]:
    """
    获取信用卡客户数据
    """
    try:
        df = bank_service.load_credit_data()
        return {
            "data": df.head(100).to_dict(orient="records"),
            "total_records": len(df),
            "columns": df.columns.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bank/train-default-model")
async def train_default_model(
    model_type: str = Query("random_forest", description="模型类型：random_forest 或 logistic_regression")
) -> Dict[str, Any]:
    """
    训练信用卡违约预测模型
    """
    try:
        # 加载数据
        df = bank_service.load_credit_data()
        
        # 训练模型
        result = bank_service.train_credit_default_model(df, model_type)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bank/predict-default")
async def predict_default(
    customer_data: Dict[str, Any],
    model_type: str = Query("random_forest", description="模型类型：random_forest 或 logistic_regression")
) -> Dict[str, Any]:
    """
    预测客户违约概率
    """
    try:
        result = bank_service.predict_default_probability(customer_data, model_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bank/analyze-factors")
async def analyze_credit_factors() -> Dict[str, Any]:
    """
    分析影响信用评分的因素
    """
    try:
        # 加载数据
        df = bank_service.load_credit_data()
        
        # 分析因素
        result = bank_service.analyze_credit_factors(df)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#---- 保险分析接口 ----#
@router.get("/insurance/car-data")
async def get_car_insurance_data() -> Dict[str, Any]:
    """
    获取车险数据
    """
    try:
        df = insurance_service.load_car_insurance_data()
        return {
            "data": df.head(100).to_dict(orient="records"),
            "total_records": len(df),
            "columns": df.columns.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insurance/health-data")
async def get_health_insurance_data() -> Dict[str, Any]:
    """
    获取医疗保险数据
    """
    try:
        df = insurance_service.load_health_insurance_data()
        return {
            "data": df.head(100).to_dict(orient="records"),
            "total_records": len(df),
            "columns": df.columns.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insurance/analyze-car-claims")
async def analyze_car_claims() -> Dict[str, Any]:
    """
    分析车险索赔影响因素
    """
    try:
        # 加载数据
        df = insurance_service.load_car_insurance_data()
        
        # 分析索赔
        result = insurance_service.analyze_car_insurance_claims(df)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insurance/predict-car-claim")
async def predict_car_claim(
    customer_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    预测车险客户的预期索赔金额
    """
    try:
        # 首先分析数据（会训练模型）
        df = insurance_service.load_car_insurance_data()
        insurance_service.analyze_car_insurance_claims(df)
        
        # 预测
        result = insurance_service.predict_car_claim_amount(customer_data)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insurance/segment-customers")
async def segment_health_customers(
    n_clusters: int = Query(5, description="分群数量")
) -> Dict[str, Any]:
    """
    对医疗保险客户进行分群
    """
    try:
        # 加载数据
        df = insurance_service.load_health_insurance_data()
        
        # 分群
        result = insurance_service.health_insurance_customer_segmentation(df, n_clusters)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insurance/predict-purchase")
async def predict_health_purchase() -> Dict[str, Any]:
    """
    预测医疗保险购买概率
    """
    try:
        # 加载数据
        df = insurance_service.load_health_insurance_data()
        
        # 预测
        result = insurance_service.predict_health_insurance_purchase(df)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insurance/recommend-products")
async def recommend_insurance_products(
    customer_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    推荐保险产品
    """
    try:
        # 首先训练模型
        df = insurance_service.load_health_insurance_data()
        insurance_service.predict_health_insurance_purchase(df)
        
        # 推荐产品
        result = insurance_service.recommend_insurance_products(customer_data)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#---- 数据分析工具接口 ----#
@router.post("/tools/basic-stats")
async def get_data_basic_stats(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    计算数据基本统计量
    """
    try:
        df = pd.DataFrame(data)
        stats = data_analysis_service.get_basic_stats(df)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/correlation")
async def calculate_correlation(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    计算相关性分析
    """
    try:
        df = pd.DataFrame(data)
        corr = data_analysis_service.correlation_analysis(df)
        return corr
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/visualization")
async def generate_data_visualization(
    data: List[Dict[str, Any]],
    viz_type: str = Query(..., description="可视化类型：histogram, boxplot, scatter, 等"),
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    生成数据可视化
    """
    try:
        df = pd.DataFrame(data)
        img_str = data_analysis_service.generate_visualization(df, viz_type, params or {})
        return {"image": img_str}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/handle-missing")
async def handle_missing_values(
    data: List[Dict[str, Any]],
    strategy: Dict[str, str]
) -> Dict[str, Any]:
    """
    处理缺失值
    """
    try:
        df = pd.DataFrame(data)
        result_df = data_analysis_service.handle_missing_values(df, strategy)
        return {"data": result_df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/normalize")
async def normalize_data(
    data: List[Dict[str, Any]],
    method: str = Query("zscore", description="规范化方法：zscore, minmax, robust"),
    columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    数据规范化
    """
    try:
        df = pd.DataFrame(data)
        result_df = data_analysis_service.normalize_data(df, method, columns)
        return {"data": result_df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/encode-categorical")
async def encode_categorical(
    data: List[Dict[str, Any]],
    method: str = Query("onehot", description="编码方法：onehot, label"),
    columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    对分类特征进行编码
    """
    try:
        df = pd.DataFrame(data)
        result_df = data_analysis_service.encode_categorical_features(df, method, columns)
        return {"data": result_df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/select-features")
async def select_data_features(
    data: List[Dict[str, Any]],
    target: str = Query(..., description="目标变量名称"),
    method: str = Query("kbest", description="特征选择方法：kbest, rfe, lasso, ridge"),
    k: int = Query(5, description="选择的特征数量")
) -> Dict[str, Any]:
    """
    特征选择
    """
    try:
        df = pd.DataFrame(data)
        selected_features, feature_scores = data_analysis_service.select_features(df, target, method, k)
        return {
            "selected_features": selected_features,
            "feature_scores": feature_scores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/pca")
async def extract_pca_features(
    data: List[Dict[str, Any]],
    n_components: int = Query(2, description="主成分数量"),
    columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    PCA特征提取
    """
    try:
        df = pd.DataFrame(data)
        result_df, pca_info = data_analysis_service.extract_features_with_pca(df, n_components, columns)
        return {
            "data": result_df.to_dict(orient="records"),
            "pca_info": pca_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/evaluate-classification")
async def evaluate_classification(
    y_true: List[int],
    y_pred: List[int],
    y_prob: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    评估分类模型
    """
    try:
        import numpy as np
        metrics = data_analysis_service.evaluate_classification_model(
            np.array(y_true),
            np.array(y_pred),
            np.array(y_prob) if y_prob is not None else None
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/evaluate-regression")
async def evaluate_regression(
    y_true: List[float],
    y_pred: List[float]
) -> Dict[str, Any]:
    """
    评估回归模型
    """
    try:
        import numpy as np
        metrics = data_analysis_service.evaluate_regression_model(
            np.array(y_true),
            np.array(y_pred)
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 