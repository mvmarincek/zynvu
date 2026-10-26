"use strict";
const $ = (id) => document.getElementById(id);
const icon = (name) => `<svg aria-hidden="true"><use href="#i-${name}"/></svg>`;
const escapeHTML = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (char) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        char
      ],
  );
const state = {
  hardware: null,
  catalog: [],
  blueprint: null,
  report: "",
  capabilities: new Set(["conversation"]),
  capsDirty: false,
  advanced: {},
  selected: "balanced",
  busy: false,
  stale: false,
};
const session = document.querySelector('meta[name="zynvu-session"]').content;
const labels = {
  conversation: "Conversa",
  coding: "Código",
  vision: "Visão",
  asr: "Transcrição",
  tts: "Síntese de voz",
  memory: "Memória",
  mcp: "MCP",
  decision: "Decisão",
};
const profiles = {
  balanced: {
    title: "Equilibrada",
    tag: "EQUILÍBRIO",
    description: "Um ponto de partida entre capacidade e uso de memória.",
  },
  fastest: {
    title: "Mais leve",
    tag: "MENOR CARGA",
    description: "Prioriza a combinação com a menor estimativa de RAM.",
  },
  highest_quality: {
    title: "Maior capacidade",
    tag: "MODELOS MAIORES",
    description: "Prioriza tamanho de modelo dentro dos limites da máquina.",
  },
};
let toastTimer;
function toast(message) {
  $("toast").textContent = message;
  $("toast").hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    $("toast").hidden = true;
  }, 4200);
}
function status(message, type = "") {
  $("status").textContent = message;
  $("status").className = `status-message ${type}`;
  $("status").hidden = !message;
}
async function api(path, payload) {
  let response;
  try {
    response = await fetch(`/ui/${path}`, {
      method: payload === undefined ? "GET" : "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Zynvu-Session": session,
      },
      ...(payload === undefined ? {} : { body: JSON.stringify(payload) }),
      signal: AbortSignal.timeout(35000),
    });
  } catch (error) {
    throw new Error(
      error.name === "TimeoutError"
        ? "A análise demorou mais que o esperado. Tente novamente."
        : "Não foi possível conectar ao Studio. Confira se o serviço local está aberto.",
    );
  }
  const data = await response.json();
  if (!response.ok)
    throw new Error(
      data.error || "Não foi possível concluir. Tente novamente.",
    );
  return data;
}
function showView(name, scroll = true) {
  if (!["studio", "catalog", "blueprint"].includes(name)) name = "studio";
  document.querySelectorAll(".view").forEach((view) => {
    const active = view.id === `view-${name}`;
    view.hidden = !active;
    view.classList.toggle("active", active);
  });
  document.querySelectorAll("[data-view]").forEach((button) => {
    const active = button.dataset.view === name;
    button.classList.toggle("active", active);
    if (active) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });
  $("breadcrumb-current").textContent = {
    studio: "STUDIO",
    catalog: "CATÁLOGO",
    blueprint: "BLUEPRINT",
  }[name];
  history.replaceState(null, "", `#${name}`);
  if (scroll) window.scrollTo({ top: 0, behavior: "instant" });
}
function setBusy(busy) {
  state.busy = busy;
  for (const id of [
    "generate",
    "diagnose",
    "suggest",
    "advanced",
    "goal",
    "context",
    "concurrent",
  ])
    $(id).disabled = busy;
  document.querySelectorAll(".capability,.preset").forEach((button) => {
    button.disabled = busy;
  });
  $("generate").querySelector("span").textContent = busy
    ? "Analisando sua arquitetura…"
    : "Criar minha arquitetura";
}
function markStale() {
  if (!state.blueprint) return;
  state.stale = true;
  $("blueprint-stale").hidden = false;
  status(
    "Você ajustou o briefing. Gere novamente para atualizar os resultados.",
  );
}
function renderCapabilities() {
  document.querySelectorAll("[data-capability]").forEach((button) => {
    const selected = state.capabilities.has(button.dataset.capability);
    button.classList.toggle("selected", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
  const notes = [];
  if (
    state.capabilities.has("vision") ||
    state.capabilities.has("asr") ||
    state.capabilities.has("tts")
  )
    notes.push(
      "Visão e voz ainda não têm candidatos: a análise indicará essa limitação.",
    );
  if (state.capabilities.has("memory") || state.capabilities.has("mcp"))
    notes.push(
      "Memória e MCP entram como plano; sua execução chega na Fase 2.",
    );
  $("capability-note").textContent =
    notes.join(" ") || "Conversa e código têm modelos no catálogo atual.";
}
function updateCount() {
  $("char-count").textContent =
    `${$("goal").value.length.toLocaleString("pt-BR")} / 10.000`;
}
async function suggest() {
  const goal = $("goal").value.trim();
  if (!goal)
    throw new Error(
      "Conte sua ideia primeiro. Ou escolha um dos exemplos abaixo.",
    );
  const parsed = await api("parse", { goal });
  state.capabilities = new Set(parsed.capabilities);
  state.capsDirty = false;
  renderCapabilities();
  return parsed;
}
async function getRequirements() {
  const goal = $("goal").value.trim();
  if (!goal) {
    $("goal").focus();
    throw new Error(
      "O primeiro passo é seu: descreva o agente que quer construir.",
    );
  }
  const parsed = await api("parse", { goal });
  if (!state.capsDirty) {
    state.capabilities = new Set(parsed.capabilities);
    renderCapabilities();
  }
  if (!state.capabilities.size)
    throw new Error("Selecione pelo menos uma capacidade para seu agente.");
  return {
    ...parsed,
    ...state.advanced,
    user_goal: goal,
    capabilities: [...state.capabilities],
    context_tokens: Number($("context").value),
    concurrent: $("concurrent").value === "true",
  };
}
async function diagnoseHardware() {
  const hardware = await api("hardware", {});
  state.hardware = hardware;
  $("hw-cpu").textContent =
    hardware.cpu === "unknown" ? "Processador não identificado" : hardware.cpu;
  $("hw-cpu").title = hardware.cpu;
  $("hw-os").textContent = `${hardware.os} · ${hardware.architecture}`;
  $("hw-ram").textContent =
    `${hardware.ram_gb.toLocaleString("pt-BR", { maximumFractionDigits: 1 })} GiB`;
  $("hw-available").textContent =
    hardware.available_ram_gb == null
      ? "RAM disponível não medida."
      : `${hardware.available_ram_gb.toLocaleString("pt-BR", { maximumFractionDigits: 1 })} GiB disponíveis agora`;
  $("hw-gpu").textContent = hardware.gpu || "GPU não identificada";
  $("hw-gpu").title = hardware.gpu || "";
  $("hw-gpu-note").textContent =
    hardware.vram_gb == null
      ? "VRAM não medida · análise em CPU"
      : `${hardware.vram_gb} GiB VRAM · análise em CPU`;
  $("diagnose").querySelector("span").textContent = "Atualizar diagnóstico";
  return hardware;
}
function modelName(id) {
  const entry = state.catalog.find((model) => model.id === id);
  return entry ? entry.name.replace("Qwen/", "") : id;
}
function humanizeReason(text) {
  return String(text).replace(
    /\b(conversation|coding|vision|asr|tts)\b/g,
    (role) => labels[role].toLowerCase(),
  );
}
function modelItem(model) {
  return `<li>
    <span>${escapeHTML(labels[model.role] || model.role)}</span>
    <strong>${escapeHTML(modelName(model.catalog_id))}</strong>
  </li>`;
}
function recommendationCard(rec, index, hardware) {
  const profile = profiles[rec.profile];
  const fit = rec.status !== "not_feasible";
  const selected = rec.profile === state.selected;
  const body = fit
    ? `
    <ul class="model-list">${rec.models.map(modelItem).join("")}</ul>
    <div class="memory-value">
      ${Number(rec.estimated_peak_ram_gb).toLocaleString("pt-BR", { maximumFractionDigits: 2 })}
      <small>GiB RAM</small>
    </div>
    <div class="memory-label">Pico estimado, incluindo reserva do sistema</div>
    <meter class="memory-meter" min="0" max="${escapeHTML(hardware.ram_gb)}"
      value="${escapeHTML(rec.estimated_peak_ram_gb)}"
      aria-label="Memória estimada em relação à RAM física"></meter>
  `
    : `<p class="no-fit">${rec.reasons.map((reason) => escapeHTML(humanizeReason(reason))).join("<br>")}</p>`;
  return `<article class="recommendation-card${selected ? " selected" : ""}">
    <div class="recommendation-kicker">
      <span>0${index + 1} / ${profile.tag}</span>
      ${selected ? '<span class="badge green-soft">EM FOCO</span>' : ""}
    </div>
    <h3>${profile.title}</h3>
    <p class="description">${profile.description}</p>
    <div class="badges">
      <span class="badge ${fit ? "outline" : "subtle"}">${fit ? "CANDIDATA" : "SEM COMBINAÇÃO"}</span>
      <span class="badge subtle">CPU · LOCAL</span>
    </div>
    ${body}
    <button class="select-profile" data-profile="${rec.profile}" aria-pressed="${selected}">
      ${selected ? "Visualizando este perfil" : "Explorar este perfil"}
      <span aria-hidden="true">↗</span>
    </button>
  </article>`;
}
function renderResults() {
  const blueprint = state.blueprint;
  $("results").hidden = false;
  $("recommendation-grid").innerHTML = blueprint.recommendations
    .map((rec, index) => recommendationCard(rec, index, blueprint.hardware))
    .join("");
  const chosen = blueprint.recommendations.find(
    (rec) => rec.profile === state.selected,
  );
  const viable = chosen.status !== "not_feasible";
  const title = viable
    ? `Arquitetura ${profiles[state.selected].title.toLowerCase()}`
    : "O catálogo ainda não cobre este plano";
  const description = viable
    ? `${chosen.models.length} modelo(s) · ${blueprint.requirements.context_tokens.toLocaleString("pt-BR")} tokens · ${blueprint.requirements.concurrent ? "carga simultânea" : "troca sequencial"}`
    : "Revise capacidades, contexto e recursos. O Blueprint registra o motivo de cada restrição.";
  $("architecture-summary").innerHTML = `
    <div><h3>${icon("box")} ${title}</h3><p>${description}</p></div>
    <button class="primary-button" id="see-blueprint">Ver Blueprint ${icon("arrow")}</button>`;
  $("see-blueprint").addEventListener("click", () => showView("blueprint"));
  document.querySelectorAll("[data-profile]").forEach((button) =>
    button.addEventListener("click", () => {
      state.selected = button.dataset.profile;
      renderResults();
    }),
  );
  $("warnings-list").replaceChildren(
    ...blueprint.warnings.map((warning) => {
      const item = document.createElement("li");
      item.textContent = warning;
      return item;
    }),
  );
  $("warning-count").textContent = blueprint.warnings.length;
  $("blueprint-empty").hidden = true;
  $("blueprint-content").hidden = false;
  $("blueprint-stale").hidden = !state.stale;
  $("blueprint-dot").hidden = false;
  $("blueprint-json").textContent = JSON.stringify(blueprint, null, 2);
}
function catalogCard(model) {
  const source = new URL(model.source);
  const safeSource = source.protocol === "https:" ? source.href : "#";
  return `<article class="catalog-card">
    <div class="catalog-top">
      <span class="square-icon">${icon(model.roles.includes("coding") ? "code" : "chat")}</span>
      <span class="badge outline">${escapeHTML(model.license.toUpperCase())}</span>
    </div>
    <h2>${escapeHTML(model.name.replace("Qwen/", "").replace("-Instruct", ""))}</h2>
    <p class="catalog-subtitle">${model.roles.map((role) => escapeHTML(labels[role] || role)).join(" · ")} · Instruct</p>
    <dl class="catalog-facts">
      <div><dt>PESOS GGUF</dt><dd>${(model.weight_bytes / 1024 ** 3).toLocaleString("pt-BR", { maximumFractionDigits: 2 })} GiB</dd></div>
      <div><dt>CONTEXTO MÁXIMO</dt><dd>${(model.max_context / 1024).toLocaleString("pt-BR")}K tokens</dd></div>
      <div><dt>QUANTIZAÇÃO</dt><dd>${escapeHTML(model.quantization)}</dd></div>
      <div><dt>RUNTIME</dt><dd>${escapeHTML(model.runtime)}</dd></div>
    </dl>
    <a href="${escapeHTML(safeSource)}" target="_blank" rel="noopener noreferrer">
      Fonte oficial · abre site externo <span>↗</span>
    </a>
  </article>`;
}
function renderCatalog() {
  $("catalog-count").textContent = state.catalog.length;
  $("catalog-summary").textContent =
    `${state.catalog.length} modelos · Conversa e programação`;
  $("catalog-grid").innerHTML = state.catalog.map(catalogCard).join("");
}
function download(content, name, type) {
  if (state.stale)
    toast(
      "Este arquivo reflete a última análise. Gere novamente para incluir seus ajustes.",
    );
  const url = URL.createObjectURL(new Blob([content], { type }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function bind() {
  document
    .querySelectorAll("[data-view]")
    .forEach((button) =>
      button.addEventListener("click", () => showView(button.dataset.view)),
    );
  document.querySelector(".brand").addEventListener("click", (event) => {
    event.preventDefault();
    showView("studio");
  });
  document.querySelector("[data-go-studio]").addEventListener("click", () => {
    showView("studio");
    $("goal").focus();
  });
  $("goal").addEventListener("input", () => {
    updateCount();
    markStale();
  });
  for (const id of ["context", "concurrent"])
    $(id).addEventListener("change", markStale);
  document.querySelectorAll("[data-capability]").forEach((button) =>
    button.addEventListener("click", () => {
      const capability = button.dataset.capability;
      if (state.capabilities.has(capability))
        state.capabilities.delete(capability);
      else state.capabilities.add(capability);
      state.capsDirty = true;
      renderCapabilities();
      markStale();
    }),
  );
  const presets = {
    code: "Quero um assistente local para conversar e ajudar a programar em Python e JavaScript.",
    chat: "Quero um assistente pessoal para conversar e organizar minhas ideias, com privacidade local.",
    docs: "Quero um assistente que converse comigo e lembre dos meus documentos por meio de memória e RAG.",
  };
  document.querySelectorAll("[data-preset]").forEach((button) =>
    button.addEventListener("click", async () => {
      if (state.busy) return;
      setBusy(true);
      $("goal").value = presets[button.dataset.preset];
      state.capsDirty = false;
      updateCount();
      markStale();
      try {
        await suggest();
      } catch (error) {
        status(error.message, "error");
      } finally {
        setBusy(false);
        $("goal").focus();
      }
    }),
  );
  $("suggest").addEventListener("click", async () => {
    if (state.busy) return;
    setBusy(true);
    try {
      await suggest();
      markStale();
      toast("Capacidades sugeridas. Revise e ajuste à sua maneira.");
    } catch (error) {
      status(error.message, "error");
    } finally {
      setBusy(false);
    }
  });
  $("diagnose").addEventListener("click", async () => {
    if (state.busy) return;
    setBusy(true);
    status("Lendo os recursos reais desta máquina…", "loading");
    try {
      await diagnoseHardware();
      markStale();
      status("Hardware atualizado. Tudo pronto para planejar sua arquitetura.");
    } catch (error) {
      status(error.message, "error");
    } finally {
      setBusy(false);
    }
  });
  $("generate").addEventListener("click", async () => {
    if (state.busy) return;
    setBusy(true);
    markStale();
    status("Interpretando seu briefing…", "loading");
    try {
      const requirements = await getRequirements();
      status(
        "Diagnosticando hardware e combinando modelos compatíveis…",
        "loading",
      );
      const hardware = await diagnoseHardware();
      const result = await api("advise", { requirements, hardware });
      state.blueprint = result.blueprint;
      state.report = result.report;
      state.stale = false;
      state.selected = "balanced";
      renderResults();
      const noFit = result.blueprint.recommendations.every(
        (rec) => rec.status === "not_feasible",
      );
      status(
        noFit
          ? "Não encontramos uma combinação completa para estes requisitos. Veja os motivos abaixo."
          : "Sua arquitetura está pronta. Explore os perfis e os detalhes antes de escolher.",
        noFit ? "error" : "",
      );
      $("results").scrollIntoView({
        behavior: matchMedia("(prefers-reduced-motion: reduce)").matches
          ? "instant"
          : "smooth",
        block: "start",
      });
    } catch (error) {
      status(
        error.name === "TimeoutError"
          ? "O diagnóstico demorou mais que o esperado. Tente novamente."
          : error.message,
        "error",
      );
    } finally {
      setBusy(false);
    }
  });
  $("advanced").addEventListener("click", async () => {
    if (state.busy) return;
    setBusy(true);
    try {
      const req = await getRequirements();
      $("requirements-json").value = JSON.stringify(req, null, 2);
      $("dialog-error").hidden = true;
      $("advanced-dialog").showModal();
    } catch (error) {
      status(error.message, "error");
    } finally {
      setBusy(false);
    }
  });
  for (const id of ["close-dialog", "cancel-dialog"])
    $(id).addEventListener("click", () => $("advanced-dialog").close());
  $("save-requirements").addEventListener("click", async () => {
    $("save-requirements").disabled = true;
    try {
      const req = await api(
        "requirements",
        JSON.parse($("requirements-json").value),
      );
      state.advanced = req;
      state.capabilities = new Set(req.capabilities);
      state.capsDirty = true;
      $("goal").value = req.user_goal;
      updateCount();
      if (
        ![...$("context").options].some(
          (option) => Number(option.value) === req.context_tokens,
        )
      ) {
        const option = document.createElement("option");
        option.value = req.context_tokens;
        option.textContent = `${req.context_tokens.toLocaleString("pt-BR")} tokens`;
        $("context").append(option);
      }
      $("context").value = String(req.context_tokens);
      $("concurrent").value = String(req.concurrent);
      renderCapabilities();
      markStale();
      $("advanced-dialog").close();
      toast("Requisitos validados e aplicados.");
    } catch (error) {
      $("dialog-error").textContent =
        error instanceof SyntaxError
          ? "JSON inválido. Confira aspas, vírgulas e chaves."
          : error.message;
      $("dialog-error").hidden = false;
    } finally {
      $("save-requirements").disabled = false;
    }
  });
  $("export-blueprint").addEventListener("click", () => {
    if (state.blueprint)
      download(
        JSON.stringify(state.blueprint, null, 2),
        "zynvu-blueprint.json",
        "application/json;charset=utf-8",
      );
  });
  $("export-report").addEventListener("click", () => {
    if (state.blueprint)
      download(
        state.report,
        "zynvu-arquitetura.md",
        "text/markdown;charset=utf-8",
      );
  });
  $("copy-blueprint").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(
        JSON.stringify(state.blueprint, null, 2),
      );
      toast("Blueprint copiado.");
    } catch {
      toast("A cópia não foi permitida. Use Exportar JSON.");
    }
  });
}
async function init() {
  bind();
  showView(location.hash.slice(1) || "studio", false);
  try {
    const catalog = await api("catalog");
    state.catalog = catalog.entries;
    renderCatalog();
  } catch (error) {
    status(
      "Não foi possível carregar o catálogo local. Reabra o Studio.",
      "error",
    );
    toast(error.message);
  }
}
init();
