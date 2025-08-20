# 1. 베이스 이미지: 파이썬 3.10 slim 버전을 사용합니다.
FROM python:3.10-slim

# 2. 작업 디렉토리: 컨테이너 내부의 작업 공간을 /app으로 설정합니다.
WORKDIR /app

# 3. 시스템 라이브러리 설치: apidetector가 사용하는 Playwright를 위해 필요합니다.
RUN apt-get update && apt-get install -y \
    libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libasound2 libxtst6 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 4. apidetector 코드 및 의존성 설치
COPY ./apidetector /app/apidetector
RUN pip install --no-cache-dir -r /app/apidetector/requirements.txt

# 5. Playwright 브라우저 설치
RUN playwright install

# 6. Flask 애플리케이션 코드 복사
COPY ./app.py /app/app.py

# 7. Flask 및 Gunicorn 설치
RUN pip install --no-cache-dir "flask" "gunicorn" "requests"

# 8. 포트 노출: 컨테이너가 8000번 포트를 사용함을 명시합니다.
EXPOSE 8000

# 9. 컨테이너 시작 명령어: Gunicorn을 사용해 앱을 실행합니다.
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "app:app"]