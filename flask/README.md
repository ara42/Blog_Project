## 진행 과정 PPT 
https://docs.google.com/presentation/d/1HxlKAHQTMZWOWTxa03r78GLLDwk3gqTJajFtPg3whVo/edit?usp=sharing

## 폴더 형식
```
/app.py
/static
  /home_main.png
/templates
  /home.html
  /page2.html
  /page3.html
```
## 필수 설치
```
pip install flask 
pip install pymysql
pip install urllib.request
pip install sqlalchemy
pip install pygal
```

## 실행 과정
1. 위의 폴더 형식과 같게 파일 위치 설정
2. 필수 라이브러리 설치
3. app.py 내의 password 부분 입력
4. photo 함수 내의 img_folder 본인의 static 폴더 경로로 설정
5. app.py 실행 후 연결된 서버로 접속
   ex) * Running on **http://127.0.0.1:5000**
