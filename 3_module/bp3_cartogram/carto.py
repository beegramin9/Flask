from flask import *
from datetime import *

from werkzeug.utils import secure_filename

from my_util.Cartogram import *
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

carto_bp = Blueprint('carto_bp', __name__)


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


@carto_bp.route('/coffee', methods=['get', 'post'])
def coffee():
    menu = {'ho': 0, 'da': 1, 'ml': 0, 'se': 0,
            'co': 0, 'cg': 0, 'cr': 1, 'st': 0, 'wc': 0}
    if request.method == 'GET':
        options = ['커피지수', '이디야 매장수', '스타벅스 매장수', '커피빈 매장수', '빽다방 매장수']
        return render_template('cartogram/coffee.html', menu=menu, weather=get_weather_main(), options=options)
    else:
        # 셀렉트박스에서 선택한 항목 받아오기
        item = request.form['item']
        # csv파일 받아오기
        f = request.files['csv']
        # secure_filename: 불특정 다수에게 입력을 받을 때 불완전요소를 막기 위한 장치
        # secure_filename(f.filename). 한글이름으로 된 파일을 어떻게 올릴 수 있을까?
        filename = os.path.join(current_app.root_path,
                                'static\\upload\\') + f.filename

        f.save(filename)
        # filename = filename.replace('\\', '/')

        current_app.logger.info(f'{filename} is saved.')

        coffee = pd.read_csv(filename, encoding='utf8')

        img_file = os.path.join(current_app.root_path, 'static/img/coffee.png')

        drawKorea(item, coffee, 'Reds', img_file)
        mtime = int(os.stat(img_file).st_mtime)

        return render_template('cartogram/coffee_res.html', menu=menu, weather=get_weather_main(), mtime=mtime)
        # cartogram = pd.read_excel('./static/data/cartogram/전국 카토그램.xlsx', engine = 'openpyxl')
