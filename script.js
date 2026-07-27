const DATA_PATH = "./vms_results.json";

const COLOR_MAP = {
  white: "#F7F7F7",
  yellow: "#FFD43B",
  red: "#FF4B4B",
  green: "#46D369",
  orange: "#FFA94D",
  gray: "#A8A8A8",
  blue: "#74C0FC",
};

let allResults = [];
let activeVmsId = null;

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value === undefined || value === null ? "" : String(value);
  return div.innerHTML;
}

async function loadResults() {
  const response = await fetch(DATA_PATH, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`가상데이터를 불러오지 못했습니다: HTTP ${response.status}`);
  }
  const data = await response.json();
  if (!Array.isArray(data)) {
    throw new Error("결과 데이터는 리스트 형식이어야 합니다.");
  }
  return data;
}

function listVmsOptions(results) {
  const labelsById = new Map();
  for (const result of results) {
    const vmsId = result.vms_id;
    if (!vmsId || labelsById.has(vmsId)) continue;
    labelsById.set(vmsId, `${result.vms_name ?? vmsId} (${result.vms_size ?? "-"})`);
  }
  return Array.from(labelsById, ([vmsId, label]) => ({ vmsId, label }));
}

function getLatestResult(results, vmsId) {
  const candidates = results.filter((result) => result.vms_id === vmsId);
  if (candidates.length === 0) return null;
  return candidates.reduce((latest, result) =>
    (result.generated_at ?? "") > (latest.generated_at ?? "") ? result : latest
  );
}

function renderStatusBadge(status) {
  const label = escapeHtml(status?.label ?? "AI 상태 확인 불가");
  document.getElementById("status-badge").innerHTML =
    `<div class="status-badge"><span class="status-dot"></span>${label}</div>`;
}

function renderMessageLine(segments) {
  return segments
    .map((segment) => {
      const text = escapeHtml(segment.text ?? "");
      const color = COLOR_MAP[String(segment.color ?? "white").toLowerCase()] ?? COLOR_MAP.white;
      return `<span style="color:${color};">${text}</span>`;
    })
    .join("");
}

function renderVmsPreview(result) {
  const header = escapeHtml(result.header_text ?? "(AI 주차정보)");
  const lines = (result.message_lines ?? [])
    .map((line) => `<div class="vms-line">${renderMessageLine(line)}</div>`)
    .join("");
  document.getElementById("vms-screen").innerHTML =
    `<div class="vms-header">${header}</div>${lines}`;
}

function renderMessageInfo(result) {
  const fields = {
    "상황 분류": `${result.situation_code ?? "-"} (${result.situation_name ?? "-"})`,
    "규격": `${result.vms_size ?? "-"} (${result.line_count ?? "-"}줄)`,
    "예측 이용률": `${result.predicted_occupancy ?? "-"}%`,
    "생성 시각": result.generated_at ?? "-",
    "예측 기준": result.prediction_base_time ?? "-",
    "예측 대상": result.prediction_target_time ?? "-",
  };
  const rows = Object.entries(fields)
    .map(
      ([label, value]) =>
        `<div class="info-row"><span class="info-label">${escapeHtml(label)}</span> · ${escapeHtml(value)}</div>`
    )
    .join("");
  document.getElementById("message-info").innerHTML =
    `<div class="info-card"><div class="info-card-title">문구 정보</div>${rows}</div>`;
}

function renderSafetyChecks(result) {
  const rows = (result.safety_checks ?? [])
    .map((check) => {
      const passed = Boolean(check.passed);
      const cssClass = passed ? "check-pass" : "check-fail";
      const icon = passed ? "✓" : "✕";
      const label = escapeHtml(check.label ?? "검사 항목");
      const detail = escapeHtml(check.detail ?? "");
      let html = `<div class="info-row ${cssClass}">${icon} ${label}</div>`;
      if (detail) html += `<div class="check-detail">${detail}</div>`;
      return html;
    })
    .join("");
  document.getElementById("safety-checks").innerHTML =
    `<div class="info-card"><div class="info-card-title">안전 검사</div>${rows}</div>`;
}

function renderWarningBanner(result) {
  const hasFailure = (result.safety_checks ?? []).some((check) => !check.passed);
  document.getElementById("warning-banner").innerHTML = hasFailure
    ? '<div class="warning-banner">표출 부적합 — 실패한 안전 검사 항목을 확인하십시오.</div>'
    : "";
}

function showError(message) {
  document.getElementById("error-banner").innerHTML =
    `<div class="error-banner">${escapeHtml(message)}</div>`;
}

let vmsOptions = [];

function renderActive() {
  const result = getLatestResult(allResults, activeVmsId);
  if (!result) {
    document.getElementById("vms-screen").innerHTML = "";
    document.getElementById("message-info").innerHTML = "";
    document.getElementById("safety-checks").innerHTML = "";
    document.getElementById("warning-banner").innerHTML = "";
    showError("선택한 VMS의 최신 결과가 없습니다.");
    return;
  }
  showError("");
  renderWarningBanner(result);
  renderVmsPreview(result);
  renderMessageInfo(result);
  renderSafetyChecks(result);

  const activeLabel = escapeHtml(
    vmsOptions.find((option) => option.vmsId === activeVmsId)?.label ?? activeVmsId
  );
  const generatedAt = escapeHtml(result.generated_at ?? "-");
  document.getElementById("result-time").innerHTML =
    `현재 조회 결과: ${activeLabel} · 생성 ${generatedAt}`;
}

async function init() {
  let results;
  try {
    results = await loadResults();
  } catch (err) {
    showError(err.message);
    return;
  }

  vmsOptions = listVmsOptions(results);
  if (vmsOptions.length === 0) {
    showError("조회할 VMS 결과가 없습니다.");
    return;
  }

  allResults = results;
  renderStatusBadge(results[0].system_status ?? {});

  const select = document.getElementById("vms-select");
  select.innerHTML = vmsOptions
    .map((option) => `<option value="${escapeHtml(option.vmsId)}">${escapeHtml(option.label)}</option>`)
    .join("");

  activeVmsId = vmsOptions[0].vmsId;
  select.value = activeVmsId;
  renderActive();

  document.getElementById("query-btn").addEventListener("click", () => {
    activeVmsId = select.value;
    renderActive();
  });
}

document.addEventListener("DOMContentLoaded", init);
