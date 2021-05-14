#
# メール送信
# 

import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase
import smtplib
import datetime
from prjlib import *


def send_mail(title,bodymsg,filepath):
    # bodymsg: ''=html, not''=bodymsg
    # filepath: 添付ファイル

    #----------------------------------------------------------------------------
    dsp_msg('メール','生成',1)
    #----------------------------------------------------------------------------

    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    smtp_account_id = get_setting('gmail','id')
    smtp_account_pass = get_setting('gmail','pass')

    from_mail = smtp_account_id
    to_mail = get_setting('gmail','to_mail')

    msg = MIMEMultipart()

    msg['Subject'] = '楽天WEBスクレイピング：' + title
    msg['From'] = from_mail
    msg['To'] = to_mail

    if len(bodymsg)>0:
        msg.attach(MIMEText(bodymsg+u'\n\r', 'plain'))
    else:
        html = make_html('メール用')
        msg.attach(MIMEText(html, 'html'))

    # 添付ファイルの設定
    if len(filepath)>0:
        attachment = MIMEBase('image', 'png')
        file = open(filepath, 'rb+')
        attachment.set_payload(file.read())
        file.close()
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", "attachment", filename=os.path.basename(filepath))
        msg.attach(attachment)

    server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(smtp_account_id, smtp_account_pass)
    server.send_message(msg)
    server.quit()
    #----------------------------------------------------------------------------
    dsp_msg('メール','送信',1)
    #----------------------------------------------------------------------------


if __name__ == '__main__':

    send_mail('テスト','','')

