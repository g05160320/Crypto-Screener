import tkinter as tk
from tkinter import ttk
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import ccxt
import pandas as pd
import concurrent.futures
import time
from datetime import datetime
import matplotlib.dates as mdates



matplotlib.use('TkAgg')

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("強勢加密貨幣篩選")
        self.geometry("1860x900")  # 調整主視窗大小
        

        self.resizable(False, False)  # 禁用窗口缩放
        # 設置grid權重，使得區域可以隨視窗大小調整
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=9)  # 給K線圖區域更多的空間
        self.grid_columnconfigure(0, weight=1)  # 將左側區域的寬度權重
        self.grid_columnconfigure(1, weight=10)  # 將中間區域的寬度權重
        self.grid_columnconfigure(2, weight=1)  # 將右側區域的寬度權重
        
        # 創建下拉式選單和按鈕的框架
        self.control_frame = tk.Frame(self)
        self.control_frame.grid(row=0, column=0, columnspan=3, sticky='ew', padx=10, pady=5)

        # 創建下拉式選單
        self.create_dropdown_menu()
            
        # 創建運行程式的按鈕
        self.create_run_button()
    
        # 創建文字輸出欄位與卷軸
        self.create_output_text()
            
        # 創建圖表區域
        self.create_chart_areas()
        
        # 進度條
        self.create_progress_bar()  # 添加這行
        
        self.btc_eth_data = {'1d': {}, '4h': {}}
    
    def create_run_button(self):
        self.run_button = ttk.Button(self.control_frame, text="執行程式", command=self.run_program)
        self.run_button.pack(side=tk.LEFT, padx=(10, 0))

    def create_progress_bar(self):
        self.progress_var = tk.DoubleVar()
        self.progress_frame = tk.Frame(self.control_frame)
        self.progress_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100, length=200)
        self.progress_bar.pack(side=tk.LEFT)
        
        self.progress_label = tk.Label(self.progress_frame, text="0%", width=5)
        self.progress_label.pack(side=tk.LEFT, padx=(5, 0))
    
      
    def update_progress(self, value):
        self.progress_var.set(value)
        self.progress_label.config(text=f"{int(value)}%")
        self.update_idletasks()  # 強制更新 GUI
        

    def create_dropdown_menu(self):
        self.exchange_label = ttk.Label(self.control_frame, text="選擇交易所:")
        self.exchange_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.selected_exchange = tk.StringVar()
        self.exchange_combobox = ttk.Combobox(self.control_frame, textvariable=self.selected_exchange, state="readonly", width=10)
        
        display_names = ('Binance', 'Bybit', 'OKX', 'Bitget', 'BingX')
        self.exchange_combobox['values'] = display_names
        self.exchange_combobox.current(0)  
        self.exchange_combobox.pack(side=tk.LEFT)
        


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
        self.chart_frame_left = tk.Frame(self)
        self.chart_frame_left.grid(row=2, column=0, sticky='nsew', padx=(0, 16), pady=0)
    
        self.figure_left = Figure(figsize=(0, 5), dpi=100)
        self.figure_left.subplots_adjust(left=0.1, right=0.9, top=0.95, bottom=0.05)
        self.chart_left = FigureCanvasTkAgg(self.figure_left, master=self.chart_frame_left)
        self.chart_left.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
        self.chart_frame_middle = tk.Frame(self)
        self.chart_frame_middle.grid(row=1, column=1, rowspan=2, sticky='nsew', padx=0, pady=0)
    
        self.notebook = ttk.Notebook(self.chart_frame_middle)
        self.notebook.pack(fill=tk.BOTH, expand=True)
    
        self.tab_1d = ttk.Frame(self.notebook)
        self.tab_4h = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_1d, text='1D - 圖表')
        self.notebook.add(self.tab_4h, text='4H - 圖表')
    
        for tab in [self.tab_1d, self.tab_4h]:
            canvas = tk.Canvas(tab)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar = tk.Scrollbar(tab, orient=tk.VERTICAL, command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.configure(yscrollcommand=scrollbar.set)
            inner_frame = tk.Frame(canvas)
            canvas.create_window((0, 0), window=inner_frame, anchor='nw')
            inner_frame.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.bind_all("<MouseWheel>", lambda event, canvas=canvas: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
    
        self.figure_1d = Figure(figsize=(15.5, 110), dpi=40)
        self.figure_1d.subplots_adjust(top=0.99, bottom=0.02, left=0.05, right=0.95, hspace=0.1)  # 减少垂直间距
        self.chart_1d = FigureCanvasTkAgg(self.figure_1d, master=self.tab_1d.winfo_children()[0].winfo_children()[0])
        self.chart_1d.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
        self.figure_4h = Figure(figsize=(15.5, 110), dpi=40)
        self.figure_4h.subplots_adjust(top=0.99, bottom=0.02, left=0.05, right=0.95, hspace=0.3)
        self.chart_4h = FigureCanvasTkAgg(self.figure_4h, master=self.tab_4h.winfo_children()[0].winfo_children()[0])
        self.chart_4h.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
        self.chart_frame_right = tk.Frame(self)
        self.chart_frame_right.grid(row=1, column=2, rowspan=2, sticky='nsew', padx=0, pady=0)
    
        self.figure_right = Figure(figsize=(15.2, 20), dpi=40)
        self.figure_right.subplots_adjust(top=0.98, bottom=0.02, left=0.05, right=0.95, hspace=0.3)
        self.chart_right = FigureCanvasTkAgg(self.figure_right, master=self.chart_frame_right)
        self.chart_right.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
        # 初始化數據存儲
        self.btc_eth_data = {'1d': {}, '4h': {}}
    
        # 綁定 Notebook 的切換事件
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
    
        self.tab_1d.update_idletasks()
        self.tab_4h.update_idletasks()
        for tab in [self.tab_1d, self.tab_4h]:
            canvas = tab.winfo_children()[0]
            canvas.config(scrollregion=canvas.bbox("all"))
    
    def _on_mousewheel(self, event):
        self.canvas_right.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_tab_change(self, event):
        selected_tab = self.notebook.index(self.notebook.select())
        if selected_tab == 0:  # 1D tab
            self.draw_btc_eth_chart('1d')
        else:  # 4H tab
            self.draw_btc_eth_chart('4h')

    def draw_btc_eth_chart(self, timeframe):
        self.figure_right.clear()
        gs = self.figure_right.add_gridspec(4, 1, height_ratios=[5, 2, 5, 2])
    
        for i, symbol in enumerate(['BTC/USDT:USDT', 'ETH/USDT:USDT']):
            ax_k = self.figure_right.add_subplot(gs[2*i])
            ax_v = self.figure_right.add_subplot(gs[2*i+1], sharex=ax_k)
    
            bar_width = 0.4 if timeframe == '1d' else 0.075
    
            try:
                df = self.btc_eth_data[timeframe][symbol]
                df_plot = df.iloc[-120:]
                ohlc = df_plot[['date_num', 'open', 'high', 'low', 'close']].values
    
                volume_ratio = df_plot['volume'] / df_plot['volume'].shift(1)
                colors = np.where(df_plot['close'] >= df_plot['open'], 'g', 'r')
                colors = np.where(volume_ratio >= 2.5, '#00E4EA', colors)
    
                for idx, (date, open, high, low, close) in enumerate(ohlc):
                    ax_k.plot([date, date], [low, high], color=colors[idx], alpha=0.6)
                    ax_k.plot([date, date-bar_width/2], [open, open], color=colors[idx], alpha=0.6)
                    ax_k.plot([date, date+bar_width/2], [close, close], color=colors[idx], alpha=0.6)
                    if close >= open:
                        ax_k.add_patch(plt.Rectangle((date-bar_width/2, open), bar_width, close-open, fill=True, color=colors[idx], alpha=0.6))
                    else:
                        ax_k.add_patch(plt.Rectangle((date-bar_width/2, close), bar_width, open-close, fill=True, color=colors[idx], alpha=0.6))
    
                ax_k.plot(df_plot['datetime'], df_plot['ma_30'], color='#DC7D00', label='MA 30', alpha=0.5)
                ax_k.plot(df_plot['datetime'], df_plot['ma_45'], color='#0040FF', label='MA 45', alpha=0.5)
                ax_k.plot(df_plot['datetime'], df_plot['ma_60'], color='#6C00F0', label='MA 60', alpha=0.5)
    
                ax_k.set_title(f"{symbol.split('/')[0]} {timeframe.upper()}", fontsize=32, y=0.9)
                ax_k.tick_params(axis='both', which='both', labelbottom=False, labelleft=False, labelsize=8)
                ax_k.tick_params(axis='both', which='both', length=0, labelsize=0)
    
                volume_colors = np.where(df_plot['close'] >= df_plot['open'], 'g', 'r')
                volume_colors = np.where(volume_ratio >= 2.5, '#00E4EA', volume_colors)
                
                ax_v.bar(df_plot['datetime'], df_plot['volume'], color=volume_colors, alpha=0.4, width=bar_width)
                ax_v.tick_params(axis='both', labelbottom=False, labelleft=False, labelsize=8)
                ax_v.tick_params(axis='both', which='both', length=0, labelsize=0)
                ax_v.tick_params(axis='y', which='both', labelleft=False)
    
            except Exception as e:
                print(f"Error drawing {symbol}: {str(e)}")
                ax_k.text(0.5, 0.5, 'No data', ha='center', fontsize=32)
                ax_k.axis('off')
                ax_v.axis('off')
    
        self.figure_right.tight_layout()
        self.chart_right.draw()


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
        
        ax.set_title(f'{current_date} {exchange_name} 強勢幣別', fontsize=14, y=0.93)
      
        ax.axis('off')  
        
        self.chart_left.draw()
        

    def draw_candlestick_chart(self, symbol_1D_split, symbol_4H_split):
        selected_exchange_proper_case = self.selected_exchange.get()
        selected_exchange = selected_exchange_proper_case.lower()
        exchange = getattr(ccxt, selected_exchange)()
        limit = 180
    
        for timeframe, symbols, figure, chart in [
            ('1d', symbol_1D_split, self.figure_1d, self.chart_1d),
            ('4h', symbol_4H_split, self.figure_4h, self.chart_4h)
        ]:
            n = len(symbols)
            figure.clear()
            figure.set_size_inches(15, 11 * n)
            figure.suptitle(f"{selected_exchange_proper_case} - {timeframe.upper()}", fontsize=48, y=0.99)
        
            gs = figure.add_gridspec(2*n, 1, height_ratios=[5, 2] * n)
            figure.subplots_adjust(top=0.998, bottom=0.02, hspace=0.2)  # 减少垂直间距
        
            for i, symbol in enumerate(symbols):
                ax_k = figure.add_subplot(gs[2*i])
                ax_v = figure.add_subplot(gs[2*i+1], sharex=ax_k)
        
                bar_width = 0.4 if timeframe == '1d' else 0.075
        
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
        
                    volume_ratio = df_plot['volume'] / df_plot['volume'].shift(1)
                    colors = np.where(df_plot['close'] >= df_plot['open'], 'g', 'r')
                    colors = np.where(volume_ratio >= 2.5, '#00E4EA', colors)
                    
                    for idx, (date, open, high, low, close) in enumerate(ohlc):
                        ax_k.plot([date, date], [low, high], color=colors[idx], alpha=0.6)
                        ax_k.plot([date, date-bar_width/2], [open, open], color=colors[idx], alpha=0.6)
                        ax_k.plot([date, date+bar_width/2], [close, close], color=colors[idx], alpha=0.6)
                        if close >= open:
                            ax_k.add_patch(plt.Rectangle((date-bar_width/2, open), bar_width, close-open, fill=True, color=colors[idx], alpha=0.6))
                        else:
                            ax_k.add_patch(plt.Rectangle((date-bar_width/2, close), bar_width, open-close, fill=True, color=colors[idx], alpha=0.6))
        
                    ax_k.plot(df_plot['datetime'], df_plot['ma_30'], color='#DC7D00', label='MA 30', alpha=0.5)
                    ax_k.plot(df_plot['datetime'], df_plot['ma_45'], color='#0040FF', label='MA 45', alpha=0.5)
                    ax_k.plot(df_plot['datetime'], df_plot['ma_60'], color='#6C00F0', label='MA 60', alpha=0.5)
        
                    ax_k.set_title(f"{symbol} {timeframe.upper()}", fontsize=32, y=0.9)
                    ax_k.tick_params(axis='both', which='both', labelbottom=False, labelleft=False, labelsize=8)
                    ax_k.tick_params(axis='both', which='both', length=0, labelsize=0)
        
                    volume_colors = np.where(df_plot['close'] >= df_plot['open'], 'g', 'r')
                    volume_colors = np.where(volume_ratio >= 2.5, '#00E4EA', volume_colors)
                    
                    ax_v.bar(df_plot['datetime'], df_plot['volume'], color=volume_colors, alpha=0.4, width=bar_width)
                    ax_v.tick_params(axis='both', labelbottom=False, labelleft=False, labelsize=8)
                    ax_v.tick_params(axis='both', which='both', length=0, labelsize=0)
                    ax_v.tick_params(axis='y', which='both', labelleft=False)
        
                except:
                    ax_k.text(0.5, 0.5, 'No data', ha='center', fontsize=32)
                    ax_k.axis('off')
                    ax_v.axis('off')
        
            figure.tight_layout()
            figure.subplots_adjust(top=0.97)
            chart.draw()
            
            self.tab_1d.update_idletasks()
            self.tab_4h.update_idletasks()
            for tab in [self.tab_1d, self.tab_4h]:
                canvas = tab.winfo_children()[0]
                canvas.config(scrollregion=canvas.bbox("all"))
            
    
    def run_program(self):
        self.update_progress(0)  # 重製進度條
        
        selected_exchange_proper_case = self.selected_exchange.get() #正確交易所名稱
        selected_exchange = selected_exchange_proper_case.lower() #ccxt辨認之交易所名稱
        
        if selected_exchange in ['binance', 'bybit']:
            def multi_threaded_output_text(message):
                self.output_text.insert(tk.END, message)
                self.output_text.see(tk.END)
                self.output_text.update_idletasks()
                  

                
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
            
                # 更新進度條
                self.update_progress(10)
                
                
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
                        try:
                            results = [executor.submit(process_symbol, symbol, timeframe) for symbol in filtered_markets]  # 提交處理符號的任務
                    
                            # 等待所有任務完成並處理結果
                            for future in concurrent.futures.as_completed(results):
                                result = future.result()  # 獲取任務的結果
                                if result:
                                    higher_base.append(result)  # 將符合條件的交易對及其評分添加到列表中
                        except:
                            pass 
                    
                    # 更新進度條
                    self.update_progress(30)
                    
                    
                    # 將符合條件的交易對按照評分降序排序
                    higher_base.sort(key=lambda x: list(x.values())[0], reverse=True)
                    # 將 higher_base 中值低於 BTC/USDT:USDT 和 ETH/USDT:USDT 的元素刪除
                    # 從 higher_base 中取得 BTC/USDT:USDT 和 ETH/USDT:USDT 的值作為閾值
                    BTC_threshold = next(item[list(item.keys())[0]] for item in higher_base if list(item.keys())[0] == 'BTC/USDT:USDT')
                    ETH_threshold = next(item[list(item.keys())[0]] for item in higher_base if list(item.keys())[0] == 'ETH/USDT:USDT')
                    
                    # 將 higher_base 中值低於 BTC/USDT:USDT 和 ETH/USDT:USDT 的元素刪除
                    higher_base = [item for item in higher_base if list(item.values())[0] >= BTC_threshold and list(item.values())[0] >= ETH_threshold and list(item.values())[0] > 0]
                    
                    # 刪除 BTC/USDT:USDT 和 ETH/USDT:USDT
                    higher_base = [item for item in higher_base if list(item.keys())[0] not in ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'USDC/USDT:USDT','BTCDOM/USDT:USDT']]
                    

                  
                    # 輸出前10名的交易對及其評分
                    for symbol_score_dict in higher_base[:10]:
                        symbol, score = list(symbol_score_dict.items())[0]
                        multi_threaded_output_text(f"\n{symbol}: {score:.2f}")
                    
                    #匯入Tradingview
                    higher_base_10 = higher_base[:10]
                    multi_threaded_output_text("\n\n匯入TV：\n")
                    for symbol in higher_base_10:
                        symbol = symbol.keys()
                        symbol = list(symbol)
                        
                        exchange_upper = selected_exchange_proper_case.upper()
                        for i in symbol:
                            multi_threaded_output_text(f"{exchange_upper}:")
                            multi_threaded_output_text(i.replace('/USDT:USDT', 'USDT.P'))
                            multi_threaded_output_text(",")
                            
                    multi_threaded_output_text("\n\n---------------------------------------------------------------------------------------------\n")
                    
                    
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
                    multi_threaded_output_text("\n")
                    multi_threaded_output_text(i)  # 將重疊的交易對輸出到文字輸出欄位中
                
    
                
                exchange = getattr(ccxt, selected_exchange)()
                limit = 180
                for timeframe in ['1d', '4h']:
                    for symbol in ['BTC/USDT:USDT', 'ETH/USDT:USDT']:
                        try:
                            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
                            df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
                            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
                            df['date_num'] = mdates.date2num(df['datetime'])
                            df['ma_30'] = df['close'].rolling(window=30).mean()
                            df['ma_45'] = df['close'].rolling(window=45).mean()
                            df['ma_60'] = df['close'].rolling(window=60).mean()
                            self.btc_eth_data[timeframe][symbol] = df
                        except Exception as e:
                            print(f"Error fetching data for {symbol} {timeframe}: {str(e)}")
                
                # 更新進度條
                self.update_progress(40)
                
                
                # 繪製圖表
                self.draw_btc_eth_chart('1d')
                # 更新進度條
                self.update_progress(60)
                
                
                self.draw_chart(symbol_1D_split, symbol_4H_split, common_symbols)
                # 更新進度條
                self.update_progress(80)
                

                self.draw_candlestick_chart(symbol_1D_split,symbol_4H_split)
                # 更新進度條
                self.update_progress(100)
                
    
                #計時
                end_time = time.time()  # 結束時間
                total_time = int(end_time - start_time)  # 計算執行時間
                multi_threaded_output_text(f"\n\n執行時間：{total_time}秒")  # 將執行時間輸出到文字輸出欄位中
                
                
            
        elif selected_exchange in ['okx','bitget','bingx']:
            
            def update_output_text(message):
            # 更新文字輸出欄位的內容
                self.output_text.insert(tk.END, message)
                self.output_text.see(tk.END)
                self.output_text.update_idletasks()
                
            
            # 清空文字輸出欄位
            self.output_text.delete(1.0, tk.END)
        

            # 從所選交易所獲取資料
            update_output_text(f"從 {selected_exchange_proper_case} 獲取資料...")
            start_time = time.time()
            exchange = getattr(ccxt, selected_exchange)()  # 使用 getattr() 動態取得交易所類別
    
            markets = exchange.load_markets()
            filtered_markets = [symbol for symbol, market in markets.items() if market['type'] == 'swap' and '/USDT:USDT' in symbol]
    

            limit = 66
            timeframes = ['1d', '4h']
            
            # 更新進度條
            self.update_progress(10)
            
            def calculate_growth_percent(df):
                growth_percent = np.zeros((5, 3))
                for i in range(0, 5):
                    d = df.iloc[-i-1]
                    d2 = df.iloc[-i-2]
                    d3 = df.iloc[-i-3]
                    d4 = df.iloc[-i-4]
                    d5 = df.iloc[-i-5]
                    # 檢查增長百分比的篩選條件
                    
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
                    try:
                        result = process_symbol(symbol, timeframe)
                        if result:
                            higher_base.append(result)
                    except:
                        pass
    
                
                # 更新進度條
                self.update_progress(30)
                
                
                # 將符合條件的交易對按照評分降序排序
                higher_base.sort(key=lambda x: list(x.values())[0], reverse=True)
                # 將 higher_base 中值低於 BTC/USDT:USDT 和 ETH/USDT:USDT 的元素刪除
                # 從 higher_base 中取得 BTC/USDT:USDT 和 ETH/USDT:USDT 的值作為閾值
                BTC_threshold = next(item[list(item.keys())[0]] for item in higher_base if list(item.keys())[0] == 'BTC/USDT:USDT')
                ETH_threshold = next(item[list(item.keys())[0]] for item in higher_base if list(item.keys())[0] == 'ETH/USDT:USDT')
                
                # 將 higher_base 中值低於 BTC/USDT:USDT 和 ETH/USDT:USDT 的元素刪除
                higher_base = [item for item in higher_base if list(item.values())[0] >= BTC_threshold and list(item.values())[0] >= ETH_threshold and list(item.values())[0] > 0]
                
                # 刪除 BTC/USDT:USDT 和 ETH/USDT:USDT
                higher_base = [item for item in higher_base if list(item.keys())[0] not in ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'USDC/USDT:USDT','BTCDOM/USDT:USDT']]


                # 輸出前10名的交易對及其評分
                for symbol_score_dict in higher_base[:10]:
                    symbol, score = list(symbol_score_dict.items())[0]
                    update_output_text(f"\n{symbol}: {score:.2f}")
                
                
                #匯入Tradingview
                higher_base_10 = higher_base[:10]
                update_output_text("\n\n匯入TV：\n")
                for symbol in higher_base_10:
                    symbol = symbol.keys()
                    symbol = list(symbol)
                    
                    exchange_upper = selected_exchange_proper_case.upper()
                    for i in symbol:
                        update_output_text(f"{exchange_upper}:")
                        update_output_text(i.replace('/USDT:USDT', 'USDT.P'))
                        update_output_text(",")
                        
                update_output_text("\n\n---------------------------------------------------------------------------------------------\n")
                
                
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

            common_symbols = list(set(symbol_1D_split) & set(symbol_4H_split))
            update_output_text("\n重複幣別：")
            for i in common_symbols:
                update_output_text("\n")
                update_output_text(i)
    
            exchange = getattr(ccxt, selected_exchange)()
            limit = 180
            for timeframe in ['1d', '4h']:
                for symbol in ['BTC/USDT:USDT', 'ETH/USDT:USDT']:
                    try:
                        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
                        df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
                        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
                        df['date_num'] = mdates.date2num(df['datetime'])
                        df['ma_30'] = df['close'].rolling(window=30).mean()
                        df['ma_45'] = df['close'].rolling(window=45).mean()
                        df['ma_60'] = df['close'].rolling(window=60).mean()
                        self.btc_eth_data[timeframe][symbol] = df
                    except Exception as e:
                        print(f"Error fetching data for {symbol} {timeframe}: {str(e)}")
    
            # 更新進度條
            self.update_progress(40)
            
            
            # 繪製圖表
            self.draw_btc_eth_chart('1d')
            # 更新進度條
            self.update_progress(60)
            
            
            self.draw_chart(symbol_1D_split, symbol_4H_split, common_symbols)
            # 更新進度條
            self.update_progress(80)
            

            self.draw_candlestick_chart(symbol_1D_split,symbol_4H_split)
            # 更新進度條
            self.update_progress(100)
            
            #計時
            end_time = time.time()
            total_time = int(end_time - start_time)
            update_output_text(f"\n\n執行時間：{total_time}秒")
          
if __name__ == "__main__":
    app = App()
    app.mainloop()