const messages = [
  {
    title: "Авито 1",
    text: `AI-мониторинг конкурентов, цен и акций для интернет-магазина

Настроим бота, который сам проверяет сайты конкурентов, цены, акции, новые товары и отзывы, а затем формирует короткий отчет для руководителя или маркетолога.

Подходит для интернет-магазинов, локальных брендов, маркетологов и e-commerce проектов.

Что входит в пилот:
- до 10 сайтов или ресурсов;
- сбор информации;
- карточки источников;
- краткая выжимка;
- выводы и рекомендации;
- мини-база знаний до 10 материалов как бонус;
- 1 месяц поддержки.

Срок запуска: 7-10 дней.
Стоимость пилота: 70 000 ₽.
Сопровождение после пилота: 15 000 ₽/мес.

Покажу демо на вашей теме за 15 минут.`
  },
  {
    title: "Авито 2",
    text: `Бот для мониторинга цен и конкурентов

Если вы вручную проверяете цены, акции, карточки товаров и сайты конкурентов, это можно автоматизировать.

Сделаем AI-аналитика, который:
- собирает данные с нужных сайтов;
- выделяет изменения;
- показывает источники;
- делает короткий отчет;
- помогает быстро понять, что изменилось на рынке.

Первый пилот: 70 000 ₽.
Срок: 7-10 дней.
После запуска сопровождение: 15 000 ₽/мес.

Для первого клиента добавим мини-базу знаний до 10 материалов.`
  },
  {
    title: "Telegram/VK",
    text: `Многие интернет-магазины до сих пор мониторят конкурентов вручную: открывают сайты, смотрят цены, акции, карточки товаров, отзывы и потом собирают отчет.

Мы настраиваем AI-мониторинг: бот сам проверяет нужные ресурсы и делает короткий отчет с выводами и ссылками.

Что можно отслеживать:
- цены конкурентов;
- акции;
- новые товары;
- отзывы;
- изменения в карточках;
- новости рынка;
- поставщиков.

Пилот за 7-10 дней: 70 000 ₽.
После запуска сопровождение: 15 000 ₽/мес.

Покажу демо на вашей теме за 15 минут.`
  },
  {
    title: "Мягкое сообщение",
    text: `Здравствуйте. Увидел ваш проект, похоже, вам может быть полезен мониторинг конкурентов и цен. Мы настраиваем AI-бота, который сам проверяет нужные сайты, акции, товары и отзывы, а потом присылает короткий отчет с выводами и ссылками. Могу показать демо на вашей теме за 15 минут?`
  },
  {
    title: "Через боль",
    text: `Здравствуйте. Подскажите, вы сейчас вручную отслеживаете цены, акции или новые товары конкурентов? Мы делаем AI-мониторинг: бот проверяет нужные ресурсы и собирает отчет. Обычно это экономит несколько часов ручной работы в неделю. Могу показать пример?`
  },
  {
    title: "Для маркетолога",
    text: `Здравствуйте. Мы помогаем маркетологам быстрее собирать конкурентный анализ: цены, акции, офферы, отзывы, новые товары. Инструмент сам собирает источники и делает краткий отчет. Хотите покажу демо на вашей нише?`
  },
  {
    title: "Для владельца",
    text: `Здравствуйте. Мы настраиваем AI-аналитика для бизнеса: он сам проверяет сайты конкурентов, цены и отзывы, а руководитель получает короткий отчет с выводами. Первый пилот запускается за 7-10 дней. Могу показать, как это выглядит?`
  },
  {
    title: "Follow-up",
    text: `Здравствуйте. Возвращаюсь к сообщению про AI-мониторинг. Могу бесплатно показать на коротком демо, как бот собирает конкурентов, цены, акции и формирует отчет. Если неактуально - просто напишите, не буду отвлекать.`
  },
  {
    title: "После демо",
    text: `Спасибо за разговор. Как обсудили, пилот можно сделать на ваших ресурсах: до 10 сайтов, отчет по ценам/акциям/отзывам, мини-база знаний до 10 материалов. Срок 7-10 дней, стоимость 70 000 ₽, сопровождение после пилота 15 000 ₽/мес. Прикладываю бриф, чтобы зафиксировать источники и формат отчета.`
  }
];

const starterLeads = Array.from({ length: 50 }, (_, index) => ({
  company: index === 0 ? "Пример: интернет-магазин товаров для дома" : "",
  niche: index === 0 ? "e-commerce" : "",
  website: index === 0 ? "https://example.com" : "",
  contact: index === 0 ? "Маркетолог / владелец" : "",
  monitor: index === 0 ? "цены конкурентов, акции, отзывы" : "",
  status: index === 0 ? "new" : "empty",
  next: index === 0 ? "send_message" : "",
  notes: index === 0 ? "заменить пример реальной компанией" : ""
}));

const messageGrid = document.querySelector("#message-grid");
const leadRows = document.querySelector("#lead-rows");
const addLeadButton = document.querySelector("#add-lead");
const exportCsvButton = document.querySelector("#export-csv");
const resetLeadsButton = document.querySelector("#reset-leads");
const storageKey = "ai-monitor-ecommerce-leads";

function getLeads() {
  try {
    return JSON.parse(localStorage.getItem(storageKey)) || starterLeads;
  } catch {
    return starterLeads;
  }
}

function saveLeads(leads) {
  localStorage.setItem(storageKey, JSON.stringify(leads));
}

let leads = getLeads();

function renderMessages() {
  messageGrid.innerHTML = messages
    .map((message, index) => `
      <article class="message-card">
        <h3>${message.title}</h3>
        <textarea id="message-${index}">${message.text}</textarea>
        <button type="button" data-copy="${index}">Скопировать</button>
      </article>
    `)
    .join("");
}

function renderLeads() {
  leadRows.innerHTML = leads
    .map((lead, index) => `
      <tr>
        <td><input data-index="${index}" data-field="company" value="${escapeAttr(lead.company)}"></td>
        <td><input data-index="${index}" data-field="niche" value="${escapeAttr(lead.niche)}"></td>
        <td><input data-index="${index}" data-field="website" value="${escapeAttr(lead.website)}"></td>
        <td><input data-index="${index}" data-field="contact" value="${escapeAttr(lead.contact)}"></td>
        <td><textarea data-index="${index}" data-field="monitor">${escapeHtml(lead.monitor)}</textarea></td>
        <td>
          <select data-index="${index}" data-field="status">
            ${["empty", "new", "sent", "follow_up", "demo", "proposal", "won", "lost"]
              .map((status) => `<option value="${status}" ${lead.status === status ? "selected" : ""}>${status}</option>`)
              .join("")}
          </select>
        </td>
        <td><input data-index="${index}" data-field="next" value="${escapeAttr(lead.next)}"></td>
        <td><textarea data-index="${index}" data-field="notes">${escapeHtml(lead.notes)}</textarea></td>
      </tr>
    `)
    .join("");
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/"/g, "&quot;");
}

function updateLead(event) {
  const target = event.target;
  const index = Number(target.dataset.index);
  const field = target.dataset.field;
  if (!Number.isInteger(index) || !field) return;
  leads[index][field] = target.value;
  saveLeads(leads);
}

function toCsvValue(value) {
  return `"${String(value || "").replace(/"/g, '""')}"`;
}

function downloadCsv() {
  const header = ["company", "niche", "website", "contact", "what_to_monitor", "status", "next_step", "notes"];
  const rows = leads.map((lead) => [
    lead.company,
    lead.niche,
    lead.website,
    lead.contact,
    lead.monitor,
    lead.status,
    lead.next,
    lead.notes
  ]);
  const csv = [header, ...rows].map((row) => row.map(toCsvValue).join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "ecommerce-leads.csv";
  link.click();
  URL.revokeObjectURL(url);
}

messageGrid.addEventListener("click", async (event) => {
  const index = event.target.dataset.copy;
  if (index === undefined) return;
  const textarea = document.querySelector(`#message-${index}`);
  await navigator.clipboard.writeText(textarea.value);
  event.target.textContent = "Скопировано";
  setTimeout(() => {
    event.target.textContent = "Скопировать";
  }, 1400);
});

leadRows.addEventListener("input", updateLead);
leadRows.addEventListener("change", updateLead);

addLeadButton.addEventListener("click", () => {
  leads.push({ company: "", niche: "", website: "", contact: "", monitor: "", status: "new", next: "", notes: "" });
  saveLeads(leads);
  renderLeads();
});

exportCsvButton.addEventListener("click", downloadCsv);

resetLeadsButton.addEventListener("click", () => {
  leads = starterLeads;
  saveLeads(leads);
  renderLeads();
});

renderMessages();
renderLeads();

