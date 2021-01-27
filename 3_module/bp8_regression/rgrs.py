from flask import Blueprint, render_template, request, session, g
from flask import current_app
from fbprophet import Prophet
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader as pdr
from my_util.weather import get_weather

rgrs_bp = Blueprint('rgrs_bp', __name__)


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


@rgrs_bp.route('/iris', methods=['GET', 'POST'])
def iris():
    menu = {'ho': 0, 'da': 0, 'ml': 10,
            'se': 0, 'co': 0, 'cg': 0, 'cr': 0, 'wc': 0,
            'cf': 0, 'ac': 0, 're': 1, 'cu': 0}
    if request.method == 'GET':
        return render_template('regression/iris.html', menu=menu, weather=get_weather())
    else:
        index = int(request.form['index'])
        feature_name = request.form['feature']
        column_dict = {'sl': 'Sepal length', 'sw': 'Sepal width',
                       'pl': 'Petal length', 'pw': 'Petal width',
                       'species': ['Setosa', 'Versicolor', 'Virginica']}
        column_list = list(column_dict.keys())

        df = pd.read_csv('static/data/regression/iris_train.csv')
        df.columns = column_list
        X = df.drop(columns=feature_name, axis=1).values
        y = df[feature_name].values

        lr = LinearRegression()
        lr.fit(X, y)
        weight, bias = lr.coef_, lr.intercept_

        df_test = pd.read_csv('static/data/regression/iris_test.csv')
        df_test.columns = column_list
        X_test = df_test.drop(columns=feature_name, axis=1).values[index]
        pred_value = np.dot(X_test, weight.T) + bias

        x_test = list(df_test.iloc[index, :-1].values)
        x_test.append(column_dict['species'][int(df_test.iloc[index, -1])])
        org = dict(zip(column_list, x_test))
        pred = dict(zip(column_list[:-1], [0, 0, 0, 0]))
        pred[feature_name] = np.round(pred_value, 2)
        return render_template('regression/iris_res.html', menu=menu, weather=get_weather(),
                               index=index, org=org, pred=pred, feature=column_dict[feature_name])


@rgrs_bp.route('/diabetes', methods=['GET', 'POST'])
def diabetes():
    menu = {'ho': 0, 'da': 0, 'ml': 10,
            'se': 0, 'co': 0, 'cg': 0, 'cr': 0, 'wc': 0,
            'cf': 0, 'ac': 0, 're': 1, 'cu': 0}
    if request.method == 'GET':
        return render_template('regression/diabetes.html', menu=menu, weather=get_weather())
    else:
        index = int(request.form['index'])
        feature = request.form['feature']
        df_train = pd.read_csv('static/data/regression/diabetes_train.csv')
        X_train = df_train[feature].values.reshape(-1, 1)
        y_train = df_train.target.values

        lr = LinearRegression()
        lr.fit(X_train, y_train)
        weight, bias = lr.coef_, lr.intercept_

        df_test = pd.read_csv('static/data/regression/diabetes_test.csv')
        X_test = df_test[feature][index]
        y_test = df_test.target[index]
        pred = X_test * weight[0] + bias

        y_min = np.min(X_train) * weight[0] + bias
        y_max = np.max(X_train) * weight[0] + bias

        plt.scatter(X_train, y_train, label='train')
        plt.plot([np.min(X_train), np.max(X_train)], [y_min, y_max], 'r', lw=3)
        plt.scatter([X_test], [y_test], c='r',
                    marker='*', s=100, label='real value')
        plt.grid()
        plt.legend()
        plt.title(f'Diabetes target vs. {feature}')

        # 경로 저장
        img_file = os.path.join(current_app.root_path,
                                'static/img/diabetes.png')
        plt.savefig(img_file)
        mtime = int(os.stat(img_file).st_mtime)

        result_dict = {'index': index,
                       'feature': feature, 'y': y_test, 'pred': pred}
        return render_template('regression/diabetes_res.html', res=result_dict, mtime=mtime,
                               menu=menu, weather=get_weather())


@rgrs_bp.route('/boston', methods=['GET', 'POST'])
def boston():
    menu = {'ho': 0, 'da': 0, 'ml': 10,
            'se': 0, 'co': 0, 'cg': 0, 'cr': 0, 'wc': 0,
            'cf': 0, 'ac': 0, 're': 1, 'cu': 0}
    if request.method == 'GET':
        feature_list = ['CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 'AGE', 'DIS', 'RAD',
                        'TAX', 'PTRATIO', 'B', 'LSTAT']
        return render_template('regression/boston.html', feature_list=feature_list,
                               menu=menu, weather=get_weather())
    else:
        index = int(request.form['index'])
        # Server에서 Client Form에서 list를 받는 방법
        feature_list = request.form.getlist('feature')
        df_train = pd.read_csv('static/data/regression/boston_train.csv')
        # 트레인셋에서 선택한 feature DF와 target Series를 2차원 array로
        X_train = df_train[feature_list].values
        y_train = df_train.target.values

        lr = LinearRegression()
        lr.fit(X_train, y_train)
        weight, bias = lr.coef_, lr.intercept_

        df_test = pd.read_csv('static/data/regression/boston_test.csv')
        # df_test[feature_list].values 까지는 DF를 2차원 Array로 바꾼 것
        # 그 2차원 어레이에서 index 행만 가져오기
        X_test = df_test[feature_list].values[index, :]
        y_test = df_test.target[index]

        # 계수값과 절편값을 더해 나온 예측값
        pred = np.dot(X_test, weight.T) + bias
        pred = np.round(pred, 2)

        result_dict = {'index': index,
                       'feature': feature_list, 'y': y_test, 'pred': pred}
        # 다중회귀에 사용된 테스트셋의 feature와 그 값들
        org = df_test.iloc[index, :-1].to_dict()
        return render_template('regression/boston_res.html', res=result_dict, org=org,
                               menu=menu, weather=get_weather())


kospi_dict, kosdaq_dict, nyse_dict, nasdaq_dict = {}, {}, {}, {}


@rgrs_bp.before_app_first_request
def before_app_first_request():
    kospi = pd.read_csv(
        './static/data/regression/KOSPI.csv', dtype={'종목코드': str})
    for i in kospi.index:
        kospi_dict[kospi['종목코드'][i]] = kospi['종목명'][i]
    kosdaq = pd.read_csv(
        './static/data/regression/KOSDAQ.csv', dtype={'종목코드': str})
    for i in kosdaq.index:
        kosdaq_dict[kosdaq['종목코드'][i]] = kosdaq['종목명'][i]


@rgrs_bp.route('/stock', methods=['GET', 'POST'])
def stock():
    menu = {'ho': 0, 'da': 0, 'ml': 10,
            'se': 0, 'co': 0, 'cg': 0, 'cr': 0, 'wc': 0,
            'cf': 0, 'ac': 0, 're': 1, 'cu': 0}

    if request.method == 'GET':
        return render_template('regression/stock.html', menu=menu, weather=get_weather(),
                               kospi=kospi_dict, kosdaq=kosdaq_dict)
    else:
        market = request.form['market']
        if market == 'KS':
            code = request.form['kospi_code']
            company = kospi_dict[code]
            code += '.KS'
        else:
            code = request.form['kosdaq_code']
            company = kosdaq_dict[code]
            code += '.KQ'
        learn_period = int(request.form['learn'])
        pred_period = int(request.form['pred'])
        # print에는 argument가 여러개 올 수 있지만 logging에서는 하나만 허용됨

        current_app.logger.debug(
            f'{market}, {code}, {learn_period}, {pred_period}')

        today = datetime.now()
        start_learn = today - timedelta(days=learn_period*365)
        end_learn = today - timedelta(days=1)

        stock_data = pdr.DataReader(
            code, data_source='yahoo', start=start_learn, end=end_learn)
        current_app.logger.debug(f"get stock data: {code}")
        df = pd.DataFrame({'ds': stock_data.index, 'y': stock_data.Close})
        df.reset_index(inplace=True)
        try:
            del df['Date']
        except:
            current_app.logger.error('Date Column not exist')

        model = Prophet(daily_seasonality=True)
        model.fit(df)
        future = model.make_future_dataframe(periods=pred_period)
        forecast = model.predict(future)

        fig = model.plot(forecast)
        img_file = os.path.join(current_app.root_path, 'static/img/stock.png')
        fig.savefig(img_file)
        mtime = int(os.stat(img_file).st_mtime)

        return render_template('/regression/stock_res.html', menu=menu, weather=get_weather(),
                               mtime=mtime, company=company, code=code)
