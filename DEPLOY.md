# Dify HTTP 服务部署指南

本文档详细说明了如何部署Dify HTTP服务。

## 环境要求

- Python 3.8+
- Docker（如果使用Docker部署）

## 方式一：直接运行

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

## 方式二：Docker部署

项目提供了基于Python 3.11.11的Docker部署方案。

### 构建Docker镜像
```bash
# 使用主机网络模式构建（解决依赖下载问题）
docker build --network=host -t dify-http-service:latest .
```

### 运行Docker容器
```bash
# 创建并运行容器
docker run -d \
  --name dify-http-service \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  dify-http-service:latest
```

### 查看容器日志
```bash
docker logs dify-http-service
```

### 停止和删除容器
```bash
docker stop dify-http-service
docker rm dify-http-service
```
