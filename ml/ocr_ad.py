import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import classification_report
import pymysql
import joblib

blogdb = pymysql.connect(host='blogdb.cm2yxwfja9ii.ap-northeast-2.rds.amazonaws.com',
                      user='admin',
                      password='blogdb!2',
                      database='blogdb',
                      charset='utf8',
                      port=3306)

cursor =blogdb.cursor(pymysql.cursors.DictCursor)

res_id1 = int(input("시작할 res_id : "))
res_id2 = int(input("끝낼 res_id : "))

# 데이터불러오기
query = f"SELECT id, ocr_text FROM post_data WHERE map=1 AND ad_status = 'NEED-TO-PROCESS' AND res_id >= {res_id1} AND res_id <= {res_id2}"
cursor.execute(query)
results = cursor.fetchall()

ad_tfidf = joblib.load('C:/work/python/blog_API/model/ad_tfidf.pkl') ## 경로 설정
ad_svm = joblib.load("C:/work/python/blog_API/model/ad_svm.pkl") ## 경로 설정

for i in range(len(results)):
    ocr_text = results[i]['ocr_text']
    post_data_id = results[i]['id']
    x_new = ad_tfidf.transform([ocr_text])
    predicted_label =ad_svm.predict(x_new)
    print(post_data_id, predicted_label)