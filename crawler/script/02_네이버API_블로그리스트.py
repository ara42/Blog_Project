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
    text3=text2.strip()# 양측 공백 제거
    return text3

def nSearch(query,start, display,cid,cs):
    url='https://openapi.naver.com/v1/search/blog.json'
    query_str=f'{url}?query={query}&start={start}&display={display}'
    req=Request(query_str)
    req.add_header("X-Naver-Client-Id",cid)
    req.add_header("X-Naver-Client-Secret",cs)
    resp=urlopen(req)  ## urlopen 만으로는 헤더 전달이 안됨
    raw_data=resp.read()
    jdata=json.loads(raw_data)
    return jdata['items'],jdata['display'], jdata['total']

# 네이버 블로그 url 100개 이상 크롤링
def nSearch_over(query,cid,cs):
    start=1
    display=100
    items , rcnt, total = nSearch(query,start,display,cid,cs)
    start += rcnt
    while start < total:
        items2 , rcnt, _ = nSearch(query,start,display,cid,cs)
        items.extend(items2)
        if len(items)>800:
            break
        start += rcnt
        if rcnt == 0:
            break
    return items, start-1, total


mysql_password=input("mysql_pw : ")
cid = input("X-Naver-Client-Id: ")
cs = input("X-Naver-Client-Secret: ")
districts=input("블로그 리스트 가져올 district : ")
district_list = districts.split(',')

conn = pymysql.connect(host='blogdb.cm2yxwfja9ii.ap-northeast-2.rds.amazonaws.com',
                      user='admin',
                      password=mysql_password,
                      database='blogdb',
                      port=3306)
curs=conn.cursor()

for dist in district_list:
    query=f"SELECT id,name FROM restaurants WHERE district='{dist}';"
    curs.execute(query)
    data = curs.fetchall()
    
    for idx in range(len(data)):
        print(data[idx][1])
        data[idx][1].split(' ')[0]+' '+dist
        
        try:
            blog_list=nSearch_over(quote(data[idx][1]),cid,cs)
            time.sleep(2)
        except Exception as e:
            print(data[idx][1])
            print('nSearch_over error',e)
            continue
            
        if len(blog_list[0])==0:
            continue
        df=pd.DataFrame(blog_list[0])
        df['title']=df['title'].apply(str_filter)
        df['description']=df['description'].apply(str_filter)
        insert_sql = 'INSERT INTO post_data (res_id,title, url, description, post_date) VALUES (%s,%s, %s, %s, %s);'

        for i in range(len(df)):
            data_to_insert = (data[idx][0],df['title'][i], df['link'][i], df['description'][i], df['postdate'][i])
            try:
                curs.execute(insert_sql, data_to_insert)
                conn.commit()
            except Exception as e:
                print(data_to_insert)
                print('curs.execute error',e)
                continue

conn.close()
    











