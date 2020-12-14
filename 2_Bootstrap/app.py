from flask import Flask, render_template, request
from my_util.weather import get_weather

app = Flask(__name__)


@app.route('/')
def index():
    menu = {'ho': 1, 'da': 0, 'ml': 0, 'se': 0,
            'co': 0, 'cg': 0, 'cr': 0, 'st': 0, 'wc': 0}
    return render_template('main.html', menu=menu, weather=get_weather())


@app.route('/park')
def park():
    menu = {'ho': 0, 'da': 1, 'ml': 0, 'se': 1,
            'co': 0, 'cg': 0, 'cr': 0, 'st': 0, 'wc': 0}
    return render_template('main.html', menu=menu, weather=get_weather())


@app.route('/stock', methods=['GET', 'POST'])
def stock():
    menu = {'ho': 0, 'da': 1, 'ml': 0, 'se': 1,
            'co': 0, 'cg': 0, 'cr': 0, 'st': 0, 'wc': 0}
    if request.method == 'GET':
        return render_template('stock.html', menu=menu, weather=get_weather())
    else:
        return render_template('stock_res.html', menu=menu, weather=get_weather())


if __name__ == '__main__':
    app.run(debug=True)
