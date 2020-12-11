from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # static처럼 기본 경로가 templates에서 시작
    return render_template('2_index.html')

@app.route('/welcome')
def welcome():
    return render_template('2_welcome.html')

if __name__ == '__main__':
    app.run(debug=True)
