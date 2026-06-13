const queryTemplates = {
  market: [
    "{topic} рынок обзор 2026",
    "{topic} конкуренты цены услуги",
    "{topic} кейсы внедрения результаты",
    "{topic} отзывы клиентов проблемы",
    "{topic} тренды спрос малый бизнес"
  ],
  supplier: [
    "{topic} поставщики рейтинг",
    "{topic} условия цены сравнение",
    "{topic} отзывы риски",
    "{topic} интеграции документация",
    "{topic} альтернативы"
  ],
  trend: [
    "{topic} тренды 2026",
    "{topic} исследования отчет",
    "{topic} статистика рынок",
    "{topic} новые технологии",
    "{topic} прогноз"
  ],
  risk: [
    "{topic} риски",
    "{topic} регулирование требования",
    "{topic} ошибки внедрения",
    "{topic} безопасность данные",
    "{topic} судебная практика"
  ]
};

const seededSources = [
  {
    title: "Отраслевое исследование",
    url: "https://example.com/research",
    summary: "Показывает рост спроса на практическое внедрение ИИ, но отмечает нехватку компетенций и сложность перехода от пилотов к регулярной работе.",
    type: "Исследование",
    reliability: 86,
    fetchedAt: ""
  },
  {
    title: "Сайт конкурента",
    url: "https://example.com/agency",
    summary: "Конкурент продает аудит, пилоты и сопровождение, но слабо показывает KPI и конкретные отраслевые сценарии.",
    type: "Конкурент",
    reliability: 72,
    fetchedAt: ""
  },
  {
    title: "Профильная статья",
    url: "https://example.com/article",
    summary: "Главная боль клиентов: много разговоров про ИИ, мало внедренных процессов, нет владельца изменений и понятного расчета окупаемости.",
    type: "Медиа",
    reliability: 64,
    fetchedAt: ""
  }
];

const form = document.querySelector("#brief-form");
const queryList = document.querySelector("#query-list");
const sourceGrid = document.querySelector("#source-grid");
const addSourceButton = document.querySelector("#add-source");
const analyzeUrlsButton = document.querySelector("#analyze-urls");
const runLiveSearchButton = document.querySelector("#run-live-search");
const serverStatus = document.querySelector("#server-status");
const findings = document.querySelector("#findings");
const risks = document.querySelector("#risks");
const recommendations = document.querySelector("#recommendations");
const score = document.querySelector("#score");
const scoreNote = document.querySelector("#score-note");

let sources = [...seededSources];
let latestQueries = [];
let serverAvailable = location.protocol.startsWith("http");

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function normalizeTopic(topic) {
  return topic
    .replace(/[.,:;!?]/g, " ")
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 10)
    .join(" ");
}

function makeQueries(topic, type) {
  const cleanTopic = normalizeTopic(topic);
  return queryTemplates[type].map((item) => item.replace("{topic}", cleanTopic));
}

function renderQueries(queries) {
  latestQueries = queries;
  queryList.innerHTML = queries.map((query) => `<div class="query-item">${escapeHtml(query)}</div>`).join("");
}

function reliabilityLabel(value) {
  if (value >= 80) return "сильный";
  if (value >= 65) return "средний";
  return "проверить";
}

function renderSources() {
  sourceGrid.innerHTML = sources
    .map((source, index) => `
      <article class="source-card">
        <label>
          Название
          <input data-index="${index}" data-field="title" value="${escapeHtml(source.title)}">
        </label>
        <label>
          URL
          <input data-index="${index}" data-field="url" value="${escapeHtml(source.url)}">
        </label>
        <label>
          Выжимка
          <textarea data-index="${index}" data-field="summary" rows="4">${escapeHtml(source.summary)}</textarea>
        </label>
        <div class="source-meta">
          <span>${escapeHtml(source.type || "Источник")}</span>
          <span class="badge">${source.reliability}% · ${reliabilityLabel(source.reliability)}</span>
        </div>
        ${source.fetchedAt ? `<p class="source-date">Проверено: ${escapeHtml(source.fetchedAt)}</p>` : ""}
      </article>
    `)
    .join("");
}

function updateSourcesFromInputs(event) {
  const target = event.target;
  const index = Number(target.dataset.index);
  const field = target.dataset.field;
  if (!Number.isInteger(index) || !field) return;
  sources[index][field] = target.value;
  renderReport();
}

function extractCommonWords() {
  const stop = new Set(["что", "это", "как", "для", "или", "при", "над", "под", "без", "про", "the", "and", "with"]);
  const words = sources
    .flatMap((source) => `${source.title} ${source.summary}`.toLowerCase().match(/[a-zа-яё0-9-]{4,}/gi) || [])
    .filter((word) => !stop.has(word));
  const counts = new Map();
  words.forEach((word) => counts.set(word, (counts.get(word) || 0) + 1));
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([word]) => word);
}

function summarizeFindings(topic) {
  const strongSources = sources.filter((source) => source.reliability >= 75).length;
  const themes = extractCommonWords();
  return [
    `По теме "${normalizeTopic(topic)}" собрано ${sources.length} источника, из них ${strongSources} выглядят достаточно надежными для первичной аналитики.`,
    themes.length ? `Повторяющиеся темы в источниках: ${themes.join(", ")}.` : "Пока мало текстовых данных для выделения устойчивых тем.",
    "Ключевые выводы нужно подтверждать минимум двумя независимыми источниками, особенно если они влияют на цену, выбор поставщика или стратегическое решение."
  ];
}

function summarizeRisks() {
  const weakSources = sources.filter((source) => source.reliability < 70).length;
  const placeholders = sources.filter((source) => source.url.includes("example.com") || source.url === "https://").length;
  return [
    weakSources > 0 ? `Есть ${weakSources} источника со средней надежностью: их нужно подтверждать вторым независимым источником.` : "Надежность источников выглядит достаточной для первичного бизнес-решения.",
    placeholders > 0 ? `В подборке осталось ${placeholders} демонстрационных или пустых URL, их нельзя использовать в финальном отчете.` : "Все карточки содержат рабочие URL для проверки.",
    "Цены, рейтинги и офферы быстро меняются, поэтому коммерческие выводы нужно обновлять перед отправкой клиенту."
  ];
}

function summarizeRecommendations(type) {
  const byType = {
    market: "Собрать таблицу конкурентов: оффер, цена, ниша, срок пилота, доказательства результата, слабое место.",
    supplier: "Проверить поставщиков по критериям: цена, SLA, безопасность данных, интеграции, отзывы и зависимость от платформы.",
    trend: "Отделить краткосрочные инфоповоды от устойчивых трендов через повторяемость в независимых источниках.",
    risk: "Собрать карту рисков: вероятность, ущерб, контроль, ответственный и правила эскалации."
  };
  return [
    byType[type],
    "Запускать автопоиск по 3-5 разным формулировкам, затем удалять дубли и слабые источники.",
    "Финальный отчет отдавать клиенту в структуре: краткий вывод, таблица источников, сравнение вариантов, рекомендации на 30 дней."
  ];
}

function renderList(element, items) {
  element.innerHTML = items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderReport() {
  const data = new FormData(form);
  const topic = data.get("topic");
  const type = data.get("researchType");
  const avgReliability = Math.round(
    sources.reduce((sum, source) => sum + source.reliability, 0) / sources.length
  );
  const coverageBonus = Math.min(18, sources.length * 3);
  const urlPenalty = sources.some((source) => source.url.includes("example.com")) ? 8 : 0;
  const finalScore = Math.max(15, Math.min(98, Math.round(avgReliability * 0.82 + coverageBonus - urlPenalty)));

  renderList(findings, summarizeFindings(topic));
  renderList(risks, summarizeRisks());
  renderList(recommendations, summarizeRecommendations(type));
  score.textContent = `${finalScore}%`;
  scoreNote.textContent = `Оценка учитывает надежность источников, количество карточек, реальные URL и полноту выводов. Сейчас в подборке ${sources.length} источника.`;
}

function syncPlan() {
  const data = new FormData(form);
  renderQueries(makeQueries(data.get("topic"), data.get("researchType")));
  renderReport();
}

function setStatus(message, isError = false) {
  serverStatus.textContent = message;
  serverStatus.classList.toggle("is-error", isError);
}

async function requestJson(url, options) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || `HTTP ${response.status}`);
  }
  return payload;
}

async function runLiveSearch() {
  if (!serverAvailable) {
    setStatus("Откройте страницу через research-server.js, чтобы включить автопоиск.", true);
    return;
  }

  const data = new FormData(form);
  const depth = data.get("depth");
  const limit = depth === "express" ? 6 : depth === "deep" ? 14 : 10;
  setStatus("Ищу источники в интернете и загружаю страницы...");
  runLiveSearchButton.disabled = true;

  try {
    const payload = await requestJson("/api/research", {
      method: "POST",
      body: JSON.stringify({
        topic: data.get("topic"),
        type: data.get("researchType"),
        queries: latestQueries,
        limit
      })
    });
    sources = payload.sources.length ? payload.sources : sources;
    renderSources();
    renderReport();
    setStatus(`Готово: найдено и проанализировано ${payload.sources.length} источников.`);
  } catch (error) {
    setStatus(`Автопоиск не сработал: ${error.message}`, true);
  } finally {
    runLiveSearchButton.disabled = false;
  }
}

async function analyzeUrls() {
  if (!serverAvailable) {
    setStatus("Анализ URL работает только через локальный сервер.", true);
    return;
  }
  const urls = sources.map((source) => source.url).filter((url) => url.startsWith("http"));
  setStatus("Загружаю и анализирую URL из карточек...");
  analyzeUrlsButton.disabled = true;

  try {
    const payload = await requestJson("/api/analyze-urls", {
      method: "POST",
      body: JSON.stringify({ urls })
    });
    sources = payload.sources.length ? payload.sources : sources;
    renderSources();
    renderReport();
    setStatus(`Готово: обновлено ${payload.sources.length} карточек.`);
  } catch (error) {
    setStatus(`Анализ URL не сработал: ${error.message}`, true);
  } finally {
    analyzeUrlsButton.disabled = false;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  syncPlan();
});

form.addEventListener("input", syncPlan);
sourceGrid.addEventListener("input", updateSourcesFromInputs);
runLiveSearchButton.addEventListener("click", runLiveSearch);
analyzeUrlsButton.addEventListener("click", analyzeUrls);

addSourceButton.addEventListener("click", () => {
  sources.push({
    title: "Новый источник",
    url: "https://",
    summary: "Кратко опишите факт, цифру или наблюдение из источника.",
    type: "Источник",
    reliability: 60,
    fetchedAt: ""
  });
  renderSources();
  renderReport();
});

if (serverAvailable) {
  setStatus("Локальный сервер активен: автопоиск и анализ URL доступны.");
} else {
  setStatus("Страница открыта как файл: ручной режим работает, автопоиск включится через локальный сервер.");
}

syncPlan();
renderSources();
renderReport();
