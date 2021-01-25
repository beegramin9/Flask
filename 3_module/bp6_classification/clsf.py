from flask import Blueprint, render_template, request, session
from flask import current_app
from fbprophet import Prophet
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
import os
import joblib
import pandas as pd
from my_util.weather import get_weather

clsf_bp = Blueprint('clsf_bp', __name__)


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


@clsf_bp.route('/cancer', methods=['GET', 'POST'])
def cancer():
    menu = {'ho': 0, 'da': 0, 'ml': 10,
            'se': 0, 'co': 0, 'cg': 0, 'cr': 0, 'wc': 0,
            'cf': 1, 'ac': 0, 're': 0, 'cu': 0}
    if request.method == 'GET':
        return render_template('classification/cancer.html', menu=menu, weather=get_weather())
    else:
        index = int(request.form['index'])
        df = pd.read_csv('static/data/classification/cancer_test.csv')
        scaler = MinMaxScaler()
        scaled_test = scaler.fit_transform(df.iloc[:, :-1])
        test_data = scaled_test[index, :].reshape(1, -1)
        label = df.iloc[index, -1]
        lrc = joblib.load('static/model/cancer_lr.pkl')
        svc = joblib.load('static/model/cancer_sv.pkl')
        rfc = joblib.load('static/model/cancer_rf.pkl')
        pred_lr = lrc.predict(test_data)
        pred_sv = svc.predict(test_data)
        pred_rf = rfc.predict(test_data)
        result = {'index': index, 'label': label,
                  'pred_lr': pred_lr[0], 'pred_sv': pred_sv[0], 'pred_rf': pred_rf[0]}
        org = df.iloc[index, :-1].to_dict()
        return render_template('classification/cancer_res.html', menu=menu,
                               res=result, org=org, weather=get_weather())


@clsf_bp.route('/titanic', methods=['GET', 'POST'])
def titanic():
    menu = {'ho': 0, 'da': 0, 'ml': 10,
            'se': 0, 'co': 0, 'cg': 0, 'cr': 0, 'wc': 0,
            'cf': 1, 'ac': 0, 're': 0, 'cu': 0}
    if request.method == 'GET':
        return render_template('classification/titanic.html', menu=menu, weather=get_weather())
    else:
        index = int(request.form['index'])
        df_train = pd.read_csv('static/data/classification/titanic_train.csv')
        scaler = joblib.load('static/model/titanic_scaler.pkl')
        # 스케일러를 잘못건드린듯
        # 여기서 문제생긴듯
        test_data = df_train.iloc[index, 1:].values.reshape(1, -1)
        test_scaled = scaler.transform(test_data)
        label = df_train.iloc[index, 0]
        lrc = joblib.load('static/model/titanic_lr.pkl')
        svc = joblib.load('static/model/titanic_sv.pkl')
        rfc = joblib.load('static/model/titanic_rf.pkl')
        pred_lr = lrc.predict(test_scaled)
        pred_sv = svc.predict(test_scaled)
        pred_rf = rfc.predict(test_scaled)
        result = {'index': index, 'label': label,
                  'pred_lr': pred_lr[0], 'pred_sv': pred_sv[0], 'pred_rf': pred_rf[0]}
        org = df_train.iloc[index, 1:].to_dict()
        return render_template('classification/titanic_res.html', menu=menu,
                               res=result, org=org, weather=get_weather())


@clsf_bp.route('/pima', methods=['GET', 'POST'])
def pima():
    menu = {'ho': 0, 'da': 0, 'ml': 10,
            'se': 0, 'co': 0, 'cg': 0, 'cr': 0, 'wc': 0,
            'cf': 1, 'ac': 0, 're': 0, 'cu': 0}
    if request.method == 'GET':
        return render_template('classification/pima.html', menu=menu, weather=get_weather())
    else:
        index = int(request.form['index'])
        df_train = pd.read_csv('static/data/classification/pima_train.csv')
        # 여기 scaler는 이미 fit이 된 상태, transform만 하면 된다.
        scaler = joblib.load('static/model/pima_scaler.pkl')
        test_data = df_train.iloc[index, :-1].values.reshape(1, -1)
        test_scaled = scaler.transform(test_data)
        label = df_train.iloc[index, -1]
        lrc = joblib.load('static/model/pima_lr.pkl')
        svc = joblib.load('static/model/pima_sv.pkl')
        rfc = joblib.load('static/model/pima_rf.pkl')
        pred_lr = lrc.predict(test_scaled)
        pred_sv = svc.predict(test_scaled)
        pred_rf = rfc.predict(test_scaled)
        result = {'index': index, 'label': label,
                  'pred_lr': pred_lr[0], 'pred_sv': pred_sv[0], 'pred_rf': pred_rf[0]}

        org = df_train.iloc[index, :-1].to_dict()
        return render_template('classification/pima_res.html', menu=menu,
                               res=result, org=org, weather=get_weather())
