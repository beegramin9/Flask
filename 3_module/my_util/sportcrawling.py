from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from msedge.selenium_tools import Edge, EdgeOptions

import time
from random import *
from tqdm import tqdm

options = EdgeOptions()
options.use_chromium = True
options.add_argument("headless")
options.add_argument("disable-gpu")

# Message: element not interactable 오류 방지
options.add_argument('--window-size=1920x1080')

driver = Edge('./msedgedriver.exe', options=options)

base_url = "https://sports.news.naver.com/index.nhn"
driver.get(base_url)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# 메뉴 태그
menu_set = soup.select('a.link_main_menu')
time.sleep(uniform(0.3, 0.7))

menu_list = []
for menu in menu_set[1:-4]:
    link = menu.get('href').split('/')[1]
    menu_list.append(link)

driver.close()

# 스포츠 기사
driver = Edge('./msedgedriver.exe', options=options)

# 모든 메뉴를 돌아가며 크롤링
for menu in tqdm(menu_list):
    time.sleep(uniform(0.3, 0.7))

    page_num = 1
    while True:
        url = f"https://sports.news.naver.com/{menu}/news/index.nhn?isphoto=N&page={page_num}"
        driver.get(url)
        time.sleep(uniform(0.3, 0.7))

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 새로운 메뉴마다 driver.get(url)로 새로운 창을 띄우지 않기 위해 기존 창으로 돌아가기
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(uniform(0.3, 0.7))

        titles = soup.select('a.title')
        today = datetime.now().strftime("%Y_%m_%d")
        f = open(f'./result/{today} 네이버스포츠 기사제목.txt', 'a', encoding='utf8')
        for title in titles:
            f.write(title.text + '\n')
        f.close()

        if page_num % 10 == 0:
            # 페이지가 10, 20, 30 일때 '다음' 버튼이 있으면 누르고 없으면 pass한다.
            try:
                # page_source를 위에서 사용했어도 여전히 driver method 사용 가능
                next = driver.find_element_by_css_selector(
                    '#_pageList > a.next')
                time.sleep(uniform(0.3, 0.7))
                next.click()
            # '다음' 버튼이 없을 때
            except:
                """ 언제 끝내야 하는가?
                페이지네이션의 마지막 페이지 넘버를 받아온다.
                그게 현재 페이지랑 같다면 루프를 닫으면 된다.

                주의: 현재 페이지의 태그는 strong이기 때문에 10배수 페이지에서 받아올 수 없다.
                (10배수 페이지 == 현재 페이지, 그러므로 마지막 태그가 10이 아닌 9가 됨) 
                """
                pass

        # 그러므로 마지막 페이저 넘버를 시작할 때, 즉 페이지넘버 = 1일때 받아야 함
        if page_num % 10 == 1:
            # '다음' 버튼이 있기 때문에 pagebox[-1]가 마지막 페이지의 인덱스다.
            try:
                pagebox = soup.select('#_pageList a')
                time.sleep(uniform(0.3, 0.7))

                # 페이지가 2개라서 a태그가 하나밖에 없을 때
                if len(pagebox) == 1:
                    last_page = int(pagebox[0].text)
                    # 여기원래 int(pagebox[0].text) + 1 이었음. 안되면 이걸로
                # 페이지 3개 이상
                else:
                    last_page = int(pagebox[-1].text)
                    # 여기원래 int(pagebox[-2].text) + 1 이었음. 안되면 이걸로
            except:
                # 페이지가 1개라서(ex.마지막 페이지가 21) a는 하나도 없고 자기자신이 strong일 때
                last_page = int(soup.select_one('#_pageList strong').text)

        if last_page == page_num:
            break
        else:
            page_num += 1
