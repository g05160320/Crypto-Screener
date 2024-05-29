import tkinter as tk
from tkinter import ttk
import ccxt
import pandas as pd
import numpy as np
import concurrent.futures
import time
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime

matplotlib.use('TkAgg')

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("強勢加密貨幣篩選")
        self.geometry("650x800")  # 調整主視窗大小
            
        # 創建下拉式選單
        self.create_dropdown_menu()
            
        # 創建文字輸出欄位與卷軸
        self.create_output_text()
            
        # 按鈕,用於運行程式並輸出結果到文字輸出欄位
        self.create_run_button()
    
        # 新增创建保存按钮的调用
        self.create_save_button()
    
        # 創建圖表區域
        self.create_chart_area()

    def create_run_button(self):
        # 創建運行程式的按鈕
        self.run_button = ttk.Button(self, text="執行程式", command=self.run_program)
        self.run_button.pack(pady=(0, 0))
        
    def create_save_button(self):
        # 创建保存按钮
        self.save_button = ttk.Button(self, text="儲存圖表", command=self.save_chart)
        self.save_button.pack(side=tk.BOTTOM, pady=(10, 0))
        
        
    def create_dropdown_menu(self):
        # 創建下拉式選單的標籤
        self.exchange_label = ttk.Label(self, text="選擇交易所:")
        self.exchange_label.pack(pady=(10, 0))
        
        # 創建下拉式選單本身
        self.selected_exchange = tk.StringVar()
        self.exchange_combobox = ttk.Combobox(self, textvariable=self.selected_exchange, state="readonly")
        
        # 在介面上顯示正確大小寫的交易所名稱
        display_names = ('Binance', 'Bybit', 'OKX', 'Bitget', 'BingX')
        self.exchange_combobox['values'] = display_names
        self.exchange_combobox.current(0)  
        self.exchange_combobox.pack(pady=(0, 10))
        
    def save_chart(self):
        # 获取当前的日期时间
        current_date = datetime.now().strftime("%Y-%m-%d")
    
        # 根据选择的交易所名称创建文件名
        exchange_name = self.selected_exchange.get()
        
        filename = f"{current_date}_強勢幣別({exchange_name}).jpg"
        # 将图表保存为图片
        self.figure.savefig(filename)

        
    def create_output_text(self):
    # 創建文字輸出欄位及相應的卷軸
        self.output_frame = tk.Frame(self)
        self.output_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.output_text = tk.Text(self.output_frame, height=15, width=60, font=("Microsoft JhengHei", 11))
        self.scrollbar = tk.Scrollbar(self.output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=self.scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_chart_area(self):
        self.chart_frame = tk.Frame(self, height=380)  # 調整高度以避免被遮擋
        self.chart_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, anchor="center")
        self.chart_frame.pack_propagate(False)  # 禁止 Frame 自動調整大小
    
        self.figure = Figure(figsize=(8, 6), dpi=100)  # 調整 Figure 的大小
        self.figure.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)  # 調整圖表周圍的留白
        self.chart = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.chart.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

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
        
        self.figure.clear()  
        ax = self.figure.add_subplot(111) 
            
        colors = [['#f7f7f7', '#ffffff', '#f7f7f7', '#ffffff']] * 5 + [['#ffffff', '#f7f7f7', '#ffffff', '#f7f7f7']] * 5
        
        # 指定每列的寬度
        col_widths = [0.1, 0.35, 0.35, 0.35]  # 根據需要調整每列的寬度
        #圖表設置
        table = ax.table(cellText=df_symbols.values, colLabels=df_symbols.columns, loc='center', 
                         cellLoc='center', cellColours=colors, colWidths=col_widths)
        
        table.set_fontsize(12)  
        for key, cell in table.get_celld().items():
            if key[0] == 0:
                cell.set_text_props(fontweight='bold', color='white')  
                cell.set_facecolor('gray')  
            elif key[0] % 2 == 0:
                cell.set_facecolor('#E6E6E6')  
            else:
                cell.set_facecolor('#CCCCCC')  
            
        table.scale(1, 1.5)  
        
        current_date = datetime.now().strftime("%Y-%m-%d")  
        exchange_name = self.selected_exchange.get()
        
        if exchange_name in ['Binance', 'Bybit']:
            ax.set_title(f'{current_date} {exchange_name} 強勢幣別', fontsize=14, y=0.98) 
            
        elif exchange_name in ['OKX', 'Bitget', 'Bingx']:
            if exchange_name == 'OKX':
                exchange_name = 'OKX'  
            elif exchange_name == 'Bitget':
                exchange_name = 'Bitget'  
            elif exchange_name == 'Bingx':
                exchange_name = 'BingX'  
            ax.set_title(f'{current_date} {exchange_name} 強勢幣別', fontsize=14, y=0.98)
      
        ax.axis('off')  
        
        self.chart.draw()

        
    def run_program(self):
        selected_exchange_proper_case = self.selected_exchange.get() #正確交易所名稱
        selected_exchange = selected_exchange_proper_case.lower() #小寫交易所名稱
        
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
                    higher_base = [item for item in higher_base if list(item.values())[0] >= BTC_threshold and list(item.values())[0] >= ETH_threshold]
                    
                    # 刪除 BTC/USDT:USDT 和 ETH/USDT:USDT
                    higher_base = [item for item in higher_base if list(item.keys())[0] not in ['BTC/USDT:USDT', 'ETH/USDT:USDT']]

                    
                  
                    # 輸出前10名的交易對及其評分
                    for symbol_score_dict in higher_base[:10]:
                        symbol, score = list(symbol_score_dict.items())[0]
                        multi_threaded_output_text(f"{symbol}: {score:.2f}")
                
                    # 根據時間間隔更新相應的交易對列表
                    for symbol_score_dict in higher_base[:10]:
                        symbol = list(symbol_score_dict.keys())[0]
                        if timeframe == "1d":
                            symbol_1D.append(symbol)  # 將1D時間間隔的交易對添加到列表中
                            symbol_1D_split = [symbol.split('/')[0] for symbol in symbol_1D]  # 將交易對進行拆分，只保留基礎貨幣部分
                        elif timeframe == "4h":
                            symbol_4H.append(symbol)  # 將4H時間間隔的交易對添加到列表中
                            symbol_4H_split = [symbol.split('/')[0] for symbol in symbol_4H]  # 將交易對進行拆分，只保留基礎貨幣部分
                
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
                    higher_base = [item for item in higher_base if list(item.values())[0] >= BTC_threshold and list(item.values())[0] >= ETH_threshold]
                    
                    # 刪除 BTC/USDT:USDT 和 ETH/USDT:USDT
                    higher_base = [item for item in higher_base if list(item.keys())[0] not in ['BTC/USDT:USDT', 'ETH/USDT:USDT']]


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
          
if __name__ == "__main__":
    app = App()
    app.mainloop()