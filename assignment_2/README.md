# 메디솔브 AI 과제 2 제출

## 소개
이 디렉터리는 메디솔브 AI 백엔드 과제 2(난수 생성 함수 구현) 제출용입니다.  
- 소스 코드: `random_generator.py` (`get_1_or_0`, `get_random`)
- 테스트 코드: `tests/test_random_generator.py`

## 환경 설정
```bash
uv sync
```
`uv` 환경을 사용해 의존성을 설치합니다.

## 테스트 실행
```bash
uv run pytest tests
```
총 11개의 테스트가 실행되며 입력 검증, 재시도 로직, 통계적 균등성을 다룹니다.

## 보고서 및 자료
- 보고서: `report.md`
- 분포 그래프: `artifacts/` 디렉터리

