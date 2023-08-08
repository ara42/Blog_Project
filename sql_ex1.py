import mysql.connector

mydb = mysql.connector.connect(
  host="blogdb.cm2yxwfja9ii.ap-northeast-2.rds.amazonaws.com",
  user="admin",
  password="",
  database="blogdb",
  port=3306
)

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM blog")

myresult = mycursor.fetchall()

for x in myresult:
  print(x)