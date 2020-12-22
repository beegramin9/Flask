import sqlite3
import pandas as pd

conn = sqlite3.connect('./db/covid.db', check_same_thread=False)
cur = conn.cursor()


def get_regional_data(date):
    sql = """ select * from sido where date = ? """
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    # print('db모듈쪽 rows', rows)
    return rows
    conn.commit()
