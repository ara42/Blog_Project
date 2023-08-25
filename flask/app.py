from flask import Flask, request, render_template
import pymysql
import urllib.request
from sqlalchemy import create_engine, MetaData, Table, select, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
import pygal
from pygal.style import Style
from datetime import datetime, timedelta

app = Flask(__name__)

## 한글 출력
app.config['JSON_AS_ASCII'] = False

## DB 연동 (SQLAlchemy)
user = "admin"
password = "blogdb!2" ## 비밀번호 입력
host = "blogdb.cm2yxwfja9ii.ap-northeast-2.rds.amazonaws.com"
port = 3306
db = "blogdb"
db_url = f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'

## 엔진 생성
engine = create_engine(db_url, echo=False) ## SQL문 출력하지 않도록 설정

## 기존 테이블을 매핑할 기본 클래스 생성
Base = automap_base()

## 엔진과 테이블 매핑
Base.prepare(engine, reflect=True)

## 테이블 클래스 가져오기
tb_res = Base.classes.restaurants
tb_post = Base.classes.post_data
#tb_post = Base.classes.post_data
#tb_post = Base.classes.post

## 세션 생성
Session = sessionmaker(engine)
session = Session()

## 차트의 style 설정
custom_style = Style(
    background='white',
    plot_background='white',
    font_family = 'sans-serif',
    title_font_size = 45,
    label_font_size = 30,
    legend_font_size = 30,
    value_font_size = 30,
    value_label_font_size = 30,
    tooltip_font_size = 30,
    no_data_font_size = 30,
    major_label_font_size = 30
)

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
    #sel_rec_name = select(tb_post.rec_name).where(tb_post.district == f'{location}')
    #sel_rec_name = select(tb_res.id, tb_post.rec_name).where(tb_res.district == f'{location}').order_by(tb_res.post_cnt.desc()).limit(5) 
    #restaurants = session.execute(sel_rec_name).all() ## 받아온 location과 같은 식당이름 저장
    restaurants = [('고도식 잠실점',), ('러반로제레스토랑 석촌호수점',), ('오레노라멘 송파점',), ('이오로 비스트로 송파점',), ('야키토리로만 송파점',)]
    
    ## Pie
    pie_chart = pygal.Pie(inner_radius=.4, style=custom_style)
    pie_chart.title = '광고 비율'
    pie_chart.add('IE', 19.5)
    pie_chart.add('Firefox', 36.6)
    pie_chart.add('Chrome', 36.3)
    pie_chart.add('Safari', 4.5)
    pie_chart.add('Opera', 2.3)
    pie_chart = pie_chart.render_data_uri()

    ## Treemap
    treemap = pygal.Treemap(style=custom_style)
    treemap.title = '단어 군집화'
    treemap.add('A', [2, 1, 12, 4, 2, 1, 1, 3, 12, 3, 4, None, 9])
    treemap.add('B', [4, 2, 5, 10, 3, 4, 2, 7, 4, -10, None, 8, 3, 1])
    treemap.add('C', [3, 8, 3, 3, 5, 3, 3, 5, 4, 12])
    treemap.add('D', [23, 18])
    treemap.add('E', [1, 2, 1, 2, 3, 3, 1, 2, 3, 4, 3, 1, 2, 1, 1, 1, 1, 1])
    treemap.add('F', [31])
    treemap.add('G', [5, 9.3, 8.1, 12, 4, 3, 2])
    treemap.add('H', [12, 3, 3])
    treemap = treemap.render_data_uri()

    return render_template('page2.html', name=location, restaurants=restaurants, pie_chart=pie_chart, treemap=treemap)

## 세 번째 페이지
@app.route('/restaurant', methods=['GET', 'POST'])
def restaurant():
    res = request.form.get('restaurant', '')
    
    #sel_url = select(tb_flask.graph_url1).where(tb_flask.rec_name == f'{res}') 
    
    post_cnt = 10
    '''
    l_img = []
    sel_url = select(tb_flask.graph_url1).limit(post_cnt)
    url = session.execute(sel_url).all()
    for i in range(post_cnt):
        img = f'img{i}.jpg'
        l_img.append(img)
        photo(url[i][0], img)
    '''

    top5 = {'고도식 잠실점':33, '러반로제레스토랑 석촌호수점':124, '오레노라멘 송파점':101, '이오로 비스트로 송파점':5, '야키토리로만 송파점':19}
    top5_id = list(top5.keys())
    sel_top5_post = select(tb_post.title, tb_post.url, tb_post.content, tb_post.images).where((tb_post.res_id == f'{top5[res]}') & (tb_post.map == 1)).limit(post_cnt)
    post = session.execute(sel_top5_post).all()

    l_post = [[],[],[],[]]
    for i in range(post_cnt):
        l_post[0].append(post[i][0])
        l_post[1].append(post[i][1])
        l_post[2].append(post[i][2][:300])
        url = post[i][3].split('\n')[0]
        img = f'img{i}.jpg'
        l_post[3].append(img)
        photo(url, img)


    ## Bar
    bar_chart = pygal.HorizontalBar(style=custom_style)
    bar_chart.title = '메뉴 언급 수'
    bar_chart.add('IE', 19.5)
    bar_chart.add('Firefox', 36.6)
    bar_chart.add('Chrome', 36.3)
    bar_chart.add('Safari', 4.5)
    bar_chart.add('Opera', 2.3)
    bar_chart = bar_chart.render_data_uri()

    ## Line
    date_chart = pygal.Line(x_label_rotation=20, style=custom_style)
    date_chart.title = '기간별 포스팅 수'
    date_chart.x_labels = map(lambda d: d.strftime('%Y-%m-%d'), [
    datetime(2013, 1, 2),
    datetime(2013, 1, 12),
    datetime(2013, 2, 2),
    datetime(2013, 2, 22)])
    date_chart.add("Visits", [300, 412, 823, 672])
    date_chart = date_chart.render_data_uri()

    return render_template('page3.html', restaurant=res, l_post=l_post, bar_chart=bar_chart, date_chart=date_chart)

if __name__ == '__main__':
    app.run(debug=True)
