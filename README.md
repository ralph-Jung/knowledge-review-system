# 🧠 Knowledge Review System

간격 반복(Spaced Repetition) 알고리즘을 활용한 개인 지식 관리 및 복습 시스템

## ✨ 주요 기능

- 📝 **지식 수집**: CLI 또는 inbox.md를 통한 지식 입력
- 🔄 **Notion 동기화**: Notion 데이터베이스와 양방향 동기화
- 🧮 **간격 반복 알고리즘**: SM-2 알고리즘 기반 최적화된 복습 스케줄링
- 📧 **이메일 알림**: 매일 복습할 내용을 자동으로 이메일 발송
- 🤖 **AI 문제 생성**: Gemini API를 활용한 자동 문제 생성
- 📊 **복습 통계**: 학습 진도 및 성과 추적

## 🚀 빠른 시작

### 설치

```bash
git clone https://github.com/ralph-Jung/knowledge-review-system.git
cd knowledge-review-system
pip install -r requirements.txt
```

### 환경 설정

`.env` 파일을 생성하고 필요한 API 키를 설정하세요:

```env
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id
GEMINI_API_KEY=your_gemini_api_key
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
TO_EMAIL=recipient@email.com
```

### 기본 사용법

```bash
# 지식 추가
python cli.py ingest "Python: 리스트 컴프리헨션 #programming"

# inbox.md에서 일괄 추가
python cli.py ingest --from-inbox

# 복습 상태 확인
python cli.py status

# 복습 시작
python cli.py review

# Notion과 동기화
python cli.py notion-sync

# 이메일 발송
python cli.py send-email
```

## 📁 프로젝트 구조

```
knowledge-review-system/
├── cli.py                 # CLI 인터페이스
├── core/                  # 핵심 모듈들
│   ├── ingest.py         # 지식 수집 및 저장
│   ├── spaced_repetition.py # SM-2 알고리즘 구현
│   ├── review_state.py   # 복습 상태 관리
│   ├── notion_sync.py    # Notion 동기화
│   ├── email_sender.py   # 이메일 발송
│   ├── question_generator.py # AI 문제 생성
│   └── feedback.py       # 사용자 피드백 처리
├── knowledge/            # 지식 파일들 (마크다운)
├── templates/            # 이메일 템플릿
├── skills/              # 특수 기능 스크립트들
└── tests/               # 테스트 파일들
```

## 🔄 워크플로우

1. **지식 입력**: CLI나 inbox.md를 통해 새로운 지식 추가
2. **자동 등록**: 새 지식이 복습 시스템에 자동 등록
3. **스케줄링**: SM-2 알고리즘으로 최적의 복습 일정 계산
4. **이메일 알림**: 매일 복습할 내용을 이메일로 발송
5. **복습 수행**: 문제를 풀고 난이도에 따라 피드백 제공
6. **Notion 동기화**: 진도를 Notion 데이터베이스와 동기화

## 🧮 SM-2 알고리즘

이 시스템은 검증된 SM-2 간격 반복 알고리즘을 사용합니다:

- **초기 간격**: 1일, 6일
- **용이성 인수**: 사용자 응답에 따라 동적 조정
- **반복 간격**: 이전 간격 × 용이성 인수로 계산
- **품질 등급**: 0-5 척도 (3 이상에서 통과)

## 🔧 고급 기능

### Notion 통합
- 양방향 동기화로 Notion에서도 지식 관리 가능
- 파일명 기반 중복 방지 시스템
- 자동 메타데이터 업데이트

### AI 문제 생성
- Gemini API를 활용한 맞춤형 문제 생성
- 지식의 복잡도에 따른 문제 난이도 조절
- 다양한 문제 유형 지원

### 이메일 시스템
- HTML 템플릿 기반 깔끔한 이메일 디자인
- 중복 발송 방지
- 복습 통계 포함

## 🤝 기여하기

1. 이 저장소를 포크하세요
2. 기능 브랜치를 생성하세요 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성하세요

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

문제나 제안사항이 있으시면 [이슈](https://github.com/ralph-Jung/knowledge-review-system/issues)를 생성해 주세요.

---

**💡 학습은 반복이다. 스마트하게 반복하자!**