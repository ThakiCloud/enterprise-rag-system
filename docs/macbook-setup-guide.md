# MacBook Setup & Testing Guide

## 개요

이 문서는 MacBook에서 Enterprise RAG System을 처음부터 끝까지 설치, 실행, 테스트하는 완전한 가이드입니다. 모든 단계가 상세히 설명되어 있으며, 실제 테스트 시나리오까지 포함되어 있습니다.

## 목차

1. [시스템 요구사항](#1-시스템-요구사항)
2. [사전 준비](#2-사전-준비)
3. [프로젝트 설치](#3-프로젝트-설치)
4. [환경 설정](#4-환경-설정)
5. [백엔드 실행 및 테스트](#5-백엔드-실행-및-테스트)
6. [UI 실행 및 테스트](#6-ui-실행-및-테스트)
7. [CLI 인터페이스 테스트](#7-cli-인터페이스-테스트)
8. [웹 대시보드 테스트](#8-웹-대시보드-테스트)
9. [통합 테스트](#9-통합-테스트)
10. [Docker 환경 테스트](#10-docker-환경-테스트)
11. [성능 테스트](#11-성능-테스트)
12. [문제 해결](#12-문제-해결)

---

## 1. 시스템 요구사항

### 1.1 하드웨어 요구사항
- **CPU**: Apple Silicon (M1/M2/M3) 또는 Intel x64
- **RAM**: 최소 8GB, 권장 16GB 이상
- **Storage**: 최소 10GB 여유 공간
- **Network**: 인터넷 연결 (LLM API 사용)

### 1.2 소프트웨어 요구사항
- **macOS**: 12.0 (Monterey) 이상
- **Python**: 3.11 이상
- **Git**: 최신 버전
- **Docker**: 선택사항 (컨테이너 테스트용)

---

## 2. 사전 준비

### 2.1 Homebrew 설치 (없는 경우)

```bash
# Homebrew 설치 확인
brew --version

# 없는 경우 설치
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2.2 Python 3.11+ 설치

```bash
# Python 버전 확인
python3 --version

# Python 3.11 설치 (필요한 경우)
brew install python@3.11

# 심볼릭 링크 생성
ln -sf /opt/homebrew/bin/python3.11 /usr/local/bin/python3
ln -sf /opt/homebrew/bin/pip3.11 /usr/local/bin/pip3
```

### 2.3 Git 설치 및 설정

```bash
# Git 설치 확인
git --version

# 없는 경우 설치
brew install git

# Git 사용자 정보 설정 (필요한 경우)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2.4 LLM API 키 준비

다음 중 하나 이상의 API 키를 준비하세요:

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Google AI**: https://makersuite.google.com/app/apikey
- **Ollama**: 로컬 설치 (API 키 불필요)

---

## 3. 프로젝트 설치

### 3.1 프로젝트 클론

```bash
# 프로젝트 클론
git clone https://github.com/your-org/enterprise-rag-system.git
cd enterprise-rag-system

# 프로젝트 구조 확인
ls -la
```

**예상 출력:**
```
total 64
drwxr-xr-x  15 user  staff   480 Dec 15 10:00 .
drwxr-xr-x   8 user  staff   256 Dec 15 10:00 ..
-rw-r--r--   1 user  staff  1234 Dec 15 10:00 README.md
drwxr-xr-x   8 user  staff   256 Dec 15 10:00 backend/
-rw-r--r--   1 user  staff   567 Dec 15 10:00 config.env.example
drwxr-xr-x   4 user  staff   128 Dec 15 10:00 docs/
drwxr-xr-x   6 user  staff   192 Dec 15 10:00 infrastructure/
-rwxr-xr-x   1 user  staff   890 Dec 15 10:00 init-cursor.sh
-rw-r--r--   1 user  staff  1024 Dec 15 10:00 LICENSE
-rw-r--r--   1 user  staff   345 Dec 15 10:00 run_backend.py
-rw-r--r--   1 user  staff   234 Dec 15 10:00 run_ui.py
drwxr-xr-x   5 user  staff   160 Dec 15 10:00 tests/
drwxr-xr-x   6 user  staff   192 Dec 15 10:00 ui/
```

### 3.2 가상환경 생성

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 가상환경 활성화 확인
which python
# 출력: /path/to/enterprise-rag-system/venv/bin/python
```

### 3.3 의존성 설치

```bash
# 백엔드 의존성 설치
pip install -r backend/requirements.txt

# UI 의존성 설치
pip install -r ui/requirements.txt

# 테스트 의존성 설치
pip install -r tests/requirements.txt

# 설치 확인
pip list | grep -E "(fastapi|lancedb|openai|anthropic)"
```

**예상 출력:**
```
anthropic                 0.25.1
fastapi                   0.115.0
lancedb                   0.23.0
openai                    1.51.0
```

---

## 4. 환경 설정

### 4.1 환경 변수 파일 생성

```bash
# 환경 변수 템플릿 복사
cp config.env.example .env

# 환경 변수 파일 편집
nano .env
```

### 4.2 필수 환경 변수 설정

`.env` 파일에 다음 내용을 설정하세요:

```bash
# LLM 프로바이더 설정 (하나 이상 필수)
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_API_KEY=your-google-ai-key-here

# 기본 LLM 프로바이더 선택
DEFAULT_LLM_PROVIDER=openai  # openai, anthropic, google, ollama 중 선택

# 서버 설정
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
UI_HOST=127.0.0.1
UI_PORT=8501

# 데이터베이스 설정
VECTOR_DB_PATH=./tmp/lancedb
SESSION_DB_PATH=./tmp/sessions.db

# 파일 업로드 설정
UPLOAD_DIR=./tmp/uploads
MAX_FILE_SIZE=10485760  # 10MB

# 로깅 설정
LOG_LEVEL=INFO
LOG_FILE=./tmp/logs/app.log
```

### 4.3 디렉토리 생성

```bash
# 필요한 디렉토리 생성
mkdir -p tmp/{lancedb,uploads,logs}

# 권한 설정
chmod -R 755 tmp/

# 디렉토리 구조 확인
tree tmp/
```

**예상 출력:**
```
tmp/
├── lancedb/
├── logs/
└── uploads/
```

### 4.4 환경 검증

```bash
# 초기화 스크립트 실행
./init-cursor.sh

# 환경 검증
python run_backend.py --check
```

**예상 출력:**
```
🔍 Enterprise RAG System - Environment Check

✅ Python Version: 3.11.5
✅ Required packages installed
✅ Environment variables loaded
✅ Database directories created
✅ LLM Provider configured: openai
✅ All systems ready!

Environment check completed successfully.
```

---

## 5. 백엔드 실행 및 테스트

### 5.1 백엔드 서버 시작

```bash
# 백엔드 서버 실행
python run_backend.py

# 또는 개발 모드로 실행 (자동 재시작)
python run_backend.py --reload
```

**예상 출력:**
```
🚀 Starting Enterprise RAG System Backend...

INFO:     Will watch for changes in these directories: ['/path/to/enterprise-rag-system']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

🌐 Web Dashboard: http://127.0.0.1:8000
📚 API Documentation: http://127.0.0.1:8000/docs
🔍 Health Check: http://127.0.0.1:8000/health
```

### 5.2 헬스체크 테스트

새 터미널 창을 열고:

```bash
# 헬스체크 API 테스트
curl http://127.0.0.1:8000/health

# 예상 응답:
# {"status":"healthy","timestamp":"2024-12-15T10:00:00Z","version":"1.0.0"}

# API 문서 접근 테스트
curl -I http://127.0.0.1:8000/docs
# 예상: HTTP/1.1 200 OK
```

### 5.3 API 엔드포인트 테스트

```bash
# 지식베이스 통계 조회
curl http://127.0.0.1:8000/api/v1/knowledge-base/stats

# 예상 응답:
# {"document_count":0,"total_chunks":0,"vector_db_size":"0 MB","session_count":0}

# 세션 목록 조회
curl http://127.0.0.1:8000/api/v1/sessions/

# 예상 응답:
# {"sessions":[],"total_count":0,"active_count":0}
```

---

## 6. UI 실행 및 테스트

### 6.1 AGUIApp UI 시작

새 터미널 창에서:

```bash
# 가상환경 활성화
source venv/bin/activate

# UI 서버 실행
python run_ui.py
```

**예상 출력:**
```
🎨 Starting Enterprise RAG System UI...

Backend URL: http://127.0.0.1:8000
Testing backend connection...
✅ Backend connection successful!

Starting AGUIApp on http://127.0.0.1:8501
```

### 6.2 UI 접근 테스트

브라우저에서 다음 URL들을 확인:

1. **AGUIApp UI**: http://127.0.0.1:8501
2. **웹 대시보드**: http://127.0.0.1:8000

### 6.3 UI 기능 테스트

#### 6.3.1 AGUIApp UI 테스트

1. **연결 상태 확인**
   - UI 상단에 "Backend Connected" 표시 확인
   - 백엔드 상태가 "Healthy"로 표시되는지 확인

2. **문서 업로드 테스트**
   - "Upload Documents" 섹션으로 이동
   - 테스트 파일 업로드 (PDF, DOCX, TXT)
   - 업로드 진행률 표시 확인
   - 성공 메시지 확인

3. **채팅 인터페이스 테스트**
   - "Chat Interface" 섹션으로 이동
   - 간단한 질문 입력
   - 실시간 응답 스트리밍 확인
   - 소스 정보 표시 확인

---

## 7. CLI 인터페이스 테스트

### 7.1 CLI 모드 시작

```bash
# CLI 모드로 백엔드 실행
python run_backend.py --cli
```

**예상 출력:**
```
🖥️  Enterprise RAG System - CLI Mode

Welcome to the Enterprise RAG System CLI!
Type '/help' for available commands or '/quit' to exit.

Available LLM Providers: openai, anthropic, google, ollama
Current Provider: openai
Current Mode: simple

CLI> 
```

### 7.2 CLI 명령어 테스트

```bash
# 도움말 확인
CLI> /help

# 시스템 정보 확인
CLI> /info

# 지식베이스 상태 확인
CLI> /status

# URL 추가 테스트
CLI> /url https://en.wikipedia.org/wiki/Artificial_intelligence

# 파일 업로드 테스트
CLI> /upload /path/to/test/document.pdf

# LLM 프로바이더 변경
CLI> /provider anthropic

# 추론 모드 전환
CLI> /reasoning

# 간단한 질문 테스트
CLI> What is artificial intelligence?
```

**예상 CLI 응답 예시:**
```
CLI> /info

📊 System Information:
├── Backend Status: Healthy
├── Vector DB: LanceDB (0 documents)
├── Session DB: SQLite (0 sessions)
├── Current Provider: openai (gpt-4o)
├── Upload Directory: ./tmp/uploads
└── Log Level: INFO

CLI> What is artificial intelligence?

🤖 Processing your question...

**Answer:**
Artificial intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. It encompasses various technologies including machine learning, natural language processing, and computer vision.

**Sources:**
📄 wikipedia_artificial_intelligence.txt (similarity: 0.95)
   "Artificial intelligence is intelligence demonstrated by machines..."

**Processing Time:** 1.23s
**Model Used:** gpt-4o
```

---

## 8. 웹 대시보드 테스트

### 8.1 대시보드 접근

브라우저에서 http://127.0.0.1:8000 접근

### 8.2 문서 업로드 테스트

1. **파일 업로드**
   ```bash
   # 테스트 문서 생성
   echo "This is a test document for Enterprise RAG System testing." > test_document.txt
   
   # 브라우저에서 파일 업로드
   # - 파일 선택: test_document.txt
   # - Upload 버튼 클릭
   # - 성공 메시지 확인
   ```

2. **URL 추가**
   - URL 입력 필드에 테스트 URL 입력
   - 예: `https://en.wikipedia.org/wiki/Machine_learning`
   - Add URL 버튼 클릭
   - 처리 완료 확인

### 8.3 채팅 기능 테스트

1. **기본 질문**
   ```
   질문: "What is machine learning?"
   
   예상 응답:
   - 실시간 스트리밍 응답
   - 소스 정보 표시
   - 처리 시간 표시
   ```

2. **고급 추론 모드**
   ```
   질문: "Compare supervised and unsupervised learning methods"
   옵션: "Use Advanced Reasoning" 체크
   
   예상 응답:
   - 단계별 추론 과정 표시
   - 더 상세한 분석
   - 추론 체인 표시
   ```

### 8.4 세션 관리 테스트

1. **세션 생성**
   - 새 채팅 시작
   - 세션 ID 자동 생성 확인

2. **세션 목록 확인**
   ```bash
   curl http://127.0.0.1:8000/api/v1/sessions/
   ```

3. **세션 삭제**
   ```bash
   curl -X DELETE http://127.0.0.1:8000/api/v1/sessions/{session_id}
   ```

---

## 9. 통합 테스트

### 9.1 전체 워크플로 테스트

다음 시나리오를 순서대로 실행:

```bash
# 1. 시스템 상태 확인
curl http://127.0.0.1:8000/health

# 2. 테스트 문서 준비
cat > test_rag_document.txt << EOF
Enterprise RAG System is a powerful document processing and question-answering system.
It supports multiple LLM providers including OpenAI, Anthropic, and Google.
The system uses LanceDB for vector storage and hybrid search capabilities.
Key features include real-time streaming, session management, and multi-agent reasoning.
EOF

# 3. 문서 업로드
curl -X POST -F "file=@test_rag_document.txt" \
     http://127.0.0.1:8000/api/v1/upload-document/

# 4. 지식베이스 상태 확인
curl http://127.0.0.1:8000/api/v1/knowledge-base/stats

# 5. 질문 테스트
curl -X POST -H "Content-Type: application/json" \
     -d '{"question":"What LLM providers does the Enterprise RAG System support?"}' \
     http://127.0.0.1:8000/api/v1/query/

# 6. 고급 추론 테스트
curl -X POST -H "Content-Type: application/json" \
     -d '{"question":"Explain the architecture of the Enterprise RAG System","use_advanced_reasoning":true}' \
     http://127.0.0.1:8000/api/v1/query/
```

### 9.2 멀티 프로바이더 테스트

```bash
# 환경 변수 변경으로 프로바이더 전환 테스트
export DEFAULT_LLM_PROVIDER=anthropic
python run_backend.py --check

export DEFAULT_LLM_PROVIDER=google
python run_backend.py --check

export DEFAULT_LLM_PROVIDER=openai
python run_backend.py --check
```

### 9.3 에러 처리 테스트

```bash
# 잘못된 파일 업로드
curl -X POST -F "file=@nonexistent.txt" \
     http://127.0.0.1:8000/api/v1/upload-document/

# 빈 질문 테스트
curl -X POST -H "Content-Type: application/json" \
     -d '{"question":""}' \
     http://127.0.0.1:8000/api/v1/query/

# 잘못된 URL 테스트
curl -X POST -H "Content-Type: application/json" \
     -d '{"url":"invalid-url"}' \
     http://127.0.0.1:8000/api/v1/add-url/
```

---

## 10. Docker 환경 테스트

### 10.1 Docker 설치 확인

```bash
# Docker 설치 확인
docker --version
docker-compose --version

# Docker 없는 경우 설치
brew install docker docker-compose
```

### 10.2 Docker Compose 빌드 및 실행

```bash
# Docker 이미지 빌드
docker-compose build

# 컨테이너 실행
docker-compose up -d

# 컨테이너 상태 확인
docker-compose ps
```

**예상 출력:**
```
NAME                          COMMAND                  SERVICE             STATUS              PORTS
enterprise-rag-backend-1      "python -m uvicorn a…"   backend             running             0.0.0.0:8000->8000/tcp
enterprise-rag-ui-1           "python main.py"         ui                  running             0.0.0.0:8501->8501/tcp
```

### 10.3 Docker 환경 테스트

```bash
# 헬스체크
curl http://localhost:8000/health

# 로그 확인
docker-compose logs backend
docker-compose logs ui

# 컨테이너 정리
docker-compose down
```

---

## 11. 성능 테스트

### 11.1 기본 성능 측정

```bash
# 응답 시간 측정
time curl -X POST -H "Content-Type: application/json" \
     -d '{"question":"What is the Enterprise RAG System?"}' \
     http://127.0.0.1:8000/api/v1/query/
```

### 11.2 부하 테스트 (Apache Bench)

```bash
# Apache Bench 설치
brew install apache-bench

# 동시 연결 테스트
ab -n 100 -c 10 http://127.0.0.1:8000/health

# POST 요청 부하 테스트
ab -n 50 -c 5 -p query.json -T application/json \
   http://127.0.0.1:8000/api/v1/query/
```

`query.json` 파일 생성:
```json
{"question":"What is artificial intelligence?"}
```

### 11.3 메모리 사용량 모니터링

```bash
# 프로세스 모니터링
ps aux | grep python
top -p $(pgrep -f "uvicorn")

# 메모리 사용량 확인
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

---

## 12. 문제 해결

### 12.1 일반적인 문제들

#### 문제 1: 포트 충돌
```bash
# 포트 사용 확인
lsof -i :8000
lsof -i :8501

# 프로세스 종료
kill -9 <PID>

# 다른 포트 사용
export BACKEND_PORT=8001
export UI_PORT=8502
```

#### 문제 2: Python 패키지 충돌
```bash
# 가상환경 재생성
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install -r ui/requirements.txt
```

#### 문제 3: API 키 문제
```bash
# API 키 확인
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# 환경 변수 재설정
source .env
python run_backend.py --check
```

#### 문제 4: 데이터베이스 문제
```bash
# 데이터베이스 초기화
rm -rf tmp/lancedb/*
rm -f tmp/sessions.db
mkdir -p tmp/{lancedb,uploads,logs}
```

### 12.2 로그 확인

```bash
# 애플리케이션 로그
tail -f tmp/logs/app.log

# 실시간 로그 모니터링
tail -f tmp/logs/app.log | grep ERROR

# 로그 레벨 변경
export LOG_LEVEL=DEBUG
python run_backend.py
```

### 12.3 디버깅 모드

```bash
# 디버그 모드로 실행
python run_backend.py --debug

# 상세 로깅 활성화
export LOG_LEVEL=DEBUG
export PYTHONPATH=$PWD
python -m backend.app.main
```

---

## 13. 테스트 체크리스트

### 13.1 설치 확인 체크리스트

- [ ] Python 3.11+ 설치됨
- [ ] 가상환경 생성 및 활성화됨
- [ ] 모든 의존성 설치됨
- [ ] 환경 변수 설정됨
- [ ] 디렉토리 구조 생성됨
- [ ] 환경 검증 통과

### 13.2 백엔드 테스트 체크리스트

- [ ] 서버 정상 시작
- [ ] 헬스체크 API 응답
- [ ] API 문서 접근 가능
- [ ] 지식베이스 통계 API 동작
- [ ] 세션 관리 API 동작
- [ ] 에러 처리 정상 동작

### 13.3 UI 테스트 체크리스트

- [ ] AGUIApp UI 접근 가능
- [ ] 웹 대시보드 접근 가능
- [ ] 백엔드 연결 상태 확인
- [ ] 문서 업로드 기능 동작
- [ ] 채팅 인터페이스 동작
- [ ] 실시간 스트리밍 동작

### 13.4 CLI 테스트 체크리스트

- [ ] CLI 모드 시작 가능
- [ ] 모든 명령어 동작
- [ ] 파일 업로드 기능
- [ ] URL 추가 기능
- [ ] 프로바이더 전환 기능
- [ ] 추론 모드 전환 기능

### 13.5 통합 테스트 체크리스트

- [ ] 전체 워크플로 완료
- [ ] 멀티 프로바이더 전환
- [ ] 에러 처리 검증
- [ ] 성능 요구사항 충족
- [ ] Docker 환경 동작
- [ ] 로그 시스템 동작

---

## 14. 다음 단계

테스트가 완료되면 다음 단계를 진행할 수 있습니다:

1. **프로덕션 배포**
   - Kubernetes 클러스터 설정
   - 모니터링 시스템 구축
   - 백업 및 복구 시스템 설정

2. **고급 기능 활용**
   - 멀티모달 문서 처리
   - 고급 RAG 기법 적용
   - 실시간 협업 기능 구현

3. **커스터마이징**
   - 사용자 정의 에이전트 개발
   - 커스텀 LLM 프로바이더 추가
   - 특화된 UI 컴포넌트 개발

---

**문서 버전**: v1.0  
**최종 업데이트**: 2024년 12월  
**테스트 환경**: macOS 14+ (Sonoma), Python 3.11+  
**예상 소요 시간**: 30-60분 (API 키 설정 포함)

이 가이드를 따라 진행하면 Enterprise RAG System을 완전히 설치하고 모든 기능을 테스트할 수 있습니다. 문제가 발생하면 문제 해결 섹션을 참조하거나 로그를 확인하여 디버깅하세요. 