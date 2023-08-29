from flask import Flask, request, render_template
import pymysql
import urllib.request
from sqlalchemy import create_engine, MetaData, Table, select, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
import pygal
from pygal.style import Style
from datetime import datetime, timedelta
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import matplotlib
import io
import base64
import json

matplotlib.use('Agg')

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
tb_post = Base.classes.post
tb_words = Base.classes.keywords

## 세션 생성
Session = sessionmaker(engine)
session = Session()

## 차트의 style 설정
custom_style = Style(
    background='transparent',
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
    sel_rec = select(tb_res.name, tb_res.id).where(tb_res.district == f'{location}').order_by(tb_res.post_cnt.desc()).limit(5) 
    restaurants = session.execute(sel_rec).all() ## 받아온 location과 같은 식당이름 저장
    print(restaurants)

    sel_cnt = session.query(
    tb_res.district,
    func.sum(tb_res.total_post_cnt),
    func.sum(tb_res.post_cnt)
    ).group_by(tb_res.district).subquery()

    result = session.query(sel_cnt).all()

    result_dict = {district: [int(total_post_cnt), int(post_cnt)] for district, total_post_cnt, post_cnt in result}
    non_ad_rat = round(result_dict[location][1] / result_dict[location][0], 3) * 100
    ad_rat = 100 - non_ad_rat

    ## Pie
    pie_chart = pygal.Pie(inner_radius=.4, style=custom_style)
    pie_chart.title = '광고 비율'
    pie_chart.add('AD', ad_rat)
    pie_chart.add('NON-AD', non_ad_rat)
    pie_chart = pie_chart.render_data_uri()

    ## WordCloud
    sel_dic = select(tb_words.key_words).where(tb_words.district == f'{location}')
    data2 = session.execute(sel_dic).all()
    data = data2[0][0]
    data_str = data.replace("'", "\"")
    data_dict = json.loads(data_str)
    #print(type(data_dict))
    
    wordcloud = WordCloud(
        font_path='malgun',
        width=800,
        height=800,
        background_color='white'
    ).generate_from_frequencies(data_dict)

    img_buffer = io.BytesIO()
    wordcloud.to_image().save(img_buffer, format='PNG')  # WordCloud를 이미지로 저장

    img_buffer.seek(0)
    img_data = base64.b64encode(img_buffer.read()).decode('utf-8')

    return render_template('page2.html', name=location, restaurants=restaurants, pie_chart=pie_chart, img_path=img_data)

## 세 번째 페이지
@app.route('/restaurant', methods=['GET', 'POST'])
def restaurant():
    res = request.form.get('restaurant', '')  
    post_cnt = 10

    clicked_restaurant = request.args.get('restaurant', '')  
    restaurant_info = clicked_restaurant.strip('()').split(', ')
    restaurant_name = restaurant_info[0]
    restaurant_id = int(restaurant_info[1])
    
    print(restaurant_name)
    print(restaurant_id)

    sel_top5_post = select(tb_post.title, tb_post.url, tb_post.description, tb_post.food_img_url).where(tb_post.res_id == restaurant_id).limit(post_cnt)
    post = session.execute(sel_top5_post).all()

    l_post = [[],[],[],[]]
    
    for i in range(post_cnt):
        l_post[0].append(post[i][0])
        l_post[1].append(post[i][1])
        l_post[2].append(post[i][2])
        #url = post[i][3].split('\n')[0]
        #img = f'img{i}.jpg'
        #l_post[3].append(img)
        #photo(url, img)
    
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

    return render_template('page3.html', restaurant=restaurant_name, l_post=l_post, bar_chart=bar_chart, date_chart=date_chart)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)