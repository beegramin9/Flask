from flask import Blueprint, render_template

# simple_bp = Blueprint('simple_bp', __name__, template_folder='template')
# 요기에 template_folder = 'template' 의 template 폴더는 지금 돌아가는
# simply.py와 같은 경로에 있는 template 파일임

simple_bp = Blueprint('simple_bp', __name__)
# 따로 아규먼트를 주지 않으면 기준이 되는 server.py와 같은 경로에 있는 template 파일

# simple은 루트가 / 이다.


@simple_bp.route('/')
def simple():
    return render_template('/stock/simple.html')
