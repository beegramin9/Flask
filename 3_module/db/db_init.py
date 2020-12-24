import sqlite3
import pandas as pd
from tqdm import tqdm

conn = sqlite3.connect('./db/covid.db', check_same_thread=False)
cur = conn.cursor()

# 매일마다 파일을 더하게 할 수는 없을까...?


def renewal_daily_sido():
    pass


def make_daily_sido():
    sql = '''create table daily_sido (
        date text not null primary key,
        seoul int default 0, busan int default 0, daegu int default 0,
        incheon int default 0, daejeon int default 0, gwangju int default 0,
        ulsan int default 0, sejong int default 0, gyeonggi int default 0,
        gangwon int default 0, chungbuk int default 0, chungnam int default 0,
        gyeongbuk int default 0, gyeongnam int default 0, jeonbuk int default 0,
        jeonnam int default 0, jeju int default 0, 
        gye int default 0);'''
    cur.execute(sql)
    conn.commit()


def insert_daily_sido():
    sql = 'insert into daily_sido values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);'
    daily = pd.read_csv('../static/data/covid/전국코로나일별.csv',
                        sep=',', encoding='utf8')
    for i in tqdm(range(len(daily))):
        params = [daily.iloc[i, 0]]
        for k in range(1, 19):
            params.append(int(daily.iloc[i, k]))
        cur.execute(sql, params)
        conn.commit()


def make_daily_sido():
    sql = '''create table daily_sido (
        date text not null,
        city text not null,
        death int default 0,
        increase int default 0,
        casenum int default 0,
        local int default 0,
        inflow int default 0,
        isolation int default 0, 
        release int default 0,
        per100k real default 0.00
    );'''
    cur.execute(sql)
    conn.commit()


def insert_daily_sido():
    sql = """ insert into daily_sido values(?,?,?,?,?,?,?,?,?,?)"""
    all = pd.read_csv('../static/data/covid/전국 모든정보.csv',
                      sep=',', encoding='utf8')
    del all['Unnamed: 0']
    for i in tqdm(range(len(all))):
        text_col = list(all.iloc[i, :2])
        for k in range(2, 9):
            text_col.append(int(all.iloc[i, k]))
        text_col.append(float(all.iloc[i, -1]))
        params = text_col
        cur.execute(sql, params)
        conn.commit()


def make_demographic():
    sql = '''create table demographic (
        date text not null,
        demo text not null,
        casenum int default 0, 
        death int default 0, 
        caserate real default 0.00,
        deathrate real default 0.00);'''
    cur.execute(sql)
    conn.commit()


def insert_demographic():
    sql = 'insert into demographic values(?,?,?,?,?,?);'
    demographic = pd.read_csv(
        '../static/data/covid/성별연령별.csv', sep=',', encoding='utf8')
    del demographic['Unnamed: 0']
    for i in tqdm(range(len(demographic))):
        text_col = list(demographic.iloc[i, 0:2])
        for k in range(2, 4):
            text_col.append(int(demographic.iloc[i, k]))
        for h in range(4, 6):
            text_col.append(float(demographic.iloc[i, h]))
        params = text_col
        cur.execute(sql, params)
        conn.commit()


def make_world():
    sql = '''create table world (
        date text not null,
        continent text not null,
        nation text not null,
        casenum int default 0, 
        death int default 0, 
        deathrate real default 0.00);'''
    cur.execute(sql)
    conn.commit()


def insert_world():
    sql = 'insert into world values(?,?,?,?,?,?);'
    world = pd.read_csv('../static/data/covid/해외.csv',
                        sep=',', encoding='utf8')
    del world['Unnamed: 0']
    for i in tqdm(range(len(world))):
        text_col = list(world.iloc[i, 0:3])
        for k in range(3, 5):
            text_col.append(int(world.iloc[i, k]))
        text_col.append(float(world.iloc[i, -1]))
        params = text_col
        cur.execute(sql, params)
        conn.commit()
