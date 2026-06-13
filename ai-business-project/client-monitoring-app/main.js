const storageKey = "ai-monitor-studio-client-app";

const demoState = {
  sources: [
    {
      name: "Конкурент Север",
      url: "https://example.ru/prices",
      topic: "prices",
      status: "активен",
    },
    {
      name: "Отзывы на маркетплейсе",
      url: "поиск по карточкам категории",
      topic: "reviews",
      status: "активен",
    },
    {
      name: "Каталог поставщиков",
      url: "таблица региональных партнеров",
      topic: "partners",
      status: "проверить",
    },
  ],
  knowledge: [
    "Приоритет: партнеры по ЦФО и Приволжью, у которых есть не только общая почта, но и косвенные контакты через страницы команды, закупок или вакансий.",
    "В отчетах показывать только изменения, которые могут повлиять на цену, ассортимент, сроки доставки или переговорную позицию.",
    "Для руководителя нужен короткий вывод: что произошло, почему важно, что сделать на этой неделе.",
  ],
  reportSeed: 0,
};

const topicLabels = {
  prices: "Цены и акции",
  assortment: "Ассортимент",
  reviews: "Отзывы",
  partners: "Партнеры и контакты",
  tenders: "Тендеры и закупки",
};

const insightLibrary = {
  prices: [
    "У конкурента появилась скидка на ключевую категорию. Это может давить на конверсию в ближайшие 3-5 дней.",
    "В двух источниках замечено изменение условий доставки. Стоит проверить, не влияет ли это на итоговую цену для клиента.",
  ],
  assortment: [
    "Появился новый товарный оффер, который можно использовать как идею для тестовой витрины.",
    "Часть популярных позиций временно скрыта из каталога. Возможен дефицит или смена поставщика.",
  ],
  reviews: [
    "В отзывах чаще встречается запрос на быструю доставку и комплекты. Это можно вынести в рекламный оффер.",
    "Появились жалобы на поддержку после покупки. Есть шанс усилить доверие через гарантию и быстрый ответ.",
  ],
  partners: [
    "Найдено несколько косвенных контактов потенциальных партнеров: страницы команды, закупок и региональных филиалов.",
    "У части партнеров обновились направления работы. Их стоит разделить на прямых поставщиков, интеграторов и информационные площадки.",
  ],
  tenders: [
    "Появились закупки со схожими требованиями. Нужно проверить сроки подачи и повторяющиеся формулировки ТЗ.",
    "В описаниях тендеров повторяется один набор характеристик. Его можно использовать как шаблон квалификации.",
  ],
};

const riskLibrary = [
  "Часть сайтов может блокировать автоматический сбор. Для них нужен резервный режим: RSS, email, ручной URL или таблица.",
  "Если не зафиксировать критерии важности, отчет станет слишком большим и потеряет ценность для руководителя.",
  "Нужна проверка человеком перед коммерческими решениями: ИИ ускоряет сбор и анализ, но не заменяет ответственность.",
];

const recommendationLibrary = [
  "Утвердить список источников и частоту проверки: ежедневно для цен, еженедельно для партнеров и отзывов.",
  "Сделать один шаблон отчета: факт, источник, влияние, действие, ответственный.",
  "После пилота выбрать 2-3 сигнала, которые реально влияют на деньги, и автоматизировать их глубже.",
];

const state = loadState();

const elements = {
  sourcesCount: document.querySelector("#sources-count"),
  alertsCount: document.querySelector("#alerts-count"),
  lastRun: document.querySelector("#last-run"),
  sourceForm: document.querySelector("#source-form"),
  sourceList: document.querySelector("#source-list"),
  knowledgeForm: document.querySelector("#knowledge-form"),
  knowledgeList: document.querySelector("#knowledge-list"),
  insightList: document.querySelector("#insight-list"),
  riskList: document.querySelector("#risk-list"),
  recommendationList: document.querySelector("#recommendation-list"),
  runAnalysis: document.querySelector("#run-analysis"),
  copyReport: document.querySelector("#copy-report"),
  resetDemo: document.querySelector("#reset-demo"),
  progressBar: document.querySelector("#progress-bar"),
  runNote: document.querySelector("#run-note"),
  assistantAnswer: document.querySelector("#assistant-answer"),
  askAssistant: document.querySelector("#ask-assistant"),
  reportDate: document.querySelector("#report-date"),
};

function loadState() {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey));
    if (saved?.sources && saved?.knowledge) return saved;
  } catch {
    localStorage.removeItem(storageKey);
  }
  return structuredClone(demoState);
}

function saveState() {
  localStorage.setItem(storageKey, JSON.stringify(state));
}

function todayLabel() {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date());
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function currentInsights() {
  const insights = [];
  state.sources.forEach((source, index) => {
    const options = insightLibrary[source.topic] || insightLibrary.prices;
    insights.push({
      source,
      text: options[(state.reportSeed + index) % options.length],
      priority: index % 2 === 0 ? "высокий" : "средний",
    });
  });
  return insights;
}

function renderSources() {
  elements.sourceList.innerHTML = "";
  state.sources.forEach((source, index) => {
    const item = document.createElement("article");
    item.className = "source-item";
    item.innerHTML = `
      <strong>${escapeHtml(source.name)}</strong>
      <span>${escapeHtml(source.url)}</span>
      <div class="tag-row">
        <span class="tag">${escapeHtml(topicLabels[source.topic] || "Мониторинг")}</span>
        <span class="tag ${source.status === "проверить" ? "hot" : ""}">${escapeHtml(source.status)}</span>
      </div>
      <button class="secondary" type="button" data-remove-source="${index}">Удалить</button>
    `;
    elements.sourceList.append(item);
  });
}

function renderKnowledge() {
  elements.knowledgeList.innerHTML = "";
  state.knowledge.forEach((note, index) => {
    const item = document.createElement("article");
    item.className = "knowledge-item";
    item.innerHTML = `
      <strong>Правило ${index + 1}</strong>
      <p>${escapeHtml(note)}</p>
      <button class="secondary" type="button" data-remove-note="${index}">Удалить</button>
    `;
    elements.knowledgeList.append(item);
  });
}

function renderReport() {
  const insights = currentInsights();
  elements.insightList.innerHTML = "";
  insights.forEach((insight) => {
    const item = document.createElement("article");
    item.className = "insight-item";
    item.innerHTML = `
      <strong>${escapeHtml(insight.text)}</strong>
      <div class="insight-meta">
        <span>${escapeHtml(insight.source.name)}</span>
        <span>${escapeHtml(topicLabels[insight.source.topic])}</span>
        <span>приоритет: ${escapeHtml(insight.priority)}</span>
      </div>
    `;
    elements.insightList.append(item);
  });

  renderList(elements.riskList, riskLibrary.slice(0, 3));
  renderList(elements.recommendationList, recommendationLibrary.slice(0, 3));
  elements.sourcesCount.textContent = state.sources.length;
  elements.alertsCount.textContent = insights.filter((item) => item.priority === "высокий").length;
  elements.reportDate.textContent = todayLabel();
}

function renderList(target, items) {
  target.innerHTML = "";
  items.forEach((text) => {
    const li = document.createElement("li");
    li.textContent = text;
    target.append(li);
  });
}

function reportMarkdown() {
  const insights = currentInsights();
  return [
    "# Отчет AI Monitor Studio",
    "",
    `Дата: ${todayLabel()}`,
    `Источников: ${state.sources.length}`,
    "",
    "## Важные изменения",
    ...insights.map(
      (item, index) =>
        `${index + 1}. ${item.text} Источник: ${item.source.name}. Приоритет: ${item.priority}.`,
    ),
    "",
    "## Риски",
    ...riskLibrary.map((item) => `- ${item}`),
    "",
    "## Рекомендации",
    ...recommendationLibrary.map((item) => `- ${item}`),
    "",
    "## Контекст из базы знаний",
    ...state.knowledge.map((item) => `- ${item}`),
  ].join("\n");
}

function render() {
  renderSources();
  renderKnowledge();
  renderReport();
}

elements.sourceForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const data = new FormData(elements.sourceForm);
  state.sources.push({
    name: data.get("name").trim(),
    url: data.get("url").trim(),
    topic: data.get("topic"),
    status: "новый",
  });
  elements.sourceForm.reset();
  saveState();
  render();
});

elements.knowledgeForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const note = new FormData(elements.knowledgeForm).get("note").trim();
  if (!note) return;
  state.knowledge.unshift(note);
  elements.knowledgeForm.reset();
  saveState();
  render();
});

elements.sourceList.addEventListener("click", (event) => {
  const index = event.target.dataset.removeSource;
  if (index === undefined) return;
  state.sources.splice(Number(index), 1);
  saveState();
  render();
});

elements.knowledgeList.addEventListener("click", (event) => {
  const index = event.target.dataset.removeNote;
  if (index === undefined) return;
  state.knowledge.splice(Number(index), 1);
  saveState();
  render();
});

elements.runAnalysis.addEventListener("click", () => {
  state.reportSeed += 1;
  saveState();
  elements.progressBar.style.width = "18%";
  elements.runNote.textContent = "Проверяем источники и ищем изменения...";
  setTimeout(() => {
    elements.progressBar.style.width = "62%";
    elements.runNote.textContent = "Собираем факты, риски и рекомендации...";
  }, 450);
  setTimeout(() => {
    elements.progressBar.style.width = "100%";
    elements.runNote.textContent = "Отчет обновлен. В боевой версии здесь будут реальные источники и ссылки.";
    elements.lastRun.textContent = "только что";
    render();
  }, 900);
});

elements.copyReport.addEventListener("click", async () => {
  const text = reportMarkdown();
  try {
    await navigator.clipboard.writeText(text);
    elements.runNote.textContent = "Отчет скопирован. Его можно отправить клиенту или вставить в КП.";
  } catch {
    elements.runNote.textContent = text;
  }
});

elements.askAssistant.addEventListener("click", () => {
  const firstInsight = currentInsights()[0]?.text || "важных изменений пока нет";
  const firstRule = state.knowledge[0] || "сначала нужно добавить правила клиента";
  elements.assistantAnswer.textContent =
    `Главный вывод: ${firstInsight} С учетом правила "${firstRule}" руководителю стоит проверить влияние на цену, сроки и переговорную позицию.`;
});

elements.resetDemo.addEventListener("click", () => {
  const fresh = structuredClone(demoState);
  state.sources = fresh.sources;
  state.knowledge = fresh.knowledge;
  state.reportSeed = 0;
  saveState();
  elements.progressBar.style.width = "0";
  elements.runNote.textContent = "Демо-данные восстановлены.";
  elements.lastRun.textContent = "сегодня";
  render();
});

render();
