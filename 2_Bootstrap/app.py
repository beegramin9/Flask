import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings
from flask import Flask, render_template, request, session
from my_util.weather import get_weather
from datetime import datetime, timedelta

import os
import pandas as pd
import pandas_datareader.data as pdr
from fbprophet import Prophet


# 한글폰트 사용
mpl.rc('font', family='Malgun Gothic')
mpl.rc('axes', unicode_minus=False)
warnings.filterwarnings("ignore")


app = Flask(__name__)
kospi_dict = {}
kosdaq_dict = {}

app.secret_key = 'any random string'


def get_weather_main():
    weather = None
    try:
        # Flask에서는 세션은 딕셔너리 형태로 저장되며 키를 통해 값을 불러올 수 있다.
        weather = session['weather']
    except:
        weather = get_weather()
        session['weather'] = weather
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=60)
    return weather


@app.before_first_request
def before_first_request():
    kospi = pd.read_csv('./static/data/KOSPI.csv', sep=',',
                        encoding='utf8', dtype={'업종코드': str})
    for index in kospi.index:
        kospi_dict[kospi['종목코드'][index]] = kospi['종목명'][index]

    kosdaq = pd.read_csv('./static/data/KOSDAQ.csv', sep=',',
                         encoding='utf8', dtype={'업종코드': str})
    for index in kosdaq.index:
        kosdaq_dict[kosdaq['종목코드'][index]] = kosdaq['종목명'][index]


@app.route('/')
def index():
    menu = {'ho': 1, 'da': 0, 'ml': 0, 'se': 0,
            'co': 0, 'cg': 0, 'cr': 0, 'st': 0, 'wc': 0}
    return render_template('main.html', menu=menu, weather=get_weather_main())


@app.route('/park')
def park():
    menu = {'ho': 0, 'da': 1, 'ml': 0, 'se': 1,
            'co': 0, 'cg': 0, 'cr': 0, 'st': 0, 'wc': 0}
    return render_template('main.html', menu=menu, weather=get_weather_main())


@app.route('/stock', methods=['GET', 'POST'])
def stock():
    menu = {'ho': 0, 'da': 1, 'ml': 0, 'se': 1,
            'co': 0, 'cg': 0, 'cr': 0, 'st': 0, 'wc': 0}
    if request.method == 'GET':
        return render_template('stock.html', menu=menu, weather=get_weather_main(), kospi=kospi_dict, kosdaq=kosdaq_dict)
    else:
        market = request.form['market']
        # 입력된 종목 코드 받기
        if market == 'KS':
            code = request.form['kospi_code']
            company = kospi_dict[code]
            code += '.KS'
        else:
            code = request.form['kosdaq_code']
            company = kosdaq_dict[code]
            code += '.KQ'

        # print(f'코드: {code}')

        # 학습, 예측기간
        learn_period = int(request.form['learn'])
        pred_period = int(request.form['pred'])
        today = datetime.today()
        end_learn = today + timedelta(days=-1)
        start_learn = today + timedelta(days=-365 * learn_period)

        stock_data = pdr.DataReader(
            code, data_source='yahoo', start=start_learn, end=end_learn)

        df = pd.DataFrame({'ds': stock_data.index,
                           'y': stock_data.Close})
        df.reset_index(inplace=True)
        del df['Date']

        model = Prophet(yearly_seasonality=True, daily_seasonality=True)
        model.fit(df)
        future = model.make_future_dataframe(periods=pred_period)
        forecast = model.predict(future)

        # 해당 그래프를 static 폴더에 저장해야 함
        fig = model.plot(forecast)
        img_file = os.path.join(app.root_path, 'static/img/stock.png')
        fig.savefig(img_file)
        mtime = int(os.stat(img_file).st_mtime)

        return render_template('stock_res.html', menu=menu, weather=get_weather_main(), mtime=mtime, company=company, code=code)


if __name__ == '__main__':
    app.run(debug=True)
