from flask import *
from datetime import *

from werkzeug.utils import secure_filename

from db.db_module import *
import os

import pandas as pd
import numpy as np
import folium

import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

# 폰트 설정
mpl.rc('font', family='Malgun Gothic')
# 유니코드에서  음수 부호설정
mpl.rc('axes', unicode_minus=False)

covid_bp = Blueprint('covid_bp', __name__)


def get_weather_main():
    weather = None
    try:
        weather = session['weather']
    except:
        current_app.logger.info("get new weather info")
        weather = get_weather()
        session['weather'] = weather
        session.permanent = True
        current_app.permanent_session_lifetime = timedelta(minutes=60)
    return weather


@covid_bp.route('/daily', methods=['get', 'post'])
def daily():
    menu = {'ho': 0, 'da': 1, 'ml': 0, 'se': 0,
            'co': 1, 'cg': 0, 'cr': 0, 'st': 0, 'wc': 0}
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    print('오늘날짜', datetime.now().strftime('%Y-%m-%d'))
    rows = get_regional_data(date)
    # print('블루프린트rows', rows)
    return render_template('covid/daily.html', menu=menu, weather=get_weather_main(),
                           date=date, rows=rows)
