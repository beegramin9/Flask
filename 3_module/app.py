from my_util.weather import get_weather
from flask import Flask, render_template, session, request

from bp1_seoul.seoul import seoul_bp
from bp2_covid.covid import covid_bp
from bp3_cartogram.carto import carto_bp
from bp4_wordcloud.wordcloud import word_bp
from bp5_stock.stock import stock_bp
from bp6_classification.clsf import clsf_bp
from bp8_regression.rgrs import rgrs_bp
from bp9_clustering.clus import clus_bp


from datetime import datetime, timedelta
import os
import folium
import json

import logging
from logging.config import dictConfig

import pandas as pd
import pandas_datareader as pdr
import matplotlib as mpl
import matplotlib.pyplot as plt
# 한글폰트 사용
mpl.rc('font', family='Malgun Gothic')
mpl.rc('axes', unicode_minus=False)

app = Flask(__name__)
app.secret_key = 'qwert12345'
# 블루프린트에서 같은 세션을 공유할 수 있도록 하는 코드
app.config['SESSION_COOKIE_PATH'] = '/'

app.register_blueprint(seoul_bp, url_prefix='/seoul')
app.register_blueprint(covid_bp, url_prefix='/covid')
app.register_blueprint(carto_bp, url_prefix='/cartogram')
app.register_blueprint(word_bp, url_prefix='/wordcloud')
app.register_blueprint(stock_bp, url_prefix='/stock')
app.register_blueprint(clsf_bp, url_prefix='/classification')
app.register_blueprint(clus_bp, url_prefix='/cluster')
app.register_blueprint(rgrs_bp, url_prefix='/regression')

""" with open('./logging.json', 'r') as file:
    config = json.load(file)
dictConfig(config)
app.logger """
# 로그 파일의 이름을 어떻게 저장할 수 있을까?


def get_weather_main():
    weather = None
    try:
        weather = session['weather']
    except:
        app.logger.info("get new weather info")
        weather = get_weather()
        session['weather'] = weather
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=60)
    return weather


@app.route('/')
def index():
    menu = {'ho': 1, 'da': 0, 'ml': 0, 'se': 0,
            'co': 0, 'cg': 0, 'cr': 0, 'st': 0, 'wc': 0}
    return render_template('main.html', menu=menu, weather=get_weather_main())


if __name__ == '__main__':
    app.run(debug=True)
