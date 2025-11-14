"""
统一股票终端 UI
- Tab1: 实时K线（复用 RealKlineUI）
- Tab2: 简易查询（复用 SimpleStockUI）
"""

import tkinter as tk
from tkinter import ttk

# 复用现有页面
from real_kline_ui import RealKlineUI
from stock_ui import StockDataUI

class UnifiedStockApp:
    def __init__(self, root):
        self.root = root
        if hasattr(self.root, "title"):
            self.root.title("股票终端 - 统一界面")
        if hasattr(self.root, "geometry"):
            self.root.geometry("1280x900")

        # Notebook 容器
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # K线页签
        self.tab_kline = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_kline, text="K线图表")
        self.kline_page = RealKlineUI(self.tab_kline)  # 以 Frame 作为父容器

        # 数据批量获取页签
        self.tab_data = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_data, text="数据批量获取")
        self.data_page = StockDataUI(self.tab_data)

def main():
    root = tk.Tk()
    app = UnifiedStockApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
