# 強勢加密貨幣篩選

![Demo](https://github.com/user-attachments/assets/699a8c84-4596-4ec6-8ed4-5d21036434e0)


## 功能

### 此程式提供一個圖形化介面，根據不同交易所加密貨幣合約市場的表現進行強勢程度篩選和排序


- 選擇交易所
- 以文字顯示強勢幣別
- 繪製成圖表
- 儲存圖表
- 顯示Ｋ線圖


## Demo





https://github.com/user-attachments/assets/43ca20c5-4bba-4de8-98f2-7ca7ebe2c063






## 支援交易所

- Binance
- Bybit
- OKX
- Bitget
- BingX

BingX跟其他交易所不同，有"永續合約"和"標準合約"兩種，當中可做交易的幣別也不完全相同
因此ccxt只能抓到同時存在於"永續合約"和"標準合約"內的幣別

## 使用方式

### 使用exe執行

優點：不須架設python環境即可直接使用

缺點：檔案較大55mb左右

1. 雙擊開啟 exe 檔
2. 從下拉式選單中選擇一個交易所
3. 點擊「執行程式」按鈕
4. 在輸出區域和圖表區域查看強勢標的篩選結果
5. 點擊「儲存圖表」可將圖表儲存於目前 exe 檔的資料夾


#### Install package :
```
pip install -r requirements.txt
```

## 執行時間

執行時間因交易所限制的 request 速度及交易所標的數量不同而有所不同：
- Binance：25-30 秒
- Bybit：30-40 秒
- OKX ：60-70 秒
- Bitget：60-70 秒
- BingX：80-120 秒

## 強勢標的計算方式

針對BTC和ETH作為比較基準,計算近5日不同時間框架(1D、4H)的MA增長百分比,作為評估強勢程度的指標
對該時間框架最近5個時間點,分別計算30MA、45MA、60MA的增長百分比，且只會篩選出增長百分比逐漸增加的幣別
再將這三個增長百分比取平均,作為平均MA增長百分比來評估強勢程度的指標
以平均MA增長百分比當作依據，排序列出前10名的幣別
僅列出強勢於BTC和ETH的幣別，因此表格可能會有不足10個幣別的狀況


## 程式運行步驟

### 第一步：篩選出近5個時間點MA增長百分比遞增的幣別
對每個交易對的MA進行篩選，確保MA呈現連續上升的趨勢
（以1D為例：即當前值大於前一天的值，前一天的值又大於前兩天的值，以此類推，持續五天）
會得到一個5x3的矩陣,每一行代表一個單位時間,每一列對應一條MA線的漲幅百分比

  30ma     45ma    60ma 
  
 [ 2.5  ,  1.8  ,  1.2 ] n-1天 
 
 [ 2.3  ,  1.7  ,  1.1 ] n-2天 
 
 [ 2.1  ,  1.6  ,  1.0 ] n-3天 
 
 [ 1.9  ,  1.5  ,  0.9 ] n-4天 
 
 [ 1.7  ,  1.4  ,  0.8 ] n-5天 


### 第二步：進行強勢程度排序
對每個交易對，計算 3 種 MA 的增長百分比的平均值，得到一個"強勢分數" ，根據強勢評分降序排列交易對

### 第三步：排序兩個時間週期前10名幣別
將強勢分數低於 BTC 或 ETH 的交易對從列表中刪除，並且最多只列出前10名幣別




## 計算公式


1. **MA增長百分比**:
   
      ### $\\frac{{Ma_i - Ma_{i-1}}}{{Ma_{i-1}}} \times 100\\% $
   

2. **平均MA增長百分比**:

      ### $\ \\% \bigtriangleup_{\text{avg}} = \frac {1} {n} \sum^n_{i=1}  \left( \frac{(Ma_{i}) - (Ma_{i-1}}{Ma_{i-1}} \right)$


## 使用colab網頁執行

#### 第一段程式 :
```
pip install ccxt pandas numpy matplotlib
```

#### 第二段程式 :
```
import ccxt
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from datetime import datetime


selected_exchange=('okx')# 可更改成binance, bybit, okx, bitget, bingx
exchange = getattr(ccxt, selected_exchange)()
markets = exchange.load_markets()


# 获取所有交易对
markets = exchange.load_markets()
filtered_markets = [symbol for symbol, market in markets.items() if market['type'] == 'swap' and '/USDT:USDT' in symbol]


limit = 66
timeframes = ['1d', '4h']  # 修改为两个时间框架

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
    # 获取当前交易对的历史价格数据
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    if len(ohlcv) >= 66:
        # 将数据转换成 DataFrame
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



# 开始时间
start_time = time.time()

symbol_1D, symbol_4H = [], []
common_symbols = []
# 遍历两个时间框架
for timeframe in timeframes:
    if timeframe == "1d":
        print("\n1D：\n")

    elif timeframe == "4h":
        print("\n4H：\n")

    higher_base = []  # 重置higher_base

    # 遍历所有 Bybit 支持的交易对
    for symbol in filtered_markets:
        result = process_symbol(symbol, timeframe)
        if result:
            higher_base.append(result)

    # 按强势分数降序排列higher_base
    higher_base.sort(key=lambda x: list(x.values())[0], reverse=True)

    # 將 higher_base 中值低於 BTC/USDT:USDT 和 ETH/USDT:USDT 的元素刪除
    # 從 higher_base 中取得 BTC/USDT:USDT 和 ETH/USDT:USDT 的值作為閾值
    BTC_threshold = next(item[list(item.keys())[0]] for item in higher_base if list(item.keys())[0] == 'BTC/USDT:USDT')
    ETH_threshold = next(item[list(item.keys())[0]] for item in higher_base if list(item.keys())[0] == 'ETH/USDT:USDT')

    # 將 higher_base 中值低於 BTC/USDT:USDT 和 ETH/USDT:USDT 的元素刪除
    higher_base = [item for item in higher_base if list(item.values())[0] >= BTC_threshold and list(item.values())[0] >= ETH_threshold and list(item.values())[0] > 0]

    # 刪除 BTC/USDT:USDT 和 ETH/USDT:USDT
    higher_base = [item for item in higher_base if list(item.keys())[0] not in ['BTC/USDT:USDT', 'ETH/USDT:USDT','USDC/USDT:USDT','BTCDOM/USDT:USDT','ETHDOM/USDT:USDT']]

    # 打印排序后的结果
    for symbol in higher_base[:10]:  # 仅打印前10个结果
        symbol, score = list(symbol.items())[0]
        print(f"{symbol}: {score:.2f}")

    # 根據時間間隔更新相應的交易對列表
    for symbol_score_dict in higher_base[:10]:
        symbol = list(symbol_score_dict.keys())[0]
        if timeframe == "1d":
            symbol_1D.append(symbol)  # 將1D時間間隔的交易對添加到列表中
            symbol_1D_split = [symbol.split('/')[0] for symbol in symbol_1D]  # 將交易對進行拆分，只保留基礎貨幣部分
        elif timeframe == "4h":
            symbol_4H.append(symbol)  # 將4H時間間隔的交易對添加到列表中
            symbol_4H_split = [symbol.split('/')[0] for symbol in symbol_4H]  # 將交易對進行拆分，只保留基礎貨幣部分


symbol_1D_split += [''] * (10 - len(symbol_1D_split))
symbol_4H_split += [''] * (10 - len(symbol_4H_split))
common_symbols += [''] * (10 - len(common_symbols))
common_symbols = []
common_symbols = list(set(symbol_1D_split) & set(symbol_4H_split))  # 找出1D和4H時間間隔中都存在的交易對
print("\n重複幣別：")
for i in common_symbols:
    print(i)  # 將重疊的交易對輸出到文字輸出欄位中

# 结束时间
end_time = time.time()

# 计算程序运行时间
total_time = int(end_time - start_time)
print(f"\n執行時間：{total_time}秒")



########繪圖設置########

# 添加編號列和填充值來確保長度為10
numbers = list(range(1, 11))
symbol_1D_split += [''] * (10 - len(symbol_1D_split))
symbol_4H_split += [''] * (10 - len(symbol_4H_split))
common_symbols += [''] * (10 - len(common_symbols))

df_symbols = pd.DataFrame({
    'No.': numbers,
    '1D': symbol_1D_split,
    '4H': symbol_4H_split,
    'Common': common_symbols
})

# 設置圖表佈局
plt.figure(figsize=(6.5, 4.5))  # 調整寬度以適應新的列

# 創建表格並配置底色
colors = [['#f7f7f7', '#ffffff', '#f7f7f7', '#ffffff']] * 5 + [['#ffffff', '#f7f7f7', '#ffffff', '#f7f7f7']] * 5
table = plt.table(cellText=df_symbols.values, colLabels=df_symbols.columns, loc='center', cellLoc='center', cellColours=colors)

# 設置表頭顏色和字體
table.set_fontsize(12)
table.auto_set_column_width(col=list(range(len(df_symbols.columns))))
for key, cell in table.get_celld().items():
    if key[0] == 0:
        cell.set_text_props(fontweight='bold', color='white')
        cell.set_facecolor('gray')  # 標題欄位
    elif key[0] % 2 == 0:
        cell.set_facecolor('#E6E6E6')  # 偶數行
    else:
        cell.set_facecolor('#CCCCCC')  # 奇數行

# 調整表格每格的長寬比例
table.scale(1, 1.5)
# 獲取當前日期並格式化為"YYYYMMDD"
current_date = datetime.now().strftime("%Y-%m-%d")

plt.subplots_adjust(top=1)

if selected_exchange in ['binance', 'bybit','okx', 'bitget', 'bingx']:
    if selected_exchange == 'binance':
        exchange_name = 'Binance'

    elif selected_exchange == 'bybit':
        exchange_name = 'Bybit'
    elif selected_exchange == 'okx':
        exchange_name = 'OKX'
    elif selected_exchange == 'bitget':
        exchange_name = 'Bitget'
    elif selected_exchange == 'bingx':
        exchange_name = 'BingX'

plt.figtext(0.5, 0.97, f'{current_date} {exchange_name} Bullish Crypto', ha='center', va='top', fontsize=14, color='black')

# 隱藏坐標軸
plt.axis('off')

# 顯示圖表
plt.show()
```
