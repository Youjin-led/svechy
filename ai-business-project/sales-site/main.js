const form = document.querySelector("#request-form");
const output = document.querySelector("#request-output");

function buildRequest(data) {
  return [
    "Заявка на демо AI Monitor Studio",
    "",
    `Имя: ${data.get("name") || "-"}`,
    `Компания: ${data.get("company") || "-"}`,
    `Контакт: ${data.get("contact") || "-"}`,
    "",
    "Что нужно мониторить:",
    data.get("task") || "-"
  ].join("\n");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(form);
  const request = buildRequest(data);
  output.textContent = `${request}\n\nСкопировано. Отправьте этот текст в Telegram или email.`;
  output.classList.add("is-visible");

  try {
    await navigator.clipboard.writeText(request);
  } catch {
    output.textContent = `${request}\n\nСкопируйте этот текст и отправьте нам в Telegram или email.`;
  }
});

