# 기반 이미지 설정
FROM python:3.12

# 작업 디에렉토리
WORKDIR /app

# 의존성 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 장고가 노출될 포트
EXPOSE 8000

# 컨테이너 시작할 때 실행될 명령어
# 이건 거의 개발용(dev).
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# 이게 운영용

# collectstatic 를 넣으면 build 단계부터 안됨...
#RUN python manage.py collectstatic --noinput

# app이나 settings 에서 환경변수를 사용한다면, build 단계에서 에러가 나므로,
# 빌드할 때는 그냥 더미 키값으로 빌드하고 run 할 때 제대로 주니까 됨.
# docker build --build-arg OPENAI_API_KEY=dummy --build-arg PINECONE_PJ_KEY=dummy -t jihunsong88/skn-4th-team4 .
ARG OPENAI_API_KEY
ARG PINECONE_PJ_KEY

ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV PINECONE_PJ_KEY=$PINECONE_PJ_KEY
ENV DEBUG=False

CMD ["gunicorn", "skn_last_small_project.wsgi:application", "--bind", "0.0.0.0:8000"]