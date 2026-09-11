"use strict";

if (typeof renderMathInElement === "function") {
  document.querySelectorAll(".question-text").forEach(element => {
    renderMathInElement(element, {
      delimiters: [{ left: "\\(", right: "\\)", display: false }, { left: "\\[", right: "\\]", display: true }],
      throwOnError: false,
      trust: false
    });
  });
}

const filters = [...document.querySelectorAll("[data-filter]")];
const resultRows = [...document.querySelectorAll("tr[data-subset]")];
const contexts = {
  "Challenge62/original": "62 problems · Original images · 744 scoring positions across three models",
  "Hard20/original": "20 problems · Original images · 240 positions already included in Challenge62",
  "Hard20/text_only": "20 problems · No image · 240 additional scoring positions across three models"
};
function selectResults(filter) {
  filters.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.filter === filter)));
  resultRows.forEach(row => { row.hidden = `${row.dataset.subset}/${row.dataset.condition}` !== filter; });
  document.getElementById("results-context").textContent = contexts[filter];
}
filters.forEach(button => button.addEventListener("click", () => selectResults(button.dataset.filter)));
document.documentElement.classList.add("js-ready");
selectResults("Challenge62/original");

document.getElementById("copy-citation").addEventListener("click", async () => {
  const content = document.getElementById("citation-code").textContent;
  const status = document.getElementById("copy-status");
  try {
    await navigator.clipboard.writeText(content);
    status.textContent = "Citation copied.";
  } catch {
    status.textContent = "Select the citation text to copy it, or download the .bib file.";
  }
});

document.querySelectorAll("[data-resource]").forEach(element => {
  const resource = window.graphTheoryResources?.[element.dataset.resource];
  if (!resource?.available) return;
  const url = new URL(resource.url);
  if (url.protocol !== "https:") return;
  const link = document.createElement("a");
  link.href = url.href;
  link.className = "button secondary";
  link.textContent = resource.label;
  element.replaceWith(link);
});
