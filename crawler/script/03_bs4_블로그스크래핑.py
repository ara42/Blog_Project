import requests
import pandas as pd
from urllib.parse import quote
from urllib.request import Request,urlopen
import json
import re
from bs4 import BeautifulSoup
import pymysql
import time

def str_filter(text):
    html_spch = ['&quot;','&amp;','&lt;','&gt;','&apos;',
             '&nbsp;','&iexcl;','&cent;','&pound;',
             '&curren;','&yen;','&brvbar;','&sect;',
             '&uml;','&copy;','&ordf;','&laquo;','&not;',
             '&shy;','&reg;','&macr;','&deg;','&plusmn;',
             '&sup2;','&sup3;','&acute;','&micro;','&para;',
             '&middot;','&cedil;','&sup1;','&ordm;','&raquo;',
             '&frac14;','&frac12;','&frac34;','&iquest;']
    html_tag = ['<b>','\n','</b>','<b/>','<a>','</a>','<a/>',
            '<br>','</br>','<br/>','<p>','</p>','<p/>',
            '<strong>','</strong>','<strong/>']
    html_spch_tag = html_spch + html_tag
    or_exp = '|'.join(html_spch_tag)
    text = re.sub(or_exp," ",text)
    text1= re.sub(r'[^\w\s]',' ',text)
    text2= re.sub(r"^\s+|\ㄴ+$","",text1)
    text3=text2.strip()# 양쪽 공백 제거
    return text3


def extract_naverBlog(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    if (str(soup).count('iframe')==2):
        ifra = soup.find('iframe', id='mainFrame')
        post_url = 'https://blog.naver.com' + ifra['src']
        res = requests.get(post_url)
        soup2 = BeautifulSoup(res.text, 'html.parser')
    elif (str(soup).count('iframe')<2):
        soup2=soup  
    
    try:
        map_address=soup2.find('p','se-map-address').text
    except:
        raise Exception (url,'지도 없음')
    


    # 제목 추출
    titles = soup2.find('title').text.replace(': 네이버 블로그','')
    titles = str_filter(titles) # 특수 문자 제거

    #본문 추출
    contents = ''
    txt_contents = soup2.find_all('div', {'class': re.compile('^se-module se-module-tex.*')})
    for p_span in txt_contents[1:]:
        for txt in p_span.find_all('span'):
            contents += txt.get_text() + '\n'

    main_text=str_filter(contents) # 특수 문자 제거
    
    contents_x=''
    try:
        contents_x=soup2.find('p','se_textarea').get_text()
    except:
        pass
    main_text_x=str_filter(contents_x)
    main_text=main_text+main_text_x

    
    # 이미지 링크 가져오기        
    img_urls=[]
    imgs = soup2.find_all('img', class_='se-image-resource')
    
    imgs_x=soup2.find_all(class_='se_mediaImage __se_img_el')
    imgs.extend(imgs_x)
    
    for img in imgs:
        if img.get('data-lazy-src')==None:
              img_urls.append(img.get('src'))
        else:
            img_urls.append(img.get('data-lazy-src'))
            

    # php 협찬 사이트
    php_links = soup2.find_all('img', class_='se-inline-image-resource')

    # 네이버 스티커
    Naver_sticker_urls=[]
    Naver_sticker= soup2.find_all('img', class_='se-sticker-image')
    for i in [-1]:
        try:
            Naver_sticker_urls.append(Naver_sticker[i].get('src'))
        except:
            pass

    img_urls.extend( Naver_sticker_urls)
    
    ## url 로 ad 거르기
    ad_words = ['seoulouba', 'mrblog', 'revu', 'dinnerqueen', 'xn--939au0g4vj8sq','modo','mrblog','hello-dm','cherrypl']
    ad_score=0
    for ad_word in ad_words:
        for php_link in php_links:
            if ad_word in php_link['src']:
                ad_score=1
    
    #img_urls 구분자 \n
    img_urls=str(img_urls)
    img_urls=img_urls.replace('[','')
    img_urls=img_urls.replace(']','')
    img_urls=img_urls.replace("'","")
    img_urls=img_urls.replace(', ','\n')

    for ad_word in ad_words:
        for img_url in img_urls:
            if img_urls.find(ad_word)>-1:
                ad_score=1
    ad_status=''
    if ad_score==1:
        ad_status='AD'
    else:
        ad_status='NEED-TO-PROCESS'

    return (url, main_text, img_urls, ad_status, map_address)

mysql_password=input("mysql_pw : ")

conn = pymysql.connect(host='blogdb.cm2yxwfja9ii.ap-northeast-2.rds.amazonaws.com',
                      user='admin',
                      password=mysql_password,
                      database='blogdb',
                      port=3306)
curs=conn.cursor()

dist=input("블로그 스크래핑할 district : ")

query=f"SELECT id FROM restaurants where district='{dist}'"
curs.execute(query)
iid = curs.fetchall()

#map_filter
for ind in range(len(iid)):
    if (dist=='송리단길'):
        ff='송파'
    if (dist=='망리단길'):
        ff='마포'
    if (dist=='용리단길'):
        ff='용산'
    if (dist=='서순라길'):
        ff='종로'
    if (dist=='샤로수길'):
        ff='관악'   
    
    query=f"SELECT id,url,res_id FROM post_data where res_id={iid[ind][0]}"
    curs.execute(query)
    data = curs.fetchall()
    for idx in range(len(data)):
        print(data[idx][0],data[idx][1])
        try:
            scraping=extract_naverBlog(data[idx][1])
        except Exception as e:
            print('extract_naverBlog error',e)
            update_sql = f"UPDATE post_data SET map=2 WHERE id={data[idx][0]};"
            curs.execute(update_sql)
            conn.commit()
            continue
            
        naver_map=0
        
        #블로그 내부의 지도 주소와 검색 지역 같은지 확인
        if scraping[4].find(ff)>-1:
            naver_map=1

        update_sql = f"UPDATE post_data SET content='{scraping[1]}', images='{scraping[2]}', map={naver_map},ad_status='{scraping[3]}' WHERE id={data[idx][0]};"
        curs.execute(update_sql)
        conn.commit()
        
        
        
        
        
        







