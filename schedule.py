#
# スケジューラ
#

import datetime
import locale
from prjlib import *


def chk_mail_schedule(in_datetime):
    # in_datetime: xx-xx-xx xx:xx

    #locale.setlocale(locale.LC_TIME, 'ja_JP')  #errorになる
    locale.setlocale(locale.LC_TIME, '')
    #print(locale.getlocale(locale.LC_TIME))

    in_date = in_datetime.strftime('%Y-%m-%d')
    in_time = in_datetime.strftime('%H:%M')
    in_weekday = in_datetime.strftime('%a')

    now_data = datetime.datetime.now().strftime('%Y-%m-%d')
    now_time = datetime.datetime.now().strftime('%H:%M')
    now_weekday = datetime.datetime.now().strftime('%a')

    on_weekdays = get_setting('mail_schedule','on_weekdays')
    on_times = get_setting('mail_schedule','on_times')
    off_weekdays = get_setting('mail_schedule','off_weekdays')
    off_times = get_setting('mail_schedule','off_times')

    flg = False
    for on_weekday in on_weekdays:
        if in_weekday==on_weekday:
            for on_time in on_times:
                on_start = on_time[:5]
                on_end = on_time[6:]
                if in_time>=on_start and in_time<=on_end:
                    flg = True
                    break
    if flg==1:
        for off_weekday in off_weekdays:
            if in_weekday==off_weekday:
                for off_time in off_times:
                    off_start = off_time[:5]
                    off_end = off_time[6:]
                    if in_time>=off_start and in_time<=off_end:
                        flg = False
                        break

    dsp_msg('メール送信スケジューラチェック',str(flg),2)

    return flg


if __name__ == '__main__':
    #----------------------------------------------------------------------------
    dsp_msg('schedule.py','開始',1)
    #----------------------------------------------------------------------------

    chk_datetime = datetime.datetime.now()

    ret = chk_mail_schedule(chk_datetime)
    print(ret)

    #----------------------------------------------------------------------------
    dsp_msg('schedule.py','終了',1)
    #----------------------------------------------------------------------------
