from flask import Blueprint, render_template, request, session
from flask import current_app
import os
import pandas as pd
from my_util.weather import get_weather
import json
import requests
from urllib.parse import quote


lang_bp = Blueprint('lang_bp', __name__)


def get_weather_main():
    ''' weather = None
    try:
        weather = session['weather']
    except:
        current_app.logger.info("get new weather info")
        weather = get_weather()
        session['weather'] = weather
        session.permanent = True
        current_app.permanent_session_lifetime = timedelta(minutes=60) '''
    weather = get_weather()
    return weather


@lang_bp.route('/translate', methods=['GET', 'POST'])
def translation():
    menu = {'ho': 0, 'da': 0, 'ml': 1,
            'se': 0, 'co': 0, 'cg': 0, 'cr': 0, 'wc': 0,
            'cf': 0, 'ac': 0, 're': 0, 'cu': 0, 'ln': 1}
    if request.method == 'GET':
        return render_template('language/translation.html', menu=menu, weather=get_weather_main())
    else:
        text = request.form['text']
        lang = request.form['lang']

        # 네이버 파파고
        with open('keys/papago_key.json') as nkey:
            json_str = nkey.read(100)
        json_obj = json.loads(json_str)
        client_id = list(json_obj.keys())[0]
        client_secret = json_obj[client_id]

        n_mapping = {'en': 'en', 'jp': 'ja',
                     'cn': 'zh-CN', 'fr': 'fr', 'es': 'es'}
        url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
        val = {
            "source": 'ko',
            "target": n_mapping[lang],
            "text": text
        }
        headers = {
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret
        }
        response = requests.post(url,  data=val, headers=headers)
        response_json = json.loads(response.text)
        naver = response_json['message']['result']['translatedText']

        # 카카오
        with open('keys/kakao_api_key.txt') as kfile:
            kai_key = kfile.read(100)

        url = "https://dapi.kakao.com/v2/translation/translate?query=" + \
            quote(text)+"&src_lang=kr&target_lang=en"
        result = requests.get(
            url, headers={'Authorization': 'KakaoAK '+kai_key}).json()
        kakao = ""
        for nested_text in result['translated_text'][0]:
            kakao += nested_text

        return render_template('language/translation_res.html', menu=menu, weather=get_weather_main(),
                               org=text, naver=naver, kakao=kakao, lang=lang)


@lang_bp.route('/tts', methods=['GET', 'POST'])
def tts():
    menu = {'ho': 0, 'da': 0, 'ml': 1,
            'se': 0, 'co': 0, 'cg': 0, 'cr': 0, 'wc': 0,
            'cf': 0, 'ac': 0, 're': 0, 'cu': 0, 'ln': 1}
    if request.method == 'GET':
        return render_template('language/tts.html', menu=menu, weather=get_weather_main())
    else:
        text = request.form['text']
        speaker = request.form['speaker']
        pitch = request.form['pitch']
        speed = request.form['speed']
        volume = request.form['volume']
        emotion = request.form['emotion']

        with open('keys/clova_key.json') as nkey:
            json_str = nkey.read(100)
        json_obj = json.loads(json_str)
        client_id = list(json_obj.keys())[0]
        client_secret = json_obj[client_id]

        url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

        headers = {
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        val = {
            "speaker": speaker, "speed": speed, "text": text,
            "pitch": pitch, "volume": volume, "emotion": emotion
        }
        response = requests.post(url,  data=val, headers=headers)
        audio_file = os.path.join(current_app.root_path, 'static/img/cpv.mp3')

        with open(audio_file, 'wb') as f:
            f.write(response.content)
        mtime = int(os.stat(audio_file).st_mtime)
        return render_template('language/tts_res.html', menu=menu, weather=get_weather_main(),
                               res=val, mtime=mtime)


@lang_bp.route('/classification', methods=['GET', 'POST'])
def classification():
    menu = {'ho': 0, 'da': 0, 'ml': 1,
            'se': 0, 'co': 0, 'cg': 0, 'cr': 0, 'wc': 0,
            'cf': 0, 'ac': 0, 're': 0, 'cu': 0, 'ln': 1}
    if request.method == 'GET':
        return render_template('language/classification.html', menu=menu, weather=get_weather_main())
    else:
        return render_template('language/classification_res.html', menu=menu,
                               weather=get_weather_main())
