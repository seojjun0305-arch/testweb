# 강릉 AI 주차정보 VMS 검수 UI — 가상데이터 버전

이 프로젝트는 실제 AI 모델을 실행하지 않습니다. `sample_data/vms_results.json`에 저장된 가상 VMS 결과를 읽어, 선택한 장비의 최신 문구를 검정색 VMS 미리보기 화면에 표시합니다.

## 폴더 구조

```text
gangneung_vms_streamlit_mock/
├─ app.py
├─ result_service.py
├─ requirements.txt
├─ README.md
├─ .streamlit/
│  └─ config.toml
└─ sample_data/
   └─ vms_results.json
```

## 실행 준비

PowerShell에서 압축을 푼 폴더로 이동합니다.

```powershell
cd "압축을_푼_경로\gangneung_vms_streamlit_mock"
```

가상환경을 생성하고 활성화합니다.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

활성화가 차단되면 현재 PowerShell 창에서만 다음 명령을 실행합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

라이브러리를 설치합니다.

```powershell
pip install -r requirements.txt
```

## UI 실행

```powershell
streamlit run app.py
```

## 화면 사용 방법

1. 드롭다운에서 VMS 장비를 선택합니다.
2. `문구 조회` 버튼을 누릅니다.
3. 선택한 장비의 최신 생성 결과가 표시됩니다.
4. 검정 화면에서 문구와 색상을 확인합니다.
5. 하단에서 상황 분류, 규격, 생성 시각, 예측 대상 시각, 안전 검사 결과를 확인합니다.

`중앙시장 진입부 (4x15)` 결과에는 안전 검사 실패 사례가 포함되어 있습니다.

## 실제 코드와 연결할 때

초기에는 `sample_data/vms_results.json`을 가상 DB처럼 사용합니다. 실제 VMS 문구 생성 코드가 완성되면 같은 JSON 구조로 결과를 저장하거나, `result_service.py`를 Tibero 조회 코드로 교체합니다.

UI의 조회 버튼은 저장된 최신 결과만 읽어야 하며, ST-GCN 재학습·전처리·예측을 다시 실행하지 않습니다.

## 주요 JSON 항목

```text
vms_id                  VMS 장비 ID
vms_name                VMS 위치명
vms_size                장비 규격
generated_at            문구 생성 시각
prediction_base_time    예측 기준 시각
prediction_target_time  예측 대상 시각
predicted_occupancy     예측 이용률
situation_name          여유·혼잡·만차 임박
message_lines           문구와 색상
safety_checks           안전 검사 결과
```

한 줄 안에서 일부 단어만 다른 색상으로 표시할 수 있습니다.

```json
[
  [
    {"text": "중앙시장 제1공영 ", "color": "white"},
    {"text": "현재 점유율 92%", "color": "yellow"}
  ]
]
```

지원 색상은 `white`, `yellow`, `red`, `green`, `orange`, `gray`, `blue`입니다.
