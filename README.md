# 強勢加密貨幣篩選

![Demo](https://github.com/user-attachments/assets/699a8c84-4596-4ec6-8ed4-5d21036434e0)


## 功能

### 此程式提供一個圖形化介面，根據不同交易所加密貨幣合約市場的表現進行強勢程度篩選和排序


- 選擇交易所
- 以文字顯示強勢幣別
- 繪製成圖表
- 顯示Ｋ線圖
- 匯入Tradingview清單


## Demo






https://github.com/user-attachments/assets/2ebdcfc1-9898-4530-9184-f0a33a59c768









## 支援交易所

- Binance
- Bybit
- OKX
- Bitget
- BingX
- Gate.io
- MEXC

BingX跟其他交易所不同，有"永續合約"和"標準合約"兩種，當中可做交易的幣別也不完全相同
因此ccxt只能抓到同時存在於"永續合約"和"標準合約"內的幣別

## 使用方式

1. 雙擊開啟 exe 檔
2. 從下拉式選單中選擇一個交易所
3. 點擊「執行程式」按鈕
4. 在輸出區域和圖表區域查看強勢標的篩選結果
5. 複製"匯入TV"後方的文字
6. 貼入Tradingview按下Enter即可匯入清單
![螢幕擷取畫面 2024-09-18 230429](https://github.com/user-attachments/assets/01c73e0b-7b46-4f82-9e1d-355ed42440cd)

![未命名](https://github.com/user-attachments/assets/b8be6f44-159b-4316-8858-92baa0aedb85)



#### Install package :
```
pip install -r requirements.txt
```

## 執行時間

執行時間因交易所限制的 request 速度及交易所標的數量不同而有所不同：
- Binance：20-30 秒
- Bybit：30-40 秒
- OKX ：50-70 秒
- Bitget：60-75 秒
- BingX：80-120 秒
- Gate.io 90-100 秒
- MEXC 120-160 秒

## 強勢標的計算方式

針對BTC和ETH作為比較基準,計算近5日不同時間框架(1D、4H)的MA增長百分比,作為評估強勢程度的指標
對該時間框架最近5個時間點,分別計算30MA、45MA、60MA的增長百分比，且只會篩選出增長百分比逐漸增加的幣別
再將這三個增長百分比取平均,作為平均MA增長百分比來評估強勢程度的指標
以平均MA增長百分比當作依據，排序列出前10名的幣別
僅列出強勢於BTC和ETH的幣別，因此表格可能會有不足10個幣別的狀況


## 程式運行步驟

### 第一步：篩選出近5個時間點MA增長百分比遞增的幣別
對每個交易對的MA進行篩選，確保MA呈現連續上升的趨勢
1. (n-1天的三個MA > n-2天的三個MA > n-3天的三個MA 以此類推)
會得到一個5x3的矩陣,每一行代表一個單位時間

2.計算n-1天之MA比n-2天成長多少百分比，且每日成長百分比需隨時間遞增

3.計算同一天內30MA相較於45MA的成長多少百分比是否大於45MA相較於60MA的成長多少百分比，且必須為隨時間遞增

4.符合所有條件之標的才會進行強勢分數比較

  30MA     45MA    60MA 
  
 [ 2.5%  ,  1.8%  ,  1.2% ] n-1天
 
 [ 2.3%  ,  1.7%  ,  1.1% ] n-2天 
 
 [ 2.1%  ,  1.6%  ,  1.0% ] n-3天 
 
 [ 1.9%  ,  1.5%  ,  0.9% ] n-4天 
 
 [ 1.7%  ,  1.4%  ,  0.8% ] n-5天 


### 第二步：進行強勢程度排序
對每個交易對，計算 3 種 MA 的增長百分比的平均值，得到一個"強勢分數" ，根據強勢評分降序排列交易對

### 第三步：排序兩個時間週期前10名幣別
列出強勢分數前10名幣別




## 計算公式


1. **MA增長百分比**:
   
      ### $\\frac{{Ma_i - Ma_{i-1}}}{{Ma_{i-1}}} \times 100\\% $
   

2. **平均MA增長百分比**:

      ### $\ \\% \bigtriangleup_{\text{avg}} = \frac {1} {n} \sum^n_{i=1}  \left( \frac{(Ma_{i}) - (Ma_{i-1}}{Ma_{i-1}} \right)$


