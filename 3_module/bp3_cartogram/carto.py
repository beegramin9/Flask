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
            'co': 0, 'cg': 1, 'cr': 0, 'st': 0, 'wc': 0}
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

        colormaps = {
            '커피지수': 'Reds',
            '스타벅스 매장수': 'Greens',
            '커피빈 매장수': 'Oranges',
            '이디야 매장수': 'Blues',
            '빽다방 매장수': 'PuRd'
        }

        coffee = pd.read_csv(filename, encoding='utf8')

        img_file = os.path.join(current_app.root_path, 'static/img/coffee.png')

        drawKorea(item, coffee, colormaps[item], img_file)
        mtime = int(os.stat(img_file).st_mtime)

        # top10
        top10 = coffee[['ID', item]].sort_values(
            by=item, ascending=False).head(10)
        top10[item] = top10.apply(lambda r: round(r[item], 2), axis=1)

        return render_template('cartogram/coffee_res.html', menu=menu, weather=get_weather_main(), mtime=mtime,
                               item=item, top10=top10)


@carto_bp.route('/population', methods=['get', 'post'])
def population():
    menu = {'ho': 0, 'da': 1, 'ml': 0, 'se': 0,
            'co': 0, 'cg': 1, 'cr': 0, 'st': 0, 'wc': 0}
    if request.method == 'GET':
        options = ['인구수계', '소멸위기지역', '여성비', '2030여성비']
        return render_template('cartogram/population.html', menu=menu, weather=get_weather_main(), options=options)
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

        colormaps = {
            '인구수계': 'Blues',
            '소멸위기지역': 'Reds',
            '여성비': 'RdBu',
            '2030여성비': 'RdBu'
        }

        population = pd.read_csv(filename, encoding='utf8')

        img_file = os.path.join(current_app.root_path, 'static/img/coffee.png')

        drawKoreaMinus(item, population, colormaps[item], img_file)
        mtime = int(os.stat(img_file).st_mtime)

        # top10
        # 여성비가 작은 지역순으로 나옴
        if item.find('여성비') >= 0:
            top10 = population[['ID', item]].sort_values(
                by=item, ascending=True).head(10)
        else:
            top10 = population[['ID', item]].sort_values(
                by=item, ascending=False).head(10)

        top10[item] = top10.apply(lambda r: round(r[item], 2), axis=1)
        top10.reset_index(inplace=True)
        del top10['index']

        return render_template('cartogram/population_res.html', menu=menu, weather=get_weather_main(), mtime=mtime,
                               item=item, top10=top10)
