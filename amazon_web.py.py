import csv
import time
import random
import locale
import datetime
import calendar
from urllib import request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def save_csv(keyword,amazon_ranking_list):
   locale.setlocale(locale.LC_CTYPE, "Japanese_Japan.932")
   date_now = datetime.datetime.now()
   name = date_now.strftime('%Y年%m月%d日 %H時%M分 ')+ str(keyword) +".csv"
   
   with open(name, "w", encoding='shift_jis', errors="ignore") as f:
       writer = csv.writer(f, lineterminator="\n")
       writer.writerows(amazon_ranking_list)



def start_chrome():
    # chromedriverのPATHを指定（Pythonファイルと同じフォルダの場合）
    driver_path = './chromedriver'

    # Chrome起動
    #driver = webdriver.Chrome(driver_path)
    driver = webdriver.Chrome(executable_path=driver_path)
    #driver.maximize_window() # 画面サイズ最大化

    # formsログインURL
    url = 'https://www.amazon.co.jp/?&tag=hydraamazonav-22&ref=pd_sl_7ibq2d37on_e&adgrpid=56100363354&hvpone=&hvptwo=&hvadid=289260145877&hvpos=&hvnetw=g&hvrand=8098979518073259849&hvqmt=e&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=1009257&hvtargid=kwd-10573980&hydadcr=27922_11415158&gclid=Cj0KCQiAwf39BRCCARIsALXWETyRJELxXcE7bjhJ10ApyZBosvRoO8U5YJPT_1Sjkc3wpEAFppXO_ZAaAv8yEALw_wcB'
    driver.get(url)

    return driver

def search_amzon(driver,keyword,wait_time):


    #検索ボックスを探す
    login_id_xpath = '//*[@id="twotabsearchtextbox"]'
    # xpathの要素が見つかるまで待機します。
    WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, login_id_xpath)))
    driver.find_element_by_name("field-keywords").send_keys(keyword)
    time.sleep(2) # クリックされずに処理が終わるのを防ぐために追加。
    driver.find_element_by_xpath('//*[@id="nav-search-submit-text"]/input').click()

    return driver

def evaluation_amzon(driver,wait_time):

    switching_xpath = '//*[@id="a-autoid-0-announce"]/span[2]'
    WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, switching_xpath)))
    driver.find_element_by_xpath(switching_xpath).click()

    evaluation_xpath = '//*[@id="s-result-sort-select_3"]'
    WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, evaluation_xpath)))
    driver.find_element_by_xpath(evaluation_xpath).click()

    return driver

def get_infomation_amazon(driver,wait_time,keyword):
    url = driver.current_url
    # Chromeを終了
    driver.quit()

    html = request.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    main_item_indexs = soup.find_all("div", "sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col sg-col-4-of-20")
    
    i = 0
    
    amazon_ranking_list = []
    for main_item_index in main_item_indexs:
       title = main_item_index.find("span", "a-size-base-plus a-color-base a-text-normal").get_text().lstrip()
       item_urls = "https://www.amazon.co.jp" + main_item_index.find("a").attrs['href']
       rank = main_item_index.find("div", "a-section a-spacing-none a-spacing-top-micro").get_text().strip()
       rank = rank.split('\n', 1)[0]
       if rank[0:1] != '5':
           rank = "評価なし"

       try:
            price = main_item_index.find("span", "a-price-whole").get_text().strip()
       except AttributeError:
            price = '価格設定なし'
        
       amazon_ranking_list.append([title,rank,price,item_urls])
       i += 1
       if i == 20:
           break

    save_csv(keyword,amazon_ranking_list)
    return driver

    

if __name__ == '__main__':


    print('検索ワードを入力してください')
    keyword = input()

    #最大待機時間（秒）
    wait_time = 30

    print('Amazonアクセス')
    driver = start_chrome()


    #検索
    search_amzon(driver,keyword,wait_time)

    #いれかえ
    evaluation_amzon(driver,wait_time)

    #情報取得
    get_infomation_amazon(driver,wait_time,keyword)


    
