from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "vms_results.json"


class ResultDataError(Exception):
    pass


def load_results(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ResultDataError("결과 데이터는 리스트 형식이어야 합니다.")
    return data


def list_vms_options(results: list[dict[str, Any]]) -> list[dict[str, str]]:
    labels_by_id: dict[str, str] = {}
    for result in results:
        vms_id = result.get("vms_id")
        if not vms_id or vms_id in labels_by_id:
            continue
        labels_by_id[vms_id] = f'{result.get("vms_name", vms_id)} ({result.get("vms_size", "-")})'
    return [{"vms_id": vms_id, "label": label} for vms_id, label in labels_by_id.items()]


def get_latest_result(results: list[dict[str, Any]], vms_id: str) -> dict[str, Any] | None:
    candidates = [result for result in results if result.get("vms_id") == vms_id]
    if not candidates:
        return None
    return max(candidates, key=lambda result: result.get("generated_at", ""))

COLOR_MAP = {
    "white": "#F7F7F7",
    "yellow": "#FFD43B",
    "red": "#FF4B4B",
    "green": "#46D369",
    "orange": "#FFA94D",
    "gray": "#A8A8A8",
    "blue": "#74C0FC",
}

st.set_page_config(
    page_title="VMS 표출 문구 검수",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #171717; }
        .block-container { max-width: 1180px; padding-top: 1.2rem; padding-bottom: 2.2rem; }
        h1, h2, h3, p, label, div {
            font-family: "Pretendard", "Noto Sans KR", "Malgun Gothic", Arial, sans-serif;
        }
        .page-title { margin: 0; color: #F8F9FA; font-size: 1.65rem; font-weight: 800; }
        .page-subtitle { margin: 0.5rem 0 1.15rem 0; color: #AEB4BC; font-size: 0.95rem; }
        .status-wrap { width: 100%; display: flex; justify-content: flex-end; align-items: center; min-height: 44px; }
        .status-badge {
            display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.5rem 0.8rem;
            color: #53D769; background: #102610; border: 1px solid #183719;
            border-radius: 8px; font-size: 0.88rem; font-weight: 700; white-space: nowrap;
        }
        .status-dot { width: 8px; height: 8px; background: #53D769; border-radius: 50%; }
        .vms-screen {
            margin-top: 0.8rem; margin-bottom: 1.15rem; min-height: 260px; padding: 1.55rem 2rem;
            background: #000; border: 3px solid #343434; border-radius: 12px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }
        .vms-header { margin-bottom: 0.95rem; color: #E9ECEF; font-size: 1.05rem; font-weight: 700; }
        .vms-line {
            width: 100%; margin: 0.22rem 0; text-align: center;
            font-size: clamp(1.45rem, 2.7vw, 2.05rem); line-height: 1.42;
            font-weight: 900; letter-spacing: -0.035em; word-break: keep-all;
        }
        .info-card {
            min-height: 176px; padding: 1rem 1.05rem; background: #2A2A29;
            border: 1px solid #494949; border-radius: 11px;
        }
        .info-card-title { margin-bottom: 0.65rem; color: #D9D2A9; font-size: 0.95rem; font-weight: 800; }
        .info-row { margin: 0.38rem 0; color: #F1F3F5; font-size: 0.92rem; line-height: 1.45; }
        .info-label { color: #DDE1E5; font-weight: 700; }
        .check-pass { color: #48C43F; font-weight: 700; }
        .check-fail { color: #FF5A5F; font-weight: 700; }
        .check-detail { color: #AEB4BC; font-size: 0.79rem; margin-left: 1.2rem; }
        .warning-banner {
            margin-bottom: 0.8rem; padding: 0.72rem 0.9rem; color: #FFD8D8;
            background: #441919; border: 1px solid #762626; border-radius: 8px; font-weight: 800;
        }
        .legend { margin-top: 0.65rem; color: #AEB4BC; font-size: 0.82rem; }
        .legend-dot { display: inline-block; width: 8px; height: 8px; margin: 0 0.28rem 0 0.72rem; border-radius: 50%; }
        .result-time { margin-top: 0.55rem; color: #8E969F; font-size: 0.78rem; text-align: right; }
        div[data-testid="stButton"] button { min-height: 42px; font-weight: 800; }
        @media (max-width: 760px) {
            .status-wrap { justify-content: flex-start; }
            .vms-screen { min-height: 230px; padding: 1.2rem 0.8rem; }
            .vms-line { font-size: 1.35rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def safe_text(value: Any) -> str:
    return html.escape(str(value))


def render_status_badge(status: dict[str, Any]) -> None:
    label = safe_text(status.get("label", "AI 상태 확인 불가"))
    st.markdown(
        f'<div class="status-wrap"><div class="status-badge">'
        f'<span class="status-dot"></span>{label}</div></div>',
        unsafe_allow_html=True,
    )


def render_message_line(segments: list[dict[str, Any]]) -> str:
    parts = []
    for segment in segments:
        text = safe_text(segment.get("text", ""))
        color = COLOR_MAP.get(str(segment.get("color", "white")).lower(), COLOR_MAP["white"])
        parts.append(f'<span style="color:{color};">{text}</span>')
    return "".join(parts)


def render_vms_preview(result: dict[str, Any]) -> None:
    header = safe_text(result.get("header_text", "(AI 주차정보)"))
    lines = "".join(
        f'<div class="vms-line">{render_message_line(line)}</div>'
        for line in result.get("message_lines", [])
    )
    st.markdown(
        f'<div class="vms-screen"><div class="vms-header">{header}</div>{lines}</div>',
        unsafe_allow_html=True,
    )


def render_message_info(result: dict[str, Any]) -> None:
    fields = {
        "상황 분류": f'{result.get("situation_code", "-")} ({result.get("situation_name", "-")})',
        "규격": f'{result.get("vms_size", "-")} ({result.get("line_count", "-")}줄)',
        "예측 이용률": f'{result.get("predicted_occupancy", "-")}%',
        "생성 시각": result.get("generated_at", "-"),
        "예측 기준": result.get("prediction_base_time", "-"),
        "예측 대상": result.get("prediction_target_time", "-"),
    }
    rows = "".join(
        f'<div class="info-row"><span class="info-label">{safe_text(k)}</span> · {safe_text(v)}</div>'
        for k, v in fields.items()
    )
    st.markdown(
        f'<div class="info-card"><div class="info-card-title">문구 정보</div>{rows}</div>',
        unsafe_allow_html=True,
    )


def render_safety_checks(result: dict[str, Any]) -> None:
    rows = []
    for check in result.get("safety_checks", []):
        passed = bool(check.get("passed"))
        css_class = "check-pass" if passed else "check-fail"
        icon = "✓" if passed else "✕"
        label = safe_text(check.get("label", "검사 항목"))
        detail = safe_text(check.get("detail", ""))
        rows.append(f'<div class="info-row {css_class}">{icon} {label}</div>')
        if detail:
            rows.append(f'<div class="check-detail">{detail}</div>')
    st.markdown(
        f'<div class="info-card"><div class="info-card-title">안전 검사</div>{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )


def render_legend() -> None:
    st.markdown(
        '<div class="legend">ⓘ 색상:'
        '<span class="legend-dot" style="background:#F7F7F7;"></span>흰색=일반정보'
        '<span class="legend-dot" style="background:#FFD43B;"></span>노랑=주의·혼잡'
        '<span class="legend-dot" style="background:#FF4B4B;"></span>빨강=경고·만차'
        '<span class="legend-dot" style="background:#46D369;"></span>녹색=여유·진입 가능'
        '</div>',
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_styles()
    try:
        results = load_results(DATA_PATH)
        options = list_vms_options(results)
    except (OSError, ResultDataError, ValueError) as exc:
        st.error(f"가상데이터를 불러오지 못했습니다: {exc}")
        st.stop()

    if not options:
        st.warning("조회할 VMS 결과가 없습니다.")
        st.stop()

    title_col, status_col = st.columns([0.7, 0.3])
    with title_col:
        st.markdown('<div class="page-title">VMS 표출 문구 검수 화면</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subtitle">표출 전 생성된 문구를 확인하는 용도입니다.</div>', unsafe_allow_html=True)
    with status_col:
        render_status_badge(results[0].get("system_status", {}))

    label_to_id = {item["label"]: item["vms_id"] for item in options}
    id_to_label = {item["vms_id"]: item["label"] for item in options}

    if "active_vms_id" not in st.session_state:
        st.session_state.active_vms_id = options[0]["vms_id"]

    selected_index = next(
        (i for i, item in enumerate(options) if item["vms_id"] == st.session_state.active_vms_id),
        0,
    )

    select_col, button_col = st.columns([0.84, 0.16])
    with select_col:
        selected_label = st.selectbox(
            "VMS 장비 선택",
            options=list(label_to_id.keys()),
            index=selected_index,
            label_visibility="collapsed",
        )
    with button_col:
        query_clicked = st.button("↻ 문구 조회", type="primary", use_container_width=True)

    if query_clicked:
        st.session_state.active_vms_id = label_to_id[selected_label]

    active_vms_id = st.session_state.active_vms_id
    result = get_latest_result(results, active_vms_id)
    if result is None:
        st.warning("선택한 VMS의 최신 결과가 없습니다.")
        st.stop()

    if any(not bool(check.get("passed")) for check in result.get("safety_checks", [])):
        st.markdown(
            '<div class="warning-banner">표출 부적합 — 실패한 안전 검사 항목을 확인하십시오.</div>',
            unsafe_allow_html=True,
        )

    render_vms_preview(result)

    info_col, safety_col = st.columns(2)
    with info_col:
        render_message_info(result)
    with safety_col:
        render_safety_checks(result)

    render_legend()
    active_label = safe_text(id_to_label.get(active_vms_id, active_vms_id))
    generated_at = safe_text(result.get("generated_at", "-"))
    st.markdown(
        f'<div class="result-time">현재 조회 결과: {active_label} · 생성 {generated_at}</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
