# 金融大数据虚拟仿真实验平台

基于金融大数据的新商科虚拟仿真实验平台，支持银行、证券、保险等金融领域的实验教学。

## 功能特点

- 支持60人同时在线操作
- 提供完整的金融数据分析流程
- 包含多个实验模块（银行、证券、保险）
- 实时数据分析和可视化
- 完整的教学评价体系

## 技术栈

- 后端：Python FastAPI
- 数据库：PostgreSQL
- 缓存：Redis
- 数据分析：Pandas, NumPy, TA-Lib
- 机器学习：Scikit-learn
- 前端：Vue.js 3, Element Plus
- 可视化：ECharts, D3.js

## 系统要求

- Docker
- Docker Compose
- 4GB+ RAM
- 20GB+ 磁盘空间

## 快速开始

1. 克隆项目
```bash
git clone https://github.com/yourusername/finance_platform.git
cd finance_platform
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

3. 启动服务
```bash
docker-compose up -d
```

4. 访问系统
打开浏览器访问 http://localhost:8000

## 项目结构

```
finance_platform/
├── backend/                # 后端代码
│   ├── app/               # 应用代码
│   │   ├── api/          # API路由
│   │   ├── core/         # 核心配置
│   │   ├── models/       # 数据模型
│   │   ├── services/     # 业务逻辑
│   │   └── utils/        # 工具函数
│   ├── tests/            # 测试代码
│   └── requirements.txt  # Python依赖
├── frontend/             # 前端代码
├── data/                # 示例数据
├── docker-compose.yml   # Docker配置
└── README.md           # 项目文档
```

## 实验模块

### 银行模块
- 银行信贷风险控制
- 信用卡客户贷款违约分析

### 证券模块
- 股票可视分析
- 技术指标分析
- 投资组合分析
- 量化交易策略

### 保险模块
- 车险索赔率分析
- 医疗保险精准营销

## 开发指南

1. 安装开发依赖
```bash
pip install -r requirements.txt
```

2. 运行测试
```bash
pytest
```

3. 代码格式化
```bash
black .
```

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License