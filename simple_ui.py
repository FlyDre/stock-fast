"""
股票数据获取工具 - 简化界面版本
极简设计，功能集中
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from data_fetcher import StockDataFetcher

class SimpleStockUI:
    def __init__(self, root):
        self.root = root
        self.root.title("股票数据查询")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # 设置简洁样式
        self.setup_style()
        
        # 初始化数据获取器
        self.fetcher = StockDataFetcher()
        
        # 创建界面
        self.create_widgets()
        
    def setup_style(self):
        """设置简洁的界面样式"""
        style = ttk.Style()
        
        # 使用系统默认主题
        available_themes = style.theme_names()
        if "vista" in available_themes:
            style.theme_use("vista")
        elif "winnative" in available_themes:
            style.theme_use("winnative")
        
    def create_widgets(self):
        """创建界面组件"""
        
        # 主容器
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="股票数据查询工具", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 输入区域
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(input_frame, text="股票代码:", font=("Arial", 11)).pack(anchor="w")
        
        entry_frame = ttk.Frame(input_frame)
        entry_frame.pack(fill="x", pady=(5, 0))
        
        self.code_entry = ttk.Entry(entry_frame, font=("Arial", 11))
        self.code_entry.pack(side="left", fill="x", expand=True)
        self.code_entry.insert(0, "000001")
        
        ttk.Button(entry_frame, text="查询", 
                  command=self.query_stock).pack(side="right", padx=(10, 0))
        
        # 说明文字
        ttk.Label(input_frame, text="输入6位股票代码，如：000001", 
                 foreground="gray", font=("Arial", 9)).pack(anchor="w", pady=(3, 0))
        
        # 分隔线
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill="x", pady=15)
        
        # 结果显示区域
        result_label = ttk.Label(main_frame, text="查询结果:", font=("Arial", 11, "bold"))
        result_label.pack(anchor="w")
        
        # 创建结果显示框架
        result_frame = ttk.Frame(main_frame, relief="sunken", borderwidth=1)
        result_frame.pack(fill="both", expand=True, pady=(5, 0))
        
        # 滚动文本框
        self.result_text = tk.Text(result_frame, wrap=tk.WORD, 
                                  font=("Courier", 10), 
                                  bg="white", fg="black",
                                  padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪 - 请输入股票代码进行查询")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                foreground="blue", font=("Arial", 9))
        status_label.pack(anchor="w", pady=(10, 0))
        
        # 初始显示帮助信息
        self.show_help()
        
    def show_help(self):
        """显示帮助信息"""
        help_text = """
═══════════════════════════════════════════════════════════════════

📋 使用说明：

1. 在上方输入框中输入6位股票代码（如：000001）
2. 点击"查询"按钮或按回车键开始查询
3. 系统将获取该股票的基本信息和最近交易数据

📊 功能特点：

• 获取股票基本信息（公司名称、市值等）
• 获取最近交易数据（价格、涨跌幅等）
• 简洁清晰的数据展示
• 无需安装额外软件

💡 常用股票代码示例：

• 000001 - 平安银行      • 600036 - 招商银行
• 000002 - 万科A        • 600519 - 贵州茅台  
• 002594 - 比亚迪       • 300750 - 宁德时代

═══════════════════════════════════════════════════════════════════

请在上方输入股票代码开始查询...
        """
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, help_text)
        
        # 绑定回车键
        self.code_entry.bind('<Return>', lambda event: self.query_stock())
        
    def query_stock(self):
        """查询股票数据"""
        code = self.code_entry.get().strip()
        
        # 验证输入
        if not code:
            messagebox.showwarning("输入错误", "请输入股票代码")
            return
            
        if not code.isdigit() or len(code) != 6:
            messagebox.showwarning("格式错误", "请输入6位数字股票代码")
            return
        
        # 在新线程中查询
        thread = threading.Thread(target=self.query_thread, args=(code,))
        thread.daemon = True
        thread.start()
        
    def query_thread(self, code):
        """查询线程"""
        try:
            self.update_status(f"正在查询 {code} 的数据...")
            self.clear_results()
            
            # 查询基本信息
            self.append_result("=" * 60)
            self.append_result(f"正在获取 {code} 的股票数据...\n")
            
            info = self.fetcher.get_stock_info(code)
            if info:
                self.append_result(f"🏢 {code} - {info.get('股票简称', 'N/A')}")
                self.append_result("-" * 40)
                
                # 格式化市值显示
                total_mv = info.get('总市值', 0)
                if isinstance(total_mv, (int, float)) and total_mv > 0:
                    mv_yi = total_mv / 100000000
                    self.append_result(f"总市值: {mv_yi:.2f} 亿元")
                
                # 其他关键信息
                items = ['流通市值', '市盈率-动态', '市净率', '每股收益']
                for item in items:
                    value = info.get(item, 'N/A')
                    if isinstance(value, (int, float)) and item == '流通市值':
                        value = f"{value / 100000000:.2f} 亿元"
                    elif isinstance(value, (int, float)):
                        value = f"{value:.2f}"
                    self.append_result(f"{item.replace('-动态', '')}: {value}")
                    
            else:
                self.append_result(f"❌ 无法获取 {code} 的基本信息")
            
            self.append_result("")
            
            # 查询历史数据
            self.append_result("📊 最近交易数据:")
            self.append_result("-" * 40)
            
            hist_data = self.fetcher.get_historical_data(code)
            if hist_data is not None:
                recent_data = hist_data.tail(5)
                
                self.append_result(f"{'日期':<12} {'收盘价':<8} {'涨跌幅':<8} {'成交量(万)':<12}")
                self.append_result("-" * 50)
                
                for _, row in recent_data.iterrows():
                    date_str = str(row['日期'])[:10]
                    volume_wan = row['成交量'] / 10000
                    change_str = f"{row['涨跌幅']:+.2f}%"
                    
                    line = f"{date_str:<12} {row['收盘']:<8.2f} {change_str:<8} {volume_wan:<12.1f}"
                    self.append_result(line)
                    
            else:
                self.append_result(f"❌ 无法获取 {code} 的历史数据")
            
            self.append_result("")
            self.append_result("=" * 60)
            self.append_result("✅ 查询完成！\n")
            
            self.update_status(f"{code} 查询完成")
            
        except Exception as e:
            self.append_result(f"❌ 查询失败: {str(e)}")
            self.update_status("查询失败")
            
    def update_status(self, message):
        """更新状态"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def append_result(self, text):
        """添加结果"""
        self.result_text.insert(tk.END, text + "\n")
        self.result_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_results(self):
        """清空结果"""
        self.result_text.delete(1.0, tk.END)

def main():
    """主程序"""
    root = tk.Tk()
    
    # 居中显示
    root.update_idletasks()
    width = 600
    height = 500
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    app = SimpleStockUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
