import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List

import akshare as ak
import pandas as pd
from pydantic import BaseModel

# 配置日志
logger = logging.getLogger(__name__)


class StockDataRequest(BaseModel):
    """股票数据请求基础模型

    Attributes:
        stock_code (str): 股票代码，如'600519'或'00700.HK'
        market_type (str): 市场类型，可选值: 'A'(A股), 'HK'(港股), 'US'(美股), 'ETF'(ETF基金), 'LOF'(LOF基金)
        start_date (Optional[str]): 开始日期，格式'YYYYMMDD'，默认一年前
        end_date (Optional[str]): 结束日期，格式'YYYYMMDD'，默认当天

    Example:
        >>> request = StockDataRequest(stock_code='600519', market_type='A')
    """
    stock_code: str
    market_type: str = 'A'
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class TechnicalIndicatorParams(BaseModel):
    """技术指标参数配置模型

    Attributes:
        ma_periods (Dict[str, int]): 移动平均线周期配置，包含:
            - short: 短期均线周期(默认5)
            - medium: 中期均线周期(默认20)
            - long: 长期均线周期(默认60)
        rsi_period (int): RSI计算周期(默认14)
        bollinger_period (int): 布林带计算周期(默认20)
        bollinger_std (int): 布林带标准差倍数(默认2)
        volume_ma_period (int): 成交量均线周期(默认20)
        atr_period (int): ATR计算周期(默认14)

    Note:
        修改这些参数会影响技术指标计算结果，建议根据市场特点调整
    """
    ma_periods: Dict[str, int] = {'short': 5, 'medium': 20, 'long': 60}
    rsi_period: int = 14
    bollinger_period: int = 20
    bollinger_std: int = 2
    volume_ma_period: int = 20
    atr_period: int = 14


class StockAnalysisResult(BaseModel):
    """股票分析结果数据模型

    Attributes:
        stock_code (str): 股票代码
        market_type (str): 市场类型(A/HK/US/ETF/LOF)
        analysis_date (str): 分析日期(YYYY-MM-DD格式)
        score (float): 综合评分(0-100)
        price (float): 最新收盘价
        price_change (float): 涨跌幅百分比
        ma_trend (str): 均线趋势，取值: 'UP'(上涨趋势)或'DOWN'(下跌趋势)
        rsi (Optional[float]): RSI指标值(14日)，范围0-100
        macd_signal (str): MACD信号，取值: 'BUY'(买入信号)或'SELL'(卖出信号)
        volume_status (str): 成交量状态，取值:
            'HIGH'(显著放量，成交量/均量>1.5)
            'NORMAL'(正常水平)
        recommendation (str): 投资建议，取值:
            '强烈推荐买入'(score≥80)
            '建议买入'(60≤score<80)
            '观望'(40≤score<60)
            '建议卖出'(20≤score<40)
            '强烈建议卖出'(score<20)

    Example:
        {
            "stock_code": "600519",
            "market_type": "A",
            "analysis_date": "2023-05-15",
            "score": 85.0,
            "price": 1800.50,
            "price_change": 2.5,
            "ma_trend": "UP",
            "rsi": 65.2,
            "macd_signal": "BUY",
            "volume_status": "HIGH",
            "recommendation": "强烈推荐买入"
        }
    """
    stock_code: str
    market_type: str
    analysis_date: str
    score: float
    price: float
    price_change: float
    ma_trend: str
    rsi: Optional[float]
    macd_signal: str
    volume_status: str
    recommendation: str


class StockAnalysisService:
    """股票分析核心服务

    提供完整的股票数据分析功能，包括:
    - 从多种市场获取股票历史数据
    - 计算各类技术指标(均线、RSI、MACD、布林带等)
    - 生成综合评分和投资建议

    Usage:
        >>> service = StockAnalysisService()
        >>> request = StockDataRequest(stock_code='600519', market_type='A')
        >>> result = service.analyze_stock(request)
        >>> print(result.recommendation)

    Note:
        - 服务初始化时会加载默认技术指标参数
        - 所有方法都带有完善的日志记录
        - 错误会通过日志记录并重新抛出
    """

    def __init__(self):
        self.params = TechnicalIndicatorParams()
        logger.info("StockAnalysisService initialized with default parameters")

    def _truncate_json_for_logging(self, json_obj: Dict, max_length: int = 500) -> str:
        """截断JSON对象用于日志记录"""
        json_str = json.dumps(
            json_obj,
            default=lambda x: x.isoformat() if isinstance(x, pd.Timestamp) else x,
            ensure_ascii=False
        )
        if len(json_str) <= max_length:
            return json_str
        return json_str[:max_length] + f"... [截断，总长度: {len(json_str)}字符]"

    def get_stock_data(self, request: StockDataRequest) -> pd.DataFrame:
        """获取指定股票的历史交易数据

        Args:
            request (StockDataRequest): 包含股票代码、市场类型和日期范围的请求对象

        Returns:
            pd.DataFrame: 包含历史交易数据的DataFrame，列包括:
                - date (datetime): 交易日期
                - open (float): 开盘价
                - close (float): 收盘价
                - high (float): 最高价
                - low (float): 最低价
                - volume (float): 成交量

        Raises:
            ValueError: 如果股票代码格式无效或市场类型不支持
            Exception: 如果数据获取失败

        Note:
            - A股数据来自akshare的stock_zh_a_hist接口
            - 港股数据来自akshare的stock_hk_daily接口
            - 默认获取最近1年数据

        Example:
            >>> request = StockDataRequest(stock_code='600519', market_type='A')
            >>> df = service.get_stock_data(request)
            >>> print(df.head())
        """
        try:
            logger.info(f"Fetching stock data for {request.stock_code} in market {request.market_type}")

            start_date = request.start_date or (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            end_date = request.end_date or datetime.now().strftime('%Y%m%d')

            # 验证股票代码格式
            if request.market_type == 'A':
                valid_prefixes = ['0', '3', '6', '688', '8']
                if not any(request.stock_code.startswith(prefix) for prefix in valid_prefixes):
                    error_msg = f"无效的A股股票代码格式: {request.stock_code}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)

                df = ak.stock_zh_a_hist(
                    symbol=request.stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
            elif request.market_type == 'HK':
                df = ak.stock_hk_daily(
                    symbol=request.stock_code,
                    adjust="qfq"
                )
            elif request.market_type == 'US':
                df = ak.stock_us_hist(
                    symbol=request.stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
            elif request.market_type == 'ETF':
                df = ak.fund_etf_hist_em(
                    symbol=request.stock_code,
                    period="daily",
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
            elif request.market_type == 'LOF':
                df = ak.fund_lof_hist_em(
                    symbol=request.stock_code,
                    period="daily",
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
            else:
                error_msg = f"不支持的市场类型: {request.market_type}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # 数据预处理
            df = df.rename(columns={
                "日期": "date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume"
            })
            df['date'] = pd.to_datetime(df['date'])
            numeric_columns = ['open', 'close', 'high', 'low', 'volume']
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
            df = df.dropna().sort_values('date')

            logger.info(f"Successfully fetched {len(df)} records for {request.stock_code}")
            return df

        except Exception as e:
            logger.error(f"获取股票数据失败: {str(e)}", exc_info=True)
            raise

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算并添加技术指标到股票数据

        Args:
            df (pd.DataFrame): 包含基础股票数据的DataFrame，必须包含以下列:
                - close: 收盘价
                - high: 最高价
                - low: 最低价
                - volume: 成交量

        Returns:
            pd.DataFrame: 添加了技术指标的DataFrame，新增列包括:
                - MA5/MA20/MA60: 5/20/60日均线
                - RSI: 相对强弱指数(14日)
                - MACD/Signal/MACD_hist: MACD指标
                - BB_upper/middle/lower: 布林带指标
                - Volume_MA/Ratio: 成交量均线及比率
                - ATR: 平均真实波幅
                - Volatility: 波动率百分比
                - ROC: 价格变动率

        Note:
            使用TechnicalIndicatorParams中的参数配置计算指标:
            - 均线: 指数移动平均(EMA)
            - RSI: 标准14日相对强弱指数
            - MACD: 12/26/9日参数
            - 布林带: 20日移动平均±2倍标准差
            - ATR: 14日平均真实波幅

        Example:
            >>> df = service.get_stock_data(request)
            >>> df_with_indicators = service.calculate_indicators(df)
            >>> print(df_with_indicators[['date','close','MA5','RSI']].tail())
        """
        try:
            logger.info("Calculating technical indicators")

            # 计算移动平均线
            df['MA5'] = self._calculate_ema(df['close'], self.params.ma_periods['short'])
            df['MA20'] = self._calculate_ema(df['close'], self.params.ma_periods['medium'])
            df['MA60'] = self._calculate_ema(df['close'], self.params.ma_periods['long'])

            # 计算RSI
            df['RSI'] = self._calculate_rsi(df['close'], self.params.rsi_period)

            # 计算MACD
            df['MACD'], df['Signal'], df['MACD_hist'] = self._calculate_macd(df['close'])

            # 计算布林带
            df['BB_upper'], df['BB_middle'], df['BB_lower'] = self._calculate_bollinger_bands(
                df['close'],
                self.params.bollinger_period,
                self.params.bollinger_std
            )

            # 成交量分析
            df['Volume_MA'] = df['volume'].rolling(window=self.params.volume_ma_period).mean()
            df['Volume_Ratio'] = df['volume'] / df['Volume_MA']

            # 计算ATR和波动率
            df['ATR'] = self._calculate_atr(df, self.params.atr_period)
            df['Volatility'] = df['ATR'] / df['close'] * 100

            # 动量指标
            df['ROC'] = df['close'].pct_change(periods=10) * 100

            logger.debug(f"Calculated indicators for {len(df)} records")
            return df

        except Exception as e:
            logger.error(f"计算技术指标时出错: {str(e)}", exc_info=True)
            raise

    def analyze_stock(self, request: StockDataRequest) -> StockAnalysisResult:
        """执行完整的股票分析流程并生成报告

        Args:
            request (StockDataRequest): 包含股票代码和市场类型的请求对象

        Returns:
            StockAnalysisResult: 包含完整分析结果的对象，包括:
                - 技术指标状态
                - 综合评分(0-100)
                - 投资建议

        Process:
            1. 获取股票历史数据
            2. 计算各类技术指标
            3. 基于以下因素计算综合评分:
                - 均线趋势(30分)
                - RSI状态(20分)
                - MACD信号(20分)
                - 成交量状态(30分)
            4. 根据评分生成投资建议

        Raises:
            Exception: 如果任何分析步骤失败

        Example:
            >>> request = StockDataRequest(stock_code='600519', market_type='A')
            >>> result = service.analyze_stock(request)
            >>> print(f"评分: {result.score}, 建议: {result.recommendation}")
        """
        try:
            logger.info(f"Starting analysis for {request.stock_code}")

            # 获取股票数据
            stock_data = self.get_stock_data(request)
            logger.debug(f"Raw stock data sample: {self._truncate_json_for_logging(stock_data.head().to_dict())}")

            # 计算技术指标
            stock_data = self.calculate_indicators(stock_data)

            # 计算评分
            score = self._calculate_score(stock_data)
            logger.info(f"Calculated score: {score}")

            # 获取最新数据
            latest = stock_data.iloc[-1]
            prev = stock_data.iloc[-2]

            # 生成报告
            report = StockAnalysisResult(
                stock_code=request.stock_code,
                market_type=request.market_type,
                analysis_date=datetime.now().strftime('%Y-%m-%d'),
                score=score,
                price=latest['close'],
                price_change=(latest['close'] - prev['close']) / prev['close'] * 100,
                ma_trend='UP' if latest['MA5'] > latest['MA20'] else 'DOWN',
                rsi=latest['RSI'] if not pd.isna(latest['RSI']) else None,
                macd_signal='BUY' if latest['MACD'] > latest['Signal'] else 'SELL',
                volume_status='HIGH' if latest['Volume_Ratio'] > 1.5 else 'NORMAL',
                recommendation=self._get_recommendation(score)
            )

            logger.info(f"Analysis completed for {request.stock_code}")
            return report

        except Exception as e:
            logger.error(f"股票分析失败: {str(e)}", exc_info=True)
            raise

    def _calculate_ema(self, series: pd.Series, period: int) -> pd.Series:
        """计算指数移动平均线"""
        return series.ewm(span=period, adjust=False).mean()

    def _calculate_rsi(self, series: pd.Series, period: int) -> pd.Series:
        """计算RSI指标"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_macd(self, series: pd.Series) -> tuple:
        """计算MACD指标"""
        exp1 = series.ewm(span=12, adjust=False).mean()
        exp2 = series.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        return macd, signal, hist

    def _calculate_bollinger_bands(self, series: pd.Series, period: int, std_dev: int) -> tuple:
        """计算布林带"""
        middle = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower

    def _calculate_atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """计算ATR指标"""
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)

        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    def _calculate_score(self, df: pd.DataFrame) -> float:
        """计算评分"""
        try:
            score = 0
            latest = df.iloc[-1]

            # 趋势得分 (30分)
            if latest['MA5'] > latest['MA20']:
                score += 15
            if latest['MA20'] > latest['MA60']:
                score += 15

            # RSI得分 (20分)
            if 30 <= latest['RSI'] <= 70:
                score += 20
            elif latest['RSI'] < 30:  # 超卖
                score += 15

            # MACD得分 (20分)
            if latest['MACD'] > latest['Signal']:
                score += 20

            # 成交量得分 (30分)
            if latest['Volume_Ratio'] > 1.5:
                score += 30
            elif latest['Volume_Ratio'] > 1:
                score += 15

            logger.debug(f"Calculated score breakdown: {score}")
            return score

        except Exception as e:
            logger.error(f"计算评分时出错: {str(e)}", exc_info=True)
            raise

    def _get_recommendation(self, score: float) -> str:
        """根据得分给出建议"""
        if score >= 80:
            return '强烈推荐买入'
        elif score >= 60:
            return '建议买入'
        elif score >= 40:
            return '观望'
        elif score >= 20:
            return '建议卖出'
        else:
            return '强烈建议卖出'
