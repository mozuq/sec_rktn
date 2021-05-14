#
# 共通関数
#

import os
import datetime
import csv
import json

def get_setting(itm,key):
    setting_info = json.load(open('info.json', 'r', encoding='utf-8'))
    return setting_info[itm][key]

def make_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path,exist_ok=True)

def dsp_msg(title,msg,lvl):
    if os.path.exists('./data')==False:
        make_dir('./data')

    if os.path.exists('./data/log.txt')==False:
        with open('./data/log.txt', 'w', encoding='shift_jis') as f:
            f.write('')

    tmp = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ') + ('*' * lvl) + title + ': ' + msg

    with open('./data/log.txt', 'r', encoding='shift_jis') as f:
        old_data = f.readlines()[0:1000]
    with open('./data/log.txt', 'w', encoding='shift_jis') as f:
        f.write(tmp+'\n')
    with open('./data/log.txt', 'a', encoding='shift_jis') as f:
        f.writelines(old_data)

    print(tmp)

def str2num(instr,numtype):
    # numtype: 0=int, 1=float
    if instr=='-' or instr=='' or instr=='未取得': return 'NULL'
    instr = instr.replace(' ','')
    instr = instr.replace(',','')
    instr = instr.replace('%','')
    instr = instr.replace('+','')
    instr = instr.replace('USD','')
    if numtype==0:
        return int(instr)
    else:
        return float(instr)

def num2str(innum,strtype):
    # strype: 0=カンマ, 1=カンマ＋符号
    str = '{:,}'.format(innum)
    if strtype==1 and innum>0:
        str = '+'+'{:,}'.format(innum)

    return str

def make_html(msg):
    dsp_msg('html生成',msg,2)

    linkurl = '<a href="' + get_setting('mail_html','pic_link') + '">※</a>'

    tbl = []
    with open(r'./data/list_shisan.csv','r') as f:
        reader = csv.reader(f)
        for r in reader:
            if r[6]!='0' and r[6]!='-' and r[0]!='資産':
                tbl.append([r[0], '', r[1], r[6], num2str(str2num(r[2],0),1), linkurl.replace('*****',r[0])]) 

    with open(r'./data/list_syouhin.csv','r') as f:
        reader = csv.reader(f)
        for r in reader:
            if r[0]=='国内株式':
                tbl.append([r[0], r[2], r[14], r[16], num2str(int(str2num(r[12],1) * str2num(r[4],0)),1), linkurl.replace('*****',r[2])]) 
            elif r[0]=='米国株式':
                tbl.append([r[0], r[2], r[14], r[16], num2str(int(str2num(r[4],0) * str2num(r[12],1) * (str2num(r[14],0) / str2num(r[8],1) / str2num(r[4],0))),1), linkurl.replace('*****',r[2])])
            elif r[0]=='投資信託':
                tbl.append([r[0], r[2], r[14], r[16], num2str(int(str2num(r[14],0) / str2num(r[8],0) * str2num(r[12],0)),1), linkurl.replace('*****',r[2])]) 

    tbl = sorted(tbl, reverse=False, key=lambda x: x[0])
    tbl = tbl[:-1]
    tbl[0][0] =tbl[0][0][5:]

    for r in tbl:
        if len(r[1])>16:
            r[1] = r[1][0:15] + '...'

    # テンプレート読み込み
    with open(r'./mail_template.html','r',encoding="utf-8") as f:
        reader = csv.reader(f)
        html = ''
        for row in reader:
            if len(row)>0:
                html += row[0]

    # 埋め込みデータ生成
    in_table = ''
    for dt in tbl:
        in_table += '<tr><td align="left">{0}</td><td align="left">{1}</td><td align="right">{2}</td><td align="right">{3}</td><td align="right">{4}</td><td align="center">{5}</td></tr>'.format(dt[0],dt[1],dt[2],dt[3],dt[4],dt[5])

    # テンプレートに埋め込み
    html = html.replace('{0}',in_table)
    html = html.replace('{1}',datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'))
    html = html.replace('{2}',get_setting('mail_html','log_link'))

    return html

