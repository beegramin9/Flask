from flask import *
from datetime import *
from werkzeug.utils import secure_filename
from my_util.Wordcloud import engCloud, korCloud
from my_util.weather import get_weather

import os

import pandas as pd
import numpy as np

word_bp = Blueprint('word_bp', __name__)


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


@word_bp.route('/<option>', methods=['get', 'post'])
def present(option):
    menu = {'ho': 0, 'da': 1, 'ml': 0, 'se': 0,
            'co': 0, 'cg': 0, 'cr': 0, 'st': 0, 'wc': 1}
    if request.method == 'GET':
        options = {
            'present': '여자친구 선물',
            'sports': '스포츠 뉴스 제목'
        }
        return render_template('/wordcloud/wordcloud.html', menu=menu, weather=get_weather(),
                               options=options, option=option)
    else:
        options = {
            'present': '여자친구 선물',
            'sports': '스포츠 뉴스 제목'
        }
        language = request.form['lang']
        # 텍스트 파일
        text_file = request.files['text']
        text_filename = os.path.join(current_app.root_path,
                                     'static\\upload\\') + text_file.filename
        text_file.save(text_filename)
        text = open(text_filename, encoding='utf8').read()

        # Stopwords
        stopwords = request.form['stop_words']

        # 워드크라우드 이미지 다운받는 경로
        download_path = os.path.join(current_app.root_path,
                                     'static/img/wordcloud.png')

        # 업로드된 마스크파일 경로 / 세이브
        mask_image = request.files['mask']
        mask_filename = os.path.join(current_app.root_path,
                                     'static\\upload\\') + mask_image.filename
        mask_image.save(mask_filename)

        # 위에는 파일을 받아오는 것이고 파일을 꺼내서 다시 읽어야 함
        if language == 'kr':
            korCloud(text, stopwords, download_path, mask_filename)
        else:
            engCloud(text, stopwords, download_path, mask_filename)

        # 다운로드한 이미지를 다시 받아와야 함 ==> 이게 안되서 여친선물만 나오는거임
        img_file = os.path.join(current_app.root_path,
                                'static/img/wordcloud.png')
        mtime = int(os.stat(img_file).st_mtime)

        # print('옵션:', option)
        # 계속 present: form의 action이 present로 간다. {{option}}으로 바꿈
        return render_template('/wordcloud/wordcloud_res.html', menu=menu, weather=get_weather(),
                               mtime=mtime, options=options, option=option)
