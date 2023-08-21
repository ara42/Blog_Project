import requests
import pandas as pd
import pymysql

kakao_api_key=input("kakao_api_key : ")
mysql_password=input("mysql_pw : ")
district=input("district : ")
rect = input("L_Y,L_X,R_Y,R_X : ")
L_Y,L_X,R_Y,R_X= rect.split(',')

#ㅣatitude = 위도 = y
# longitude = 경도 = x
L_X=float(L_X)
L_Y=float(L_Y)
R_X=float(R_X)
R_Y=float(R_Y)

loc1=L_X,L_Y,(L_X+(R_X-L_X)*(1/3)),(L_Y+R_Y)*(1/2)
loc2=(L_X+(R_X-L_X)*(1/3)),(L_Y+R_Y)*(1/2),(L_X+(R_X-L_X)*(2/3)),L_Y
loc3=(L_X+(R_X-L_X)*(2/3)),L_Y,R_X,(L_Y+R_Y)*(1/2)
loc4=R_X,(L_Y+R_Y)*(1/2),(L_X+(R_X-L_X)*(2/3)),R_Y
loc5=(L_X+(R_X-L_X)*(2/3)),R_Y,(L_X+(R_X-L_X)*(1/3)),(L_Y+R_Y)*(1/2)
loc6=(L_X+(R_X-L_X)*(1/3)),(L_Y+R_Y)*(1/2),L_X,R_Y

locs=[loc1,loc2,loc3,loc4,loc5,loc6]

df = pd.DataFrame()
n=1
tot_cnt=[]
for loc in locs:
    location='partial_area'+str(n)
    df1=pd.DataFrame()
    for page in range(1,4):
        url = f"https://dapi.kakao.com/v2/local/search/category.json?category_group_code=FD6&page={page}&rect={loc[0]},{loc[1]},{loc[2]},{loc[3]}"
        header = {'Authorization': 'KakaoAK ' + kakao_api_key}
        req = requests.get(url, headers=header)
        resp = req.json()
        
        df2=pd.DataFrame(resp['documents'])
        df1=pd.concat([df2,df1])

        if resp['meta']['total_count'] == len(df1):
            tot_cnt.append(resp['meta']['total_count'])
            break;
    n+=1
    df1['partial_area']=location
    df=pd.concat([df1,df])
df = df.sort_values(by='partial_area')
df = df.reset_index(drop=True)
df['district']=district

conn = pymysql.connect(host='blogdb.cm2yxwfja9ii.ap-northeast-2.rds.amazonaws.com',
                      user='admin',
                      password=mysql_password,
                      database='blogdb',
                      port=3306)
curs=conn.cursor()


for i in range(len(df)):
    data_to_insert = (df['place_name'][i], df['road_address_name'][i], df['district'][i], df['y'][i], df['x'][i])
    insert_sql = 'INSERT INTO restaurants (name, address, district, latitude, longitude) VALUES (%s, %s, %s, %s, %s);'
    curs.execute(insert_sql, data_to_insert)
    conn.commit()





