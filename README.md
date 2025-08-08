# SKN14-4th-4Team


# 4팀: 다이어트를 위한 식단 관리 및 운동 추천 챗봇

## 1. 팀 소개
- **팀명**: GYM-PT
- **팀원**: 공지환, 송지훈, 조성렬, 한성규

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/0jihwan">
        <img src="https://github.com/0jihwan.png" width="80"/><br />
        <sub><b>공지환</b></sub>
      </a>
    </td>
    </td>
    <td align="center">
      <a href="https://github.com/teolex">
        <img src="https://github.com/teolex.png" width="80"/><br />
        <sub><b>송지훈</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/ezcome-ezgo">
        <img src="https://github.com/ezcome-ezgo.png" width="80"/><br />
        <sub><b>조성렬</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Seonggyu-Han">
        <img src="https://github.com/Seonggyu-Han.png" width="80"/><br />
        <sub><b>한성규</b></sub>
      </a>
    </td>
  </tr>
</table>


## 2. 프로젝트 개요

### 프로젝트 소개
다이어트를 위한 식단 관리 및 운동 추천 챗봇, **GYM-PT**는 인공지능 기반으로, 바쁜 현대인도 효율적으로 올바른 식단과 운동 습관을 관리할 수 있도록 설계된 통합 헬스케어 솔루션입니다.

이 시스템은 음식 사진 또는 간단한 텍스트 입력만으로 칼로리, 영양 성분, 재료 등 공식 데이터베이스와 연동하여 신뢰성 있는 정보를 빠르게 제공합니다. 대화형 챗봇은 사용자별 목표와 상황에 맞는 운동 루틴을 안내하여 시간과 비용 부담을 줄이고 누구나 지속가능한 건강관리를 실천할 수 있도록 지원합니다.

본 프로젝트는 복잡한 건강관리 과정을 간소화하고, 사용자 중심의 맞춤형 데이터 기반 안내를 통해 실생활에서 자기관리와 삶의 질 향상에 기여하는 것을 목표로 합니다.

<br>

### 개발 배경 및 필요성

<img width="2693" height="1022" alt="Section 1 (1)" src="https://github.com/user-attachments/assets/00178ced-e868-40c0-a85e-d657fe8412ac" />
*▲ 운동부족 관련 기사(좌), 영양 부족의 원인을 보여주는 다이어그램(우)*

빠르게 변화하는 라이프스타일, 급격한 도시화, 바쁜 일정, 쏟아지는 정보의 접근성 한계 등으로 현대인의 건강 습관 유지가 점점 더 어려워지고 있습니다. 많은 사람들이 시간·비용의 제약, 부정확한 건강 정보, 운동시설 부족, 동기 저하 등으로 식단 관리와 규칙적 운동 실천이 어렵습니다.

그 결과 운동 부족과 영양 불균형 문제가 심각해지고 만성질환과 사회적 부담도 커지고 있습니다. 누구나 쉽게 접근 가능한 신뢰 있는 정보와, 개인 환경과 목표에 맞춘 건강 관리가 필요합니다.

**[GYM-PT]는**
- 바쁜 일상과 시간·비용의 제약 속에서도 **간편하게 식단 정보와 운동 추천**을 제공하며,
- **지속 가능한 건강관리 습관** 형성,  
- **만성 건강 문제 예방과 삶의 질 향상**에 실질적으로 기여하고자 개발됐습니다.

---

## 3. 기술 스택 및 파일구조

| **Category**         | **Tech Stack**                                                                                                                                                                                                                                                                                     |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Language**         | <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>                                                                                                                                                                                           |
| **Frontend**         | <img src="https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white"/><br><img src="https://img.shields.io/badge/CSS-blue?style=for-the-badge&logo=css&logoColor=white"/><br><img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=white"/> |
| **Backend Framework**| <img src="https://img.shields.io/badge/django-FF7300?style=for-the-badge&logo=django&logoColor=white"/><br><img src="https://img.shields.io/badge/langchain-2296f3?style=for-the-badge&logo=langchain&logoColor=white"/>                                                                          |
| **Server / Proxy**   | <img src="https://img.shields.io/badge/nginx-009639?style=for-the-badge&logo=nginx&logoColor=white"/>                                                                                                                                                                                             |
| **Database**         | <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>                                                                                                                                                                                           |
| **Container / DevOps**| <img src="https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>                                                                                                                                                                                        |
| **LLM Model**        | <img src="https://img.shields.io/badge/OpenAI-GPT--4.0--mini-10a37f?style=for-the-badge&logo=openai&logoColor=white"/>                                                                                                                                    |
| **Vector DB**        | <img src="https://img.shields.io/badge/Pinecone-27AE60?style=for-the-badge&logo=pinecone&logoColor=white"/>                                                                                                                                                                                      |
| **Collaboration**    | <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white"/><br><img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white"/><br><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white"/><br><img src="https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white"/> |
| **IDE / Editor**     | <img src="https://img.shields.io/badge/VSCode-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white"/><br><img src="https://img.shields.io/badge/PyCharm-000000?style=for-the-badge&logo=pycharm&logoColor=white"/>                                                                    |

```
skn_last_small_project/
├── media/
│   └── profile/
├── skn_last_small_project/
│   ├── __pycache__/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/
│   ├── css/
│   │   ├── chat.css
│   │   └── global.css
│   └── js/
│       ├── chat.js
│       └── global.js
├── templates/
│   ├── layout/
│   │   ├── base_content_only.html
│   │   ├── base_default.html
│   │   ├── form_error_toast.html
│   │   ├── loading.html
│   │   └── nav.html
│   └── mainapp/
│       ├── chat.html
│       ├── intro.html
│       ├── login.html
│       ├── main.html
│       ├── mypage.html
│       └── signup.html
├── .dockerignore
├── .env
├── db.sqlite3
├── Dockerfile
├── manage.py
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```
<br><br>

---

## 4. 주요 기능

- **메인 페이지 사용 안내**
    - 프로젝트 사용법, 개인정보 입력, 챗봇 활용, AI 분석 절차 등 직관적 안내

- **회원가입 및 로그인**
    - 회원가입 및 로그인을 통한 회원별 대화 기록/관리 및 맞춤형 답변 
    - 회원가입 시 키, 몸무게, 성별, 나이 입력으로, 이후 사용자 입력 신체정보 기반 프롬프트 작성

- **챗봇 프롬프팅 및 상호작용**
    - 텍스트 또는 이미지 기반 자유로운 질의
    - 건강, 식단, 운동 Q&A
    - 음식 이미지 업로드 시 AI가 질문·이미지 모두 분석하여 답변

- **AI 기반 식단·운동 추천 및 정보 제공**
    - 입력 정보를 종합 분석해 맞춤형 식단관리, 운동 루틴, 음식정보(칼로리, 영양, 재료), 생활습관 등 다양한 답변

- **맞춤형 문서 생성 및 편의성**
    - 사용자 정보 바탕 식단·운동 플랜 문서 제공
    - 사용성 높은 인터페이스

---

## 5. 전체 워크 플로우
![alt text](</images/SKN14_4th_Team4 infra.svg>)

## 중요 코드 설명

### **1. chat_form.py**<br>
django.forms 에서 기본제공하는 field 로는 사용자로부터 한 번에 여러개의 파일을 받을 수가 없기때문에, 이를 해결하기 위해 forms.FileField 를 상속받아 여러개의 파일을 받을 수 있는 MultipleFileField 를 직접 만들어 사용.


### **2. vector_store.py, util.py**<br>
request 를 받을 때마다 langchain, Vector DB 객체들을 매번 생성해서 사용하기보다 별도의 관리용 class 를 선언하고 class variable, classmethod 를 사용함으로써 메모리 최적화에 기여.


### **3. inferer.py**<br>
여러개의 음식 이미지들을 벡터 DB 에서 조회할 때 한 번에 하나씩 질의하면 개당 5초정도의 시간이 소요되는 것을 해결하기 위해 각 질의마다 Thread 를 만들어 실행하도록 수정함으로써 총 실행시간을 3초 미만으로 줄임.

<br>

## 시스템 구현 단계 및 핵심 흐름

### 1. 주요 구현 단계

#### 프로젝트 처리 단계 요약

1. **데이터 수집 및 전처리**  
   - 외부 공개 식품DB(식품의약안전처 공공데이터 조리식품 레시피DB)에서 음식 정보, 레시피 데이터 수집  
   - [공공데이터 API 바로가기](https://www.foodsafetykorea.go.kr/api/openApiInfo.do?menu_grp=MENU_GRP31&menu_no=661&show_cnt=10&start_idx=1&svc_no=COOKRCP01)  
   - [data.go.kr 바로가기](https://www.data.go.kr/data/15100070/standard.do?utm_source=chatgpt.com#tab_layer_grid)
2. **임베딩 및 벡터DB 구축**  
   - 음식명·재료 기반 텍스트와 이미지에서 추출한 특징을 임베딩  
   - Pinecone 벡터DB에 저장
3. **입력 타입 분기**  
   - 업로드 데이터가 이미지(음식 사진)인지 텍스트(개인정보)인지 판별 후 경로 분기
4. **AI 정보 추출 및 유사도 검색**  
   - 이미지 입력 시 GPT-4.0  음식명 추출
   - 추출된 음식명을 Pinecone에서 유사 메뉴 Top-5(k=5, 유사도 ≥ 0.4) 검색
5. **칼로리 정보 확보**  
   - DB에서 찾으면 build_context()로 메뉴명·칼로리 확보  
   - 없으면 ask_LLM_calorie()로 GPT 칼로리값 획득
6. **프롬프트 조립 및 추천**  
   - DB·예측 값·사용자 정보 및 입력값 등으로 프롬프트 생성  
   - GPT-4.0로 식단·운동 추천
7. **결과 출력 및 반복**  
   - html 결과 카드로 정보 시각화  
   - 이미지 여러 장 입력 시 위 과정을 반복 처리
   - 기존 대화 내용 기반 멀티턴 대화

### 2. 시스템 워크플로우 요약
0. **로그인 및 회원가입**
   - main 페이지 혹은 chat 페이지에서 회원가입 및 로그인 (비회원 또한 진행 가능)
   - 회원 정보 sqllite 생성 및 저장

1. **입력**  
   - 사용자는 html에서 이미지와 텍스트(신체정보, 음식 등)를 입력

2. **입력 타입 자동 분기**  
   - 이미지는 GPT-4.0를 통해 음식명·재료 추출
   - Pinecone 벡터DB에서 **Top-5(최대 k=5, 유사도 0.4 이상)** 유사도 기반 검색을 통해 음식명 추출

3. **칼로리 및 컨텍스트 확보**  
   - DB 결과 있으면 메타정보 바로 활용  
   - 없을 경우 GPT로 칼로리 추론

4. **프롬프트 조합 및 모델 응답**  
   - DB/예측값, 텍스트, 사용자 정보 등으로 프롬프트 조립  
   - ChatOpenAI GPT-4.0에 전달하여 식단·운동 포함 맞춤 추천 생성

5. **결과 시각화 및 반복 처리**  
   - html 결과 카드에 칼로리, 운동, 식단 결과 제공  
   - 기존 대화를 통해 멀티턴 대화 진행

---

## 6. 웹페이지 구성

### **Main 페이지**
![alt text](</images/스크린샷 2025-08-08 102149.png>)
![alt text](</images/스크린샷 2025-08-08 102159.png>)
- 회원가입, 로그인, chat page로 넘어가는 '오늘의 식사 입력하기'버튼
- 비회원 또한 버튼을 통해 바로 chat page 이용 가능
<br>

### **Sign Up 페이지**
![alt text](</images/스크린샷 2025-08-08 103120.png>)
![alt text](</images/스크린샷 2025-08-08 103042.png>)
![alt text](</images/스크린샷 2025-08-08 103313.png>)
![alt text](</images/스크린샷 2025-08-08 103333.png>)
- 아이디, 이름, 이메일, 비밀번호, 생일, 신장, 몸무게, 프로필 이미지 입력
- 비밀번호 형식 입력 오류 등 입력 오류시 오류 메세지 출력
- 회원가입 완료시 자동 로그인 및 chat 페이지 이동

### **Sign in 페이지**
![alt text](</images/스크린샷 2025-08-08 102903.png>)
![alt text](</images/스크린샷 2025-08-08 103218.png>)
![alt text](</images/스크린샷 2025-08-08 102916.png>)
- 로그인 정보 입력 오류 시 오류 메세지 출력
- 로그인 시 chat 페이지 자동 이동


### **Mypage 페이지**
![alt text](</images/스크린샷 2025-08-08 102929.png>)
![alt text](</images/스크린샷 2025-08-08 103203.png>)
- 로그인 상태에서 프로필 클릭 시 mypage 창 이동
- 회원 탈퇴 기능, 버튼 누를 시 마지막 확인

### **Chat 페이지**
![alt text](</images/스크린샷 2025-08-08 102216.png>)
![alt text](</images/스크린샷 2025-08-08 102225.png>)
- main페이지로 이동하는 '메인으로' 버튼
- 비회원 진행시 chat 페이지에서도 회원가입, 로그인 가능
- 이미지 파일 업로드 칸, 텍스트 입력 칸, '오늘의 식사 입력하기'버튼

![alt text](</images/스크린샷 2025-08-08 102247.png>)
![alt text](</images/스크린샷 2025-08-08 102712.png>)
- 이미지 파일 업로드(최대 5개 입력 가능, 파일 1개당 5Mb 용량제한)
- 이미지 업로드 시 업로드 이미지 썸네일 출력
- 이미지 or 텍스트 or 이미지&텍스트 입력 후 버튼 통해 분석 시작

![alt text](</images/스크린샷 2025-08-08 102717.png>)
- Spinner 통해 분석상태 표시
- 이미지 전송 시 사용자 메세지에 이미지 썸네일 출력

![alt text](</images/스크린샷 2025-08-08 102752.png>)
![alt text](</images/스크린샷 2025-08-08 102805.png>)
- 섭취 음식 정보 (음식명, 열량), 총 칼로리
- 추천 운동(운동 종류, 분당 소모 칼로리, 운동 시간)



---

## 7. 시연 영상
[![시연영상](https://img.youtube.com/vi/cRpDm9iIDCM/0.jpg)](https://youtu.be/cRpDm9iIDCM)
---

## 8. 추후 발전 계획

1. 학습용 음식 이미지 데이터셋을 확장해 pinecone DB를 업데이트, 정확도를 높여 서비스 고도화
2. 모바일 앱 출시, 웨어러블 기기 연동, 다국어 지원으로 사용자 경험 개선 및 플랫폼 확장
3. 무료 이용자에겐 광고 도입, 유료 회원에겐 멤버십 기능을 제공하여 사용자 맞춤 혜택을 강화, 서비스의 지속 가능성과 수익 모델 확보

---


<table>
  <tr>
       <td>
         <b>한성규</b>
       </td>
       <td> 프로젝트를 하며 모르던 부분들을이 어떤 부분들이었는지 다시 마주할 수 있었고, 팀원들에게 질문하고 도움 받으며 많이 배울 수 있었습니다.<br>
       그저 말하는 감자인 저를 끌고 가주신 팀원들에게 무한한 감사의 마음만 가득입니다.
       이어질 최종 프로젝트도 화이팅하세요!♥️
       </td>
 </tr>
 <tr>
    <td>
       <b>공지환</b>
    </td>
    <td>이번 기회로 웹개발과 친해질 수 있도록 많은 시간을 보냈습니다. 평생 프론트엔드와는 친해질 수 없을 것 같았지만, 지금 이후로 손 정도는 잡을수 있게 되었습니다. 팀원분들 진짜 너무 많이 고생하셨습니다 남은 최종프로젝트도 파이팅</td>
<tr>
    <td>
       <b>송지훈</b>
    </td>
    <td>
        <ol>
            <li>여느 프레임워크들과 마찬가지로 django 도 디테일하게 들어갈 수록 사전에 준비하고 조치해야 하는 것들이 많았습니다. 특히, 개발/운영환경에서의 정정파일 서비스 가불가는 약간 당황스러웠습니다.<br/></li>
            <li>LLM 과 관련된 어플리케이션을 만들기 위해서는 첫 번째로 프롬프터가 정말 큰 부분을 차지한다는걸 알수 있었습니다. 원하는 결과를 얻기 위해서는 모든 예상가능한 결과들을 종합하여 공통형식으로 뽑아낼 수 있도록 프롬프팅해야 하는데 이에 대한 대책도 고민해봐야겠습니다.</li>
        </ol>
    </td>
</tr>
<tr>
    <td>
      <b>조성렬</b>
    </td>
    <td>먼저 3차프로젝트에 이어서 4차프로젝트도 같이하게 되어 소통이 잘 이루어졌던것같습니다. 기존에 구성한 페이지를 django 웹으로 변환하는 작업을 하며 수업시간에 배웠던 django구조를 잘 이해할 수 있었습니다. Docker로 배포하는 과정에서 어려움을 겪어서 아쉽지만 배포가 된 코드를 참고하여 다시 한번 시도해보려고 합니다.
    </td>
           
    

</table>


