# 股票数据获取配置文件

# 关注的股票代码列表（可根据需要修改）
STOCK_CODES = [
    "601127",  #
    "603081",  #
    "002594",  # 比亚迪
    "300750",  # 宁德时代 
]

# 数据存储配置
DATA_DIR = "data"
LOG_DIR = "logs"

# 请求配置
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）
RETRY_TIMES = 3       # 重试次数
RETRY_DELAY = 1       # 重试间隔（秒）

# 数据更新频率（分钟）
UPDATE_INTERVAL = 5
