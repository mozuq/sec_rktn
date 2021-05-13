#
# グラフを描画する
#   引数あり：画像表示する
#

import sys
import os
import csv2db
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import japanize_matplotlib
import datetime
import csv
from prjlib import make_dir, dsp_msg


def get_item(tbl,col,srch_word):
    tmp = []
    for x in tbl:
        if x[col]==srch_word: tmp.append(x)
    return tmp

def get_ylim(lst):
    # チャートのY軸リミット
    unum=max(lst)
    lnum=min(lst)
    gap=(unum-lnum)/10
    return [lnum-gap,unum+gap]

def plt_set_fullscreen():
    backend = str(plt.get_backend())
    mgr = plt.get_current_fig_manager()
    if backend == 'TkAgg':
        if os.name == 'nt':
            mgr.window.state('zoomed')
        else:
            mgr.resize(*mgr.window.maxsize())
    elif backend == 'wxAgg':
        mgr.frame.Maximize(True)
    elif backend == 'Qt4Agg':
        mgr.window.showMaximized()

def get_tbl(tbl_name):
    sql = 'select * from {0} order by datetime asc;'.format(tbl_name)
    tbl = csv2db.get_table(sql)
    ####for i in range(len(tbl)): tbl[i]=[0 if n is None else n for n in tbl[i]]        # NULL -> 0
    return tbl

def make_chart(tbl_name,tbl_data,flg,itm,y1d,y2d):
    # tbl_data:テーブルデータ, flg:画面表示フラグ, itm[項目名,カラム], y1d[Y1軸ラベル名,カラム], y2d[Y2軸ラベル名,カラム]

    #----------------------------------------------------------------------------
    dsp_msg('チャート作成',itm[0],2)
    #----------------------------------------------------------------------------

    if itm[1]!=-1:       # table:ginkou
        tbl = []
        for x in tbl_data:
            if x[itm[1]]==itm[0]: tbl.append(x)
    else:
        tbl = tbl_data

    with open('./data/{0}.csv'.format(itm[0]), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(tbl)

    fig = plt.figure(figsize=(12, 8),facecolor='skyblue', tight_layout=True)
    if flg=='OFF': plt.ion()
    xFmt = mdates.DateFormatter('%Y-%m-%d')
    yFmt = plt.FuncFormatter(lambda y, loc: '{:,}'.format(int(y)))

    x  = [r[1] for r in tbl]
    if tbl_name == 'shisan':
        y1 = [r[y1d[1]] for r in tbl]
        y2 = [r[y2d[1]] for r in tbl]
    elif tbl_name == 'syouhin':
        y1 = [r[y1d[1]] for r in tbl]
        y2 = []         
        for r in tbl:
            if r[2]=='国内株式':
                y2.append(r[6]*r[14])           # 保有数量 * 前日比
            elif r[2]=='米国株式':
                y2.append(r[6]*r[14]*(r[16]/r[10]/r[6]))       # 保有数量 * 前日比 * USD( 時価評価額 / 現在値 / 保有数量 )
            elif r[2]=='投資信託':
                y2.append(r[16]/r[10]*r[14])    # 時価評価額 / 現在値 * 前日比
    elif tbl_name == 'ginkou':
        y1 = [r[y1d[1]] for r in tbl]

    ax1 = fig.add_subplot(111,title=itm[0])
    ax1.plot(x, y1, marker='o', color = 'blue', linestyle = '-',label=y1d[0])
    if itm[1]!=-1:
        ax2 = ax1.twinx()
        ax2.plot(x, y2, marker='o', color = 'green', linestyle = ':',label=y2d[0])
        handler1, label1 = ax1.get_legend_handles_labels()
        handler2, label2 = ax2.get_legend_handles_labels()
        ax1.legend(handler1 + handler2, label1 + label2)
        ax1.tick_params(axis='x',colors='black',direction='in')
        ax1.tick_params(axis='y',colors='blue',direction='in')
        ax2.tick_params(axis='y',colors='green',direction='in')
        ax1.yaxis.set_major_formatter(yFmt)
        ax2.yaxis.set_major_formatter(yFmt)
    else:
        handler1, label1 = ax1.get_legend_handles_labels()
        ax1.legend(handler1, label1)
        ax1.tick_params(axis='x',colors='black',direction='in')
        ax1.tick_params(axis='y',colors='blue',direction='in')
        ax1.yaxis.set_major_formatter(yFmt)

    ax_pos = ax1.get_position()
    fig.text(ax_pos.x1-0.05, ax_pos.y0, datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), color='red', fontsize=8)

    ax1.xaxis.set_major_formatter(xFmt)
    ax1.grid(True)

    fig.autofmt_xdate()
    plt.tight_layout()
    fig.savefig('./chart/img_{0}.png'.format(itm[0]))
    if flg=='ON':
        plt_set_fullscreen()
        plt.show()
    else:
        plt.ioff()

def plot(flg):
    #----------------------------------------------------------------------------
    dsp_msg('グラフ生成','開始',1)
    #----------------------------------------------------------------------------

    if flg!='ON': flg='OFF'
    #----------------------------------------------------------------------------
    dsp_msg('グラフ表示',flg,1)
    #----------------------------------------------------------------------------

    make_dir('./chart')

	  #
	  # 処理銘柄を個別指定するのは冴えない、自動処理の案なし
    #
	
    # table: shisan
    tbl_name = 'shisan'
    tbl_data = get_tbl(tbl_name)
    make_chart(tbl_name,tbl_data,flg,['資産合計',2],['評価損益',8],['前日比',4])
    make_chart(tbl_name,tbl_data,flg,['保有商品の評価額合計',2],['評価損益',8],['前日比',4])
    make_chart(tbl_name,tbl_data,flg,['国内株式',2],['評価損益',8],['前日比',4])
    make_chart(tbl_name,tbl_data,flg,['米国株式',2],['評価損益',8],['前日比',4])
    make_chart(tbl_name,tbl_data,flg,['投資信託',2],['評価損益',8],['前日比',4])

    # table: syouhin
    tbl_name = 'syouhin'
    tbl_data = get_tbl(tbl_name)
    make_chart(tbl_name,tbl_data,flg,['イオン',4],['評価損益',18],['前日比',-1])
    make_chart(tbl_name,tbl_data,flg,['アップル',4],['評価損益',18],['前日比',-1])
    make_chart(tbl_name,tbl_data,flg,['楽天日本株4.3倍ブル',4],['評価損益',18],['前日比',-1])

    # table: syouhin
    tbl_name = 'ginkou'
    tbl_data = get_tbl(tbl_name)
    make_chart(tbl_name,tbl_data,flg,['楽天銀行普通預金残高',-1],['金額',2],['',-1])

    #----------------------------------------------------------------------------
    dsp_msg('グラフ生成','終了',1)
    #----------------------------------------------------------------------------


if __name__ == '__main__':
    #----------------------------------------------------------------------------
    dsp_msg('plot.py','開始',1)
    #----------------------------------------------------------------------------

    rgs = sys.argv

    if len(rgs) == 1:
        flg = 'OFF'
    else:
        flg = 'ON'

    plot(flg)

    #----------------------------------------------------------------------------
    dsp_msg('plot.py','終了',1)
    #----------------------------------------------------------------------------
