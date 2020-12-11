from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello Flask :)'

if __name__ == '__main__':
    # debug=True Option: nodemon과 같은 역할
    app.run(debug=True)
