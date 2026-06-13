const http = require("http");
const fs = require("fs");
const path = require("path");

const root = __dirname;
const port = Number(process.env.PORT || 5190);
const timeoutMs = 12000;
const userAgent =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 AIResearchAnalyst/1.0";

const mimeTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".csv": "text/csv; charset=utf-8",
  ".png": "image/png"
};

function sendJson(response, status, payload) {
  response.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store"
  });
  response.end(JSON.stringify(payload, null, 2));
}

function readBody(request) {
  return new Promise((resolve, reject) => {
    let body = "";
    request.on("data", (chunk) => {
      body += chunk;
      if (body.length > 1_000_000) {
        reject(new Error("Слишком большой запрос"));
        request.destroy();
      }
    });
    request.on("end", () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch {
        reject(new Error("Некорректный JSON"));
      }
    });
    request.on("error", reject);
  });
}

function cleanText(value) {
  return String(value || "")
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<noscript[\s\S]*?<\/noscript>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/\s+/g, " ")
    .trim();
}

function extractTag(html, pattern) {
  const match = html.match(pattern);
  return match ? cleanText(match[1]) : "";
}

function extractTitle(html, url) {
  return (
    extractTag(html, /<title[^>]*>([\s\S]*?)<\/title>/i) ||
    extractTag(html, /<h1[^>]*>([\s\S]*?)<\/h1>/i) ||
    new URL(url).hostname
  ).slice(0, 140);
}

function extractDescription(html) {
  return (
    extractTag(html, /<meta[^>]+name=["']description["'][^>]+content=["']([^"']+)["'][^>]*>/i) ||
    extractTag(html, /<meta[^>]+property=["']og:description["'][^>]+content=["']([^"']+)["'][^>]*>/i)
  ).slice(0, 360);
}

function extractMainText(html) {
  const text = cleanText(html);
  return text.slice(0, 2400);
}

function sourceTypeFromUrl(url) {
  const host = new URL(url).hostname.replace(/^www\./, "");
  if (host.includes("gov") || host.includes("edu")) return "Официальный";
  if (host.includes("wikipedia")) return "Справочник";
  if (host.includes("vc.") || host.includes("rb.") || host.includes("forbes")) return "Медиа";
  if (host.includes("habr") || host.includes("medium")) return "Экспертный материал";
  return "Источник";
}

function scoreReliability(url, text) {
  const host = new URL(url).hostname;
  let score = 58;
  if (/\.(gov|edu)(\.|$)/i.test(host)) score += 22;
  if (/\.(ru|com|org|net)$/i.test(host)) score += 5;
  if (/research|report|study|исслед|отчет|аналит/i.test(text)) score += 9;
  if (/\d{4}|%|₽|\$|млн|тыс/i.test(text)) score += 7;
  if (/advert|promo|купить|скидка|лучший/i.test(text)) score -= 8;
  return Math.max(35, Math.min(94, score));
}

function summarizeText(description, text) {
  const source = description || text;
  const sentences = source
    .split(/(?<=[.!?])\s+|(?<=\.)\s+/)
    .map((item) => item.trim())
    .filter((item) => item.length > 35);
  return (sentences.slice(0, 2).join(" ") || source.slice(0, 260)).slice(0, 520);
}

async function fetchText(url) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        "User-Agent": userAgent,
        Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
      }
    });
    const contentType = response.headers.get("content-type") || "";
    const text = await response.text();
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    if (!/text|html|xml|json/i.test(contentType)) throw new Error(`Неподдерживаемый тип ${contentType}`);
    return text;
  } finally {
    clearTimeout(timer);
  }
}

function decodeDuckUrl(value) {
  try {
    const parsed = new URL(value, "https://duckduckgo.com");
    const uddg = parsed.searchParams.get("uddg");
    return uddg ? decodeURIComponent(uddg) : parsed.href;
  } catch {
    return "";
  }
}

function parseSearchResults(html) {
  const results = [];
  const seen = new Set();
  const linkPattern = /<a[^>]+class=["'][^"']*(?:result-link|result__a)[^"']*["'][^>]+href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi;
  let match;
  while ((match = linkPattern.exec(html))) {
    const url = decodeDuckUrl(match[1]);
    if (!url || seen.has(url) || !url.startsWith("http")) continue;
    seen.add(url);
    results.push({ title: cleanText(match[2]), url });
  }

  if (results.length) return results;

  const fallbackPattern = /<a[^>]+href=["'](https?:\/\/[^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi;
  while ((match = fallbackPattern.exec(html))) {
    const url = match[1];
    if (seen.has(url)) continue;
    seen.add(url);
    results.push({ title: cleanText(match[2]), url });
  }
  return results;
}

async function searchWeb(query) {
  const url = `https://duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
  const html = await fetchText(url);
  return parseSearchResults(html).slice(0, 6);
}

async function analyzeUrl(url, fallbackTitle = "") {
  const html = await fetchText(url);
  const title = extractTitle(html, url) || fallbackTitle || new URL(url).hostname;
  const description = extractDescription(html);
  const text = extractMainText(html);
  const summary = summarizeText(description, text);
  return {
    title,
    url,
    summary,
    type: sourceTypeFromUrl(url),
    reliability: scoreReliability(url, `${title} ${description} ${text}`),
    fetchedAt: new Date().toISOString().slice(0, 10)
  };
}

async function handleResearch(request, response) {
  try {
    const body = await readBody(request);
    const queries = Array.isArray(body.queries) && body.queries.length ? body.queries : [body.topic].filter(Boolean);
    const limit = Math.max(3, Math.min(Number(body.limit || 10), 16));
    const candidates = [];
    const seen = new Set();

    for (const query of queries.slice(0, 5)) {
      const results = await searchWeb(query);
      for (const result of results) {
        if (seen.has(result.url)) continue;
        seen.add(result.url);
        candidates.push(result);
        if (candidates.length >= limit) break;
      }
      if (candidates.length >= limit) break;
    }

    const settled = await Promise.allSettled(candidates.map((item) => analyzeUrl(item.url, item.title)));
    const sources = settled
      .filter((item) => item.status === "fulfilled")
      .map((item) => item.value)
      .slice(0, limit);

    sendJson(response, 200, { sources, candidates: candidates.length });
  } catch (error) {
    sendJson(response, 500, { error: error.message });
  }
}

async function handleAnalyzeUrls(request, response) {
  try {
    const body = await readBody(request);
    const urls = [...new Set((body.urls || []).filter((url) => /^https?:\/\//i.test(url)))].slice(0, 16);
    const settled = await Promise.allSettled(urls.map((url) => analyzeUrl(url)));
    const sources = settled
      .filter((item) => item.status === "fulfilled")
      .map((item) => item.value);
    sendJson(response, 200, { sources });
  } catch (error) {
    sendJson(response, 500, { error: error.message });
  }
}

function serveStatic(request, response) {
  const requestUrl = new URL(request.url, `http://127.0.0.1:${port}`);
  if (requestUrl.pathname === "/favicon.ico") {
    response.writeHead(204);
    response.end();
    return;
  }
  const pathname = decodeURIComponent(requestUrl.pathname === "/" ? "/research-assistant.html" : requestUrl.pathname);
  const filePath = path.normalize(path.join(root, pathname));
  if (!filePath.startsWith(root)) {
    response.writeHead(403);
    response.end("Forbidden");
    return;
  }

  fs.readFile(filePath, (error, content) => {
    if (error) {
      response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      response.end("Not found");
      return;
    }
    response.writeHead(200, { "Content-Type": mimeTypes[path.extname(filePath)] || "application/octet-stream" });
    response.end(content);
  });
}

const server = http.createServer((request, response) => {
  if (request.method === "POST" && request.url === "/api/research") {
    handleResearch(request, response);
    return;
  }
  if (request.method === "POST" && request.url === "/api/analyze-urls") {
    handleAnalyzeUrls(request, response);
    return;
  }
  if (request.method === "GET") {
    serveStatic(request, response);
    return;
  }
  response.writeHead(405, { "Content-Type": "text/plain; charset=utf-8" });
  response.end("Method not allowed");
});

server.listen(port, "127.0.0.1", () => {
  console.log(`AI Research Analyst: http://127.0.0.1:${port}/research-assistant.html`);
});
