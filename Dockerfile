FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# 复制项目文件
COPY . .

# 设置环境变量
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 8000

# 设置启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run:app"]
