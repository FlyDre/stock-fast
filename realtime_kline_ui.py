"""
实时K线图表界面
提供比同花顺更快的数据更新和清晰的图表展示
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time

from data_fetcher import StockDataFetcher

class RealtimeKlineUI:
    def __init__(self, root):
        self.root = root
        self.root.title("实时K线图表 - 高频更新")
        self.root.geometry("1200x800")
        self.root.state('zoomed')  # 最大化窗口
        
        # 数据相关
        self.fetcher = StockDataFetcher()
        self.current_stock = "601127"
        self.update_interval = 30  # 30秒更新一次，比同花顺更快
        self.is_updating = False
        self.update_thread = None
        
        # 存储数据
        self.kline_data = pd.DataFrame()
        self.realtime_prices = []
        self.price_timestamps = []
        
        # 创建界面
        self.create_widgets()
        self.setup_matplotlib_style()
        
    def create_widgets(self):
        """创建界面组件"""
        
        # 顶部控制栏
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill="x", side="top")
        
        # 股票选择
        ttk.Label(control_frame, text="股票代码:", font=("Arial", 11)).pack(side="left")
        
        self.stock_var = tk.StringVar(value=self.current_stock)
        self.stock_entry = ttk.Entry(control_frame, textvariable=self.stock_var, width=10, font=("Arial", 11))
        self.stock_entry.pack(side="left", padx=(5, 10))
        
        # 更新频率选择
        ttk.Label(control_frame, text="更新间隔:", font=("Arial", 11)).pack(side="left", padx=(20, 5))
        
        self.interval_var = tk.StringVar(value="30秒")
        interval_combo = ttk.Combobox(control_frame, textvariable=self.interval_var, 
                                     values=["15秒", "30秒", "60秒"], width=8, state="readonly")
        interval_combo.pack(side="left", padx=(0, 10))
        interval_combo.bind('<<ComboboxSelected>>', self.on_interval_change)
        
        # 控制按钮
        self.start_btn = ttk.Button(control_frame, text="开始实时更新", 
                                   command=self.start_realtime_update, style="Accent.TButton")
        self.start_btn.pack(side="left", padx=(10, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="停止更新", 
                                  command=self.stop_realtime_update, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        ttk.Button(control_frame, text="刷新图表", command=self.refresh_chart).pack(side="left", padx=5)
        
        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(control_frame, textvariable=self.status_var, foreground="blue").pack(side="right")
        
        # 主内容区域
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # 左侧：K线图表
        chart_frame = ttk.LabelFrame(main_frame, text="K线图表", padding=5)
        chart_frame.pack(side="left", fill="both", expand=True)
        
        # 创建matplotlib图表
        self.create_chart(chart_frame)
        
        # 右侧：数据信息
        info_frame = ttk.LabelFrame(main_frame, text="实时信息", padding=10)
        info_frame.pack(side="right", fill="y", padx=(10, 0))
        info_frame.config(width=300)
        
        self.create_info_panel(info_frame)
        
    def create_chart(self, parent):
        """创建K线图表"""
        # 创建matplotlib图形
        self.fig = Figure(figsize=(10, 8), dpi=100, facecolor='white')
        self.ax1 = self.fig.add_subplot(2, 1, 1)  # K线图
        self.ax2 = self.fig.add_subplot(2, 1, 2)  # 成交量
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # 初始化图表
        self.init_empty_chart()
        
    def setup_matplotlib_style(self):
        """设置matplotlib样式"""
        plt.style.use('default')
        self.fig.patch.set_facecolor('white')
        
    def init_empty_chart(self):
        """初始化空图表"""
        self.ax1.clear()
        self.ax2.clear()
        
        self.ax1.set_title(f"{self.current_stock} 实时K线图", fontsize=14, fontweight='bold')
        self.ax1.set_ylabel("价格 (元)", fontsize=10)
        self.ax1.grid(True, alpha=0.3)
        
        self.ax2.set_ylabel("成交量", fontsize=10)
        self.ax2.set_xlabel("时间", fontsize=10)
        self.ax2.grid(True, alpha=0.3)
        
        self.canvas.draw()
        
    def create_info_panel(self, parent):
        """创建信息面板"""
        # 股票基本信息
        basic_frame = ttk.LabelFrame(parent, text="基本信息", padding=10)
        basic_frame.pack(fill="x", pady=(0, 10))
        
        self.stock_name_var = tk.StringVar(value="--")
        self.current_price_var = tk.StringVar(value="--")
        self.change_var = tk.StringVar(value="--")
        self.volume_var = tk.StringVar(value="--")
        
        info_items = [
            ("股票名称:", self.stock_name_var),
            ("当前价格:", self.current_price_var),
            ("涨跌幅:", self.change_var),
            ("成交量:", self.volume_var),
        ]
        
        for i, (label, var) in enumerate(info_items):
            ttk.Label(basic_frame, text=label, font=("Arial", 9)).grid(row=i, column=0, sticky="w", pady=2)
            ttk.Label(basic_frame, textvariable=var, font=("Arial", 9, "bold")).grid(row=i, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # 实时价格动态
        realtime_frame = ttk.LabelFrame(parent, text="价格动态", padding=10)
        realtime_frame.pack(fill="x", pady=(0, 10))
        
        self.price_listbox = tk.Listbox(realtime_frame, height=8, font=("Courier", 9))
        scrollbar = ttk.Scrollbar(realtime_frame, orient="vertical", command=self.price_listbox.yview)
        self.price_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.price_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 更新统计
        stats_frame = ttk.LabelFrame(parent, text="更新统计", padding=10)
        stats_frame.pack(fill="x")
        
        self.update_count_var = tk.StringVar(value="0")
        self.last_update_var = tk.StringVar(value="--")
        
        ttk.Label(stats_frame, text="更新次数:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Label(stats_frame, textvariable=self.update_count_var, font=("Arial", 9, "bold")).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(stats_frame, text="最后更新:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(stats_frame, textvariable=self.last_update_var, font=("Arial", 8)).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)
        
    def on_interval_change(self, event=None):
        """更新间隔改变"""
        interval_text = self.interval_var.get()
        if "15秒" in interval_text:
            self.update_interval = 15
        elif "30秒" in interval_text:
            self.update_interval = 30
        elif "60秒" in interval_text:
            self.update_interval = 60
            
    def start_realtime_update(self):
        """开始实时更新"""
        self.current_stock = self.stock_var.get().strip()
        if not self.current_stock:
            messagebox.showwarning("输入错误", "请输入股票代码")
            return
            
        if self.is_updating:
            return
            
        self.is_updating = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        # 启动更新线程
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        
        self.update_status(f"开始实时更新 {self.current_stock} (间隔: {self.update_interval}秒)")
        
    def stop_realtime_update(self):
        """停止实时更新"""
        self.is_updating = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.update_status("已停止更新")
        
    def update_loop(self):
        """更新循环"""
        update_count = 0
        
        # 首次加载历史数据
        self.load_historical_data()
        
        while self.is_updating:
            try:
                update_count += 1
                
                # 模拟获取实时价格（实际场景中这里会调用实时API）
                self.simulate_realtime_price()
                
                # 更新图表
                self.root.after(0, self.update_chart)
                
                # 更新统计信息
                self.root.after(0, lambda: self.update_count_var.set(str(update_count)))
                self.root.after(0, lambda: self.last_update_var.set(datetime.now().strftime("%H:%M:%S")))
                
                # 等待下次更新
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"更新错误: {str(e)}"))
                break
                
    def load_historical_data(self):
        """加载历史数据"""
        try:
            self.update_status("加载历史数据...")
            
            # 获取历史数据
            hist_data = self.fetcher.get_historical_data(self.current_stock)
            if hist_data is not None:
                self.kline_data = hist_data.tail(50)  # 只取最近50根K线
                
                # 获取基本信息
                info = self.fetcher.get_stock_info(self.current_stock)
                if info:
                    self.root.after(0, lambda: self.stock_name_var.set(info.get('股票简称', '--')))
                    
            self.update_status("历史数据加载完成")
            
        except Exception as e:
            self.update_status(f"历史数据加载失败: {str(e)}")
            
    def simulate_realtime_price(self):
        """模拟实时价格数据（演示用）"""
        if self.kline_data.empty:
            return
            
        # 基于最后价格生成模拟实时价格
        last_price = float(self.kline_data.iloc[-1]['收盘'])
        
        # 随机波动 ±1%
        change_percent = np.random.uniform(-0.01, 0.01)
        new_price = last_price * (1 + change_percent)
        
        current_time = datetime.now()
        
        # 存储实时价格点
        self.realtime_prices.append(new_price)
        self.price_timestamps.append(current_time)
        
        # 只保留最近100个价格点
        if len(self.realtime_prices) > 100:
            self.realtime_prices = self.realtime_prices[-100:]
            self.price_timestamps = self.price_timestamps[-100:]
            
        # 更新实时信息
        change_amount = new_price - last_price
        change_percent = (change_amount / last_price) * 100
        
        self.root.after(0, lambda: self.current_price_var.set(f"{new_price:.2f}"))
        self.root.after(0, lambda: self.change_var.set(f"{change_percent:+.2f}%"))
        
        # 添加价格动态记录
        time_str = current_time.strftime("%H:%M:%S")
        price_text = f"{time_str} {new_price:.2f} ({change_percent:+.2f}%)"
        
        self.root.after(0, lambda: self.add_price_record(price_text))
        
    def add_price_record(self, text):
        """添加价格记录"""
        self.price_listbox.insert(0, text)
        if self.price_listbox.size() > 20:
            self.price_listbox.delete(20, tk.END)
            
    def update_chart(self):
        """更新图表"""
        if self.kline_data.empty:
            return
            
        try:
            # 清空图表
            self.ax1.clear()
            self.ax2.clear()
            
            # 绘制K线图
            self.draw_kline()
            
            # 绘制实时价格线
            if len(self.realtime_prices) > 1:
                self.draw_realtime_line()
            
            # 绘制成交量
            self.draw_volume()
            
            # 设置图表样式
            self.setup_chart_style()
            
            # 刷新画布
            self.canvas.draw()
            
        except Exception as e:
            self.update_status(f"图表更新失败: {str(e)}")
            
    def draw_kline(self):
        """绘制K线图"""
        df = self.kline_data.copy()
        
        # 转换日期
        df['日期'] = pd.to_datetime(df['日期'])
        
        # 绘制K线
        for i, row in df.iterrows():
            date = mdates.date2num(row['日期'])
            open_price = float(row['开盘'])
            high_price = float(row['最高'])
            low_price = float(row['最低'])
            close_price = float(row['收盘'])
            
            # 确定颜色
            color = 'red' if close_price >= open_price else 'green'
            
            # 绘制影线
            self.ax1.plot([date, date], [low_price, high_price], color='black', linewidth=1)
            
            # 绘制实体
            height = abs(close_price - open_price)
            bottom = min(open_price, close_price)
            
            rect = Rectangle((date - 0.3, bottom), 0.6, height, 
                           facecolor=color, alpha=0.7, edgecolor='black', linewidth=0.5)
            self.ax1.add_patch(rect)
            
    def draw_realtime_line(self):
        """绘制实时价格线"""
        if len(self.realtime_prices) < 2:
            return
            
        # 转换时间戳
        timestamps = [mdates.date2num(ts) for ts in self.price_timestamps]
        
        # 绘制实时价格线
        self.ax1.plot(timestamps, self.realtime_prices, 'blue', linewidth=2, alpha=0.8, label='实时价格')
        self.ax1.legend()
        
    def draw_volume(self):
        """绘制成交量"""
        df = self.kline_data.copy()
        df['日期'] = pd.to_datetime(df['日期'])
        
        dates = [mdates.date2num(date) for date in df['日期']]
        volumes = [float(vol) for vol in df['成交量']]
        
        self.ax2.bar(dates, volumes, width=0.6, alpha=0.7, color='gray')
        
    def setup_chart_style(self):
        """设置图表样式"""
        # K线图样式
        self.ax1.set_title(f"{self.current_stock} 实时K线图", fontsize=14, fontweight='bold')
        self.ax1.set_ylabel("价格 (元)", fontsize=10)
        self.ax1.grid(True, alpha=0.3)
        
        # 成交量图样式
        self.ax2.set_ylabel("成交量", fontsize=10)
        self.ax2.set_xlabel("时间", fontsize=10)
        self.ax2.grid(True, alpha=0.3)
        
        # 设置时间轴格式
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        
        # 自动调整布局
        self.fig.tight_layout()
        
    def refresh_chart(self):
        """刷新图表"""
        if not self.is_updating:
            threading.Thread(target=self.load_historical_data, daemon=True).start()
            
    def update_status(self, message):
        """更新状态"""
        self.status_var.set(message)

def main():
    """主程序"""
    root = tk.Tk()
    
    # 设置样式
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
        
    app = RealtimeKlineUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.stop_realtime_update()

if __name__ == "__main__":
    main()
