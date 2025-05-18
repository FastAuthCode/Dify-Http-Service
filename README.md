# Dify HTTP 服务项目

## 项目简介

这是一个基于FastAPI的HTTP服务项目，提供AI新闻爬取和股票数据分析功能。项目采用模块化设计，包含API端点、服务层和核心功能模块。

## 主要功能

### 1. AI新闻爬取
- 从AIbase网站抓取最新AI相关新闻
- 返回新闻标题、内容和发布日期
- 支持限制返回新闻数量

### 2. 股票数据分析
- 支持A股、港股、美股市场
- 提供K线数据和技术指标分析
- 支持MACD、KDJ、RSI等指标

## 技术栈

- Python 3.8+
- FastAPI (Web框架)
- Requests (HTTP客户端)
- BeautifulSoup4 (HTML解析)
- Pydantic (数据验证)
- Logging (日志记录)

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行服务
```bash
uvicorn main:app --reload
```

### 环境配置
复制.env.example文件并重命名为.env，根据需要进行配置：
```bash
cp .env.example .env
```

> **注意**：详细的部署说明（包括Docker部署方式）请参考项目根目录下的[部署文档](DEPLOY.md)文件。

## API文档

### 新闻爬取API
`GET /api/v1/news`
- 参数: `limit` (返回新闻数量，1-20)
- 示例: `/api/v1/news?limit=5`

### 股票分析API
`POST /api/v1/analyze`
- 请求体:
```json
{
    "stock_code": "600000",
    "start_date": "20230101",
    "end_date": "20231231",
    "market_type": "A股"
   
}
```

## 项目结构

```
.
├── api/              # API端点
├── core/             # 核心功能
├── services/         # 业务服务
├── utils/            # 工具类
├── main.py           # 应用入口
├── requirements.txt  # Python依赖
└── README.md         # 项目文档
```

## 贡献指南

1. Fork项目仓库
2. 创建特性分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -am 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建Pull Request

## 许可证

MIT License
