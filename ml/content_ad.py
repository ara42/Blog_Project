## 비밀번호 설정, 모델 경로 설정 필수

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import classification_report
import pymysql
import joblib
import re
import json
import requests


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
sel_query = f"SELECT id, content FROM post_data_set WHERE (ad_status = 'NEED-TO-PROCESS' OR ad_status = 'NON-AD') AND content <> '' AND res_id >= {res_id1} AND res_id <= {res_id2}"
#query = f"SELECT id, ocr_text FROM post_data WHERE map=1 AND ad_status = 'AD' AND ocr_text <> '' AND res_id >= {res_id1} AND res_id <= {res_id2}"
cursor.execute(sel_query)
results = cursor.fetchall()

#print(results)

ad_tfidf = joblib.load('C:/work/python/blog_API/model/tfidf_vectorizer6.pkl') ## 경로 설정
ad_svm = joblib.load("C:/work/python/blog_API/model/svm_model6.pkl") ## 경로 설정

for i in range(len(results)):
    post_data_id = results[i]['id']
    content = results[i]['content']
    
    ## 본문 맨 뒤에서 15단어만 추출해서 한 문장으로
    main_t= re.sub(r'\s+', ' ', content)
    main_te=main_t.split(' ')
    ntext =' '.join(main_te[-15:])

    ## 추출한 문장 맞춤법 검사
    try:
        response = requests.post('http://164.125.7.61/speller/results', data={'text1': ntext})
        data = response.text.split('data = [', 1)[-1].rsplit('];', 1)[0]
        data = json.loads(data)
        etext = ntext

        for i in data['errInfo']:
            etext = etext.replace(i['orgStr'], i['candWord'])
    except:
        pass
    
    ## 전처리 완료한 문장 model에 넣어 광고 유무 판단
    x_new = ad_tfidf.transform([etext])
    predicted_label = ad_svm.predict(x_new)
    if predicted_label[0]:
        ad = 'AD'
    else:
        ad = 'NON-AD'
    
    #up_query = f"update post_data set ad_status = %s where id = %s"
    #data = (ad, post_data_id)
    #cursor.execute(up_query, data)
    print(post_data_id, ad, etext)

#blogdb.commit()
