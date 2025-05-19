from fastapi import APIRouter, Query
from services.news_crawler import NewsCrawler
from utils.response import CustomResponse
import logging

router = APIRouter(
    tags=["news crawler"],
    responses={404: {"description": "Not found"}},
)

# 配置日志
logger = logging.getLogger(__name__)


@router.get("/news")
async def get_news(
        limit: int = Query(
            default=5,
            description="返回的新闻数量，范围1-20",
            ge=1,
            le=20,
            example=5
        )
):
    """
    ## 获取AI新闻数据
    
    ### 功能
    - 从AIbase网站抓取最新的AI相关新闻
    - 返回新闻标题、内容、发布日期等信息
    
    ### 参数
    - `limit`: 控制返回的新闻数量(1-20条)
    
    ### 返回数据结构
    ```json
    {
        "success": true,
        "code": 200,
        "message": "success",
        "data": {
            "news": [
                {
                    "title": "新闻标题",
                    "publication_date": "发布日期",
                    "content": "新闻内容"
                }
            ],
            "news_detail": "拼接后的新闻详情字符串"
        }
    }
    ```
    
    ### 错误码
    - 400: 参数错误
    - 500: 服务器内部错误
    
    ### 使用示例
    ```
    GET /api/v1/news?limit=3
    ```
    """
    try:
        result = await NewsCrawler.fetch_news(limit)
        return CustomResponse.success(data=result)
    except Exception as e:
        logger.error(f"获取新闻失败: {str(e)}", exc_info=True)
        return CustomResponse.error(data=str(e))
