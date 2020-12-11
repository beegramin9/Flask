from flask import *

app = Flask(__name__)

@app.route('/child1')
def child1(name=None):
    return render_template('7_child.html')

@app.route('/child2')
def child2(name=None):
    return render_template('7_child2.html')

if __name__ == '__main__':
    app.run(debug=True)