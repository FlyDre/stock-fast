"""
股票数据获取工具 - 图形界面版本
简洁清晰的UI设计，逻辑明确
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from datetime import datetime
import pandas as pd
import os

from data_fetcher import StockDataFetcher
from config import STOCK_CODES
from display_utils import format_stock_info, format_historical_summary

class StockDataUI:
    def __init__(self, root):
        self.root = root
        self.root.title("股票数据获取工具")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # 初始化数据获取器
        self.fetcher = StockDataFetcher()
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面组件"""
        
        # 主标题
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill="x", padx=10, pady=5)
        
        title_label = ttk.Label(title_frame, text="股票数据获取工具", font=("Arial", 16, "bold"))
        title_label.pack()
        
        # 分隔线
        separator1 = ttk.Separator(self.root, orient="horizontal")
        separator1.pack(fill="x", padx=10, pady=5)
        
        # 输入区域
        input_frame = ttk.LabelFrame(self.root, text="股票代码设置", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # 股票代码输入
        code_frame = ttk.Frame(input_frame)
        code_frame.pack(fill="x", pady=2)
        
        ttk.Label(code_frame, text="股票代码:").pack(side="left")
        self.code_entry = ttk.Entry(code_frame, width=30)
        self.code_entry.pack(side="left", padx=(10, 5))
        self.code_entry.insert(0, "000001,002594,600519")  # 默认股票代码
        
        ttk.Button(code_frame, text="使用默认", command=self.load_default_codes).pack(side="left", padx=5)
        
        # 说明文字
        help_label = ttk.Label(input_frame, text="提示：多个股票代码用逗号分隔，如: 000001,002594,600519", 
                              foreground="gray")
        help_label.pack(anchor="w", pady=(2, 0))
        
        # 功能选择区域
        function_frame = ttk.LabelFrame(self.root, text="功能选择", padding=10)
        function_frame.pack(fill="x", padx=10, pady=5)
        
        # 功能选项
        func_grid_frame = ttk.Frame(function_frame)
        func_grid_frame.pack(fill="x")
        
        self.function_var = tk.StringVar(value="basic_info")
        
        ttk.Radiobutton(func_grid_frame, text="获取基本信息", variable=self.function_var, 
                       value="basic_info").grid(row=0, column=0, sticky="w", padx=(0, 20))
        ttk.Radiobutton(func_grid_frame, text="获取历史数据", variable=self.function_var, 
                       value="historical").grid(row=0, column=1, sticky="w", padx=(0, 20))
        ttk.Radiobutton(func_grid_frame, text="获取全部数据", variable=self.function_var, 
                       value="both").grid(row=0, column=2, sticky="w")
        
        # 数据保存选项
        save_frame = ttk.Frame(function_frame)
        save_frame.pack(fill="x", pady=(10, 0))
        
        self.save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(save_frame, text="保存数据到CSV文件", variable=self.save_var).pack(side="left")
        
        # 操作按钮区域
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="开始获取", command=self.start_fetch_data, 
                  style="Accent.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="清空结果", command=self.clear_results).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="打开数据目录", command=self.open_data_dir).pack(side="left", padx=(0, 10))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=10)
        
        ttk.Label(status_frame, text="状态:").pack(side="left")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="blue")
        self.status_label.pack(side="left", padx=(5, 0))
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill="x", padx=10, pady=2)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(self.root, text="获取结果", padding=5)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 创建文本显示框
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, font=("Courier", 10))
        self.result_text.pack(fill="both", expand=True)
        
    def load_default_codes(self):
        """加载默认股票代码"""
        default_codes = ",".join(STOCK_CODES[:6])  # 取前6只股票
        self.code_entry.delete(0, tk.END)
        self.code_entry.insert(0, default_codes)
        
    def start_fetch_data(self):
        """开始获取数据（在新线程中执行）"""
        # 验证输入
        codes_text = self.code_entry.get().strip()
        if not codes_text:
            messagebox.showwarning("输入错误", "请输入股票代码")
            return
            
        # 在新线程中执行数据获取
        thread = threading.Thread(target=self.fetch_data_thread, args=(codes_text,))
        thread.daemon = True
        thread.start()
        
    def fetch_data_thread(self, codes_text):
        """数据获取线程"""
        try:
            # 更新UI状态
            self.update_status("正在获取数据...")
            self.progress.start(10)
            
            # 解析股票代码
            stock_codes = [code.strip() for code in codes_text.split(",") if code.strip()]
            
            # 获取功能类型
            function_type = self.function_var.get()
            
            self.clear_results()
            self.append_result(f"开始获取 {len(stock_codes)} 只股票的数据...")
            self.append_result(f"股票列表: {', '.join(stock_codes)}")
            self.append_result(f"获取类型: {self.get_function_name(function_type)}")
            self.append_result("=" * 60 + "\n")
            
            success_count = 0
            
            for i, code in enumerate(stock_codes, 1):
                self.update_status(f"正在处理 {code} ({i}/{len(stock_codes)})...")
                
                try:
                    if function_type in ["basic_info", "both"]:
                        self.process_basic_info(code)
                        
                    if function_type in ["historical", "both"]:
                        self.process_historical_data(code)
                        
                    success_count += 1
                    self.append_result(f"✅ {code} 处理完成\n")
                    
                except Exception as e:
                    self.append_result(f"❌ {code} 处理失败: {str(e)}\n")
            
            # 完成总结
            self.append_result("=" * 60)
            self.append_result(f"数据获取完成！成功: {success_count}/{len(stock_codes)}")
            
            if self.save_var.get():
                self.append_result(f"数据已保存到 data/ 目录")
                
            self.update_status("获取完成")
            
        except Exception as e:
            self.append_result(f"❌ 获取过程中出现错误: {str(e)}")
            self.update_status("获取失败")
            
        finally:
            self.progress.stop()
            
    def process_basic_info(self, code):
        """处理基本信息获取"""
        info = self.fetcher.get_stock_info(code)
        if info:
            formatted_info = format_stock_info(info, code)
            self.append_result(formatted_info + "\n")
        else:
            self.append_result(f"❌ 无法获取 {code} 的基本信息\n")
            
    def process_historical_data(self, code):
        """处理历史数据获取"""
        hist_data = self.fetcher.get_historical_data(code)
        if hist_data is not None:
            self.append_result(f"📊 {code} 历史数据 ({len(hist_data)} 条记录):")
            
            # 显示最近3天的数据
            summary = format_historical_summary(hist_data, 3)
            self.append_result(summary + "\n")
            
            # 保存数据
            if self.save_var.get():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{code}_data_{timestamp}.csv"
                self.fetcher.save_to_csv(hist_data, filename)
                self.append_result(f"💾 已保存为: {filename}\n")
        else:
            self.append_result(f"❌ 无法获取 {code} 的历史数据\n")
            
    def get_function_name(self, func_type):
        """获取功能类型的中文名称"""
        names = {
            "basic_info": "基本信息",
            "historical": "历史数据", 
            "both": "基本信息 + 历史数据"
        }
        return names.get(func_type, "未知")
        
    def update_status(self, message):
        """更新状态栏"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def append_result(self, text):
        """添加结果文本"""
        self.result_text.insert(tk.END, text + "\n")
        self.result_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_results(self):
        """清空结果显示"""
        self.result_text.delete(1.0, tk.END)
        
    def open_data_dir(self):
        """打开数据目录"""
        try:
            data_path = os.path.abspath("data")
            if not os.path.exists(data_path):
                os.makedirs(data_path)
            
            # Windows
            if os.name == 'nt':
                os.startfile(data_path)
            # macOS
            elif os.name == 'posix' and os.uname().sysname == 'Darwin':
                os.system(f'open "{data_path}"')
            # Linux
            else:
                os.system(f'xdg-open "{data_path}"')
                
        except Exception as e:
            messagebox.showerror("错误", f"无法打开数据目录: {str(e)}")

def main():
    """主程序入口"""
    root = tk.Tk()
    
    # 设置简洁的样式
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
        
    app = StockDataUI(root)
    
    # 居中显示窗口
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
