const packages = {
  audit: {
    title: "AI-аудит",
    text: "Короткая диагностика бизнеса: процессы, ручные операции, данные, риски и 3 приоритетных сценария внедрения.",
    items: ["3-5 рабочих дней", "карта процессов", "матрица AI-возможностей", "расчет эффекта"]
  },
  pilot: {
    title: "Быстрый пилот",
    text: "Рабочая автоматизация одного процесса: ассистент, промпт-система, база знаний или связка с таблицами и CRM.",
    items: ["10-14 дней", "реальные задачи клиента", "инструкция для команды", "метрики до/после"]
  },
  scale: {
    title: "Внедрение отдела",
    text: "Системное внедрение 3-5 AI-сценариев в отдел продаж, поддержки, маркетинга, документов или операций.",
    items: ["4-8 недель", "регламенты и роли", "обучение сотрудников", "dashboard KPI"]
  }
};

const detail = document.querySelector("#package-detail");
const packageButtons = document.querySelectorAll(".package");

function renderPackage(key) {
  const current = packages[key];
  detail.innerHTML = `
    <h3>${current.title}</h3>
    <p>${current.text}</p>
    <ul>${current.items.map((item) => `<li>${item}</li>`).join("")}</ul>
  `;
}

packageButtons.forEach((button) => {
  button.addEventListener("click", () => {
    packageButtons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    renderPackage(button.dataset.package);
  });
});

const form = document.querySelector("#ai-calc");
const result = document.querySelector("#calc-result");
const automationValue = document.querySelector("#automation-value");

function formatRub(value) {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0
  }).format(value);
}

function calculate() {
  const data = new FormData(form);
  const people = Number(data.get("people"));
  const hours = Number(data.get("hours"));
  const rate = Number(data.get("rate"));
  const automation = Number(data.get("automation")) / 100;
  const weekly = people * hours * rate * automation;
  const monthly = weekly * 4.3;
  automationValue.textContent = `${Math.round(automation * 100)}%`;
  result.textContent = `Оценка экономии: ${formatRub(monthly)} в месяц`;
}

form.addEventListener("input", calculate);
renderPackage("audit");
calculate();

