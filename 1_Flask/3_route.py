from flask import Flask, render_template, request

app = Flask(__name__)

# 정적 라우팅
@app.route('/')
def index():
    return render_template('2_index.html')

# 동적 라우팅
@app.route('/user/<uid>')
# nodeJs에서는 /bbs/<bid>로 받으면
# req.params.bid로 받음
# 여기서는 함수의 parameter로 들어옴 
def string_fn(uid):
    # console.log처럼 터미널에 띄움
    print(uid)
    return uid

@app.route('/int/<int:number>')
def int_fn(number):
    return str(100*number)

@app.route('/float/<float:number>')
def float_fn(number):
    return str(number * 10)

@app.route('/path/<path:path>')
def path_fn(path):
    return f'path: {path}'

@app.route('/login',methods = ['GET','POST'])
def login():
    # show the login form
    if request.method == 'GET':
        return render_template('3_login.html') 
    
    # do the login process
    else:
        return render_template('2_welcome.html') 
        

if __name__ == '__main__':
    app.run(debug=True)
