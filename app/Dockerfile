# 使用官方 Python 镜像作为基础
FROM python:3.9-slim

#防止python输出缓冲，确保日志实时可见
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app

# 复制依赖列表并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录下的所有代码到容器里
COPY . .

# 默认执行的命令（我们先让它什么都不做，或者跑个测试）
# 注意：这里我们不急着启动脚本，因为数据库启动需要几秒钟，我们后面在 compose 里处理
# RUN chmod +x ./start.sh
# CMD ["sh", "./start.sh"]
# CMD ["tail", "-f", "/dev/null"]
CMD ["python", "database.py"]
