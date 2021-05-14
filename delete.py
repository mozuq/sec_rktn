#
# datetime指定でデータを削除
#

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import psycopg2
from prjlib import *


def get_table(sql):
    try:
        dbcon = get_setting('database','conn')
        with psycopg2.connect(dbcon) as con:
            cur = con.cursor()
            cur.execute(sql)
            tmp = cur.fetchall()
            return tmp
    except:
        return -1

def run_sql(sql):
    dbcon = get_setting('database','conn')
    with psycopg2.connect(dbcon) as con:
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        return

def btn1_clk():
    textbox.delete(0, tk.END)

def btn2_clk():
    datetime = textbox.get()
    if datetime=='':
        words4['text'] = '検索キーワードなし'
        return

    tbl_shisan = get_table('SELECT * FROM shisan WHERE datetime=\'{0}\';'.format(datetime))
    if tbl_shisan!=-1:
        tbl_syouhin = get_table('SELECT * FROM syouhin WHERE datetime=\'{0}\';'.format(datetime))
        tbl_kawase = get_table('SELECT * FROM kawase WHERE datetime=\'{0}\';'.format(datetime))
        tbl_ginkou = get_table('SELECT * FROM ginkou WHERE datetime=\'{0}\';'.format(datetime))
        words4['text'] = 'shisan: {0}\nsyouhin: {1}\nkawase: {2}\nginkou: {3}'.format(len(tbl_shisan),len(tbl_syouhin),len(tbl_kawase),len(tbl_ginkou))
    else:
        words4['text'] = '検索データなし'


def btn3_clk():
    datetime = textbox.get()
    if datetime=='':
        words4['text'] = '削除キーワードなし'
        return

    tbl_shisan = get_table('SELECT * FROM shisan WHERE datetime=\'{0}\';'.format(datetime))
    if tbl_shisan!=-1:
        run_sql('DELETE FROM shisan WHERE datetime=\'{0}\';'.format(datetime))
        run_sql('DELETE FROM syouhin WHERE datetime=\'{0}\';'.format(datetime))
        run_sql('DELETE FROM kawase WHERE datetime=\'{0}\';'.format(datetime))
        run_sql('DELETE FROM ginkou WHERE datetime=\'{0}\';'.format(datetime))
        words4['text'] = '削除完了'
    else:
        words4['text'] = '検索データなし'


if __name__ == '__main__':
    #----------------------------------------------------------------------------
    dsp_msg('delete.py','開始',1)
    #----------------------------------------------------------------------------

    root = tk.Tk()
    root.title('データ削除')
    root.geometry('400x250')

    words = tk.Label(text=u'削除日時：')
    words.place(x=20, y=20)

    textbox = tk.Entry()
    textbox.insert(tk.END, 'xxxx/xx/xx xx:xx:xx')
    textbox.place(x=40, y=60, height=20, width=200)

    button1 = tk.Button(text=u'クリア', command=btn1_clk)
    button1.place(x=250, y=60, height=20, width=100)

    button2 = tk.Button(text=u'検索', command=btn2_clk)
    button2.place(x=250, y=100, height=20, width=100)

    button3 = tk.Button(text=u'データ削除', bg='red', command=btn3_clk)
    button3.place(x=250, y=140, height=20, width=100)

    words4 = tk.Label(text=u'　', anchor='e', justify='left')
    words4.place(x=40, y=100)

    root.mainloop()

    #----------------------------------------------------------------------------
    dsp_msg('delete.py','終了',1)
    #----------------------------------------------------------------------------
