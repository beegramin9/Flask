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


def renewal_daily_sido():
    today = datetime.today().date()

    sql = """ select * from daily_sido ORDER BY ROWID DESC LIMIT 1 """
    cur.execute(sql)
    row = cur.fetchone()
    # DB 맨 마지막 행 말짜
    db_last_day = row[0]
    print(db_last_day)
    conn.commit()

    # DB 마지막 날짜 datetime형식으로
    last_day = parse(db_last_day).date()

    if today == last_day:
        print('이미 최신정보로 업데이트되었습니다.')
    else:
        elapsed_count = (today - last_day).days

        elapsed_series = pd.date_range(
            last_day + timedelta(1), periods=elapsed_count)

        corona_url = "http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson"
        total_date_list, total_city_list, total_posi_list = [], [], []
        for date in elapsed_series:
            date = date.strftime('%Y%m%d')

            url = f"{corona_url}?serviceKey={govapi_key}&pageNo=1&numOfRows=1&startCreateDt={date}&endCreateDt={date}"

            result = requests.get(url)
            soup = BeautifulSoup(result.text, 'xml')
            date_list_tmp = soup.select('createDt')
            for date in date_list_tmp:
                total_date_list.append(parse(date.text).date())

            # 도시 리스트
            city_list_tmp = soup.select('gubun')
            for city in city_list_tmp:
                total_city_list.append(city.text)
            # 일일 확진자 발생 수
            posi_list_tmp = soup.select('incDec')
            for posi in posi_list_tmp:
                total_posi_list.append(int(posi.text))

        korea = pd.DataFrame({
            '일자': total_date_list,
            '지역': total_city_list,
            '확진자': total_posi_list
        })
        korea = pd.pivot_table(data=korea,
                               index='일자',
                               columns='지역',
                               values='확진자',
                               fill_value=0)
        korea.reset_index(inplace=True)
        sql_insert = 'insert into daily_sido values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);'
        for i in range(len(korea)):
            params = [korea.iloc[i, 0]]
            for k in range(1, 19):
                params.append(int(korea.iloc[i, k]))
            cur.execute(sql_insert, params)
            conn.commit()


def get_all_info_data(date):
    sql = """ select * from all_info where date = ? """
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    # print('db모듈쪽 rows', rows)
    return rows
    conn.commit()


def get_daily_sido_data(date):
    sql = """ select * from daily_sido where date = ? """
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    # print('db모듈쪽 rows', rows)
    return rows
    conn.commit()


def get_demographic_data(date):
    sql = """ select * from demographic where date = ? """
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    return rows
    conn.commit()


def get_world_data(date):
    sql = """ select * from world where date = ? """
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    return rows
    conn.commit()
