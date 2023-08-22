from flask import Flask, request, render_template
import pymysql
import urllib.request
from sqlalchemy import create_engine, MetaData, Table, select, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base

app = Flask(__name__)

## 한글 출력
app.config['JSON_AS_ASCII'] = False

## DB 연동 (SQLAlchemy)
user = "admin"
password = "" ## 비밀번호 입력
host = "blogdb.cm2yxwfja9ii.ap-northeast-2.rds.amazonaws.com"
port = 3306
db = "Naver_Blogs"
db_url = f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'

## 엔진 생성
engine = create_engine(db_url, echo=False) ## SQL문 출력하지 않도록 설정

## 기존 테이블을 매핑할 기본 클래스 생성
Base = automap_base()

## 엔진과 테이블 매핑
Base.prepare(engine, reflect=True)

## 테이블 클래스 가져오기
tb_res = Base.classes.restaurants
tb_flask = Base.classes.flask_exDB

## 세션 생성
Session = sessionmaker(engine)
session = Session()

## url로 사진 저장하는 함수
def photo(img_url, img_name):
    img_folder = "C:/work/python/blog_API/static/"
    urllib.request.urlretrieve(img_url, img_folder+img_name)

## 첫 번째 페이지
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

## 두 번째 페이지
@app.route('/place', methods=['GET', 'POST'])
def place():
    location = request.form.get('location', '') ## HTML에서 location값 받아옴
    sel_rec_name = select(tb_flask.rec_name).where(tb_flask.district == f'{location}') 
    restaurants = session.execute(sel_rec_name).all() ## 받아온 location과 같은 식당이름 저장
    return render_template('page2.html', name=location, restaurants=restaurants)

## 세 번째 페이지
@app.route('/restaurant', methods=['GET', 'POST'])
def restaurant():
    res = request.form.get('restaurant', '')
    
    #sel_url = select(tb_flask.graph_url1).where(tb_flask.rec_name == f'{res}') 
    
    post_cnt = 10
    l_img = []
    sel_url = select(tb_flask.graph_url1).limit(post_cnt)
    url = session.execute(sel_url).all()
    for i in range(post_cnt):
        img = f'img{i}.jpg'
        l_img.append(img)
        photo(url[i][0], img)
    print(l_img)
    return render_template('page3.html', restaurant=res, img_list=l_img)

if __name__ == '__main__':
    app.run(debug=True)
