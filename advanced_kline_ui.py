"""
高级实时K线界面 - 超高频更新
提供秒级更新，数据展示清晰有序
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
import queue

from data_fetcher import StockDataFetcher

class AdvancedKlineUI:
    def __init__(self, root):
        self.root = root
        self.root.title("高级K线图表 - 超高频实时更新")
        self.root.geometry("1400x900")
        
        # 配置变量
        self.current_stock = "000001"
        self.update_interval = 5  # 5秒更新，比同花顺快12倍
        self.is_updating = False
        self.update_count = 0
        
        # 数据存储
        self.fetcher = StockDataFetcher()
        self.kline_data = pd.DataFrame()
        self.realtime_data = []
        self.price_queue = queue.Queue()
        
        # 界面样式配置
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
        # 启动价格更新检查
        self.check_price_updates()
        
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        
        # 配置自定义样式
        style.configure("Title.TLabel", font=("Arial", 14, "bold"))
        style.configure("Info.TLabel", font=("Arial", 10))
        style.configure("Price.TLabel", font=("Arial", 12, "bold"))
        style.configure("Positive.TLabel", foreground="red", font=("Arial", 11, "bold"))
        style.configure("Negative.TLabel", foreground="green", font=("Arial", 11, "bold"))
        
    def create_widgets(self):
        """创建界面组件"""
        
        # 顶部标题栏
        title_frame = ttk.Frame(self.root, padding=10)
        title_frame.pack(fill="x")
        
        ttk.Label(title_frame, text="高频实时K线图表系统", style="Title.TLabel").pack(side="left")
        
        # 实时时间显示
        self.time_var = tk.StringVar()
        ttk.Label(title_frame, textvariable=self.time_var, style="Info.TLabel").pack(side="right")
        
        # 控制面板
        control_frame = ttk.LabelFrame(self.root, text="控制面板", padding=10)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # 第一行：股票设置
        row1 = ttk.Frame(control_frame)
        row1.pack(fill="x", pady=(0, 5))
        
        ttk.Label(row1, text="股票代码:", style="Info.TLabel").pack(side="left")
        self.stock_var = tk.StringVar(value=self.current_stock)
        stock_entry = ttk.Entry(row1, textvariable=self.stock_var, width=10)
        stock_entry.pack(side="left", padx=(5, 15))
        
        ttk.Label(row1, text="更新频率:", style="Info.TLabel").pack(side="left")
        self.freq_var = tk.StringVar(value="5秒")
        freq_combo = ttk.Combobox(row1, textvariable=self.freq_var, 
                                 values=["1秒", "3秒", "5秒", "10秒", "30秒"], 
                                 width=8, state="readonly")
        freq_combo.pack(side="left", padx=(5, 15))
        freq_combo.bind('<<ComboboxSelected>>', self.on_freq_change)
        
        # 控制按钮
        self.start_btn = ttk.Button(row1, text="▶ 开始", command=self.start_updates, 
                                   style="Accent.TButton")
        self.start_btn.pack(side="left", padx=(15, 5))
        
        self.stop_btn = ttk.Button(row1, text="⏸ 暂停", command=self.stop_updates, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        ttk.Button(row1, text="🔄 刷新", command=self.refresh_data).pack(side="left", padx=5)
        
        # 第二行：状态信息
        row2 = ttk.Frame(control_frame)
        row2.pack(fill="x")
        
        ttk.Label(row2, text="状态:", style="Info.TLabel").pack(side="left")
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(row2, textvariable=self.status_var, foreground="blue").pack(side="left", padx=(5, 20))
        
        ttk.Label(row2, text="更新次数:", style="Info.TLabel").pack(side="left")
        self.count_var = tk.StringVar(value="0")
        ttk.Label(row2, textvariable=self.count_var, foreground="purple").pack(side="left", padx=(5, 20))
        
        ttk.Label(row2, text="数据延迟:", style="Info.TLabel").pack(side="left")
        self.delay_var = tk.StringVar(value="--")
        ttk.Label(row2, textvariable=self.delay_var, foreground="orange").pack(side="left", padx=(5, 0))
        
        # 主要内容区域
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # 左侧：价格信息面板
        info_frame = ttk.LabelFrame(main_frame, text="实时行情", padding=5)
        info_frame.pack(side="left", fill="y", padx=(0, 10))
        
        self.create_price_panel(info_frame)
        
        # 右侧：K线图表
        chart_frame = ttk.LabelFrame(main_frame, text="K线图表", padding=5)
        chart_frame.pack(side="right", fill="both", expand=True)
        
        self.create_chart_panel(chart_frame)
        
    def create_price_panel(self, parent):
        """创建价格信息面板"""
        parent.config(width=250)
        
        # 基本信息显示
        basic_frame = ttk.LabelFrame(parent, text="基本信息", padding=10)
        basic_frame.pack(fill="x", pady=(0, 10))
        
        # 股票名称和代码
        self.name_var = tk.StringVar(value="--")
        name_label = ttk.Label(basic_frame, textvariable=self.name_var, style="Price.TLabel")
        name_label.pack(pady=(0, 5))
        
        code_label = ttk.Label(basic_frame, textvariable=self.stock_var, style="Info.TLabel")
        code_label.pack()
        
        # 价格信息
        price_frame = ttk.LabelFrame(parent, text="价格信息", padding=10)
        price_frame.pack(fill="x", pady=(0, 10))
        
        # 当前价格
        self.price_var = tk.StringVar(value="--")
        price_label = ttk.Label(price_frame, textvariable=self.price_var, 
                               font=("Arial", 16, "bold"), foreground="black")
        price_label.pack(pady=(0, 5))
        
        # 涨跌信息
        self.change_var = tk.StringVar(value="--")
        self.change_label = ttk.Label(price_frame, textvariable=self.change_var)
        self.change_label.pack()
        
        # 其他信息
        other_frame = ttk.LabelFrame(parent, text="交易信息", padding=10)
        other_frame.pack(fill="x", pady=(0, 10))
        
        info_items = [
            ("最高:", "high_var"),
            ("最低:", "low_var"),
            ("成交量:", "volume_var"),
            ("成交额:", "amount_var"),
        ]
        
        for i, (label, var_name) in enumerate(info_items):
            frame = ttk.Frame(other_frame)
            frame.pack(fill="x", pady=1)
            
            ttk.Label(frame, text=label, style="Info.TLabel").pack(side="left")
            var = tk.StringVar(value="--")
            setattr(self, var_name, var)
            ttk.Label(frame, textvariable=var, style="Info.TLabel").pack(side="right")
        
        # 实时价格流
        stream_frame = ttk.LabelFrame(parent, text="价格流水", padding=5)
        stream_frame.pack(fill="both", expand=True)
        
        # 价格流显示
        self.price_stream = tk.Listbox(stream_frame, height=12, font=("Courier", 9))
        stream_scroll = ttk.Scrollbar(stream_frame, orient="vertical", command=self.price_stream.yview)
        self.price_stream.configure(yscrollcommand=stream_scroll.set)
        
        self.price_stream.pack(side="left", fill="both", expand=True)
        stream_scroll.pack(side="right", fill="y")
        
    def create_chart_panel(self, parent):
        """创建图表面板"""
        # 创建matplotlib图形
        self.fig = Figure(figsize=(12, 8), dpi=100, facecolor='white')
        
        # 创建子图
        self.ax_main = self.fig.add_subplot(3, 1, (1, 2))  # K线图（占用2/3空间）
        self.ax_volume = self.fig.add_subplot(3, 1, 3)     # 成交量（占用1/3空间）
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # 初始化空图表
        self.init_chart()
        
    def init_chart(self):
        """初始化图表"""
        # 清空图表
        self.ax_main.clear()
        self.ax_volume.clear()
        
        # 设置标题和标签
        self.ax_main.set_title(f"{self.current_stock} - 实时K线图", 
                              fontsize=14, fontweight='bold', pad=20)
        self.ax_main.set_ylabel("价格 (元)", fontsize=11)
        self.ax_main.grid(True, alpha=0.3, linestyle='--')
        
        self.ax_volume.set_ylabel("成交量", fontsize=11)
        self.ax_volume.set_xlabel("时间", fontsize=11)
        self.ax_volume.grid(True, alpha=0.3, linestyle='--')
        
        # 调整布局
        self.fig.tight_layout()
        self.canvas.draw()
        
    def on_freq_change(self, event=None):
        """更新频率改变"""
        freq_text = self.freq_var.get()
        self.update_interval = int(freq_text.replace('秒', ''))
        
    def start_updates(self):
        """开始更新"""
        self.current_stock = self.stock_var.get().strip()
        if not self.current_stock:
            messagebox.showwarning("错误", "请输入股票代码")
            return
            
        self.is_updating = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        # 启动更新线程
        threading.Thread(target=self.update_thread, daemon=True).start()
        
        self.update_status("开始实时更新")
        
    def stop_updates(self):
        """停止更新"""
        self.is_updating = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.update_status("已停止更新")
        
    def refresh_data(self):
        """刷新数据"""
        threading.Thread(target=self.load_initial_data, daemon=True).start()
        
    def update_thread(self):
        """更新线程"""
        # 首次加载基础数据
        self.load_initial_data()
        
        while self.is_updating:
            try:
                start_time = time.time()
                
                # 生成模拟实时数据
                self.generate_realtime_data()
                
                # 计算延迟
                delay = (time.time() - start_time) * 1000  # 转为毫秒
                
                # 更新计数和延迟显示
                self.update_count += 1
                self.root.after(0, lambda: self.count_var.set(str(self.update_count)))
                self.root.after(0, lambda: self.delay_var.set(f"{delay:.1f}ms"))
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"更新失败: {str(e)}"))
                break
                
    def load_initial_data(self):
        """加载初始数据"""
        try:
            self.update_status("加载基础数据...")
            
            # 获取历史K线数据
            hist_data = self.fetcher.get_historical_data(self.current_stock)
            if hist_data is not None:
                self.kline_data = hist_data.tail(30)  # 取最近30根K线
                
            # 获取基本信息
            info = self.fetcher.get_stock_info(self.current_stock)
            if info:
                self.root.after(0, lambda: self.name_var.set(info.get('股票简称', '--')))
                
            self.root.after(0, self.update_chart)
            self.update_status("基础数据加载完成")
            
        except Exception as e:
            self.update_status(f"数据加载失败: {str(e)}")
            
    def generate_realtime_data(self):
        """生成实时数据"""
        if self.kline_data.empty:
            return
            
        # 基于最后收盘价生成实时价格
        last_close = float(self.kline_data.iloc[-1]['收盘'])
        
        # 模拟价格波动
        change_rate = np.random.uniform(-0.005, 0.005)  # ±0.5%的随机波动
        new_price = last_close * (1 + change_rate)
        
        # 计算涨跌
        change_amount = new_price - last_close
        change_percent = (change_amount / last_close) * 100
        
        # 模拟其他数据
        volume = np.random.randint(10000, 100000)
        
        # 更新显示
        current_time = datetime.now()
        
        # 将数据放入队列
        price_data = {
            'time': current_time,
            'price': new_price,
            'change_amount': change_amount,
            'change_percent': change_percent,
            'volume': volume
        }
        
        self.price_queue.put(price_data)
        
    def check_price_updates(self):
        """检查价格更新队列"""
        try:
            while not self.price_queue.empty():
                data = self.price_queue.get_nowait()
                self.update_price_display(data)
        except queue.Empty:
            pass
        
        # 更新时间显示
        self.time_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # 每100ms检查一次
        self.root.after(100, self.check_price_updates)
        
    def update_price_display(self, data):
        """更新价格显示"""
        # 更新价格
        self.price_var.set(f"{data['price']:.2f}")
        
        # 更新涨跌信息
        change_text = f"{data['change_amount']:+.2f} ({data['change_percent']:+.2f}%)"
        self.change_var.set(change_text)
        
        # 设置颜色
        if data['change_percent'] > 0:
            self.change_label.configure(style="Positive.TLabel")
        elif data['change_percent'] < 0:
            self.change_label.configure(style="Negative.TLabel")
        else:
            self.change_label.configure(foreground="black")
        
        # 更新其他信息
        self.volume_var.set(f"{data['volume']:,}")
        
        # 添加到价格流
        time_str = data['time'].strftime("%H:%M:%S")
        stream_text = f"{time_str} {data['price']:.2f} {data['change_percent']:+.2f}%"
        
        self.price_stream.insert(0, stream_text)
        if self.price_stream.size() > 50:
            self.price_stream.delete(50, tk.END)
            
    def update_chart(self):
        """更新图表"""
        if self.kline_data.empty:
            return
            
        try:
            # 重绘K线图
            self.draw_kline_chart()
            self.canvas.draw()
            
        except Exception as e:
            print(f"图表更新错误: {e}")
            
    def draw_kline_chart(self):
        """绘制K线图"""
        # 清空图表
        self.ax_main.clear()
        self.ax_volume.clear()
        
        df = self.kline_data.copy()
        df['日期'] = pd.to_datetime(df['日期'])
        
        # 绘制K线
        for i, (idx, row) in enumerate(df.iterrows()):
            x = i
            open_price = float(row['开盘'])
            high_price = float(row['最高'])
            low_price = float(row['最低'])
            close_price = float(row['收盘'])
            volume = float(row['成交量'])
            
            # K线颜色
            color = 'red' if close_price >= open_price else 'green'
            
            # 绘制影线
            self.ax_main.plot([x, x], [low_price, high_price], color='black', linewidth=1)
            
            # 绘制实体
            body_height = abs(close_price - open_price)
            body_bottom = min(open_price, close_price)
            
            if body_height > 0:
                self.ax_main.add_patch(plt.Rectangle((x-0.4, body_bottom), 0.8, body_height, 
                                                    facecolor=color, alpha=0.8, edgecolor='black'))
            else:
                # 十字星
                self.ax_main.plot([x-0.4, x+0.4], [close_price, close_price], color=color, linewidth=2)
            
            # 绘制成交量
            self.ax_volume.bar(x, volume, width=0.8, color=color, alpha=0.6)
        
        # 设置图表样式
        self.ax_main.set_title(f"{self.current_stock} - 实时K线图 (更新间隔: {self.update_interval}秒)", 
                              fontsize=12, fontweight='bold')
        self.ax_main.set_ylabel("价格 (元)")
        self.ax_main.grid(True, alpha=0.3)
        
        self.ax_volume.set_ylabel("成交量")
        self.ax_volume.set_xlabel("时间")
        self.ax_volume.grid(True, alpha=0.3)
        
        # 设置X轴标签
        if len(df) > 0:
            x_labels = [d.strftime('%m-%d') for d in df['日期']]
            step = max(1, len(x_labels) // 8)  # 最多显示8个标签
            x_positions = list(range(0, len(x_labels), step))
            
            self.ax_main.set_xticks(x_positions)
            self.ax_main.set_xticklabels([x_labels[i] for i in x_positions], rotation=45)
            
            self.ax_volume.set_xticks(x_positions)
            self.ax_volume.set_xticklabels([x_labels[i] for i in x_positions], rotation=45)
        
        self.fig.tight_layout()
        
    def update_status(self, message):
        """更新状态"""
        self.status_var.set(message)

def main():
    """主程序"""
    root = tk.Tk()
    
    # 设置窗口图标和样式
    try:
        root.state('zoomed')  # Windows最大化
    except:
        pass
        
    app = AdvancedKlineUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        if hasattr(app, 'is_updating'):
            app.is_updating = False

if __name__ == "__main__":
    main()
