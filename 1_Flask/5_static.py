from flask import *
import os

app = Flask(__name__)

@app.route('/')
def index():
    # 이미지 cache에 상관없이 바로바로 반영이 되게하는 코드
    img_file = os.path.join(app.root_path, 'static/img/tickets.jpg')
    mtime = int(os.st(img_file).st_mtime) # 이미지가 마지막으로 modified된 시간
    return render_template('5_index.html', mtime = mtime)
    
    # BootStrap을 사용할 때도 필요한 코드


if __name__ == '__main__':
    # debug=True Option: nodemon과 같은 역할
    app.run(debug=True)
