import streamlit as st
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException , TimeoutException , ElementClickInterceptedException , ElementNotInteractableException
import time
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome import service as fs
import time
import concurrent.futures
from PIL import Image
import random
import os



def time_measurement(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if minutes == 0 and hours == 0:
        return f"{seconds}秒"
    if hours == 0 and minutes != 0:
        return f"{minutes}分{seconds}秒"
    if hours != 0 and minutes != 0:
        return f"{hours}時間{minutes}分{seconds}秒"


def browser_setup():
    """ブラウザを起動する関数"""
    #ブラウザの設定
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument("--incognito")

    #ブラウザの起動（webdriver_managerによりドライバーをインストール）
    CHROMEDRIVER = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()  # chromiumを使用したいので引数でchromiumを指定しておく
    service = fs.Service(CHROMEDRIVER)
    browser = webdriver.Chrome(
        options=options,
        service=service
    )
    browser.implicitly_wait(3)
    return browser

def random_time_sleep():
    random.seed(time.time())
    random_number = random.uniform(1.5, 3)
    time.sleep(random_number)


def insert_newlines(keyword_list, target):
    """ 特定の単語ごとに改行する関数 """
    for i, keyword in enumerate(keyword_list):
        if i == 0:
            continue
        target = target.replace(keyword, "\n" + keyword)
    return target


def mulch_scraping(name , place1 , place2 , detail_url):
    # detailのページにアクセス
    detail_browser = browser_setup()
    detail_browser.get(detail_url)
    st.write("detail_url : " , detail_url)
    time.sleep(1)

    # ページのHTML要素を取得
    page_html = detail_browser.page_source
    soup = BeautifulSoup(page_html, 'html.parser')

    try:
        detail = soup.select_one('#description > div > div.dive-center-details').text
    except (TypeError, AttributeError):
        detail = ""
    # return data


def screenshot_image_display(browser , file_name):
    browser.save_screenshot(file_name)
    image = Image.open(file_name)
    st.write("ファイル名 : " , file_name)
    st.image(image, caption=file_name)


def page_shift_button(browser):
    """ ボタンを押してページを繰り返す関数 """
    # ページ切り替えボタン
    wait = WebDriverWait(browser, 10)
    next_page_is_valid = True
    scroll_6300 = True
    while True:
        try:
            page_shift_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#dsl-list > div > div.pagination--3KOqw > i.arrow--26Z62.padi-icons.padi-icons--carret-right')))
            if scroll_6300:
                browser.execute_script("window.scrollBy(0, 6300)")
            time.sleep(2)
            page_shift_button.click()
            break
        except TimeoutException:
            next_page_is_valid = False
            break
        except ElementClickInterceptedException:
            browser.execute_script("window.scrollBy(0, -500)")
            scroll_6300 = False
            time.sleep(2)
    return next_page_is_valid


def split_list(lst, chunk_size):
    """ リストを特定の長さごとに分割し、それら全てを一つのリストに格納する関数 """
    return [lst[i:i+chunk_size] for i in range(0, len(lst), chunk_size)]
def merge_lists(chunked_list):
    """ split_list()の逆を行う関数 """
    return [item for sublist in chunked_list for item in sublist]


def mulch_thread(function , mulch_argu_list , mulch_divide):
    """
    マルチスレッド並行処理を実行する関数
    function : 並行処理したい関数
    mulch_argu_list : 上記関数入力する引数
    mulch_divide : 一度に何個ずつ並行処理するか
    """
    chunked_mulch_argu_list = split_list(mulch_argu_list, mulch_divide)
    chunked_data_list = []

    def enter_ThreadPoolExecutor(mulch_argu):
        """ 
        ThreadPoolExecutor()に引数を代入する関数
        ※ 入力関数の引数の数だけリストの要素を入力関数に代入し実行
        """
        num_args = function.__code__.co_argcount  # 関数が要求する引数の数を取得
        if len(mulch_argu) < num_args:
            raise ValueError("引数の数が不足しています。")
        args = mulch_argu[:num_args]  # 引数の数だけリストの要素を取り出す
        # 関数を引数で実行
        data = function(*args)
        return data

    st.write(f"<h5>{mulch_divide}個ずつに分割して実行する並行処理開始</h5>", unsafe_allow_html=True)
    start_time = time.time()
    for loop, divided_mulch_argu_list in enumerate(chunked_mulch_argu_list):
        st.write(f"<h4>{loop + 1}個目 / {len(chunked_mulch_argu_list)}個</h4>", unsafe_allow_html=True)
        current_time = time.time()
        elapsed_time = time_measurement( round(current_time - start_time) )
        st.write("経過時間 : " , elapsed_time)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            divided_data_list = executor.map(enter_ThreadPoolExecutor , divided_mulch_argu_list)
        chunked_data_list.append( list(divided_data_list) )
    data_list = merge_lists(chunked_data_list)
    return data_list


def remove_commas(string):
    if ',' in string:
        string = string.replace(',', '')
    return string


def mulch_scraping(main_keyword):
    browser = browser_setup()
    url = 'https://ruri-co.biz-samurai.com'
    browser.get(url)

    # 検索窓にキーワードを入力
    search_box = browser.find_element(By.CSS_SELECTOR, '#keyword')
    search_box.send_keys(main_keyword)
    search_box.send_keys(Keys.ENTER)

    # 利用規約の確認ボタン
    time.sleep(2)
    site_rule_button = browser.find_element(By.CSS_SELECTOR, 'body > div.ui.dimmer.modals.page.transition.visible.active > div > div.actions > button.ui.green.ok.button')
    site_rule_button.click()
    time.sleep(2)

    soup = BeautifulSoup( browser.page_source , 'html.parser')
    suggest_keyword_list = soup.select(f'div > div.ui.active.tab.segment > div.ui.bottom.active.tab.segment > analyzed-by-keyword-rank > table > tbody > tr > td:nth-child(1)')
    search_vol_list = soup.select(f'#s_04 > div > div.ui.active.tab.segment > div.ui.bottom.active.tab.segment > analyzed-by-keyword-rank > table > tbody > tr > td:nth-child(2)')

    all_data = []
    for loop in range(len(suggest_keyword_list)):
        suggest_keyword = suggest_keyword_list[loop].text
        search_vol = search_vol_list[loop].text
        search_vol = int( remove_commas(search_vol) )
        data = {
            'suggest keyword':suggest_keyword,
            'search vol':search_vol,
        }
        all_data.append(data)
    
    sorted_all_data = sorted(all_data, key=lambda x: x['search vol'], reverse=True)
    return sorted_all_data



def main():
    st.write("<p></p>", unsafe_allow_html=True)
    st.title("サジェストキーワードとそのvolを取得")
    st.write("<p></p>", unsafe_allow_html=True)
    main_keyword = st.text_input("キーワードを入力してください")

    if st.button("検索ボリュームを取得"):
        all_data = mulch_scraping(main_keyword)
        df = pd.DataFrame(all_data)
        # CSVファイルのダウンロードボタンを表示
        csv = df.to_csv(index=False)
        st.write("<p></p>", unsafe_allow_html=True)
        st.download_button(
            label='CSV形式でダウンロード',
            data=csv,
            file_name='サジェストキーワードの検索vol.csv',
            mime='text/csv'
        )
        st.st.dataframe(df)


if __name__ == '__main__':
    main()
