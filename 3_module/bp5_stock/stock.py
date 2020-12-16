from flask import *
from fbprophet import Prophet
from datetime import *
import pandas as pd
import pandas_datareader as pdr
from my_util.weather import get_weather
import os

stock_bp = Blueprint('stock_bp', __name__)


kospi_dict, kosdaq_dict = {}, {}


@stock_bp.before_app_first_request
def before_app_first_request():
    kospi = pd.read_csv('./static/data/stock/KOSPI.csv', dtype={'종목코드': str})
    for i in kospi.index:
        kospi_dict[kospi['종목코드'][i]] = kospi['종목명'][i]
    kosdaq = pd.read_csv('./static/data/stock/KOSDAQ.csv', dtype={'종목코드': str})
    for i in kosdaq.index:
        kosdaq_dict[kosdaq['종목코드'][i]] = kosdaq['종목명'][i]

# stock은 루트를 /로 써주면 get은 되는데 post가 제대로 안 되서
# 기본 루트를 /stock으로 써줬음
# 그래서 /simple 인데 /stock/stock인거임


@stock_bp.route('/stock', methods=['GET', 'POST'])
def stock():
    menu = {'ho': 0, 'da': 1, 'ml': 0, 'se': 0,
            'co': 0, 'cg': 0, 'cr': 0, 'st': 1, 'wc': 0}

    if request.method == 'GET':
        return render_template('stock/stock.html', menu=menu, weather=get_weather(),
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

        return render_template('/stock/stock_res.html', menu=menu, weather=get_weather(),
                               mtime=mtime, company=company, code=code)
