---
confusion_points:
- HTTPS가 완전히 새로운 프로토콜이라고 오해하는 경우 (HTTP 위에 TLS/SSL 계층이 추가된 것임)
- HTTPS 사용 시 모든 보안 문제가 해결된다고 생각하는 경우 (애플리케이션 계층 보안은 별개)
- TLS/SSL 인증서 발급 비용이 부담스러워 사용을 꺼리는 경우 (무료 인증서도 존재)
- 암호화로 인해 성능 저하가 크다고 오해하는 경우 (최신 하드웨어 및 프로토콜 최적화로 영향 최소화)
created: '2026-03-22'
difficulty: intermediate
source: ingest
tags:
- internet
- encryption
- protocol
- web
- network
- security
title: HTTPS 와 HTTP 차이
---

HTTP(Hypertext Transfer Protocol)는 웹에서 정보를 주고받는 데 사용되는 비암호화 통신 프로토콜입니다. 웹 브라우저가 웹 서버와 통신할 때 데이터를 평문(plain text) 형태로 전송하기 때문에 중간에 가로채기(eavesdropping) 공격에 취약하며, 전송되는 정보의 무결성이나 송신자의 신원을 보장하기 어렵습니다.

반면, HTTPS(Hypertext Transfer Protocol Secure)는 HTTP에 TLS/SSL(Transport Layer Security/Secure Sockets Layer) 프로토콜을 결합하여 보안을 강화한 버전입니다. TLS/SSL은 전송되는 데이터를 암호화하여 기밀성을 보장하고, 디지털 인증서를 통해 서버의 신원을 확인하여 데이터 위변조를 방지함으로써 무결성을 확보합니다. 따라서 사용자 정보, 결제 정보 등 민감한 데이터를 안전하게 주고받을 수 있게 해줍니다.

## Key Concepts

- HTTP (Hypertext Transfer Protocol)
- HTTPS (Hypertext Transfer Protocol Secure)
- TLS/SSL (Transport Layer Security/Secure Sockets Layer)
- 암호화 (Encryption)
- 기밀성 (Confidentiality)
- 무결성 (Integrity)
- 인증 (Authentication)
- 디지털 인증서 (Digital Certificate)
- 포트 80 (HTTP)
- 포트 443 (HTTPS)

## Related Topics

- TCP/IP
- 공개키 기반 구조 (PKI)
- 웹 보안 (Web Security)
- SSL 핸드셰이크 (SSL Handshake)
- 암호 스위트 (Cipher Suites)