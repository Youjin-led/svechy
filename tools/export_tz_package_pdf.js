const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer");

const ROOT = path.resolve(__dirname, "..");
const DIR = path.join(ROOT, "чертежи_ТЗ_для_производства");

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function markdownToHtml(md) {
  const lines = md.split(/\r?\n/);
  let html = "";
  let inTable = false;
  let inList = false;

  function closeTable() {
    if (inTable) {
      html += "</tbody></table>";
      inTable = false;
    }
  }
  function closeList() {
    if (inList) {
      html += "</ol>";
      inList = false;
    }
  }

  for (const line of lines) {
    if (/^\|.+\|$/.test(line.trim())) {
      closeList();
      const cells = line.trim().slice(1, -1).split("|").map((c) => c.trim());
      if (cells.every((c) => /^:?-{3,}:?$/.test(c))) continue;
      if (!inTable) {
        html += "<table><tbody>";
        inTable = true;
      }
      html += "<tr>" + cells.map((c) => `<td>${escapeHtml(c)}</td>`).join("") + "</tr>";
      continue;
    }
    closeTable();
    if (/^\d+\.\s+/.test(line)) {
      if (!inList) {
        html += "<ol>";
        inList = true;
      }
      html += `<li>${escapeHtml(line.replace(/^\d+\.\s+/, ""))}</li>`;
      continue;
    }
    closeList();
    if (line.startsWith("# ")) html += `<h1>${escapeHtml(line.slice(2))}</h1>`;
    else if (line.startsWith("## ")) html += `<h2>${escapeHtml(line.slice(3))}</h2>`;
    else if (line.startsWith("### ")) html += `<h3>${escapeHtml(line.slice(4))}</h3>`;
    else if (line.trim() === "") html += "";
    else html += `<p>${escapeHtml(line)}</p>`;
  }
  closeTable();
  closeList();
  return html;
}

function htmlDoc(title, body) {
  return `<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>${escapeHtml(title)}</title>
<style>
  @page { size: A4; margin: 16mm 14mm; }
  body { font-family: Arial, sans-serif; color: #161616; line-height: 1.42; font-size: 11pt; }
  h1 { font-size: 22pt; margin: 0 0 12mm; }
  h2 { font-size: 15pt; margin: 9mm 0 3mm; border-bottom: 1px solid #bbb; padding-bottom: 1.5mm; }
  h3 { font-size: 12pt; margin: 6mm 0 2mm; }
  p { margin: 0 0 3mm; }
  table { width: 100%; border-collapse: collapse; margin: 3mm 0 6mm; page-break-inside: avoid; }
  td { border: 1px solid #888; padding: 2mm; vertical-align: top; }
  tr:first-child td { background: #eee; font-weight: 700; }
  ol { margin: 1mm 0 5mm 7mm; }
  li { margin-bottom: 1.5mm; }
  .notice { border: 2px solid #9b1c1c; padding: 4mm; margin-bottom: 8mm; font-weight: 700; color: #7d1111; }
</style>
</head>
<body>
<div class="notice">Документ является техническим заданием/предпроектом. Это не финальная КД и не комплект файлов для немедленной резки.</div>
${body}
</body>
</html>`;
}

(async () => {
  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();
  const files = [
    "TZ_DLYA_PROIZVODSTVA.md",
    "VOPROSY_KONSTRUKTORU.md",
    "PRIMER_PISMA_V_CEH.md",
  ];
  for (const file of files) {
    const md = fs.readFileSync(path.join(DIR, file), "utf8");
    const html = htmlDoc(file.replace(".md", ""), markdownToHtml(md));
    const htmlName = file.replace(".md", ".html");
    const pdfName = file.replace(".md", ".pdf");
    fs.writeFileSync(path.join(DIR, htmlName), html, "utf8");
    await page.setContent(html, { waitUntil: "load" });
    await page.pdf({
      path: path.join(DIR, pdfName),
      format: "A4",
      printBackground: true,
      margin: { top: "16mm", right: "14mm", bottom: "16mm", left: "14mm" },
    });
  }
  await browser.close();
  console.log("PDF package exported");
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
