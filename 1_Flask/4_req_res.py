from flask import Flask, request, render_template
from flask import Response, make_response
app = Flask(__name__)


@app.route('/area')
def area():
    pi = request.args.get('pi', '3.14')
    # pi의 default값 "3.14", 즉 str임
    radius = request.args['radius']
    # 계산하고 싶다면 type을 줘야 함
    s = float(pi) * float(radius) ** 2
    return f"pi={pi}, radius={radius}, area={s}"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('3_login.html')

    else:
        # 둘다 됨. form에서 받아오는 값
        # values
        uid = request.form['uid']
        pwd = request.values['pwd']
        return f'uid = {uid}, pwd = {pwd}'
        # return render_template('2_welcome.html')


@app.route('/response')
def response_fn():
    custom_res = Response('Custom Response', 200, {'test': 'ttt'})
    return make_response(custom_res)


if __name__ == '__main__':
    app.run(debug=True)
