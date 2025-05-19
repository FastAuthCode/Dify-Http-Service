import json
import logging
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class NewsArticle(BaseModel):
    """单篇新闻数据模型"""
    title: str
    publication_date: str
    content: str


class NewsCrawler:
    """新闻爬取服务"""

    BASE_URL = "https://www.aibase.com/zh/news"

    @staticmethod
    def get_news_urls(proxy: Optional[str] = None) -> List[str]:
        """获取新闻列表页面的所有新闻URL
        Args:
            proxy: 代理服务器地址，格式为"http://ip:port"或"https://ip:port"
        """
        logger.info(f"开始获取新闻列表: {NewsCrawler.BASE_URL}")
        try:
            response = requests.get(NewsCrawler.BASE_URL, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            news_urls = []

            # 查找所有新闻链接
            news_items = soup.find_all('a', href=True)
            for item in news_items:
                link = item['href']
                # 过滤出符合新闻详情页的链接
                if '/news/' in link and len(link.split('/')) > 2:
                    full_url = f"https://www.aibase.com/zh{link}"
                    news_urls.append(full_url)

            logger.info(f"共找到 {len(news_urls)} 条新闻链接")
            return news_urls

        except Exception as e:
            logger.error(f"获取新闻列表失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def fetch_news(limit: int = 5) -> list[NewsArticle]:
        """获取新闻数据"""
        logger.info(f"开始获取新闻，限制数量: {limit}")

        try:
            news_urls = NewsCrawler.get_news_urls()
            news_urls = news_urls[:limit]
            news_data = []

            for index, url in enumerate(news_urls, start=1):
                article_data = await NewsCrawler.extract_article(url)
                if article_data:
                    article = NewsArticle(
                        title=article_data.get("title", "无标题"),
                        publication_date=article_data.get("publication_date", "未知日期"),
                        content=article_data.get("content", "无法提取内容")
                    )
                    news_data.append(article)

            return news_data

        except Exception as e:
            logger.error(f"获取新闻数据失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def extract_article(url: str, proxy: Optional[str] = None) -> Optional[NewsArticle]:
        """提取单个新闻文章的数据
        Args:
            url: 新闻文章URL
            proxy: 代理服务器地址，格式为"http://ip:port"或"https://ip:port"
        """
        logger.info(f"开始提取新闻文章: {url}")

        try:
            proxies = {"http": proxy, "https": proxy} if proxy else None
            response = requests.get(url, timeout=10, proxies=proxies)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            extracted_data = {
                "title": soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else "无标题",
                "publication_date": soup.select_one(
                    'div.flex.flex-col > div.flex.flex-wrap > span:nth-child(6)').get_text(strip=True)
                if soup.select_one('div.flex.flex-col > div.flex.flex-wrap > span:nth-child(6)')
                else "未知日期",
                "content": soup.select_one('div.post-content').get_text(strip=True)
                if soup.select_one('div.post-content')
                else "无法提取内容"
            }
            result = type('', (), {'extracted_content': json.dumps([extracted_data]), 'success': True})()

            if not result.success:
                logger.warning(f"页面爬取失败: {url}")
                return None

            extracted_data = json.loads(result.extracted_content)
            logger.info(f"成功提取新闻: {extracted_data[0]['title']}")
            return extracted_data[0]

        except Exception as e:
            logger.error(f"提取新闻文章失败: {url} - {str(e)}", exc_info=True)
            raise
