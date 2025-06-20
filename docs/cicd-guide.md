# CI/CD 가이드

이 문서는 Enterprise RAG System의 최소화된 CI/CD 프로세스에 대한 가이드입니다.

## 📋 개요

우리의 CI/CD는 **개발 효율성**과 **배포 안정성**의 균형을 맞추도록 설계되었습니다:

- ✅ **자동 린트 & 테스트**: 모든 커밋과 PR에서 코드 품질 검사
- 🎯 **명시적 빌드 & 배포**: 개발자가 의도적으로 요청할 때만 실행
- 🚀 **원클릭 로컬 배포**: 개발 환경에서 즉시 테스트 가능

## 🔄 워크플로우 구조

### 1. 자동 CI (Lint & Test) - `.github/workflows/ci.yml`

**트리거**: 모든 push, PR  
**실행 시간**: ~2-3분  
**목적**: 코드 품질 보장

```yaml
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
```

**실행 단계**:
1. **기본 문법 검사** (flake8)
   - 문법 오류 및 미정의 변수 체크만
   - 핵심적인 코드 오류만 탐지

2. **단위 테스트**
   - 기본 단위 테스트 실행
   - 최대 5개 실패 시 중단

### 2. 수동 빌드 & 배포 - `.github/workflows/build-deploy.yml`

**트리거**: 
- 수동 실행 (GitHub Actions UI)
- 버전 태그 push (`v*`)

**실행 시간**: ~10-15분  
**목적**: 컨테이너 이미지 빌드 및 배포

```yaml
on:
  workflow_dispatch:  # 수동 트리거
    inputs:
      deploy_target:
        type: choice
        options: [development, staging, production]
  push:
    tags: ['v*']  # 버전 태그만
```

**실행 단계**:
1. **Docker 이미지 빌드**
   - Backend 및 UI 컨테이너 빌드
   - GitHub Container Registry에 푸시
   - 캐싱으로 빌드 시간 단축

2. **배포** (수동 트리거 시만)
   - 선택된 환경에 배포
   - 현재는 로그만 출력 (실제 배포 로직 추가 필요)

## 🛠️ 사용법

### 일반적인 개발 워크플로우

1. **코드 작성 후 커밋**
   ```bash
   git add .
   git commit -m "feat: 새로운 기능 추가"
   git push
   ```
   → 자동으로 린트 & 테스트 실행

2. **PR 생성**
   ```bash
   gh pr create --title "새로운 기능" --body "설명"
   ```
   → 자동으로 린트 & 테스트 실행

3. **로컬 테스트**
   ```bash
   # 환경변수 설정
   export OPENAI_API_KEY="your-key"
   
   # 원클릭 배포
   ./deploy.sh
   ```

### 프로덕션 배포

#### 방법 1: 수동 배포 (권장)
1. GitHub Actions 탭 이동
2. "Build & Deploy" 워크플로우 선택
3. "Run workflow" 클릭
4. 배포 환경 선택 (development/staging/production)
5. "Run workflow" 실행

#### 방법 2: 버전 태그 배포
```bash
# 버전 태그 생성 및 푸시
git tag v1.0.0
git push origin v1.0.0
```
→ 자동으로 빌드 & 배포 실행

## 🎯 장점

### ✅ 개발자 친화적
- **빠른 피드백**: 린트/테스트는 2-3분 내 완료
- **불필요한 대기 없음**: 빌드는 필요할 때만 실행
- **로컬 개발 우선**: `./deploy.sh`로 즉시 테스트

### ✅ 안정성 보장
- **코드 품질**: 모든 변경사항이 린트/테스트 통과
- **의도적 배포**: 실수로 배포되지 않음
- **환경 선택**: 배포 전 환경 명시적 선택

### ✅ 리소스 효율성
- **최소 CI 실행 시간**: 불필요한 빌드 제거
- **캐싱 활용**: Docker 빌드 캐시로 시간 단축
- **병렬 처리**: 린트와 테스트 병렬 실행

## 🔧 설정 방법

### 로컬 개발 환경 설정

1. **환경변수 파일 생성**
   ```bash
   cp config.env.example .env
   # .env 파일에 필요한 값 설정
   ```

2. **의존성 설치**
   ```bash
   pip install flake8 black isort mypy
   ```

3. **pre-commit 훅 설정** (선택사항)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### GitHub 환경 설정

1. **Secrets 설정** (필요한 경우)
   - Repository Settings → Secrets and variables → Actions
   - 배포에 필요한 환경변수 추가

2. **Branch Protection 설정**
   - Settings → Branches → main 브랜치
   - "Require status checks to pass" 체크
   - "lint-and-test" 상태 체크 필수 설정

## 📊 모니터링

### CI/CD 상태 확인
- **GitHub Actions 탭**: 워크플로우 실행 상태
- **PR 상태 체크**: PR에서 바로 테스트 결과 확인
- **배포 로그**: 배포 워크플로우에서 상세 로그 확인

### 성능 메트릭
- **평균 CI 시간**: 2-3분 목표
- **빌드 성공률**: 95% 이상 목표
- **배포 빈도**: 주 1-2회 권장

## 🚨 문제 해결

### 린트 실패 시
```bash
# 로컬에서 기본 문법 검사 실행
flake8 backend/app --select=E9,F63,F7,F82
```

### 테스트 실패 시
```bash
# 로컬에서 테스트 실행
cd backend
python -m pytest ../tests/backend/ -v

# 특정 테스트만 실행
python -m pytest ../tests/backend/test_specific.py -v
```

### 빌드 실패 시
```bash
# 로컬에서 Docker 빌드 테스트
docker build -t test-backend ./backend
docker build -t test-ui ./ui
```

## 🔄 향후 개선 계획

1. **자동 배포 환경 구축**
   - Staging 환경 자동 배포
   - Health check 자동화

2. **테스트 커버리지 개선**
   - 커버리지 리포트 자동 생성
   - 최소 커버리지 요구사항 설정

3. **보안 스캔 추가**
   - 의존성 취약점 스캔
   - 컨테이너 이미지 보안 스캔

4. **성능 모니터링**
   - 빌드 시간 추적
   - 배포 성공률 모니터링

---

## 📞 지원

문제가 발생하면:
1. **GitHub Issues**에 문제 보고
2. **워크플로우 로그** 확인
3. **로컬 환경**에서 재현 시도

이 가이드는 지속적으로 업데이트됩니다. 개선사항이나 질문이 있으면 언제든 제안해주세요! 🚀 