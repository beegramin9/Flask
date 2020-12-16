from flask import *
from datetime import *
from my_util.weather import get_weather
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import matplotlib as mpl
import matplotlib.pyplot as plt

import folium
# 폰트 설정
mpl.rc('font', family='Malgun Gothic')
# 유니코드에서  음수 부호설정
mpl.rc('axes', unicode_minus=False)
seoul_bp = Blueprint('seoul_bp', __name__)


@seoul_bp.route('/park', methods=['GET', 'POST'])
def park():
    menu = {'ho': 0, 'da': 1, 'ml': 0, 'se': 1,
            'co': 0, 'cg': 0, 'cr': 0, 'st': 0, 'wc': 0}
    park_new = pd.read_csv('./static/data/seoul/공원 위치, 면적, 인구.csv')
    park_gu = pd.read_csv('./static/data/seoul/구 공원.csv', index_col='지역')

    if request.method == 'GET':
        map = folium.Map(location=[37.5502, 126.982], zoom_start=11)
        for i in park_new.index:
            folium.CircleMarker([park_new.lat[i], park_new.lng[i]],
                                radius=int(park_new['size'][i]),
                                tooltip=f"{park_new['공원명'][i]}({int(park_new.area[i])}㎡)",
                                color='#3186cc', fill_color='#3186cc').add_to(map)
        html_file = os.path.join(current_app.root_path, 'static/img/park.html')
        map.save(html_file)
        mtime = int(os.stat(html_file).st_mtime)
        return render_template('/seoul/park.html', menu=menu, weather=get_weather(),
                               park_list=list(park_new['공원명']), gu_list=list(park_gu.index),
                               mtime=mtime)
    else:
        gubun = request.form['gubun']
        if gubun == 'park':
            park_name = request.form['name']
            df = park_new[park_new['공원명'] == park_name].reset_index()
            park_result = {'name': park_name, 'addr': df['공원주소'][0],
                           'area': int(df.area[0]), 'desc': df['공원개요'][0]}
            map = folium.Map(location=[37.5502, 126.982], zoom_start=11)
            # park_new는 공원 개별로 구분해 정보(위도,경도)를 담은 데이터프레임
            for i in park_new.index:
                folium.CircleMarker([park_new.lat[i], park_new.lng[i]],
                                    radius=int(park_new['size'][i]),
                                    tooltip=f"{park_new['공원명'][i]}({int(park_new.area[i])}㎡)",
                                    color='#3186cc', fill_color='#3186cc').add_to(map)
            # df는 선택한 공원 행 하나만 들어있는 데이터프레임
            # 선택된 공원은 CircleMarker가 두 번 들어가 덮어씌우는 결과가 됨
            folium.CircleMarker([df.lat[0], df.lng[0]], radius=int(df['size'][0]),
                                tooltip=f"{df['공원명'][0]}({int(df.area[0])}㎡)",
                                color='crimson', fill_color='crimson').add_to(map)
            html_file = os.path.join(
                current_app.root_path, 'static/img/park_res.html')
            map.save(html_file)
            mtime = int(os.stat(html_file).st_mtime)
            return render_template('/seoul/park_res.html', menu=menu, weather=get_weather(),
                                   park_result=park_result, mtime=mtime)
        else:
            gu_name = request.form['gu']
            df = park_gu[park_gu.index == gu_name].reset_index()
            # park_gu는 전체 구의 통합된 공원 정보(면적, 개수 등)가 들어있음
            # df는 선택된 구 정보가 들어있는 행 하나의 데이터프레임
            park_result = {'gu': df['지역'][0],
                           'area': int(df['공원면적'][0]), 'm_area': int(park_gu['공원면적'].mean()),
                           'count': df['공원수'][0], 'm_count': round(park_gu['공원수'].mean(), 1),
                           'area_ratio': round(df['공원면적비율'][0], 2), 'm_area_ratio': round(park_gu['공원면적비율'].mean(), 2),
                           'per_person': round(df['인당공원면적'][0], 2), 'm_per_person': round(park_gu['인당공원면적'].mean(), 2)}
            # park_new는 공원 개별로 구분해 정보(위도,경도)를 담은 데이터프레임
            df = park_new[park_new['지역'] == gu_name].reset_index()
            map = folium.Map(
                location=[df.lat.mean(), df.lng.mean()], zoom_start=13)
            for i in df.index:
                folium.CircleMarker([df.lat[i], df.lng[i]],
                                    radius=int(df['size'][i])*3,
                                    tooltip=f"{df['공원명'][i]}({int(df.area[i])}㎡)",
                                    color='#3186cc', fill_color='#3186cc').add_to(map)
            html_file = os.path.join(
                current_app.root_path, 'static/img/park_res.html')
            map.save(html_file)
            mtime = int(os.stat(html_file).st_mtime)
            return render_template('/seoul/park_res2.html', menu=menu, weather=get_weather(),
                                   park_result=park_result, mtime=mtime)


@seoul_bp.route('/park_gu/<option>')
def park_gu(option):
    menu = {'ho': 0, 'da': 1, 'ml': 0, 'se': 1,
            'co': 0, 'cg': 0, 'cr': 0, 'st': 0, 'wc': 0}
    park_new = pd.read_csv('./static/data/seoul/공원 위치, 면적, 인구.csv')
    park_gu = pd.read_csv('./static/data/seoul/구 공원.csv', index_col='지역')

    geo_str = json.load(
        open('./static/data/seoul/서울시 구별 경계선.json', encoding='utf8'))

    # 화면 제목 표기/ 반복문을 피하기 위한 딕셔너리
    option_dict = {'area': '공원면적', 'count': '공원수',
                   'area_ratio': '공원면적 비율', 'per_person': '인당 공원면적'}

    column_index = option_dict[option].replace(' ', '')
    map = folium.Map(location=[37.5502, 126.982],
                     zoom_start=11, tiles='Stamen Toner')

    map.choropleth(geo_data=geo_str,
                   data=park_gu[column_index],
                   columns=[park_gu.index, park_gu[column_index]],
                   fill_color='PuRd',
                   key_on='feature.id')

    for i in park_new.index:
        folium.CircleMarker([park_new.lat[i], park_new.lng[i]],
                            radius=int(park_new['size'][i]),
                            tooltip=f"{park_new['공원명'][i]}({int(park_new.area[i])}㎡)",
                            color='green', fill_color='green').add_to(map)
    html_file = os.path.join(current_app.root_path, 'static/img/park_gu.html')
    map.save(html_file)
    mtime = int(os.stat(html_file).st_mtime)
    return render_template('/seoul/park_gu.html', menu=menu, weather=get_weather(),
                           option=option, option_dict=option_dict, mtime=mtime)


@seoul_bp.route('/crime/<option>', methods=['GET', 'POST'])
def crime(option):
    menu = {'ho': 0, 'da': 1, 'ml': 0, 'se': 1,
            'co': 0, 'cg': 0, 'cr': 0, 'st': 0, 'wc': 0}
    crime = pd.read_csv('./static/data/seoul/구별 상대비교_5대범죄.csv', index_col='구별')
    police_loc = pd.read_csv('./static/data/seoul/서울 경찰서 위도, 경도.csv')

    option_dict = {'total': '범죄 총합',
                   'murder': '살인',
                   'robbery': '강도',
                   'rape': '강간',
                   'larceny': '절도',
                   'assault': '폭력',
                   'total_rate': '검거율 총합',
                   'murder_rate': '살인 검거율',
                   'robbery_rate': '강도 검거율',
                   'rape_rate': '강간 검거율',
                   'larceny_rate': '절도 검거율',
                   'assault_rate': '폭력 검거율'
                   }

    column_index = option_dict[option]

    geo_data = json.load(
        open('./static/data/seoul/서울시 구별 경계선.json', encoding='utf8'))

    map = folium.Map(location=[37.5502, 126.982],
                     zoom_start=11)

    # 검거율은 파란색, 경찰서 표시
    if option.find('rate') >= 0:
        for i in police_loc.index:
            folium.Marker([police_loc.lat[i], police_loc.lng[i]],
                          popup=police_loc['관서명'][i],
                          icon=folium.Icon(color='green', icon='flag')).add_to(map)

            folium.CircleMarker([police_loc.lat[i], police_loc.lng[i]], radius=15,
                                color='green', fill_color='blue').add_to(map)
        color_set = 'YlGnBu'
    # 범죄율은 빨간색
    else:
        color_set = 'PuRd'

    map.choropleth(geo_data=geo_data,
                   data=crime[column_index],
                   columns=[crime.index, crime[column_index]],
                   fill_color=color_set,
                   key_on='id')

    html_file = os.path.join(
        current_app.root_path, 'static/img/crime.html')
    map.save(html_file)
    mtime = int(os.stat(html_file).st_mtime)

    return render_template('/seoul/crime.html', menu=menu, weather=get_weather(), mtime=mtime,
                           option=option, option_dict=option_dict)
