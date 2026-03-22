---
title: "SMTP 프로토콜 + 메일 보내는 방법"
tags:
  - network
  - smtp
  - email
  - protocol
  - dns
  - mx-record
created: "2026-03-22"
updated: "2026-03-22"
source: notion_cs
notion_id: "32bddb9e-dfce-8004-b8b6-db1460c1d9c9"
notion_last_edited_time: "2026-03-22T07:21:00.000Z"
difficulty: "intermediate"
confusion_points:
  - "HTTPS와 SMTP의 역할 구분 (HTTPS는 브라우저-서버 통신, SMTP는 메일서버 간 통신)"
  - "MX 레코드와 A 레코드의 차이 (MX는 메일서버 주소, A는 IP 주소)"
  - "IMAP과 POP의 차이점을 모르는 경우"
  - "DNS 조회 순서를 헷갈리는 경우 (MX 레코드 → A/AAAA 레코드 순)"
---

# SMTP 프로토콜 + 메일 보내는 방법

## 웹 브라우저를 이용해서 메일을 보낼 때

1. 브라우저가 HTTPS로 Gmail 서버에 메일 전송 요청을 보낸다.

2. Gmail 웹 애플리케이션이 요청을 받아 사용자 인증, 요청 형식, 수신자 정보 등을 확인한다.

3. Gmail은 제목, 본문, 첨부파일, 송수신자 정보를 이용해 실제 이메일 메시지를 구성한다.

4. 이 메일을 발송 작업으로 내부 큐 또는 전송 파이프라인에 넘긴다.

5. Gmail의 SMTP 송신 기능이 수신자 도메인을 확인한다.

6. 해당 도메인에 대해 DNS 서버에 MX 레코드를 조회한다.

7. MX 레코드에서 우선순위가 높은 메일 서버를 선택한다.

8. 그 메일 서버의 IP를 알아내기 위해 A 레코드 또는 AAAA 레코드를 조회한다.

9. Gmail이 SMTP로 상대 메일 서버에 메일을 전달한다.

10. 상대 메일 서버는 메일을 저장한다.

11. 수신자는 IMAP 또는 POP으로 그 메일을 읽는다.