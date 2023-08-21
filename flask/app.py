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
restaurants = Base.classes.restaurants
flask_exDB = Base.classes.flask_exDB

## 세션 생성
Session = sessionmaker(engine)
session = Session()

## 첫 번째 페이지
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

## 두 번째 페이지
@app.route('/place', methods=['GET', 'POST'])
def place():
    location = request.form.get('location', '')
    stmt = select(flask_exDB.rec_name).where(flask_exDB.district == f'{location}')
    restaurants = session.execute(stmt).all()
    return render_template('page2.html', name=location, restaurants=restaurants)

## 세 번째 페이지
@app.route('/restaurant', methods=['GET', 'POST'])
def restaurant():
    res = request.form.get('restaurant', '')
    return render_template('page3.html', restaurant=res)

if __name__ == '__main__':
    app.run(debug=True)
