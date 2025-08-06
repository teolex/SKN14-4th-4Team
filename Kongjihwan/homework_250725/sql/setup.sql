-- Active: 1753665114292@@127.0.0.1@3306@mysql
# root 사용자로 실행

## 사용자 django/django 생성

create user 'django'@'%' identified by 'django';

# djangodb 데이처베이스 생성
# - 인코딩 utf8mb4 (다국어/이모지 텍스트 지원)
# - 정렬방식 utf8mb_unicode_ci (대소문자 구분 없음)

create database userinfodb character set utf8mb4 collate utf8mb4_unicode_ci;

# django 계정 권한 부여
grant all privileges on django.* to 'django'@'%';
flush privileges;

drop user skn14_4th_4team;
