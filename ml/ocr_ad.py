## 비밀번호 입력, 경로설정

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
sel_query = f"SELECT id, ocr_text FROM post_data_set WHERE ad_status = 'NEED-TO-PROCESS' AND ocr_text <> '' AND res_id >= {res_id1} AND res_id <= {res_id2}"
#query = f"SELECT id, ocr_text FROM post_data WHERE map=1 AND ad_status = 'AD' AND ocr_text <> '' AND res_id >= {res_id1} AND res_id <= {res_id2}"
cursor.execute(sel_query)
results = cursor.fetchall()

#print(results)

ad_tfidf = joblib.load('C:/work/python/blog_API/model/tfidf_vectorizer6.pkl') ## 경로 설정
ad_svm = joblib.load("C:/work/python/blog_API/model/svm_model6.pkl") ## 경로 설정

for i in range(len(results)):
    ocr_text = results[i]['ocr_text']
    post_data_id = results[i]['id']
    x_new = ad_tfidf.transform([ocr_text])
    predicted_label = ad_svm.predict(x_new)
    if predicted_label[0]:
        ad = 'AD'
    else:
        ad = 'NON-AD'
    up_query = f"update post_data_set set ad_status = %s where id = %s"
    data = (ad, post_data_id)
    cursor.execute(up_query, data)
    print(post_data_id, ad)

blogdb.commit()
    
