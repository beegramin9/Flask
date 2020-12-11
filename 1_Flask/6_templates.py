from flask import *

app = Flask(__name__)

@app.route('/hello')
@app.route('/hello/<name>')
def hello(name=None):
    # 플라스크의 dictionary는 JSON처럼 사용 가능
    dt = {'key1':'value1','key2':'value2'}
    return render_template('5_index.html', name = name, dt = dt)

if __name__ == '__main__':
    app.run(debug=True)