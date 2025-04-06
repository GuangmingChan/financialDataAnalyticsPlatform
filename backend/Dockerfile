FROM python:3.9-slim

WORKDIR /app

# 先只复制依赖文件 - 这样只有依赖变化时才会重新构建这一层
COPY requirements.txt .

RUN echo "deb https://mirrors.aliyun.com/debian/ bookworm main" > /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian-security/ bookworm-security main" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bookworm-updates main" >> /etc/apt/sources.list && \
    rm -f /etc/apt/sources.list.d/*.list  && \
    apt-get update && apt-get install -y \
    build-essential \
    wget fonts-noto-cjk fonts-wqy-microhei fonts-wqy-zenhei\
    && rm -rf /var/lib/apt/lists/* \
    # 安装 TA-Lib
    && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xvzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib/ \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib-0.4.0-src.tar.gz ta-lib/ 

# 尝试多个镜像源，设置重试和超时
RUN pip install --upgrade pip && \
    # 临时注释掉ta-lib安装，因为我们已经在系统层面安装了C库
    sed -i 's/ta-lib==/#ta-lib==/g' requirements.txt && \
    pip install --no-cache-dir \
    --retries 5 \
    --timeout 60 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    -r requirements.txt || \
    pip install --no-cache-dir \
    --retries 5 \
    --timeout 60 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple/ \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    -r requirements.txt || \
    pip install --no-cache-dir \
    --retries 5 \
    --timeout 60 \
    -r requirements.txt

# 在依赖安装完成后手动安装TA-Lib
RUN pip install --no-cache-dir \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    TA-Lib==0.4.24 || \
    pip install --no-cache-dir \
    -i https://pypi.tuna.tsinghua.edu.cn/simple/ \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    TA-Lib==0.4.24 || \
    pip install --no-cache-dir TA-Lib==0.4.24

# 最后才复制项目文件 - 这样代码变化不会触发重新安装依赖
COPY . .

# 设置Python路径
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8002

# 修改启动命令，确保使用正确的入口文件
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]