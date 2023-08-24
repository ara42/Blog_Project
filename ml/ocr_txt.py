from google.cloud import vision
import io
import os
import requests
import re
import pymysql

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:/work/python/blog_API/project1-393401-6e3fff67ffb5.json"

def str_filter(text):
    html_spch = ['"','&','<','>', '\'',
             ' ','¡','¢','£',
             '¤','¥','¦','§',
             '¨','©','ª','«','¬',
             '­','®','¯','°','±',
             '²','³','´','µ','¶',
             '·','¸','¹','º','»',
             '¼','½','¾','¿']
    html_tag = ['','\n','','','','','',
            '','','','','','',
            '','','']
    html_spch_tag = html_spch + html_tag
    or_exp = '|'.join(html_spch_tag)
    text = re.sub(or_exp," ",text)
    text1= re.sub(r'[^\w\s]',' ',text)
    text2= re.sub(r"^\s+|\ㄴ+$","",text1) # 양측 공백 제거
    return text2

def image_text(img_path):
    # Initialize the client
    client = vision.ImageAnnotatorClient()

    # Load the image
    image_link = img_path

    image_response = requests.get(image_link)
    image_content = image_response.content
    image = vision.Image(content=image_content)

    # Perform text detection
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        img_text = str(texts[0].description)
    else:
        img_text = None

    return img_text

def extract_alpha_korean(text):
    pattern = re.compile('[a-zA-Z가-힣]+')
    matches = pattern.findall(text)
    combined_result = ' '.join(matches)  # 추출된 문자열들을 공백으로 구분하여 결합
    return combined_result

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
query = f"SELECT id, images FROM post_data WHERE images<>'' AND map=1 AND ad_status = 'NEED-TO-PROCESS' AND res_id >= {res_id1} AND res_id <= {res_id2}"
cursor.execute(query)
results = cursor.fetchall()

for i in range(len(results)):
    image_urls = results[i]['images'].split('\n')
    post_data_id = results[i]['id']
    search_s = 'store'
    st_urls = [url for url in image_urls if search_s in url] ## 스티커 url 리스트
    im_urls = [url for url in image_urls if search_s not in url] ## 이미지 url 리스트
    if st_urls: ## 스티커 url이 존재할 경우
        st_url = st_urls[-1] ## 마지막 스티커 url만 사용
        try:
            st_txt = image_text(st_url)
            st_txt = extract_alpha_korean(st_txt).replace('\n',' ')
            if st_txt == "":
                st_txt = 'NULL'
        except Exception as e:
            if 'expected string or bytes-like object' not in str(e):
                print(f"Error processing sticker URL for id {post_data_id}: {e}")
            st_txt = 'None'
    else:
        st_txt = 'NULL'

    if im_urls: ## 이미지 url이 존재할 경우
        im_url = im_urls[-1] ## 마지막 이미지 url만 사용
        try:
            im_txt = image_text(im_url)
            im_txt = extract_alpha_korean(im_txt).replace('\n',' ')
            if im_txt == "":
                im_txt = 'NULL'
        except Exception as e:
            if 'expected string or bytes-like object' not in str(e):
                print(f"Error processing image URL for id {post_data_id}: {e}")
            im_txt = 'None'
    else:
        im_txt = 'NULL'

    ocr_txt = f'{st_txt}, {im_txt}'
    query = f"update post_data set ocr_text = %s where id = %s"
    data = (ocr_txt, post_data_id)
    cursor.execute(query, data)
    print(post_data_id)
    blogdb.commit()

