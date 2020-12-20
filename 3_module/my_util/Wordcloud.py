import re
import os

import nltk
from konlpy.tag import Okt, Kkma, Hannanum
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
from konlpy.corpus import kobill

import pandas as pd
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt

# 폰트 설정
mpl.rc('font', family='Malgun Gothic')
# 유니코드에서  음수 부호설정
mpl.rc('axes', unicode_minus=False)


def engCloud(text, stopwords, img_file, mask=None):
    # text: 분석할 텍스트
    # mask: mask 이미지 파일, default = None
    # 색깔도 바꿔줘야함, none일떈 black 아닐땐 white
    # stopwords: 리스트 형태
    # 리스트로 들어가면 안되니까 for문으로 해체해야해야할듯
    # img_file: 이미지파일 save할 경로

    org_stopwords = set(STOPWORDS)
    # split으로 가공해줘야 함
    for word in stopwords.split():
        org_stopwords.add(word)

    if mask == None:
        background_color = 'black'
    else:
        mask = np.array(Image.open(mask))
        background_color = 'white'

    wc = WordCloud(background_color=background_color,
                   max_words=2000,
                   stopwords=org_stopwords,
                   mask=mask
                   )
    wc = wc.generate(text)

    # 여기에 dpi=100을 주면 여백없이 딱 그려짐
    plt.figure(figsize=(9, 9))
    # Image Show
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(img_file)


def korCloud(text, stopwords, img_file, mask=None):
    text = re.sub('[a-zA-Z0-9]', '', text).strip()

    # 명사 뽑아오기
    okt = Okt()
    tokens = okt.nouns(text)
    # 사용된 총 단어 개수
    ko = nltk.Text(tokens)

    # 불용어
    org_stopwords = ['.', '(', ')', ',', "'", '%', '-', 'X', ').', 'x', '의', '자',
                     '에', '안', '번', '호', '을', '이', '다', '만', '로', '가', '를', '누', '해', '제', '및', '것']

    # 리스트로 더해줘야 함
    for word in stopwords.split():
        org_stopwords.append(word)

    ko = [each_word for each_word in ko if each_word not in org_stopwords]
    ko = nltk.Text(ko)

    data = ko.vocab().most_common(150)

    if mask == None:
        background_color = 'black'
    else:
        mask = np.array(Image.open(mask))
        background_color = 'white'

    wc = WordCloud(font_path="c:/Windows/Fonts/malgun.ttf",
                   relative_scaling=0.2,
                   background_color=background_color,
                   max_words=2000,
                   stopwords=org_stopwords,
                   mask=mask).generate_from_frequencies(dict(data))

    plt.figure(figsize=(9, 9))
    # 여기에 dpi=100을 주면 여백없이 딱 그려짐
    plt.imshow(wc, interpolation='bilinear')  # Image Show
    plt.axis('off')
    plt.savefig(img_file)
