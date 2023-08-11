from flask import Flask, request
import mysql.connector

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

mydb = mysql.connector.connect(
    host="blogdb.cm2yxwfja9ii.ap-northeast-2.rds.amazonaws.com",
    user="admin",
    password="blogdb!2", ##비밀번호 입력 필수
    database="Naver_Blogs",
    port=3306, 
    charset="utf8")

@app.route('/')
def home():
    return "Hello"

@app.route('/map/<place>/')
def getblog(place):
    text = []

    mycursor = mydb.cursor()

    sql = f"SELECT * FROM blogs WHERE search_word LIKE '{place}%'"

    mycursor.execute(sql)

    results = mycursor.fetchall()

    for x in results:
        temp = {'id' : x[0],
                'post_date' : x[2],
                'title' : x[3],
                'link' : x[4],
                'main_text' : x[5],
                'place' : place}
        text.append(temp)
    return text

'''
@app.route('/map')
def get_place():
    place = request.args.get("place", "")
    return place, 200
'''

if __name__ == '__main__':
    app.run(debug=True)
