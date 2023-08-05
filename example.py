from flask import Flask
import mysql.connector

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def getblog():
    text = []
    mydb = mysql.connector.connect(
        host="blogdb.cm2yxwfja9ii.ap-northeast-2.rds.amazonaws.com",
        user="admin",
        password="blogdb!2",
        database="blogdb",
        port=3306, 
        charset="utf8")

    mycursor = mydb.cursor()

    sql = "SELECT * FROM blog"

    mycursor.execute(sql)

    results = mycursor.fetchall()

    for x in results:
        temp = {'id' : x[0],
                'url' : x[1],
                'content' : x[2],
                'score' : x[3],
                'keywords' : x[4],
                'created_date' : x[5]}
        text.append(temp)
    return text

if __name__ == '__main__':
    app.run()