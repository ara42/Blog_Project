## 비밀번호 입력 및 모델 경로 설정 필수

import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import requests
from PIL import Image
from io import BytesIO
import numpy as np
import pymysql
import pickle
import joblib

blogdb = pymysql.connect(host='blogdb.cm2yxwfja9ii.ap-northeast-2.rds.amazonaws.com',
                      user='admin',
                      password='',
                      database='blogdb',
                      charset='utf8',
                      port=3306)

cursor =blogdb.cursor(pymysql.cursors.DictCursor)

id1 = int(input("시작 id : "))
id2 = int(input("끝 id : "))

# 데이터불러오기
query = f"SELECT p.url AS post_url, pds.url AS post_data_set_url, pds.images, p.id as id FROM post p JOIN post_data_set pds ON p.url = pds.url WHERE p.id >= {id1} and p.id <= {id2};"
cursor.execute(query)
results = cursor.fetchall()

#model = pickle.load("C:/work/python/blog_API/model/food_classification_model.pkl")

# 모델 불러오기
with open("C:/work/python/blog_API/model/food_classification_model.pkl", "rb") as f:
    model = pickle.load(f)

for result in results:
    image_urls = result['images'].split('\n')
    selected_url = None  # 선택된 이미지 URL을 저장하는 변수
    
    for image_url in image_urls:
        response = requests.get(image_url)
        new_image = Image.open(BytesIO(response.content))
        new_image = new_image.resize((224, 224))
        new_image_array = img_to_array(new_image)
        new_image_array = new_image_array / 255.0
        new_image_array = tf.expand_dims(new_image_array, axis=0)
        
        try:
            prediction = model(new_image_array)
            
            if prediction[0] < 0.5:
                #print(f"Found 'food' image: {image_url}")
                selected_url = image_url
                break  # 작업 중단
        
        except Exception as e:
            print(f"Error occurred for image {image_url}: {e}")
            selected_url = image_urls[0]  # 에러 발생 시 첫 번째 URL 선택
            break
    
    # food로 분류되는 이미지가 없을 경우, 젤 위의 URL 선택
    if selected_url is None and len(image_urls) > 0:
        selected_url = image_urls[0]
        print(f"No 'food' images found. Selecting the top URL: {selected_url}")
    
    if selected_url:
        # 이미지 예측 결과가 'food'인 경우 해당 이미지 URL을 post 테이블의 food_img_url 컬럼에 업데이트
        update_query = f"UPDATE post SET food_img_url = '{selected_url}' WHERE url = '{result['post_url']}';"
        cursor.execute(update_query)
        print(result['id'])
        blogdb.commit()
