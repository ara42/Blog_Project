from flask import Flask, request, render_template
import pymysql
import urllib.request

app = Flask(__name__)

## 한글 출력
app.config['JSON_AS_ASCII'] = False

## DB 연동
mydb = pymysql.connect(
    host="blogdb.cm2yxwfja9ii.ap-northeast-2.rds.amazonaws.com",
    user="admin",
    password="", ## 비밀번호 입력 필수
    database="Naver_Blogs",
    port=3306, 
    charset="utf8")

## DB 데이터 추출
def db_result(sql):
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    results = mycursor.fetchall()
    return results

## 첫 번째 페이지
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

## 두 번째 페이지
@app.route('/place', methods=['GET', 'POST'])
def place():
    location = request.form.get('location', '')
    sql1 = f"SELECT rec_name FROM flask_exDB WHERE district = '{location}' ORDER BY `rank`"
    restaurants = db_result(sql1)
    return render_template('page2.html', name=location, restaurants=restaurants)

## 세 번째 페이지
@app.route('/restaurant', methods=['GET', 'POST'])
def restaurant():
    store = request.form.get('restaurant', '')
    img_folder = "/content/imgs/"

    for i in data:
        try:
            url = i[1]
            urllib.request.urlretrieve(url, img_folder+str(i[0])+".jpg")
        except:
            print(i)
    return store

if __name__ == '__main__':
    app.run(debug=True)
