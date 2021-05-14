#
# 楽天証券サイトへログインしてデータを取得する
#

import os
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.select import Select
from selenium import webdriver
import datetime
import time
import requests
from bs4 import BeautifulSoup
import re
from distutils.dir_util import copy_tree
import shutil
from csv2db import csv2db
from plot import plot
from prjlib import *
from schedule import chk_mail_schedule
from mail import send_mail

#----------------------------------------------------------------------------
DISP_BROWSER = 1
#----------------------------------------------------------------------------

def get_latest_fname(fpath):
    if len(os.listdir(fpath)) == 0:
        return None
    return max (
        [fpath+'/'+ f for f in os.listdir(fpath)], 
        key=os.path.getctime
    )

def make_snapshot(driver):
    if os.path.exists('./sc')==False:
        make_dir('./sc')

    # 画面キャプチャ保存
    driver.set_window_size(1300, 2200)
    dt_now = datetime.datetime.now()
    dt = dt_now.strftime('%Y%m%d-%H%M%S')
    ssfile = './sc/' + dt + '.png'
    driver.save_screenshot(ssfile)
    return ssfile


if __name__ == "__main__":
    try:
        #----------------------------------------------------------------------------
        dsp_msg('rakuten.py','開始',1)
        #----------------------------------------------------------------------------

        #----------------------------------------------------------------------------
        dsp_msg('firefox','設定',1)
        #----------------------------------------------------------------------------
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList",2)
        fp.set_preference("browser.download.dir", os.getcwd()+"\\data")
        fp.set_preference("browser.download.manager.showWhenStarting",False)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/comma-separated-values")

        #----------------------------------------------------------------------------
        dsp_msg('firefox','起動',1)
        #----------------------------------------------------------------------------
        if DISP_BROWSER == 0:
            # Firefoxのヘッドレスモードを有効にする
            options = FirefoxOptions()
            options.add_argument('--headless')

            # Firefoxを起動する
            driver = Firefox(options=options,firefox_profile=fp)
        else:
            driver = Firefox(firefox_profile=fp)

        #----------------------------------------------------------------------------
        dsp_msg('firefox','ログイン',1) 
        #----------------------------------------------------------------------------
        URL = get_setting('sec_rakuten','url')
        USER = get_setting('sec_rakuten','id')
        PASS = get_setting('sec_rakuten','pass')

        # ログイン
        driver.get(URL)

        # 入力
        e = driver.find_element_by_id("form-login-id")
        e.clear()
        e.send_keys(USER)
        e = driver.find_element_by_id("form-login-pass")
        e.clear()
        e.send_keys(PASS)
        # ログイン
        frm = driver.find_element_by_name("loginform")
        frm.submit()

        #----------------------------------------------------------------------------
        dsp_msg('情報取得','開始',1)
        #----------------------------------------------------------------------------
        # 「お知らせ」対応
        # 「楽天証券ロゴ」クリック
        dsp_msg('操作','「楽天証券ロゴ」クリック',2)
        selector = '.pcm-logo-img'
        WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        driver.find_element_by_css_selector(selector).click()

        # ページロード完了まで待機
        #selector = 'asset_total_possess_btn'
        #WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, selector)))

        # 「保有商品一覧」クリック
        dsp_msg('操作','「保有商品一覧」クリック',2)
        time.sleep(1)
        selector = '#asset_total_possess_btn > a:nth-child(1) > img:nth-child(1)'
        #WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        driver.find_element_by_css_selector(selector).click()

        # 「内訳を表示」クリック
        dsp_msg('操作','「内訳を表示」クリック',2)
        time.sleep(1)
        selector = 'td.T0:nth-child(1)'
        #WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        driver.find_element_by_css_selector(selector).click()

        # 「残高情報を取得」クリック
        dsp_msg('操作','「残高情報を取得」クリック',2)
        time.sleep(1)
        selector = '#rbank_async_progless > a:nth-child(1) > img:nth-child(1)'
        #WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        driver.find_element_by_css_selector(selector).click()

        #  ドロップダウン選択
        dsp_msg('操作','ドロップダウン選択',2)
        time.sleep(1)
        selector ='dispBalanceSelect'
        dropdown = driver.find_element_by_id(selector)
        select = Select(dropdown)
        select.select_by_visible_text('前日比')

        # 「CSVで保存」クリック
        dsp_msg('操作','「CSVで保存」クリック',2)
        time.sleep(1)
        selector = '#printLink > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(4) > div:nth-child(1) > a:nth-child(1) > img:nth-child(1)'
        driver.find_element_by_css_selector(selector).click()

        #----------------------------------------------------------------------------
        dsp_msg('firefox','画面キャプチャ保存',1)
        #----------------------------------------------------------------------------
        # 画面キャプチャ保存
        ssfile = make_snapshot(driver)

        #----------------------------------------------------------------------------
        dsp_msg('情報取得','終了',1)
        #----------------------------------------------------------------------------
        driver.quit()

        # DB保存モジュールをコール
        out_csv_fname = get_latest_fname('./data')
        dsp_msg('保存CSV',out_csv_fname,1)
        ret = csv2db(out_csv_fname)

        if ret != -1:
            # プロットモジュールをコール
            plot('OFF')

            # ファイルコピー(メールからの参照用)
            copy_tree('./chart', '//QNAP-TS328/Web/rakuten/chart')

        # html生成
        html = make_html('WEB用')
        with open('./data/rakuten.html','w',encoding='utf-8') as f:
            f.write(html)

        if chk_mail_schedule( datetime.datetime.now() )==True:
            send_mail('正常','','')

    except Exception as e:
        import traceback
        send_mail('エラー',traceback.format_exc(),'')

    finally:
        #----------------------------------------------------------------------------
        dsp_msg('rakuten.py','終了',1)
        #----------------------------------------------------------------------------
