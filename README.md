# Blog_Project

## 디렉토리 구조

- crawler 
  - 데이터 수집 프로그램

- flask
  - API 서버  

- ml
  - 데이터 분석 및 광고판단

- web
  - HTML 작성

## 프로그램 실행 방법
먼저 데이터후 DB에 저장

```bash
crawler/scrap.sh
```

광고 문구 학습
```bash
ml/learning.sh
```

위 프로그램을 실행하면 DB에 데이터 쌓인다. 


## DB 구조
```sql 
CREATE TABLE restaurants(
  `id` INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
  `name` VARCHAR(255) NOT NULL COMMENT '식당이름',
  `address` VARCHAR(255) NOT NULL COMMENT '식당 주소. ex) 서울 특별시 ~~',
  `district` VARCHAR(255) NOT NULL COMMENT  '지역명. ex) 종로' ,
  `latitude` FLOAT NOT NULL COMMENT '위도',
  `longitude` FLOAT NOT NULL COMMENT '경도',
  `total_post_cnt` INT DEFAULT NULL COMMENT '관련 포스트 전체수',
  `post_cnt` INT DEFAULT NULL COMMENT '광고가 아닌 포스트 전체수',
  `features` TEXT NOT NULL COMMENT '부가정보.',
  `menu_count` TEXT NULL COMMENT '{"메뉴명_1": 2, "메뉴명_2": 3} 식당별 메뉴언급횟수',
  `finished` TINYINT(1) DEFAULT 0 COMMENT '데이터 분석 완료유무',
  INDEX (district)
);

SELECT * FROM restaurants WHERE district = '' ORDER BY post_cnt LIMIT 5;

CREATE TABLE post(
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `res_id` INT NOT NULL,
  `title` VARCHAR(255) NOT NULL COMMENT '포스팅 제목',
  `url` VARCHAR(255) NOT NULL COMMENT '포스팅 URL',
  `description` TEXT NOT NULL COMMENT  '포스트 설명',
  `post_date` DATE NOT NULL COMMENT  '포스팅 날짜',
  `content` TEXT NOT NULL  COMMENT  '포스트 본문',
  `menu_count` TEXT NULL COMMENT '{"메뉴명_1": 2, "메뉴명_2": 3} 포스트별 메뉴 언급횟수',
  FOREIGN KEY (res_id) REFERENCES restaurants(id)
) COMMENT '광고아닌 포스트. 화면 출력용';

CREATE TABLE post_data(
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `res_id` INT NOT NULL,
  `title` VARCHAR(255) NOT NULL COMMENT '포스팅 제목',
  `url` VARCHAR(255) NOT NULL COMMENT '포스팅 URL',
  `description` TEXT NOT NULL COMMENT '포스트 설명',
  `post_date` DATE NOT NULL COMMENT  '포스팅 날짜',  
  `content` TEXT NOT NULL COMMENT '포스트 본문',
  `images` TEXT DEFAULT NULL COMMENT '["url_1", "url_2"]',
  `ocr_text` TEXT DEFAULT NULL COMMENT '["url_text_1", "url_text_2"] 상위 이미지 OCR, images 컬럼과 순서를 맞춰야 함.',
  `ad_status` enum('AD', 'NON-AD', 'NEED-TO-PROCESS') DEFAULT 'NEED-TO-PROCESS' COMMENT '상태', 
  FOREIGN KEY (res_id) REFERENCES restaurants(id),
  INDEX (ad_status)
) COMMENT '데이터 분석용 테이블';'
```

