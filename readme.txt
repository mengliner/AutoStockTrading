stock_data_project/
├── .env                # 环境变量（敏感配置，不提交git）
├── .gitignore          # git忽略文件（.env、__pycache__、数据文件等）
├── README.md           # 项目说明（环境搭建、运行方式、配置说明）
├── requirements.txt    # 依赖清单
├── config/             # 配置层：统一管理所有配置 所有配置集中管理，通过.env 解耦敏感信息	
│   ├── __init__.py
│   ├── db_config.py    # 数据库配置
│   └── tushare_config.py # Tushare配置（可合并到db_config）
├── db/                 # 数据持久层：仅处理数据库操作 仅封装数据库连接、CRUD，与业务逻辑解耦
│   ├── __init__.py
│   ├── base_client.py  # 基础数据库连接封装（可选，抽离通用逻辑）
│   └── mysql_client.py # MySQL具体操作
├── data/               # 数据获取层：对接外部数据源 仅对接外部数据源（Tushare / 新浪财经等）
│   ├── __init__.py
│   ├── tushare_client.py # Tushare数据获取
│   └── data_clean.py   # 数据清洗工具（可选，复杂清洗逻辑抽离）
├── service/            # 业务逻辑层：核心业务处理（扩展用） 处理核心业务（如数据增量更新、指标计算）
│   ├── __init__.py
│   ├── stock_basic_service.py # 股票基础数据业务
│   └── daily_k_service.py     # 日K线数据业务
├── utils/              # 工具层：通用工具函数 通用工具（日志、时间、数据校验）
│   ├── __init__.py
│   ├── log_utils.py    # 日志配置
│   └── time_utils.py   # 时间处理工具
└── main.py             # 入口文件：整合所有逻辑