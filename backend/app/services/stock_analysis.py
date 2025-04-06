import pandas as pd
import numpy as np
import talib
import requests
import datetime
import os
from typing import Dict, List, Optional, Any, Union

class StockAnalysisService:
    """股票分析服务，提供数据获取和技术指标计算"""
    
    def __init__(self, data_dir: str = "./data"):
        """初始化股票分析服务
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def get_stock_data(self, symbol: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """从网络获取股票数据或从本地缓存读取
        
        Args:
            symbol: 股票代码，如 '600000.SH'
            start_date: 开始日期，如 '2020-01-01'
            end_date: 结束日期，如 '2020-12-31'，默认为今天
            
        Returns:
            股票数据 DataFrame，包含 OHLCV 数据
        """
        # 如果未指定结束日期，则使用今天
        if end_date is None:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
            
        # 构建缓存文件路径
        cache_file = os.path.join(self.data_dir, f"{symbol}_{start_date}_{end_date}.csv")
        
        # 如果缓存文件存在，直接读取
        if os.path.exists(cache_file):
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        
        # 否则从网络获取数据
        # 这里使用模拟数据，实际项目中可以连接真实API
        df = self._mock_stock_data(symbol, start_date, end_date)
        
        # 保存到缓存
        df.to_csv(cache_file)
        
        return df
    
    def _mock_stock_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """生成模拟股票数据，用于演示和测试
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            模拟的股票数据 DataFrame
        """
        # 生成日期范围
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        dates = pd.date_range(start=start, end=end, freq='B')
        
        # 生成随机数据
        np.random.seed(42)  # 设置随机种子，使结果可复现
        n = len(dates)
        
        # 模拟价格走势
        close = np.random.randn(n).cumsum() + 100
        # 确保价格为正
        close = np.maximum(close, 1)
        
        # 生成其他价格数据
        high = close * (1 + np.random.rand(n) * 0.03)
        low = close * (1 - np.random.rand(n) * 0.03)
        open_price = low + np.random.rand(n) * (high - low)
        volume = np.random.randint(1000, 1000000, size=n)
        
        # 创建 DataFrame
        df = pd.DataFrame({
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        }, index=dates)
        
        return df
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算常用技术指标
        
        Args:
            data: 股票OHLCV数据
            
        Returns:
            添加了技术指标的DataFrame
        """
        df = data.copy()
        
        # 移动平均线 - 趋势类指标
        df['MA5'] = talib.MA(df['close'], timeperiod=5)
        df['MA10'] = talib.MA(df['close'], timeperiod=10)
        df['MA20'] = talib.MA(df['close'], timeperiod=20)
        df['MA60'] = talib.MA(df['close'], timeperiod=60)
        
        # 指数移动平均线
        df['EMA12'] = talib.EMA(df['close'], timeperiod=12)
        df['EMA26'] = talib.EMA(df['close'], timeperiod=26)
        
        # MACD - 趋势类指标
        df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(
            df['close'], fastperiod=12, slowperiod=26, signalperiod=9
        )
        
        # RSI - 摆动类指标
        df['RSI14'] = talib.RSI(df['close'], timeperiod=14)
        
        # 布林带 - 通道类指标
        df['BOLL_upper'], df['BOLL_middle'], df['BOLL_lower'] = talib.BBANDS(
            df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
        )
        
        # KDJ指标
        df['K'], df['D'] = talib.STOCH(
            df['high'], df['low'], df['close'],
            fastk_period=9, slowk_period=3, slowk_matype=0,
            slowd_period=3, slowd_matype=0
        )
        df['J'] = 3 * df['K'] - 2 * df['D']
        
        # ATR - 波动性指标
        df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
        
        # OBV - 成交量指标
        df['OBV'] = talib.OBV(df['close'], df['volume'])
        
        return df
    
    def calculate_basic_stats(self, data: pd.DataFrame) -> Dict[str, float]:
        """计算基本统计量
        
        Args:
            data: 股票价格数据
            
        Returns:
            包含基本统计量的字典
        """
        returns = data['close'].pct_change().dropna()
        
        stats = {
            'mean': returns.mean(),
            'median': returns.median(),
            'std': returns.std(),
            'min': returns.min(),
            'max': returns.max(),
            'skew': returns.skew(),
            'kurtosis': returns.kurtosis(),
            'annualized_return': returns.mean() * 252,
            'annualized_volatility': returns.std() * np.sqrt(252),
            'sharpe_ratio': (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0,
            'positive_days': (returns > 0).sum() / len(returns),
            'negative_days': (returns < 0).sum() / len(returns),
        }
        
        return stats
    
    def portfolio_optimization(self, stock_data: Dict[str, pd.DataFrame], risk_free_rate: float = 0.03) -> Dict[str, Any]:
        """投资组合优化 - 马科维茨模型和夏普比率优化
        
        Args:
            stock_data: 股票数据字典，键为股票代码，值为DataFrame
            risk_free_rate: 无风险利率，默认为3%
            
        Returns:
            包含优化结果的字典
        """
        # 计算每只股票的日收益率
        returns_dict = {}
        for symbol, data in stock_data.items():
            returns_dict[symbol] = data['close'].pct_change().dropna()
        
        # 构建收益率DataFrame
        returns = pd.DataFrame(returns_dict)
        
        # 计算年化收益率和协方差矩阵
        annual_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        
        # 生成随机投资组合
        num_portfolios = 10000
        results = np.zeros((3, num_portfolios))
        weights_record = []
        
        for i in range(num_portfolios):
            # 生成随机权重
            weights = np.random.random(len(returns.columns))
            weights /= np.sum(weights)
            weights_record.append(weights)
            
            # 计算组合收益率和风险
            portfolio_return = np.sum(weights * annual_returns)
            portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # 计算夏普比率
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std_dev
            
            # 记录结果
            results[0, i] = portfolio_return
            results[1, i] = portfolio_std_dev
            results[2, i] = sharpe_ratio
        
        # 找到最优组合（最高夏普比率）
        max_sharpe_idx = np.argmax(results[2])
        max_sharpe_weights = weights_record[max_sharpe_idx]
        max_sharpe_return = results[0, max_sharpe_idx]
        max_sharpe_std_dev = results[1, max_sharpe_idx]
        max_sharpe_ratio = results[2, max_sharpe_idx]
        
        # 找到最小方差组合
        min_vol_idx = np.argmin(results[1])
        min_vol_weights = weights_record[min_vol_idx]
        min_vol_return = results[0, min_vol_idx]
        min_vol_std_dev = results[1, min_vol_idx]
        min_vol_sharpe = results[2, min_vol_idx]
        
        # 构建有效前沿
        return {
            'symbols': list(returns.columns),
            'max_sharpe': {
                'weights': dict(zip(returns.columns, max_sharpe_weights)),
                'return': max_sharpe_return,
                'volatility': max_sharpe_std_dev,
                'sharpe_ratio': max_sharpe_ratio
            },
            'min_volatility': {
                'weights': dict(zip(returns.columns, min_vol_weights)),
                'return': min_vol_return,
                'volatility': min_vol_std_dev,
                'sharpe_ratio': min_vol_sharpe
            },
            'efficient_frontier': {
                'returns': results[0, :].tolist(),
                'volatilities': results[1, :].tolist(),
                'sharpe_ratios': results[2, :].tolist()
            }
        }

# 创建服务实例
stock_service = StockAnalysisService() 