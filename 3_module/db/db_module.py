import pandas as pd
import numpy as np

from bs4 import BeautifulSoup
import requests

from datetime import *
from dateutil.parser import parse

import sqlite3
conn = sqlite3.connect('./db/covid.db', check_same_thread=False)
cur = conn.cursor()

# app.py 기준
key_fd = open('./keys/gov_data_api_key.txt', mode='r')
govapi_key = key_fd.read(100)
key_fd.close()

# db 마지막 날짜와 오늘 날짜를 비교해서 그 사이 데이터를 모두 받아오도록
# 모든 빈 날짜들을 다 받아올 수 있지만 코드가 매우 길어진다.


def renewal_all_info():
    # 오늘 날짜
    today = datetime.today().date()

    sql = """ select * from all_info ORDER BY ROWID DESC LIMIT 1 """
    cur.execute(sql)
    row = cur.fetchone()
    # DB 맨 마지막 행 말짜
    db_last_day = row[0]
    conn.commit()

    # DB 마지막 날짜 datetime형식으로
    last_day = parse(db_last_day).date()

    if today == last_day:
        print('이미 최신정보로 업데이트되었습니다.')
    else:
        elapsed_count = (today - last_day).days
        elapsed_series = pd.date_range(last_day, periods=elapsed_count + 1)

        date_list, city_list, death_toll_list, increase_list, case_list, local_list, inflow_list, isolation_list, release_list, per100k_list = [
        ], [], [], [], [], [], [], [], [], []

        corona_url = "http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson"

        for date in elapsed_series:
            date = date.strftime('%Y%m%d')

            url = f"{corona_url}?serviceKey={govapi_key}&pageNo=1&numOfRows=1&startCreateDt={date}&endCreateDt={date}"

            result = requests.get(url)
            soup = BeautifulSoup(result.text, 'xml')

            # 날짜
            date = soup.select('createDt')
            # 도시
            city = soup.select('gubun')
            # 사망자 수
            death_toll = soup.select('deathCnt')
            # 전일대비 증감 수
            increase = soup.select('incDec')
            # 일일 확진자 수
            case = soup.select('defCnt')
            # 지역발생 수
            local = soup.select('localOccCnt')
            # 해외유입 수
            inflow = soup.select('overFlowCnt')
            # 격리중 확진자 수
            isolation = soup.select('isolIngCnt')
            # 일일 격리 해제 수
            release = soup.select('isolClearCnt')
            # 10만명당 발생률
            per100k = soup.select('qurRate')

            # 초반에 아직 해외유입이 없다거나, 사망자가 없다거나 해서 누락되는 데이터들이 있으므로 삼항연산자 혹은 오류처리를 해줘야 함
            for i in date:
                date_list.append(parse(i.text).date())
            for i in city:
                city_list.append(i.text)
            for i in death_toll:
                death_toll_list.append(int(i.text))
            for i in increase:
                increase_list.append(int(i.text))
            if len(case) != 0:
                for i in case:
                    case_list.append(int(i.text))
            else:
                # 일자 length를 기준으로
                for i in range(len(date)):
                    case_list.append(0)

            if len(local) != 0:
                for i in local:
                    local_list.append(int(i.text))
            else:
                for i in range(len(date)):
                    local_list.append(0)

            if len(inflow) != 0:
                for i in inflow:
                    inflow_list.append(int(i.text))
            else:
                for i in range(len(date)):
                    inflow_list.append(0)

            if len(isolation) != 0:
                for i in isolation:
                    isolation_list.append(int(i.text))
            else:
                for i in range(len(date)):
                    isolation_list.append(0)
            if len(isolation) != 0:
                for i in release:
                    release_list.append(int(i.text))
            else:
                for i in range(len(date)):
                    release_list.append(0)

            for i in per100k:
                try:
                    per100k_list.append(
                        float(i.text) if i.text.find('.') >= 0 else 0.00)
                # 51.13. 같은 이상한 값이 껴있음
                except:
                    per100k_list.append(
                        float(i.text[:-1]) if i.text.find('.') >= 0 else 0.00)
        df = pd.DataFrame({
            '일자': date_list,
            '지역': city_list, '사망자': death_toll_list,
            '확진자': case_list, '전일대비': increase_list, '격리해제': release_list,
            '격리중': isolation_list, '지역발생': local_list, '해외유입': inflow_list,
            '10만명당': per100k_list
        })
        sql = """ insert into all_info values(?,?,?,?,?,?,?,?,?,?)
        """
        for i in range(len(df)):
            text_col = list(df.iloc[i, :2])
            for k in range(2, 9):
                text_col.append(int(df.iloc[i, k]))
            text_col.append(float(df.iloc[i, -1]))
            params = text_col
            cur.execute(sql, params)
            conn.commit()


# 해당 날짜만 받아올 수 있도록
# 그러려면 args로 들어오는 date를 받아야 함
# 또 맨 마지막 날짜랑 비교하는게 아닌 현재 데이트가 있는지를 봐야 함
# 애는 갱신되는 시간이 늦음
def renewal_demographic(date):
    sql = """ select * from demographic where date = ? """
    cur.execute(sql, (date,))
    row = cur.fetchone()
    # 요거 받아올때 날짜 형식은 20201220 이어야 함
    date = date.replace('-', '')
    conn.commit()

    # 현재 페이지의 날짜
    if row is None:
        corona_url = "http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19GenAgeCaseInfJson"
        url = f"{corona_url}?serviceKey={govapi_key}&pageNo=1&numOfRows=1&startCreateDt={date}&endCreateDt={date}"
        result = requests.get(url)
        soup = BeautifulSoup(result.text, 'xml')
        date_list, gubun_list, death_list, death_rate_list, case_list, case_rate_list = [
        ], [], [], [], [], []
        # '남성' 카테고리만 빼고 같은 게 두 번씩 들어옴

        # 일자
        date = soup.select('createDt')[:11]
        # 구분(성별, 연령별)
        gubun = soup.select('gubun')[:11]
        # 확진자 수
        case = soup.select('confCase')[:11]
        # 확진률
        case_rate = soup.select('confCaseRate')[:11]
        # 사망자 수
        death = soup.select('death')[:11]
        # 사망률
        death_rate = soup.select('deathRate')[:11]

        for i in date:
            date_list.append(parse(i.text).date())
        for i in gubun:
            gubun_list.append(i.text)
        for i in case:
            case_list.append(int(i.text))
        for i in case_rate:
            case_rate_list.append(float(i.text))
        for i in death:
            death_list.append(int(i.text))
        for i in death_rate:
            death_rate_list.append(float(i.text))

        df = pd.DataFrame({
            '일자': date_list,
            '구분': gubun_list, '확진자': case_list,
            '확진률': case_rate_list, '사망자': death_list, '사망률': death_rate_list
        })
        sql = 'insert into demographic values(?,?,?,?,?,?);'
        for i in range(len(df)):
            text_col = list(df.iloc[i, 0:2])
            for k in range(2, 4):
                text_col.append(int(df.iloc[i, k]))
            for h in range(4, 6):
                text_col.append(float(df.iloc[i, h]))
            params = text_col
            cur.execute(sql, params)
            conn.commit()
    else:
        print('이미 최신정보로 업데이트되었습니다.')


def renewal_world(date):
    sql = """ select * from world where date = ? """
    cur.execute(sql, (date,))
    row = cur.fetchone()
    # 요거 받아올때 날짜 형식은 20201220 이어야 함
    date = date.replace('-', '')
    conn.commit()
    # 현재 페이지의 날짜
    if row is None:
        corona_url = "http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19NatInfStateJson"
        url = f"{corona_url}?serviceKey={govapi_key}&pageNo=1&numOfRows=1&startCreateDt={date}&endCreateDt={date}"
        result = requests.get(url)
        soup = BeautifulSoup(result.text, 'xml')
        date_list, continent_list, country_list, case_list, death_list, death_rate_list = [
        ], [], [], [], [], []

        # 일자
        date = soup.select('createDt')
        # 지역명
        continent = soup.select('areaNm')
        # 국가명
        country = soup.select('nationNm')
        # 확진자 수
        case = soup.select('natDefCnt')
        # 사망자 수
        death = soup.select('natDeathCnt')
        # 치사률(확진자 대비 사망률)
        death_rate = soup.select('natDeathRate')

        for i in date:
            date_list.append(parse(i.text).date())
        for i in continent:
            continent_list.append(i.text)
        for i in country:
            country_list.append(i.text)
        for i in case:
            case_list.append(int(i.text))
        for i in death:
            death_list.append(int(i.text))
        for i in death_rate:
            death_rate_list.append(float(i.text))
        df = pd.DataFrame({
            '일자': date_list,
            '대륙': continent_list, '국가': country_list,
            '확진자': case_list, '사망자': death_list, '사망률': death_rate_list
        })
        sql = 'insert into world values(?,?,?,?,?,?);'
        for i in range(len(df)):
            text_col = list(df.iloc[i, 0:3])
            for k in range(3, 5):
                text_col.append(int(df.iloc[i, k]))
            text_col.append(float(df.iloc[i, -1]))
            params = text_col
            cur.execute(sql, params)
            conn.commit()
    else:
        print('이미 최신정보로 업데이트되었습니다.')


def get_all_info_data(date):
    sql = """ select * from all_info where date = ? """
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    # print('db모듈쪽 rows', rows)
    return rows
    conn.commit()


def get_daily_sido_data(date):
    sql = """ select date, city, casenum from all_info where date = ? """
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    # print('db모듈쪽 rows', rows)
    return rows
    conn.commit()


def get_demographic_data(date):
    sql = """ select * from demographic where date = ? """
    cur.execute(sql, (date,))
    rows = cur.fetchall()[:11]
    return rows
    conn.commit()


def get_world_data(date):
    sql = """ select * from world where date = ? """
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    return rows
    conn.commit()
