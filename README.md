# 股票数据获取工具

基于AkShare的轻量级股票数据获取工具，支持获取实时价格和历史数据。

## 功能特性

- 📈 **实时价格获取**：支持批量获取股票实时价格、涨跌幅等信息
- 📊 **历史数据获取**：支持获取股票历史K线数据
- 💾 **数据存储**：支持将数据保存为CSV格式，方便后续分析
- 🔄 **容错机制**：内置重试机制和错误处理，提高数据获取稳定性
- ⚙️ **灵活配置**：支持自定义股票列表和获取参数

## 安装依赖

```bash
# 安装Python依赖包
pip install -r requirements.txt
```

## 快速开始

### 1. 图形界面版本（推荐）

```bash
# 启动完整功能的图形界面
python stock_ui.py

# 或启动简化版图形界面
python simple_ui.py

# Windows用户也可以双击
启动界面.bat
```

### 2. 命令行版本

```bash
# 直接运行，查看功能演示
python main.py
```

### 3. 获取实时价格（命令行）

```bash
# 获取默认股票列表的实时价格
python main.py --mode realtime

# 获取指定股票的实时价格
python main.py --mode realtime --codes 000001 600036 600519

# 获取实时价格并保存到文件
python main.py --mode realtime --save
```

### 4. 获取历史数据（命令行）

```bash
# 获取默认股票列表的历史数据
python main.py --mode historical

# 获取指定时间段的历史数据
python main.py --mode historical --start 20240101 --end 20241101

# 同时获取实时和历史数据
python main.py --mode both --save
```

## 配置说明

在 `config.py` 文件中可以修改以下配置：

```python
# 关注的股票代码列表
STOCK_CODES = [
    "000001",  # 平安银行
    "600036",  # 招商银行
    "600519",  # 贵州茅台
    # ... 添加更多股票代码
]

# 请求配置
REQUEST_TIMEOUT = 10  # 请求超时时间
RETRY_TIMES = 3       # 重试次数
RETRY_DELAY = 1       # 重试间隔
```

## 编程接口使用

```python
from data_fetcher import StockDataFetcher

# 初始化数据获取器
fetcher = StockDataFetcher()

# 获取单只股票实时价格
price_data = fetcher.get_realtime_price("000001")
print(f"股票价格: {price_data['price']}")

# 获取历史数据
hist_data = fetcher.get_historical_data("000001")
print(f"历史数据条数: {len(hist_data)}")

# 批量获取多只股票数据
codes = ["000001", "600036", "600519"]
realtime_data = fetcher.get_multiple_stocks_realtime(codes)
historical_data = fetcher.get_multiple_stocks_historical(codes)
```

## 目录结构

```
stock_data_fetcher/
├── main.py              # 主程序入口
├── data_fetcher.py      # 数据获取核心模块
├── config.py           # 配置文件
├── requirements.txt    # 依赖包列表
├── README.md          # 说明文档
├── data/              # 数据存储目录（自动创建）
└── logs/              # 日志文件目录（自动创建）
```

## 数据说明

### 实时数据字段

- `code`: 股票代码
- `name`: 股票名称
- `price`: 最新价格
- `change`: 涨跌幅（%）
- `change_amount`: 涨跌额
- `volume`: 成交量
- `amount`: 成交额
- `high/low`: 最高/最低价
- `open`: 开盘价
- `yesterday_close`: 昨收价

### 历史数据字段

- `日期`: 交易日期
- `开盘/收盘`: 开盘/收盘价格
- `最高/最低`: 最高/最低价格
- `成交量`: 成交量
- `成交额`: 成交金额
- `涨跌幅`: 涨跌幅百分比
- `换手率`: 换手率

## 注意事项

1. **数据来源**：本工具使用AkShare获取数据，数据来源于公开的金融网站
2. **使用频率**：请适度使用，避免过于频繁的请求导致IP被限制
3. **数据准确性**：数据仅供参考，投资决策请以官方数据为准
4. **网络环境**：需要稳定的网络连接，建议在网络良好的环境下使用

## 后续扩展方向

- 添加更多技术指标计算
- 支持数据库存储（SQLite/MySQL）
- 实现数据可视化图表
- 添加股票筛选和预警功能
- 支持更多市场（港股、美股）

## 问题反馈

如遇到问题，请检查：
1. 网络连接是否正常
2. 依赖包是否正确安装
3. 股票代码格式是否正确
4. 查看logs目录下的日志文件获取详细错误信息
