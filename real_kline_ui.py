"""
真实数据K线界面
基于真实股票数据的K线图表系统
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time

# 设置matplotlib支持中文
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

from data_fetcher import StockDataFetcher

class RealKlineUI:
    def __init__(self, root, proxy_host: str = "127.0.0.1", proxy_port: int = 7890):
        self.root = root
        # 作为独立窗口时设置窗口属性；嵌入到父 Frame 时忽略
        try:
            self.root.title("真实数据K线图表")
            self.root.geometry("1200x800")
        except Exception:
            pass
        
        # 数据获取器 - 配置代理
        self.fetcher = StockDataFetcher(proxy_host=proxy_host, proxy_port=proxy_port)
        self.current_stock = "601127"
        
        # 数据存储
        self.current_data = None
        self.basic_info = None
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面组件"""
        
        # 顶部控制栏
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill="x")
        
        ttk.Label(control_frame, text="股票代码:", font=("Arial", 11)).pack(side="left")
        
        self.stock_var = tk.StringVar(value=self.current_stock)
        self.stock_entry = ttk.Entry(control_frame, textvariable=self.stock_var, width=10)
        self.stock_entry.pack(side="left", padx=(5, 15))
        
        ttk.Button(control_frame, text="获取数据", command=self.load_real_data, 
                  style="Accent.TButton").pack(side="left", padx=5)
        
        ttk.Button(control_frame, text="刷新", command=self.refresh_data).pack(side="left", padx=5)
        
        # 状态显示
        self.status_var = tk.StringVar(value="请选择股票并获取数据")
        ttk.Label(control_frame, textvariable=self.status_var, foreground="blue").pack(side="right")
        
        # 主要内容区域
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # 左侧：股票信息
        info_frame = ttk.LabelFrame(main_frame, text="股票信息", padding=10)
        info_frame.pack(side="left", fill="y", padx=(0, 10))
        info_frame.config(width=250)
        
        self.create_info_panel(info_frame)
        
        # 右侧：K线图表
        chart_frame = ttk.LabelFrame(main_frame, text="K线图表", padding=5)
        chart_frame.pack(side="right", fill="both", expand=True)
        
        self.create_chart_panel(chart_frame)
        
    def create_info_panel(self, parent):
        """创建信息面板"""
        
        # 基本信息
        basic_frame = ttk.LabelFrame(parent, text="基本信息", padding=10)
        basic_frame.pack(fill="x", pady=(0, 10))
        
        self.info_labels = {}
        info_items = [
            ("股票名称", "name"),
            ("股票代码", "code"),
            ("总市值", "market_cap"),
            ("流通市值", "float_cap"),
        ]
        
        for i, (display_name, key) in enumerate(info_items):
            frame = ttk.Frame(basic_frame)
            frame.pack(fill="x", pady=2)
            
            ttk.Label(frame, text=f"{display_name}:", font=("Arial", 9)).pack(side="left")
            
            var = tk.StringVar(value="--")
            self.info_labels[key] = var
            ttk.Label(frame, textvariable=var, font=("Arial", 9, "bold")).pack(side="right")
        
        # 最新数据信息
        latest_frame = ttk.LabelFrame(parent, text="最新交易数据", padding=10)
        latest_frame.pack(fill="x", pady=(0, 10))
        
        self.latest_labels = {}
        latest_items = [
            ("最新价格", "latest_price"),
            ("涨跌幅", "change_pct"),
            ("最高价", "high"),
            ("最低价", "low"),
            ("成交量", "volume"),
        ]
        
        for display_name, key in latest_items:
            frame = ttk.Frame(latest_frame)
            frame.pack(fill="x", pady=2)
            
            ttk.Label(frame, text=f"{display_name}:", font=("Arial", 9)).pack(side="left")
            
            var = tk.StringVar(value="--")
            self.latest_labels[key] = var
            label = ttk.Label(frame, textvariable=var, font=("Arial", 9, "bold"))
            label.pack(side="right")
            
            # 为涨跌幅设置颜色标识
            if key == "change_pct":
                self.change_label = label
        
        # 数据统计
        stats_frame = ttk.LabelFrame(parent, text="数据统计", padding=10)
        stats_frame.pack(fill="x")
        
        self.stats_labels = {}
        stats_items = [
            ("数据条数", "count"),
            ("数据范围", "date_range"),
            ("更新时间", "update_time"),
        ]
        
        for display_name, key in stats_items:
            frame = ttk.Frame(stats_frame)
            frame.pack(fill="x", pady=2)
            
            ttk.Label(frame, text=f"{display_name}:", font=("Arial", 8)).pack(side="left")
            
            var = tk.StringVar(value="--")
            self.stats_labels[key] = var
            ttk.Label(frame, textvariable=var, font=("Arial", 8)).pack(side="right")
            
    def create_chart_panel(self, parent):
        """创建图表面板"""
        
        # 创建matplotlib图形
        self.fig = Figure(figsize=(10, 8), dpi=100, facecolor='white')
        
        # K线图（占60%高度）
        self.ax_kline = self.fig.add_subplot(2, 1, 1)
        # 成交量图（占40%高度）  
        self.ax_volume = self.fig.add_subplot(2, 1, 2)
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # 初始化空图表
        self.init_empty_chart()
        
    def init_empty_chart(self):
        """初始化空图表"""
        self.ax_kline.clear()
        self.ax_volume.clear()
        
        self.ax_kline.text(0.5, 0.5, '请选择股票并获取数据\n点击"获取数据"按钮开始', 
                          ha='center', va='center', transform=self.ax_kline.transAxes, 
                          fontsize=14, color='gray')
        
        self.ax_volume.text(0.5, 0.5, '成交量数据将在此显示', 
                           ha='center', va='center', transform=self.ax_volume.transAxes, 
                           fontsize=12, color='gray')
        
        self.canvas.draw()
        
    def load_real_data(self):
        """加载真实数据"""
        stock_code = self.stock_var.get().strip()
        if not stock_code:
            messagebox.showwarning("输入错误", "请输入股票代码")
            return
            
        # 在新线程中加载数据
        threading.Thread(target=self.load_data_thread, args=(stock_code,), daemon=True).start()
        
    def load_data_thread(self, stock_code):
        """数据加载线程"""
        try:
            self.current_stock = stock_code
            self.update_status("正在获取数据...")
            
            # 1. 获取基本信息
            self.update_status("获取基本信息...")
            basic_info = self.fetcher.get_stock_info(stock_code)
            
            if basic_info:
                self.basic_info = basic_info
                self.root.after(0, self.update_basic_info)
            else:
                self.root.after(0, lambda: self.update_status("获取基本信息失败"))
                return
            
            # 2. 获取历史数据
            self.update_status("获取历史K线数据...")
            hist_data = self.fetcher.get_historical_data(stock_code)
            
            if hist_data is not None and not hist_data.empty:
                self.current_data = hist_data
                self.root.after(0, self.update_latest_data)
                self.root.after(0, self.update_stats)
                self.root.after(0, self.draw_real_chart)
                self.root.after(0, lambda: self.update_status("数据加载完成"))
            else:
                self.root.after(0, lambda: self.update_status("获取历史数据失败"))
                
        except Exception as e:
            print(f"数据加载错误: {e}")
            msg = str(e)[:100]
            self.root.after(0, lambda: self.update_status(f"数据加载失败"))
            
    def update_basic_info(self):
        """更新基本信息显示"""
        if not self.basic_info:
            return
            
        try:
            # 更新基本信息
            self.info_labels["name"].set(self.basic_info.get('股票简称', '--'))
            self.info_labels["code"].set(self.current_stock)
            
            # 格式化市值显示
            total_mv = self.basic_info.get('总市值', 0)
            if isinstance(total_mv, (int, float)) and total_mv > 0:
                mv_yi = total_mv / 100000000
                self.info_labels["market_cap"].set(f"{mv_yi:.2f} 亿元")
            else:
                self.info_labels["market_cap"].set("--")
            
            float_mv = self.basic_info.get('流通市值', 0)
            if isinstance(float_mv, (int, float)) and float_mv > 0:
                fmv_yi = float_mv / 100000000
                self.info_labels["float_cap"].set(f"{fmv_yi:.2f} 亿元")
            else:
                self.info_labels["float_cap"].set("--")
                
        except Exception as e:
            print(f"更新基本信息错误: {e}")
            
    def update_latest_data(self):
        """更新最新交易数据"""
        if self.current_data is None or self.current_data.empty:
            return
            
        try:
            # 获取最新一条数据
            latest = self.current_data.iloc[-1]
            
            # 更新最新交易数据
            self.latest_labels["latest_price"].set(f"{latest['收盘']:.2f}")
            
            # 涨跌幅颜色设置
            change_pct = float(latest['涨跌幅'])
            self.latest_labels["change_pct"].set(f"{change_pct:+.2f}%")
            
            if change_pct > 0:
                self.change_label.configure(foreground="red")
            elif change_pct < 0:
                self.change_label.configure(foreground="green")
            else:
                self.change_label.configure(foreground="black")
            
            self.latest_labels["high"].set(f"{latest['最高']:.2f}")
            self.latest_labels["low"].set(f"{latest['最低']:.2f}")
            
            # 格式化成交量
            volume = int(latest['成交量'])
            if volume >= 10000:
                volume_str = f"{volume/10000:.1f}万"
            else:
                volume_str = f"{volume:,}"
            self.latest_labels["volume"].set(volume_str)
            
        except Exception as e:
            print(f"更新最新数据错误: {e}")
            
    def update_stats(self):
        """更新数据统计"""
        if self.current_data is None or self.current_data.empty:
            return
            
        try:
            # 数据条数
            self.stats_labels["count"].set(str(len(self.current_data)))
            
            # 数据范围
            start_date = str(self.current_data.iloc[0]['日期'])[:10]
            end_date = str(self.current_data.iloc[-1]['日期'])[:10]
            self.stats_labels["date_range"].set(f"{start_date} 至 {end_date}")
            
            # 更新时间
            self.stats_labels["update_time"].set(datetime.now().strftime("%H:%M:%S"))
            
        except Exception as e:
            print(f"更新统计信息错误: {e}")
            
    def draw_real_chart(self):
        """绘制真实数据图表"""
        if self.current_data is None or self.current_data.empty:
            return
            
        try:
            # 清空图表
            self.ax_kline.clear()
            self.ax_volume.clear()
            
            # 准备数据
            df = self.current_data.copy()
            
            # 确保日期列格式正确
            if '日期' in df.columns:
                df['日期'] = pd.to_datetime(df['日期'])
                # 重置索引，使用连续的数字索引
                df = df.reset_index(drop=True)
            
            # 只显示最近30根K线，避免图表过于拥挤
            if len(df) > 30:
                df = df.tail(30).reset_index(drop=True)
            
            # 绘制K线图
            self.draw_kline_bars(df)
            
            # 绘制成交量
            self.draw_volume_bars(df)
            
            # 设置图表样式
            self.setup_chart_style(df)
            
            # 刷新画布
            self.canvas.draw()
            
        except Exception as e:
            print(f"绘制图表错误: {e}")
            self.update_status(f"绘制图表失败: {str(e)}")
            
    def draw_kline_bars(self, df):
        """绘制K线柱"""
        try:
            for i in range(len(df)):
                row = df.iloc[i]
                
                # 安全转换数值，处理可能的数据类型问题
                try:
                    open_price = float(row['开盘'])
                    high_price = float(row['最高'])
                    low_price = float(row['最低'])
                    close_price = float(row['收盘'])
                except (ValueError, KeyError) as e:
                    print(f"数据转换错误 第{i}行: {e}")
                    continue
                
                # 确定K线颜色（中国习惯：红涨绿跌）
                if close_price >= open_price:
                    color = '#FF0000'  # 红色
                    edge_color = '#CC0000'
                else:
                    color = '#00AA00'  # 绿色
                    edge_color = '#008800'
                
                # 绘制上下影线
                self.ax_kline.plot([i, i], [low_price, high_price], 
                                  color='black', linewidth=1, solid_capstyle='round')
                
                # 绘制K线实体
                body_height = abs(close_price - open_price)
                body_bottom = min(open_price, close_price)
                
                if body_height > 0.01:  # 避免过小的实体
                    # 有实体的K线
                    from matplotlib.patches import Rectangle
                    rect = Rectangle((i-0.4, body_bottom), 0.8, body_height,
                                   facecolor=color, edgecolor=edge_color, 
                                   alpha=0.8, linewidth=0.5)
                    self.ax_kline.add_patch(rect)
                else:
                    # 十字星（开盘价=收盘价）
                    self.ax_kline.plot([i-0.4, i+0.4], [close_price, close_price], 
                                     color=color, linewidth=2)
        except Exception as e:
            print(f"绘制K线错误: {e}")
                                 
    def draw_volume_bars(self, df):
        """绘制成交量柱状图"""
        try:
            volumes = []
            colors = []
            
            for i in range(len(df)):
                row = df.iloc[i]
                
                try:
                    volume = float(row['成交量'])
                    open_price = float(row['开盘'])
                    close_price = float(row['收盘'])
                    
                    volumes.append(volume)
                    # 成交量柱颜色与K线一致
                    color = '#FF0000' if close_price >= open_price else '#00AA00'
                    colors.append(color)
                    
                except (ValueError, KeyError) as e:
                    print(f"成交量数据错误 第{i}行: {e}")
                    volumes.append(0)
                    colors.append('#CCCCCC')
            
            # 批量绘制成交量柱
            bars = self.ax_volume.bar(range(len(volumes)), volumes, 
                                     width=0.8, color=colors, alpha=0.7)
            
        except Exception as e:
            print(f"绘制成交量错误: {e}")
            
    def setup_chart_style(self, df):
        """设置图表样式"""
        try:
            # K线图设置
            stock_name = self.info_labels["name"].get()
            title = f"{self.current_stock} {stock_name} - 真实K线数据"
            
            self.ax_kline.set_title(title, fontsize=14, fontweight='bold', pad=15)
            self.ax_kline.set_ylabel("价格 (元)", fontsize=11)
            self.ax_kline.grid(True, alpha=0.3, linestyle='--')
            
            # 成交量图设置
            self.ax_volume.set_ylabel("成交量", fontsize=11)
            self.ax_volume.set_xlabel("交易日期", fontsize=11)
            self.ax_volume.grid(True, alpha=0.3, linestyle='--')
            
            # 设置X轴标签 - 修复坐标问题
            if len(df) > 0 and '日期' in df.columns:
                # 确定标签间隔，避免过于密集
                total_bars = len(df)
                if total_bars <= 10:
                    step = 1
                elif total_bars <= 20:
                    step = 2
                else:
                    step = max(1, total_bars // 8)
                
                # 生成X轴位置和标签
                x_positions = list(range(0, total_bars, step))
                x_labels = []
                
                for pos in x_positions:
                    if pos < len(df):
                        try:
                            date_obj = df.iloc[pos]['日期']
                            if pd.isna(date_obj):
                                x_labels.append('')
                            else:
                                # 处理日期格式
                                if isinstance(date_obj, str):
                                    date_obj = pd.to_datetime(date_obj)
                                x_labels.append(date_obj.strftime('%m-%d'))
                        except Exception as e:
                            print(f"日期格式处理错误: {e}")
                            x_labels.append(f"Day{pos+1}")
                
                # 设置X轴刻度 - 留出右边空间以显示完整的K线
                self.ax_kline.set_xlim(-1, total_bars)
                self.ax_kline.set_xticks(x_positions)
                self.ax_kline.set_xticklabels(x_labels, rotation=45, ha='right')
                
                self.ax_volume.set_xlim(-1, total_bars)
                self.ax_volume.set_xticks(x_positions)
                self.ax_volume.set_xticklabels(x_labels, rotation=45, ha='right')
                
                # 设置Y轴格式
                self.ax_kline.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.2f}'))
                self.ax_volume.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
            
            # 调整布局 - 增加右边距
            self.fig.tight_layout(rect=[0, 0.03, 0.95, 0.97])
            self.fig.subplots_adjust(right=0.92)
            
        except Exception as e:
            print(f"设置图表样式错误: {e}")
        
    def refresh_data(self):
        """刷新当前数据"""
        if self.current_stock:
            self.load_real_data()
        else:
            messagebox.showinfo("提示", "请先选择股票代码")
            
    def update_status(self, message):
        """更新状态显示"""
        self.status_var.set(message)

def main():
    """主程序入口"""
    root = tk.Tk()
    
    # 设置窗口样式
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    
    # 使用代理配置创建应用
    # 代理地址：127.0.0.1:7890
    app = RealKlineUI(root, proxy_host="127.0.0.1", proxy_port=7890)
    
    # 居中显示窗口
    root.update_idletasks()
    width = 1200
    height = 800
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
