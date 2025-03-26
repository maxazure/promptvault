FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 确保安装必要的包
RUN pip install --no-cache-dir gunicorn PyMySQL

# 复制项目文件
COPY . .

# 设置环境变量
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 8000

# 设置启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run:app"]
