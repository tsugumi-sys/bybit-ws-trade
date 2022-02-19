import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy.orm import Session
from sqlalchemy import text
import numpy as np
import pandas as pd
import sys

sys.path.append(".")
from bybit_websocket.db.database import SessionLocal


def get_ohlcv_data(db: Session, symbol: str):
    query = text("select * from ohlcv where ohlcv.symbol = :symbol")
    return db.execute(query, {"symbol": symbol}).all()


def volume_plot(ax, ohlcv_data):
    volumes = [item.volume for item in ohlcv_data]
    ax.plot([i for i in range(len(volumes))], volumes)


def get_ohlcv_df(ohlcv_data) -> pd.DataFrame:
    data = {"timestamp":[], "open":[], "high":[], "low":[], "close":[], "volume":[]}
    print(data["open"])
    for item in ohlcv_data:
        data["open"].append(item.open)
        data["high"].append(item.high)
        data["low"].append(item.low)
        data["close"].append(item.close)
        data["volume"].append(item.volume)
        data["timestamp"].append(item.timestamp)

    df = pd.DataFrame(data)
    return df    


def ohlcv_plot(ax,df):
    """
    matplotlibのAxesオブジェクトにローソク足を描画する.
    :param ax:ローソク足を描画するAxesオブジェクト.
    :param df:DataFrameオブジェクト. 必要なカラムはtimestamp,open,high,low,close,volume.
    """
    # timestampからdatetimeを作りindexにする。datetimeは日本時間を指定。
    # df["datetime"]=pd.to_datetime(df["timestamp"], unit='s')
    # df=df.set_index("datetime")
    # df=df.tz_localize('utc').tz_convert('Asia/Tokyo')

    # ローソク足の幅を設定
    # matplotlib上でwidth=1->1日となるのでローソク足の時間軸に応じて幅を設定
    time_span=5
    w=time_span/(24*60*60)

    # ローソク足
    # 陽線と陰線で色を変えるため、それぞれのindexを取得
    idx1=df.index[df["close"]>=df["open"]]
    idx0=df.index[df["close"]<df["open"]]

    # 実体
    df["body"]=df["close"]-df["open"]
    df["body"]=df["body"].abs()
    ax.bar(idx1,df.loc[idx1,"body"],width=w * (1-0.2),bottom=df.loc[idx1,"open"],linewidth=1,color="red",zorder=2)
    ax.bar(idx0,df.loc[idx0,"body"],width=w * (1-0.2),bottom=df.loc[idx0,"close"],linewidth=1,color="green",zorder=2)

    # ヒゲ
    # zorderを指定して実体の後ろになるようにする。
    ax.vlines(df.index,df["low"],df["high"],linewidth=1,color="blue",zorder=1)

    # 指標 (SMA,BB)
    window=20

    # SMA
    sma=df["close"].rolling(window).mean()
    ax.plot(df.index,sma,linewidth=.5)

    # 価格目盛調整
    # グラフ下部に出来高の棒グラフを描画するので、そのためのスペースを空けるよう目盛を調整する
    ymin,ymax=df["low"].min(),df["high"].max()
    ticks=ax.get_yticks()
    margin=(len(ticks)+4)/5
    tick_span=ticks[1]-ticks[0]
    min_tick=ticks[0]-tick_span*margin
    ax.set_ylim(min_tick, ticks[-1])
    ax.set_yticks(ticks[1:])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M")) 
    plt.xticks(rotation=30)
    ax.set_axisbelow(True)
    ax.grid(True)

    # 出来高
    axv=ax.twinx()
    axv.bar(idx1,df.loc[idx1,"volume"],width=w,color="#33c076",edgecolor="#33b066",linewidth=1)
    axv.bar(idx0,df.loc[idx0,"volume"],width=w,color="#ff6060",edgecolor="#ff5050",linewidth=1)
    # 出来高目盛が価格目盛にかぶらないよう調整
    ymax=df["volume"].max()
    axv.set_ylim(0,ymax*5)
    ytick=ymax//3
    tmp=0
    cnt=0
    while ytick-tmp>0:
        cnt+=1
        ytick-=tmp
        tmp=ytick%(10**cnt)
    axv.set_axisbelow(True)
    axv.set_yticks(np.arange(0,ymax,ytick))
    axv.tick_params(left=True,labelleft=True,right=False,labelright=False)
    axv.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

    plt.show()
    

def main():
    symbol = "BTCUSDT"
    
    with SessionLocal() as db:
        ohlcv_data = get_ohlcv_data(db=db, symbol=symbol)

    # fig, axes = plt.subplots(2, 1, figsize=(16, 8))
    # axes = axes.flatten()

    ohlcv_df = get_ohlcv_df(ohlcv_data)

    fig, ax = plt.subplots(figsize=(16, 8))
    ohlcv_plot(ax, ohlcv_df)

if __name__ == "__main__":
    main()