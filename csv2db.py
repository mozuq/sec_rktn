#
# 楽天証券のWEBログイン後の保有商品一覧から「CSVで保存」ボタンで取得したCSVをDBに保存する
#
#  python csv2db.py [楽天証券ログcsv]
#    引数1：楽天証券ログcsv
# 　 引数なければファイル選択ダイアログ
#

import sys
import csv
import os
import psycopg2
import datetime
import tkinter, tkinter.filedialog, tkinter.messagebox
import json
from prjlib import make_dir, dsp_msg, str2num

def con_db():
    # DB接続文字列
    login_info = json.load(open("info.json", "r", encoding="utf-8"))
    return login_info["database"]["conn"]

def get_table(sql):
    dbcon = con_db()
    with psycopg2.connect(dbcon) as con:
        cur = con.cursor()
        cur.execute(sql)
        tmp = cur.fetchall()
        return tmp

def get_table_col(tbl,typ):
    dbcon = con_db()
    with psycopg2.connect(dbcon) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM {0} LIMIT 1;'.format(tbl))
        if typ == 0:
            # 連結
            tbl_col = ''
            for tmp in [col.name for col in cur.description]: tbl_col += tmp + ','
            return tbl_col[:-1] 
        else:
            # リスト
            return [col.name for col in cur.description]

def insert_table(sql):
    dbcon = con_db()
    with psycopg2.connect(dbcon) as con:
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        return

def csv2list(fname):
    with open(fname) as f:
        reader = csv.reader(f)

        shisan = []
        ginkou = []
        syouhin = []
        kawase = []
        flg = ''
        for row in reader:
            if len(row)==0: continue

            if flg=='':
                if row[0]=='■資産合計欄':
                    flg='資産'
            elif flg=='資産':
                if row[0]=='楽天銀行普通預金残高':
                    ginkou.append(row)
                    flg='保有'
                else:
                    shisan.append(row)
            elif flg=='保有':
                if row[0]=='■ 保有商品詳細 (すべて）':
                    flg='種別'
            elif flg=='種別':
                if row[0]=='■参考為替レート':
                    flg='為替'
                else:
                    syouhin.append(row)
            elif flg=='為替':
                kawase.append(row)

    shisan[0][0]='資産'

    return shisan, ginkou, syouhin, kawase

def list2csv(fname, lname):
    dsp_msg('list2csv',fname,2)
    with open(fname, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(lname)

def csv2db(incsv):
    #----------------------------------------------------------------------------
    dsp_msg('CSV -> DB','開始',1)
    #----------------------------------------------------------------------------
    # csv -> list
    list_shisan, list_ginkou, list_syouhin, list_kawase = csv2list(incsv)

    # csvファイルのタイムスタンプ取得
    time_stamp = datetime.datetime.fromtimestamp(os.path.getmtime(incsv))
    incsv_stamp = time_stamp.strftime('%Y-%m-%d %H:%M:%S')
    outcsv_stamp = time_stamp.strftime('%Y%m%d_%H%M%S')

    #----------------------------------------------------------------------------
    dsp_msg('データチェック','',1)
    #----------------------------------------------------------------------------
    col = get_table_col('syouhin',0)
    for i,rec in enumerate(list_syouhin):
        if rec[0]=='米国株式' and rec[8]=='-':
            dsp_msg('CSV無効','DB登録中止',1)
            return -1

    #----------------------------------------------------------------------------
    dsp_msg('資産データ','',1)
    #----------------------------------------------------------------------------
    # list_shisan -> csv
    list2csv('data/list_shisan.csv',list_shisan)

    # list_shisan -> DB    
    dsp_msg('データ追加','table:shisan',2)

    col = get_table_col('shisan',0)
    for i,rec in enumerate(list_shisan):
        if i==0: continue

        sql = 'SELECT * FROM shisan WHERE datetime=\'{0}\' and shisan=\'{1}\';'.format(incsv_stamp,rec[0])
        tbl = get_table(sql)

        if len(tbl)==0:

            sql = 'INSERT INTO shisan ({0}) VALUES (\'{1}\',\'{2}\',{3},{4},{5},{6},{7},{8},{9});'.format( \
                col[3:], \
                incsv_stamp, \
                rec[0], \
                str2num(rec[1],0), \
                str2num(rec[2],0), \
                str2num(rec[3],1), \
                str2num(rec[4],0), \
                str2num(rec[5],1), \
                str2num(rec[6],0), \
                str2num(rec[7],0)) 

            insert_table(sql)
            dsp_msg(rec[0],'追加',3)
        else:
            dsp_msg(rec[0],'処理なし',3)

    #----------------------------------------------------------------------------
    dsp_msg('銀行口座データ','',1)
    #----------------------------------------------------------------------------
    # list_ginkou -> csv
    list2csv('data/list_ginkou.csv',list_ginkou)

    # list_ginkou -> DB    
    dsp_msg('データ追加','table:ginkou',2)
    
    col = get_table_col('ginkou',0)
    for i,rec in enumerate(list_ginkou):
        sql = 'SELECT * FROM ginkou WHERE datetime=\'{0}\';'.format(incsv_stamp)
        tbl = get_table(sql)

        if len(tbl)==0:

            sql = 'INSERT INTO ginkou ({0}) VALUES (\'{1}\',{2});'.format( \
                col[3:], \
                incsv_stamp, \
                str2num(rec[1],0)) 

            insert_table(sql)
            dsp_msg(rec[0],'追加',3)
        else:
            dsp_msg(rec[0],'処理なし',3)

    #----------------------------------------------------------------------------
    dsp_msg('保有商品データ','',1)
    #----------------------------------------------------------------------------
    # list_syouhin -> csv
    list2csv('data/list_syouhin.csv',list_syouhin)

    # list_syouhin -> DB    
    dsp_msg('データ追加','table:syouhin',2)

    col = get_table_col('syouhin',0)
    for i,rec in enumerate(list_syouhin):
        if i==0: continue

        sql = 'SELECT * FROM syouhin WHERE datetime=\'{0}\' and meigara=\'{1}\';'.format(incsv_stamp,rec[2])
        tbl = get_table(sql)

        if len(tbl)==0:

            sql = 'INSERT INTO syouhin ({0}) VALUES (\'{1}\',\'{2}\',\'{3}\',\'{4}\',\'{5}\',{6},\'{7}\',{8},\'{9}\',{10},\'{11}\',\'{12}\',\'{13}\',{14},\'{15}\',{16},{17},{18},{19});'.format( \
                col[3:], \
                incsv_stamp, \
                rec[0], \
                rec[1], \
                rec[2], \
                rec[3], \
                str2num(rec[4],1), \
                rec[5], \
                str2num(rec[6],1), \
                rec[7], \
                str2num(rec[8],1), \
                rec[9], \
                rec[10], \
                rec[11], \
                str2num(rec[12],1), \
                rec[13], \
                str2num(rec[14],1), \
                str2num(rec[15],1), \
                str2num(rec[16],1), \
                str2num(rec[17],1))     
                
            insert_table(sql)

            dsp_msg(rec[2],'追加',3)
        else:
            dsp_msg(rec[2],'処理なし',3)

    #----------------------------------------------------------------------------
    dsp_msg('為替データ','',1)
    #----------------------------------------------------------------------------
    # list_kawase -> csv
    list2csv('data/list_kawase.csv',list_kawase)

    # list_syouhin -> DB    
    dsp_msg('データ追加','table:kawase',2)

    col = get_table_col('kawase',0)
    for i,rec in enumerate(list_kawase):
        sql = 'SELECT * FROM kawase WHERE datetime=\'{0}\' and tsuuka=\'{1}\';'.format(incsv_stamp,rec[0])
        tbl = get_table(sql)

        if len(tbl)==0:

            sql = 'INSERT INTO kawase ({0}) VALUES (\'{1}\',\'{2}\',\'{3}\',\'{4}\',\'{5}\');'.format( \
                col[3:], \
                incsv_stamp, \
                rec[0], \
                str2num(rec[1],1), \
                rec[2], \
                rec[3], \
                )     

            insert_table(sql)

            dsp_msg(rec[0],'追加',3)
        else:
            dsp_msg(rec[0],'処理なし',3)

    #----------------------------------------------------------------------------
    dsp_msg('CSV -> DB','終了',1)
    #----------------------------------------------------------------------------
    return 0

if __name__ == "__main__":
    #----------------------------------------------------------------------------
    dsp_msg('csv2db.py','開始',1)
    #----------------------------------------------------------------------------

    rgs = sys.argv

    if len(rgs) == 1:
        # ファイル選択ダイアログの表示
        root = tkinter.Tk()
        root.withdraw()
        fTyp = [("csvファイル","*.csv")]
        iDir = os.path.abspath(os.path.dirname(__file__)) + '\\data'
        incsv = tkinter.filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)
        if incsv=='':
            dsp_msg('error','no input file',1)
            exit()
        else:
            dsp_msg('input file',incsv,1)
    else:
        incsv = rgs[1]

    ret = csv2db(incsv)

    #----------------------------------------------------------------------------
    dsp_msg('csv2db.py','終了',1)
    #----------------------------------------------------------------------------
