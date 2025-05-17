import logging

from fastapi import APIRouter

from services.stock_analysis import StockAnalysisService, StockDataRequest
from utils.response import CustomResponse

# 配置日志
logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["stock analysis"],
    responses={404: {"description": "Not found"}},
)


@router.post("/analyze")
async def analyze_stock(request: StockDataRequest):
    """
    股票数据分析接口
    
    功能：
    - 对指定股票进行技术分析
    - 支持A股、港股、美股等市场
    - 返回K线数据和技术指标分析结果
    
    参数说明(StockDataRequest)：
    - stock_code (str): 股票代码，如'600519'或'00700.HK'
    - market_type (str): 市场类型，可选值: 'A'(A股), 'HK'(港股), 'US'(美股), 'ETF'(ETF基金), 'LOF'(LOF基金)
    - start_date (str): 开始日期，格式'YYYYMMDD'，
    - end_date (str): 结束日期，格式'YYYYMMDD'，
    
    返回数据：
    - 成功: 返回包含K线数据和技术指标的StockAnalysisResult对象
    - 失败: 返回错误信息
    
    错误码：
    - 400: 参数错误(股票代码无效/日期格式错误)
    - 500: 服务器内部错误
    
    示例请求：
    {
        "stock_code": "600519",
        "start_date": "20250101",
        "end_date": "20250517",
        "market_type": "A"
    }
    """
    try:
        logger.info(
            f"收到股票分析请求: stock_code={request.stock_code}, start_date={request.start_date}, "
            f"end_date={request.end_date}, market_type={request.market_type}")

        # 初始化分析服务
        service = StockAnalysisService()

        # 执行分析
        result = service.analyze_stock(request)

        logger.info(f"股票分析完成: stock_code={request.stock_code}, 分析结果={result}")

        return CustomResponse.success(data=result)

    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        return CustomResponse.error(message=f"参数错误: {str(e)}")
    except Exception as e:
        logger.error(f"分析失败: {str(e)}", exc_info=True)
        return CustomResponse.error(message=f"分析失败: {str(e)}")
