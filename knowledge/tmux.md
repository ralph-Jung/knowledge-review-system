---
confusion_points:
- tmux가 셸(shell)을 대체하는 것이 아니라 셸을 실행하는 컨테이너 역할을 합니다.
- 처음에는 단축키 시스템에 익숙해지는 데 시간이 걸릴 수 있습니다.
- GNU Screen과 유사하지만, tmux는 현대적인 기능과 설정 유연성에서 차이가 있습니다.
created: '2026-03-22'
difficulty: intermediate
source: ingest
tags:
- tmux
- 터미널
- linux
- 개발도구
- 멀티플렉서
- 시스템관리
- 생산성
- CLI
title: tmux
---

tmux는 터미널 멀티플렉서(Terminal Multiplexer)의 한 종류로, 단일 터미널 화면에서 여러 개의 가상 터미널 세션을 관리할 수 있도록 해주는 강력한 도구입니다. 가장 큰 장점은 SSH 연결이 끊어지거나 터미널 에뮬레이터를 닫더라도 실행 중인 세션이 백그라운드에서 독립적으로 유지된다는 점입니다. 이는 원격 서버에서 장시간 실행되는 작업을 처리하거나, 네트워크 연결이 불안정한 환경에서 작업 연속성을 유지해야 할 때 매우 유용합니다. 사용자는 언제든지 기존 세션에 다시 연결(attach)하여 작업을 중단한 지점부터 이어서 할 수 있습니다.

tmux는 하나의 세션 내에서 여러 개의 '창(window)'을 만들고, 각 창을 다시 여러 개의 '패널(pane)'로 분할할 수 있습니다. 이를 통해 개발자는 코드 편집, 로그 확인, 서버 모니터링 등 다양한 작업을 하나의 터미널 인터페이스 내에서 효율적으로 전환하고 동시에 볼 수 있습니다. 모든 조작은 '접두어 키(prefix key)'와 함께 사용하는 단축키를 통해 이루어지며, 사용자 설정 파일(.tmux.conf)을 통해 키 바인딩, 색상 테마, 상태 바 등 다양한 설정을 커스터마이징할 수 있습니다.

초기 학습 곡선은 존재하지만, tmux에 익숙해지면 CLI 환경에서의 작업 효율성을 혁신적으로 향상시킬 수 있습니다. 특히 서버 관리자, 개발자, DevOps 엔지니어 등 커맨드 라인 인터페이스를 주로 사용하는 전문가들에게는 필수적인 도구로 자리매김하고 있습니다.

## Key Concepts

- 세션 (Session)
- 창 (Window)
- 패널 (Pane)
- 분리 (Detach)
- 연결 (Attach)
- 접두어 키 (Prefix Key)
- 상태 바 (Status Bar)

## Related Topics

- SSH
- Linux CLI
- 셸 스크립팅 (Shell Scripting)
- Vim/Emacs
- GNU Screen
- 원격 개발 (Remote Development)