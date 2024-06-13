###增加K線圖

import tkinter as tk
from tkinter import ttk
import ccxt
import pandas as pd
import numpy as np
import concurrent.futures
import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_finance import candlestick_ohlc
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime


matplotlib.use('TkAgg')

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("強勢加密貨幣篩選")
        self.geometry("1200x900")  # 調整主視窗大小
        self.resizable(False, False)  # 禁用窗口缩放
        # 設置grid權重，使得區域可以隨視窗大小調整
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)  # 將左側區域的寬度權重
        self.grid_columnconfigure(1, weight=10)  # 將右側區域的寬度權重
        
            
        # 創建下拉式選單和按鈕的框架
        self.control_frame = tk.Frame(self)
        self.control_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        # 創建下拉式選單
        self.create_dropdown_menu()
            
        # 創建運行程式的按鈕
        self.create_run_button()
    
        # 創建保存圖表的按鈕
        self.create_save_button()
            
        # 創建文字輸出欄位與卷軸
        self.create_output_text()
            
        # 創建圖表區域
        self.create_chart_areas()

    def create_run_button(self):
        # 創建運行程式的按鈕
        self.run_button = ttk.Button(self.control_frame, text="執行程式", command=self.run_program)
        self.run_button.pack(side=tk.LEFT, padx=(10, 0))
        
    def create_save_button(self):
        # 创建保存按钮
        self.save_button = ttk.Button(self.control_frame, text="儲存圖表", command=self.save_chart)
        self.save_button.pack(side=tk.LEFT, padx=10)
        
    def create_dropdown_menu(self):
        # 創建下拉式選單的標籤
        self.exchange_label = ttk.Label(self.control_frame, text="選擇交易所:")
        self.exchange_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # 創建下拉式選單本身
        self.selected_exchange = tk.StringVar()
        self.exchange_combobox = ttk.Combobox(self.control_frame, textvariable=self.selected_exchange, state="readonly", width=10)
        
        # 在介面上顯示的交易所名稱
        display_names = ('Binance', 'Bybit', 'OKX', 'Bitget', 'BingX')
        self.exchange_combobox['values'] = display_names
        self.exchange_combobox.current(0)  
        self.exchange_combobox.pack(side=tk.LEFT)
        
    def save_chart(self):
        # 获取当前的日期时间
        current_date = datetime.now().strftime("%Y-%m-%d")
    
        # 根据选择的交易所名称创建文件名
        exchange_name = self.selected_exchange.get()
        
        filename = f"{current_date}_強勢幣別({exchange_name}).jpg"
        # 将左下图表保存为图片
        self.figure_left.savefig(filename)

    def create_output_text(self):
        # 創建文字輸出欄位及相應的卷軸
        self.output_frame = tk.Frame(self)
        self.output_frame.grid(row=1, column=0, sticky='nsew', padx=0, pady=(0, 10))
        
        self.output_text = tk.Text(self.output_frame, height=15, width=60, font=("Microsoft JhengHei", 11))
        self.scrollbar = tk.Scrollbar(self.output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=self.scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        

    def create_chart_areas(self):
        # 左下區域的圖表
        self.chart_frame_left = tk.Frame(self)
        self.chart_frame_left.grid(row=2, column=0, sticky='nsew', padx=(0, 16), pady=0)
    
        self.figure_left = Figure(figsize=(0, 5), dpi=100)
        self.figure_left.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)  # 調整圖表周圍的留白
        self.chart_left = FigureCanvasTkAgg(self.figure_left, master=self.chart_frame_left)
        self.chart_left.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
        # 右側區域的新圖表
        self.chart_frame_right = tk.Frame(self)
        self.chart_frame_right.grid(row=1, column=1, rowspan=2, sticky='nsew', padx=0, pady=0)
    
        # 創建Canvas以容納圖表
        self.canvas_right = tk.Canvas(self.chart_frame_right)
        self.canvas_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
        # 創建滾動條
        self.scrollbar_right = tk.Scrollbar(self.chart_frame_right, orient=tk.VERTICAL, command=self.canvas_right.yview)
        self.scrollbar_right.pack(side=tk.RIGHT, fill=tk.Y)
    
        # 將滾動條與Canvas進行綁定
        self.canvas_right.configure(yscrollcommand=self.scrollbar_right.set)
        
        # 創建內部框架以包含圖表
        self.inner_frame_right = tk.Frame(self.canvas_right)
        self.canvas_right.create_window((0, 0), window=self.inner_frame_right, anchor='nw')
    
        self.figure_right = Figure(figsize=(15.2, 220), dpi=40)
        self.chart_right = FigureCanvasTkAgg(self.figure_right, master=self.inner_frame_right)
        self.chart_right.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
        # 配置滾動區域
        self.inner_frame_right.bind("<Configure>", lambda event: self.canvas_right.configure(scrollregion=self.canvas_right.bbox("all")))
    
        # 綁定滾輪事件以進行垂直滾動
        self.canvas_right.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        self.canvas_right.yview_scroll(int(-1 * (event.delta / 120)), "units")

    


    def draw_chart(self, symbol_1D_split, symbol_4H_split, common_symbols):
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  
        plt.rcParams['axes.unicode_minus'] = False  
        
        numbers = list(range(1, 11))  
        symbol_1D_split += [''] * (10 - len(symbol_1D_split))  
        symbol_4H_split += [''] * (10 - len(symbol_4H_split))  
        common_symbols += [''] * (10 - len(common_symbols))  
        
        df_symbols = pd.DataFrame({
            '排名': numbers,
            '1D': symbol_1D_split,
            '4H': symbol_4H_split,
            '重複幣別': common_symbols
        })
        
        self.figure_left.clear()
        ax = self.figure_left.add_subplot(111) 
            
        colors = [['#f7f7f7', '#ffffff', '#f7f7f7', '#ffffff']] * 5 + [['#ffffff', '#f7f7f7', '#ffffff', '#f7f7f7']] * 5
        
        # 指定每列的寬度
        col_widths = [0.08, 0.35, 0.35, 0.35]  # 根據需要調整每列的寬度
        #圖表設置
        table = ax.table(cellText=df_symbols.values, colLabels=df_symbols.columns, loc='center', 
                         cellLoc='center', cellColours=colors, colWidths=col_widths)
        
        table.set_fontsize(14)  
        for key, cell in table.get_celld().items():
            if key[0] == 0:
                cell.set_text_props(fontweight='bold', color='white')  
                cell.set_facecolor('gray')  
            elif key[0] % 2 == 0:
                cell.set_facecolor('#E6E6E6')  
            else:
                cell.set_facecolor('#CCCCCC')  
            
        table.scale(1, 2)  
        
        current_date = datetime.now().strftime("%Y-%m-%d")  
        exchange_name = self.selected_exchange.get()
        
        ax.set_title(f'{current_date} {exchange_name} 強勢幣別', fontsize=14, y=1)
      
        ax.axis('off')  
        
        self.chart_left.draw()
        

    def draw_candlestick_chart(self, symbol_1D_split, symbol_4H_split):
        selected_exchange_proper_case = self.selected_exchange.get()
        selected_exchange = selected_exchange_proper_case.lower()
        exchange = getattr(ccxt, selected_exchange)()
        limit = 180
    
        n = max(len(symbol_1D_split) + len(symbol_4H_split), 1)  # 確保至少有一個圖
    
        self.figure_right.clear()
        self.figure_right.set_size_inches(15, 11 * n)  # 增加圖表的高度
        self.figure_right.subplots_adjust(hspace=5)  # 進一步增加子圖之間的垂直間距
        self.figure_right.suptitle(f"{selected_exchange_proper_case}", fontsize=48, y=0.998)
    
        gs = self.figure_right.add_gridspec(2*n, 1, height_ratios=[5, 2] * n)  # 調整子圖的高度比例

    
        for i, symbol in enumerate(symbol_1D_split + symbol_4H_split):
            ax_k = self.figure_right.add_subplot(gs[2*i])
            ax_v = self.figure_right.add_subplot(gs[2*i+1], sharex=ax_k)
    
            if i < len(symbol_1D_split):
                timeframe = '1d'
                bar_width = 0.4
            else:
                timeframe = '4h'
                bar_width = 0.075
    
            symbol_full = symbol + '/USDT:USDT'
    
            try:
                ohlcv = exchange.fetch_ohlcv(symbol_full, timeframe=timeframe, limit=limit)
                df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
                df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
                df['date_num'] = mdates.date2num(df['datetime'])
    
                df['ma_30'] = df['close'].rolling(window=30).mean()
                df['ma_45'] = df['close'].rolling(window=45).mean()
                df['ma_60'] = df['close'].rolling(window=60).mean()
    
                df_plot = df.iloc[-120:]
                ohlc = df_plot[['date_num', 'open', 'high', 'low', 'close']].values
    
                candlestick_ohlc(ax_k, ohlc, width=bar_width, colorup='g', colordown='r', alpha=0.6)
    
                ax_k.plot(df_plot['datetime'], df_plot['ma_30'], color='#DC7D00', label='MA 30', alpha=0.5)
                ax_k.plot(df_plot['datetime'], df_plot['ma_45'], color='#0040FF', label='MA 45', alpha=0.5)
                ax_k.plot(df_plot['datetime'], df_plot['ma_60'], color='#6C00F0', label='MA 60', alpha=0.5)
    
                ax_k.set_title(f"{symbol} {timeframe.upper()}", fontsize=32, y=0.9)
                ax_k.tick_params(axis='both', which='both', labelbottom=False, labelleft=False, labelsize=8)
                ax_k.tick_params(axis='both', which='both', length=0, labelsize=0)# 隱藏x軸和y軸標籤
    
                volume_colors = np.where(df_plot['close'] >= df_plot['open'], 'g', 'r')
                ax_v.bar(df_plot['datetime'], df_plot['volume'], color=volume_colors, alpha=0.4, width=bar_width)
                ax_v.tick_params(axis='both', labelbottom=False, labelleft=False, labelsize=8)
                
                ax_v.tick_params(axis='both', which='both', length=0, labelsize=0)# 隱藏x軸和y軸標籤，以及'log'標籤
                ax_v.tick_params(axis='y', which='both', labelleft=False)  # 隱藏y軸標籤，包括 'log'
    
            except :
                ax_k.text(0.5, 0.5, 'No data', ha='center', fontsize=32)
                ax_k.axis('off')
                ax_v.axis('off')
    
        self.figure_right.tight_layout()
        self.chart_right.draw()
        self.inner_frame_right.update_idletasks()
        self.canvas_right.config(scrollregion=self.canvas_right.bbox("all"))
    
    
    def run_program(self):
        selected_exchange_proper_case = self.selected_exchange.get() #正確交易所名稱
        selected_exchange = selected_exchange_proper_case.lower() #ccxt辨認之交易所名稱
        
        if selected_exchange in ['binance', 'bybit']:
            def multi_threaded_output_text(message):
                self.output_text.insert(tk.END, message + "\n")
                self.update_idletasks()  

                
            # 清空文字輸出欄位
            self.output_text.delete(1.0, tk.END)
        
            if selected_exchange in ['binance', 'bybit']:
                multi_threaded_output_text(f"從 {selected_exchange_proper_case} 獲取資料...")
                start_time = time.time()
                exchange = getattr(ccxt, selected_exchange)()
        
                markets = exchange.load_markets()
                filtered_markets = [symbol for symbol, market in markets.items() if market['type'] == 'swap' and '/USDT:USDT' in symbol]
        
                limit = 66
                timeframes = ['1d', '4h']  
        
                # 函式：計算增長百分比
                def calculate_growth_percent(df):
                    growth_percent = np.zeros((5, 3))
                    for i in range(0, 5):
                        d = df.iloc[-i-1]
                        d2 = df.iloc[-i-2]

                        
                        # 計算增長百分比
                        growth_percent[i, 0] = ((d['ma_30'] - d2['ma_30']) / d2['ma_30']) * 100
                        growth_percent[i, 1] = ((d['ma_45'] - d2['ma_45']) / d2['ma_45']) * 100
                        growth_percent[i, 2] = ((d['ma_60'] - d2['ma_60']) / d2['ma_60']) * 100
                        
                
                    return growth_percent

    
        
                # 函式：處理單個交易對符號
                def process_symbol(symbol, timeframe):
 
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)  # 從交易所獲取指定時間間隔的開高低收量數據
                    
                    if len(ohlcv) >= 66:  # 確保收集到足夠的數據
                        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])  # 創建DataFrame對象
                        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')  # 將timestamp轉換為日期時間格式
                        df['ma_30'] = df['close'].rolling(window=30).mean()  # 計算30日移動平均線
                        df['ma_45'] = df['close'].rolling(window=45).mean()  # 計算45日移動平均線
                        df['ma_60'] = df['close'].rolling(window=60).mean()  # 計算60日移動平均線
                        
                        growth_percent_symbol = calculate_growth_percent(df)  # 計算增長百分比
                        growth_average = (growth_percent_symbol[:, 0] + growth_percent_symbol[:, 1] + growth_percent_symbol[:, 2]) / 3  # 計算平均增長率
                        strength_score = growth_average.mean()  # 計算強勢評分
                        
                        return {symbol: strength_score}  # 返回交易對符號和對應的強勢評分
                    else:
                        return None
    
        
                symbol_1D, symbol_4H = [], []  
                common_symbols = []  
        
                # 迭代不同的時間間隔
                for timeframe in timeframes:
                    if timeframe == "1d":
                        multi_threaded_output_text("\n1D：\n")  # 更新文字輸出欄位，顯示正在處理1D數據
                    elif timeframe == "4h":
                        multi_threaded_output_text("\n4H：\n")  # 更新文字輸出欄位，顯示正在處理4H數據
                
                    higher_base = []  # 初始化列表，用於存儲符合條件的交易對

                
                    # 使用多線程處理符號
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        results = [executor.submit(process_symbol, symbol, timeframe) for symbol in filtered_markets]  # 提交處理符號的任務
                
                        # 等待所有任務完成並處理結果
                        for future in concurrent.futures.as_completed(results):
                            result = future.result()  # 獲取任務的結果
                            if result:
                                higher_base.append(result)  # 將符合條件的交易對及其評分添加到列表中

                    # 將符合條件的交易對按照評分降序排序
                    higher_base.sort(key=lambda x: list(x.values())[0], reverse=True)
                    # 將 higher_base 中值低於 BTC/USDT:USDT 和 ETH/USDT:USDT 的元素刪除
                    # 從 higher_base 中取得 BTC/USDT:USDT 和 ETH/USDT:USDT 的值作為閾值
                    BTC_threshold = next(item[list(item.keys())[0]] for item in higher_base if list(item.keys())[0] == 'BTC/USDT:USDT')
                    ETH_threshold = next(item[list(item.keys())[0]] for item in higher_base if list(item.keys())[0] == 'ETH/USDT:USDT')
                    
                    # 將 higher_base 中值低於 BTC/USDT:USDT 和 ETH/USDT:USDT 的元素刪除
                    higher_base = [item for item in higher_base if list(item.values())[0] >= BTC_threshold and list(item.values())[0] >= ETH_threshold and list(item.values())[0] > 0]
                    
                    # 刪除 BTC/USDT:USDT 和 ETH/USDT:USDT
                    higher_base = [item for item in higher_base if list(item.keys())[0] not in ['BTC/USDT:USDT', 'ETH/USDT:USDT','BTCDOM/USDT:USDT','ETHDOM/USDT:USDT']]

                    
                  
                    # 輸出前10名的交易對及其評分
                    for symbol_score_dict in higher_base[:10]:
                        symbol, score = list(symbol_score_dict.items())[0]
                        multi_threaded_output_text(f"{symbol}: {score:.2f}")
                
                    # 根據時間間隔更新相應的交易對列表
                    for symbol_score_dict in higher_base[:10]:
                        symbol = list(symbol_score_dict.keys())[0]
                        if timeframe == "1d":
                            symbol_1D.append(symbol)
                            symbol_1D_split = [symbol.split('/')[0] for symbol in symbol_1D]
                            
                        elif timeframe == "4h":
                            symbol_4H.append(symbol)
                            symbol_4H_split = [symbol.split('/')[0] for symbol in symbol_4H]
                            
                
                # 找出重疊的交易對
                common_symbols = list(set(symbol_1D_split) & set(symbol_4H_split))  # 找出1D和4H時間間隔中都存在的交易對
                multi_threaded_output_text("\n重複幣別：")
                for i in common_symbols:
                    multi_threaded_output_text(i)  # 將重疊的交易對輸出到文字輸出欄位中
                
                end_time = time.time()  # 結束時間
                total_time = int(end_time - start_time)  # 計算執行時間
                multi_threaded_output_text(f"\n執行時間：{total_time}秒")  # 將執行時間輸出到文字輸出欄位中
            
        elif selected_exchange in ['okx','bitget','bingx']:
            
            def update_output_text(message):
            # 更新文字輸出欄位的內容
                self.output_text.insert(tk.END, message + "\n")
                self.update_idletasks()
            
            # 清空文字輸出欄位
            self.output_text.delete(1.0, tk.END)
        
            if selected_exchange in ['okx','bitget','bingx']:
                # 從所選交易所獲取資料
                update_output_text(f"從 {selected_exchange_proper_case} 獲取資料...")
                start_time = time.time()
                exchange = getattr(ccxt, selected_exchange)()  # 使用 getattr() 動態取得交易所類別
        
                markets = exchange.load_markets()
                filtered_markets = [symbol for symbol, market in markets.items() if market['type'] == 'swap' and '/USDT:USDT' in symbol]
        

                limit = 66
                timeframes = ['1d', '4h']
        
                def calculate_growth_percent(df):
                    growth_percent = np.zeros((5, 3))
                    for i in range(0, 5):
                        d = df.iloc[-i-1]
                        d2 = df.iloc[-i-2]
                        d3 = df.iloc[-i-3]
                        d4 = df.iloc[-i-4]
                        d5 = df.iloc[-i-5]
                        # 檢查增長百分比的篩選條件
                        
                        # 計算增長百分比
                        growth_percent[i, 0] = ((d['ma_30'] - d2['ma_30']) / d2['ma_30']) * 100
                        growth_percent[i, 1] = ((d['ma_45'] - d2['ma_45']) / d2['ma_45']) * 100
                        growth_percent[i, 2] = ((d['ma_60'] - d2['ma_60']) / d2['ma_60']) * 100
                        
                        
                        if (d['ma_30'] > d2['ma_30'] > d3['ma_30'] > d4['ma_30'] > d5['ma_30'] and
                            d['ma_45'] > d2['ma_45'] > d3['ma_45'] > d4['ma_45'] > d5['ma_45'] and
                            d['ma_60'] > d2['ma_60'] > d3['ma_60'] > d4['ma_60'] > d5['ma_60']):
                            
                            # 計算增長百分比
                            growth_percent[i, 0] = ((d['ma_30'] - d2['ma_30']) / d2['ma_30']) * 100
                            growth_percent[i, 1] = ((d['ma_45'] - d2['ma_45']) / d2['ma_45']) * 100
                            growth_percent[i, 2] = ((d['ma_60'] - d2['ma_60']) / d2['ma_60']) * 100
                        else:
                            # 如果不符合條件，則將增長百分比設置為 0，表示這個交易對不符合篩選條件
                            growth_percent[i, :] = 0
                
                    return growth_percent
        
                def process_symbol(symbol, timeframe):
                    # 處理單個交易對的資料
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
                    if len(ohlcv) >= 66:
                        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                        df['ma_30'] = df['close'].rolling(window=30).mean()
                        df['ma_45'] = df['close'].rolling(window=45).mean()
                        df['ma_60'] = df['close'].rolling(window=60).mean()
        
                        growth_percent_symbol = calculate_growth_percent(df)
                        growth_average = (growth_percent_symbol[:, 0] + growth_percent_symbol[:, 1] + growth_percent_symbol[:, 2]) / 3
                        strength_score = growth_average.mean()
        
                        return {symbol: strength_score}
        
                symbol_1D, symbol_4H = [], []
                common_symbols = []
        
                for timeframe in timeframes:
                    if timeframe == "1d":
                        update_output_text("\n1D：\n")
                    elif timeframe == "4h":
                        update_output_text("\n4H：\n")
        
                    higher_base = []
    
        
                    for symbol in filtered_markets:
                        result = process_symbol(symbol, timeframe)
                        if result:
                            higher_base.append(result)
        

                    # 將符合條件的交易對按照評分降序排序
                    higher_base.sort(key=lambda x: list(x.values())[0], reverse=True)
                    # 將 higher_base 中值低於 BTC/USDT:USDT 和 ETH/USDT:USDT 的元素刪除
                    # 從 higher_base 中取得 BTC/USDT:USDT 和 ETH/USDT:USDT 的值作為閾值
                    BTC_threshold = next(item[list(item.keys())[0]] for item in higher_base if list(item.keys())[0] == 'BTC/USDT:USDT')
                    ETH_threshold = next(item[list(item.keys())[0]] for item in higher_base if list(item.keys())[0] == 'ETH/USDT:USDT')
                    
                    # 將 higher_base 中值低於 BTC/USDT:USDT 和 ETH/USDT:USDT 的元素刪除
                    higher_base = [item for item in higher_base if list(item.values())[0] >= BTC_threshold and list(item.values())[0] >= ETH_threshold and list(item.values())[0] > 0]
                    
                    # 刪除 BTC/USDT:USDT 和 ETH/USDT:USDT
                    higher_base = [item for item in higher_base if list(item.keys())[0] not in ['BTC/USDT:USDT', 'ETH/USDT:USDT','BTCDOM/USDT:USDT','ETHDOM/USDT:USDT']]


                    for symbol_score_dict in higher_base[:10]:
                        symbol, score = list(symbol_score_dict.items())[0]
                        update_output_text(f"{symbol}: {score:.2f}")
        
                    for symbol_score_dict in higher_base[:10]:
                        symbol = list(symbol_score_dict.keys())[0]
                        if timeframe == "1d":
                            symbol_1D.append(symbol)
                            symbol_1D_split = [symbol.split('/')[0] for symbol in symbol_1D]
                            
                        elif timeframe == "4h":
                            symbol_4H.append(symbol)
                            symbol_4H_split = [symbol.split('/')[0] for symbol in symbol_4H]
                            
        
                common_symbols = list(set(symbol_1D_split) & set(symbol_4H_split))
                update_output_text("\n重複幣別：")
                for i in common_symbols:
                    update_output_text(i)
        
                end_time = time.time()
                total_time = int(end_time - start_time)
                update_output_text(f"\n執行時間：{total_time}秒")
            
        # 繪製圖表
        self.draw_chart(symbol_1D_split, symbol_4H_split, common_symbols)

        self.draw_candlestick_chart(symbol_1D_split,symbol_4H_split)
          
if __name__ == "__main__":
    app = App()
    app.mainloop()