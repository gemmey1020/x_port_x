(() => {
  const BOOT = window.OMEGA_BOOTSTRAP || {};
  const state = {
    route: (window.location.hash || "#/skills").replace(/^#\//, "") || "skills",
    health: BOOT,
    skills: null,
    audit: null,
    skillDetail: null,
    memory: null,
    drawerHtml: "",
    confirm: null,
    toasts: [],
  };

  const root = document.getElementById("app-root");
  const drawer = document.getElementById("detail-drawer");
  const drawerScrim = document.getElementById("drawer-scrim");
  const modalLayer = document.getElementById("modal-layer");
  const modalBackdrop = document.getElementById("modal-backdrop");
  const toastStack = document.getElementById("toast-stack");

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function bi(ar, en) {
    return `<span data-lang="ar">${escapeHtml(ar)}</span><span data-lang="en">${escapeHtml(en)}</span>`;
  }

  function codeTag(value) {
    return `<span class="inline-tag code-tag">${escapeHtml(value)}</span>`;
  }

  function inlineTag(ar, en, tone = "") {
    const toneClass = tone ? ` inline-tag--${tone}` : "";
    return `<span class="inline-tag${toneClass}">${bi(ar, en)}</span>`;
  }

  function statusPill(label, tone = "") {
    const toneClass = tone ? ` status-pill--${tone}` : "";
    return `<span class="status-pill${toneClass}">${escapeHtml(label)}</span>`;
  }

  function prettyPath(path) {
    return `<span class="path-label">${escapeHtml(path)}</span>`;
  }

  function emptyState(ar, en) {
    return `<div class="empty-state">${bi(ar, en)}</div>`;
  }

  function jsonRequest(path, options = {}) {
    const init = { ...options };
    init.headers = { ...(init.headers || {}) };
    if (init.body && !(init.body instanceof FormData)) {
      init.headers["Content-Type"] = "application/json";
    }
    return fetch(path, init)
      .then(async (response) => {
        const payload = await response.json();
        if (!response.ok || !payload.ok) {
          const message = payload?.error?.message || `Request failed: ${response.status}`;
          throw new Error(message);
        }
        return payload.data;
      });
  }

  function get(path) {
    return jsonRequest(path);
  }

  function post(path, body = {}) {
    return jsonRequest(path, {
      method: "POST",
      headers: { "X-Omega-Session-Nonce": state.health.session_nonce || "" },
      body: JSON.stringify(body),
    });
  }

  function setRoute(route) {
    state.route = route === "memory" ? "memory" : "skills";
    localStorage.setItem("omega-cockpit:last-route", state.route);
    updateNav();
  }

  function updateNav() {
    document.querySelectorAll(".route-anchor").forEach((anchor) => {
      const href = anchor.getAttribute("href") || "";
      const route = href.replace(/^#\//, "");
      anchor.classList.toggle("is-active", route === state.route);
    });
  }

  function pushToast(message, tone = "success") {
    const id = `${Date.now()}-${Math.random()}`;
    state.toasts = [{ id, message, tone }, ...state.toasts].slice(0, 4);
    renderToasts();
    setTimeout(() => {
      state.toasts = state.toasts.filter((item) => item.id !== id);
      renderToasts();
    }, 3800);
  }

  function renderToasts() {
    toastStack.innerHTML = state.toasts
      .map((toast) => `<div class="toast toast--${escapeHtml(toast.tone)}">${escapeHtml(toast.message)}</div>`)
      .join("");
  }

  function openDrawer(html) {
    state.drawerHtml = html;
    drawer.innerHTML = `<div class="detail-drawer__panel">${html}</div>`;
    drawer.classList.add("is-open");
    drawerScrim.classList.add("is-open");
  }

  function closeDrawer() {
    state.drawerHtml = "";
    drawer.classList.remove("is-open");
    drawerScrim.classList.remove("is-open");
    drawer.innerHTML = "";
  }

  function openConfirm(config) {
    state.confirm = config;
    modalBackdrop.classList.add("is-open");
    modalLayer.classList.add("is-open");
    modalLayer.innerHTML = `
      <div class="modal-card">
        <div class="surface-header">
          <p class="section-kicker">${bi("تأكيد التنفيذ", "Confirm action")}</p>
          <h3>${escapeHtml(config.title)}</h3>
          <p class="muted-copy">${escapeHtml(config.body)}</p>
        </div>
        <div class="action-row">
          <button class="action-button is-danger" data-action="cancel-confirm">${bi("إلغاء", "Cancel")}</button>
          <button class="action-button is-accent" data-action="run-confirm">${bi("نفّذ", "Run")}</button>
        </div>
      </div>
    `;
  }

  function closeConfirm() {
    state.confirm = null;
    modalBackdrop.classList.remove("is-open");
    modalLayer.classList.remove("is-open");
    modalLayer.innerHTML = "";
  }

  function metricRow(items) {
    return `
      <div class="tag-row">
        ${items
          .map((item) => `<span class="inline-tag${item.tone ? ` inline-tag--${item.tone}` : ""}"><strong>${escapeHtml(item.value)}</strong><span>${bi(item.ar, item.en)}</span></span>`)
          .join("")}
      </div>
    `;
  }

  function kvList(items) {
    if (!items.length) return emptyState("لا توجد بيانات.", "No data.");
    return `
      <ul class="fact-list">
        ${items.map(([key, value]) => `<li><span>${escapeHtml(key)}</span><span>${escapeHtml(value)}</span></li>`).join("")}
      </ul>
    `;
  }

  function reportList(items) {
    if (!items.length) return emptyState("لا توجد عناصر.", "No items.");
    return `<ul class="report-list">${items.map((item) => `<li>${item}</li>`).join("")}</ul>`;
  }

  function renderSkillsSurface() {
    if (!state.skills || !state.audit) {
      return emptyState("جاري تحميل المهارات الحية...", "Loading live skills...");
    }

    const skills = state.skills.skills || [];
    const audit = state.audit;
    const summary = audit.summary || {};
    const cards = skills.map((skill) => `
      <article class="surface-card">
        <div class="surface-card__header">
          <div class="stack-column">
            <h3>${escapeHtml(skill.display_name)}</h3>
            ${prettyPath(skill.source_path)}
          </div>
          <div class="tag-row">
            ${codeTag(skill.skill_id)}
            ${codeTag(skill.invoke)}
            ${inlineTag(skill.scope === "system" ? "system" : "top-level", skill.scope, skill.scope === "top-level" ? "accent" : "")}
          </div>
        </div>
        <p class="muted-copy">${escapeHtml(skill.description || "No description.")}</p>
        <div class="tag-row">
          ${skill.has_scripts ? inlineTag("scripts", "scripts") : ""}
          ${skill.has_assets ? inlineTag("assets", "assets") : ""}
          ${skill.has_references ? inlineTag("references", "references") : ""}
          ${skill.doc_status === "stale" ? inlineTag("doc stale", "doc stale", "warn") : ""}
          ${!skill.catalog_present ? inlineTag("خارج الكتالوج", "uncatalogued", "accent") : ""}
        </div>
        <div class="action-row">
          <button class="action-button is-accent" data-action="skill-detail" data-skill-key="${escapeHtml(skill.skill_key)}">${bi("تفاصيل", "Details")}</button>
          <button class="action-button" data-action="copy-text" data-value="${escapeHtml(skill.invoke)}">${bi("انسخ invoke", "Copy invoke")}</button>
        </div>
      </article>
    `).join("");

    return `
      <div class="surface-grid">
        <div class="surface-header">
          <p class="section-kicker">${bi("Skill Review", "Skill Review")}</p>
          <h2>${bi("فحص حي للمصدر الفعلي للمهارات", "Live audit of the actual skill source")}</h2>
          <div class="toolbar-line">
            <button class="action-button" data-action="refresh-skills">${bi("تحديث", "Refresh")}</button>
            <button class="action-button is-accent" data-action="export-surface" data-surface="skills-review">${bi("تصدير HTML", "Export HTML")}</button>
          </div>
        </div>
        <div class="panel-grid">
          <article class="insight-panel">
            <h3>${bi("ملخص مباشر", "Live summary")}</h3>
            ${kvList([
              ["live_total", String(summary.live_total || 0)],
              ["top_level_total", String(summary.top_level_total || 0)],
              ["system_total", String(summary.system_total || 0)],
              ["catalog_total", String(summary.catalog_total || 0)],
            ])}
          </article>
          <article class="insight-panel">
            <h3>${bi("drift summary", "Drift summary")}</h3>
            ${kvList([
              ["missing_from_catalog", String(summary.missing_from_catalog || 0)],
              ["missing_on_disk", String(summary.missing_on_disk || 0)],
              ["metadata_drift", String(summary.metadata_drift || 0)],
              ["stale_docs", String(summary.stale_docs || 0)],
            ])}
          </article>
          <article class="insight-panel">
            <h3>${bi("Open findings", "Open findings")}</h3>
            ${reportList(
              (audit.missing_from_catalog || []).slice(0, 8).map((item) => `${codeTag(item.skill_key)} ${prettyPath(item.source_path)}`)
            )}
          </article>
        </div>
        <div class="card-grid">${cards}</div>
      </div>
    `;
  }

  function memoryActionCard(titleAr, titleEn, bodyHtml, extra = "") {
    return `<article class="surface-card"><div class="surface-header"><h3>${bi(titleAr, titleEn)}</h3>${extra}</div>${bodyHtml}</article>`;
  }

  function renderQueue(queue) {
    const sample = (queue.items || []).slice(0, 6);
    return `
      <article class="surface-card">
        <div class="surface-card__header">
          <div class="stack-column">
            <h3>${bi(queue.label_ar, queue.label_en)}</h3>
            <p class="muted-copy">${bi(queue.description_ar, queue.description_en)}</p>
          </div>
          <div class="tag-row">
            ${codeTag(queue.id)}
            ${statusPill(`items ${queue.total}`)}
            ${queue.actionable_total ? statusPill(`actionable ${queue.actionable_total}`, "accent") : ""}
          </div>
        </div>
        ${sample.length ? `
          <div class="table-list">
            ${sample.map((item) => `
              <div class="table-row">
                <div class="table-row__meta">
                  ${codeTag(item.candidate_id)}
                  ${statusPill(item.normalized_key, item.executable ? "accent" : "")}
                  ${item.age_hours != null ? statusPill(`${item.age_hours}h`) : ""}
                </div>
                <div>${escapeHtml(item.normalized_value)}</div>
              </div>
            `).join("")}
          </div>
        ` : emptyState("لا توجد عناصر.", "No items.")}
        <div class="action-row">
          <button class="action-button" data-action="preview-cleanup">${bi("تحديث الـ preview", "Refresh preview")}</button>
          ${queue.actionable_total ? `<button class="action-button is-danger" data-action="execute-queue" data-queue-id="${escapeHtml(queue.id)}">${bi("تنفيذ التنضيف", "Execute cleanup")}</button>` : ""}
        </div>
      </article>
    `;
  }

  function renderMemorySurface() {
    if (!state.memory) {
      return emptyState("جاري تحميل Surface الميموري...", "Loading memory surface...");
    }

    const doctor = state.memory.doctor;
    const inspect = state.memory.inspect;
    const triage = state.memory.triage;
    const suggest = state.memory.suggest || [];
    const analytics = state.memory.analytics;
    const history = state.memory.history;
    const tokenCost = state.memory.tokenCost;
    const cleanup = state.memory.cleanup;
    const promotable = (triage.promotable || []).slice(0, 8);
    const suggestSample = suggest.slice(0, 8);
    const historyRows = (history.items || []).slice(0, 12).map((item) => `
      <div class="ledger-row">
        <div class="ledger-row__meta">
          ${codeTag(item.event_type)}
          ${codeTag(item.event_id)}
          ${statusPill(item.created_at)}
        </div>
        <div class="action-row">
          ${item.event_id ? `<button class="action-button" data-action="rollback-event" data-event-id="${escapeHtml(item.event_id)}">${bi("Rollback", "Rollback")}</button>` : ""}
        </div>
      </div>
    `).join("");

    return `
      <div class="surface-grid">
        <div class="surface-header">
          <p class="section-kicker">${bi("Memory Control", "Memory Control")}</p>
          <h2>${bi("صفحة التحكم الوحيدة التي تفتح الأدوات", "The only surface that opens tools")}</h2>
          <div class="toolbar-line">
            <button class="action-button" data-action="refresh-memory">${bi("تحديث", "Refresh")}</button>
            <button class="action-button is-accent" data-action="export-surface" data-surface="memory">${bi("تصدير HTML", "Export HTML")}</button>
            <button class="action-button" data-action="backfill-memory">${bi("Backfill", "Backfill")}</button>
          </div>
        </div>

        <div class="panel-grid">
          ${memoryActionCard("Doctor + state", "Doctor + state", kvList([
            ["memory_root", doctor.memory_root],
            ["state_db", doctor.state_db],
            ["resolved_project", doctor.resolved_project || "-"],
            ["issues", String((doctor.issues || []).length)],
          ]))}
          ${memoryActionCard("Triage summary", "Triage summary", kvList([
            ["pending_total", String(triage.summary.pending_total)],
            ["promotable_total", String(triage.summary.promotable_total)],
            ["ephemeral_total", String(triage.summary.ephemeral_total)],
            ["conflict_count", String(triage.summary.conflict_count)],
          ]))}
          ${memoryActionCard("Age + key pressure", "Age + key pressure", `
            ${kvList([
              ["0-24h", String(analytics.age_bands["0-24h"])],
              ["24-72h", String(analytics.age_bands["24-72h"])],
              ["72h+", String(analytics.age_bands["72h+"])],
              ["pending_total", String(analytics.pending_total)],
            ])}
            ${reportList((analytics.pending_by_key || []).map((item) => `${codeTag(item.normalized_key)} ${statusPill(item.count)}`))}
          `)}
        </div>

        <div class="panel-grid">
          ${memoryActionCard("Promotable candidates", "Promotable candidates", promotable.length ? `
            <div class="table-list">
              ${promotable.map((item) => `
                <div class="table-row">
                  <div class="table-row__meta">
                    ${codeTag(item.candidate_id)}
                    ${statusPill(item.normalized_key, "accent")}
                    ${statusPill(item.confidence)}
                  </div>
                  <div>${escapeHtml(item.normalized_value)}</div>
                  <div class="action-row">
                    <button class="action-button is-accent" data-action="promote-candidate" data-candidate-id="${escapeHtml(item.candidate_id)}">${bi("Promote", "Promote")}</button>
                    <button class="action-button is-danger" data-action="reject-candidate" data-candidate-id="${escapeHtml(item.candidate_id)}">${bi("Reject", "Reject")}</button>
                  </div>
                </div>
              `).join("")}
            </div>
          ` : emptyState("لا توجد عناصر promotable حاليًا.", "No promotable items right now."))}
          ${memoryActionCard("Suggest sample", "Suggest sample", suggestSample.length ? `
            <div class="table-list">
              ${suggestSample.map((item) => `
                <div class="table-row">
                  <div class="table-row__meta">
                    ${codeTag(item.candidate_id)}
                    ${statusPill(item.normalized_key)}
                    ${statusPill(item.confidence)}
                  </div>
                  <div>${escapeHtml(typeof item.normalized_value === "string" ? item.normalized_value : JSON.stringify(item.normalized_value))}</div>
                  <div class="action-row">
                    <button class="action-button is-danger" data-action="reject-candidate" data-candidate-id="${escapeHtml(item.candidate_id)}">${bi("Reject", "Reject")}</button>
                  </div>
                </div>
              `).join("")}
            </div>
          ` : emptyState("لا توجد pending candidates.", "No pending candidates."))}
        </div>

        <div class="card-grid">
          ${(cleanup.queues || []).map(renderQueue).join("")}
        </div>

        <div class="panel-grid">
          ${memoryActionCard("Mutation history", "Mutation history", historyRows || emptyState("لا يوجد تاريخ حتى الآن.", "No history yet."))}
          ${memoryActionCard("Token cost", "Token cost", reportList((tokenCost.commands || []).map((item) => {
            if (item.error) return `${codeTag(item.command)} ${escapeHtml(item.error)}`;
            return `${codeTag(item.command)} ${statusPill(`${item.approx_tokens_low}..${item.approx_tokens_high} tokens`, "accent")}`;
          })))}
          ${memoryActionCard("Inspect snapshot", "Inspect snapshot", `
            <pre class="code-panel">${escapeHtml(JSON.stringify({
              user_profile: inspect.user_profile || {},
              project_profile: inspect.project_profile || {},
            }, null, 2))}</pre>
          `)}
        </div>

        <div class="panel-grid">
          ${memoryActionCard("Forget key", "Forget key", `
            <form id="forget-form" class="field-grid">
              <div class="field">
                <label>${bi("النطاق", "Scope")}</label>
                <select name="scope">
                  <option value="global">global</option>
                  <option value="project">project</option>
                </select>
              </div>
              <div class="field">
                <label>${bi("المفتاح", "Key")}</label>
                <input name="key" placeholder="communication.language">
              </div>
              <div class="field">
                <label>${bi("القيمة الاختيارية", "Optional value")}</label>
                <input name="value" placeholder="arabic-egyptian-mixed">
              </div>
              <div class="action-row">
                <button class="action-button is-danger" type="submit">${bi("نفّذ forget", "Run forget")}</button>
              </div>
            </form>
          `)}
          ${memoryActionCard("Manual rollback", "Manual rollback", `
            <form id="rollback-form" class="field-grid">
              <div class="field">
                <label>${bi("event id", "event id")}</label>
                <input name="event_id" placeholder="mem-evt-...">
              </div>
              <div class="action-row">
                <button class="action-button" type="submit">${bi("نفّذ rollback", "Run rollback")}</button>
              </div>
            </form>
          `)}
        </div>
      </div>
    `;
  }

  function render() {
    root.innerHTML = state.route === "memory" ? renderMemorySurface() : renderSkillsSurface();
    updateNav();
  }

  function loadSkills() {
    return Promise.all([get("/api/skills/live"), get("/api/skills/audit")]).then(([skills, audit]) => {
      state.skills = skills;
      state.audit = audit;
      render();
    });
  }

  function loadMemory() {
    return Promise.all([
      get("/api/memory/doctor"),
      get("/api/memory/inspect"),
      get("/api/memory/triage"),
      get("/api/memory/suggest"),
      get("/api/memory/analytics"),
      get("/api/memory/history"),
      get("/api/memory/token-cost"),
      post("/api/memory/cleanup/preview", {}),
    ]).then(([doctor, inspect, triage, suggest, analytics, history, tokenCost, cleanup]) => {
      state.memory = { doctor, inspect, triage, suggest, analytics, history, tokenCost, cleanup };
      render();
    });
  }

  function refreshRoute() {
    if (state.route === "memory") {
      return loadMemory();
    }
    return loadSkills();
  }

  function showSkillDetail(skillKey) {
    get(`/api/skills/${encodeURIComponent(skillKey)}`).then((detail) => {
      state.skillDetail = detail;
      openDrawer(`
        <div class="surface-header">
          <p class="section-kicker">${bi("Skill detail", "Skill detail")}</p>
          <h3>${escapeHtml(detail.display_name)}</h3>
          <div class="action-row">
            <button class="action-button" data-action="close-drawer">${bi("إغلاق", "Close")}</button>
            <button class="action-button" data-action="copy-text" data-value="${escapeHtml(detail.invoke)}">${bi("Copy invoke", "Copy invoke")}</button>
          </div>
        </div>
        ${kvList([
          ["skill_id", detail.skill_id],
          ["skill_key", detail.skill_key],
          ["scope", detail.scope],
          ["source_path", detail.source_path],
          ["invoke", detail.invoke],
          ["catalog_present", String(detail.catalog_present)],
          ["doc_status", detail.doc_status],
          ["mtime", detail.mtime],
        ])}
        <div class="surface-card">
          <h4>${bi("Description", "Description")}</h4>
          <p>${escapeHtml(detail.description || "")}</p>
        </div>
        <div class="surface-card">
          <h4>${bi("Drift flags", "Drift flags")}</h4>
          ${reportList((detail.drift_flags || []).map((item) => escapeHtml(item)))}
        </div>
      `);
    }).catch((error) => pushToast(error.message, "danger"));
  }

  function runConfirmed(title, body, action) {
    openConfirm({
      title,
      body,
      async onConfirm() {
        try {
          closeConfirm();
          await action();
        } catch (error) {
          pushToast(error.message, "danger");
        }
      },
    });
  }

  async function handleExport(surface) {
    const result = await post(`/api/export/${surface}`, {});
    pushToast(`Exported ${result.output_path}`, "success");
  }

  document.addEventListener("click", (event) => {
    const target = event.target.closest("[data-action]");
    if (!target) return;
    const action = target.getAttribute("data-action");

    if (action === "close-drawer") {
      closeDrawer();
      return;
    }
    if (action === "cancel-confirm") {
      closeConfirm();
      return;
    }
    if (action === "run-confirm" && state.confirm) {
      state.confirm.onConfirm();
      return;
    }
    if (action === "skill-detail") {
      showSkillDetail(target.getAttribute("data-skill-key"));
      return;
    }
    if (action === "copy-text") {
      navigator.clipboard.writeText(target.getAttribute("data-value") || "").then(() => {
        pushToast("Copied to clipboard", "success");
      }).catch(() => pushToast("Clipboard copy failed", "danger"));
      return;
    }
    if (action === "refresh-skills") {
      loadSkills().catch((error) => pushToast(error.message, "danger"));
      return;
    }
    if (action === "refresh-memory") {
      loadMemory().catch((error) => pushToast(error.message, "danger"));
      return;
    }
    if (action === "export-surface") {
      handleExport(target.getAttribute("data-surface")).catch((error) => pushToast(error.message, "danger"));
      return;
    }
    if (action === "backfill-memory") {
      runConfirmed("Backfill memory", "سيتم تشغيل backfill على store الحالية.", async () => {
        const result = await post("/api/memory/backfill", {});
        pushToast(`Backfill processed ${result.processed_threads} threads`, "success");
        await loadMemory();
      });
      return;
    }
    if (action === "promote-candidate") {
      const candidateId = target.getAttribute("data-candidate-id");
      runConfirmed(`Promote ${candidateId}`, "سيتم ترقية الـ candidate إلى durable memory.", async () => {
        await post("/api/memory/promote", { candidate_id: candidateId });
        pushToast(`Promoted ${candidateId}`, "success");
        await loadMemory();
      });
      return;
    }
    if (action === "reject-candidate") {
      const candidateId = target.getAttribute("data-candidate-id");
      runConfirmed(`Reject ${candidateId}`, "سيتم رفض الـ candidate وإبقاؤه خارج durable memory.", async () => {
        await post("/api/memory/reject", { candidate_id: candidateId, reason: "omega-cockpit manual reject" });
        pushToast(`Rejected ${candidateId}`, "success");
        await loadMemory();
      });
      return;
    }
    if (action === "execute-queue") {
      const queueId = target.getAttribute("data-queue-id");
      runConfirmed(`Execute cleanup: ${queueId}`, "سيتم تنفيذ cleanup على العناصر actionables فقط.", async () => {
        const result = await post("/api/memory/cleanup/execute", { queue_id: queueId });
        pushToast(`Cleanup ${queueId}: ${result.summary.succeeded} succeeded`, "success");
        await loadMemory();
      });
      return;
    }
    if (action === "preview-cleanup") {
      post("/api/memory/cleanup/preview", {}).then((cleanup) => {
        state.memory.cleanup = cleanup;
        render();
        pushToast("Cleanup preview refreshed", "success");
      }).catch((error) => pushToast(error.message, "danger"));
      return;
    }
    if (action === "rollback-event") {
      const eventId = target.getAttribute("data-event-id");
      runConfirmed(`Rollback ${eventId}`, "سيتم استرجاع الحالة من الـ snapshot المرتبط بهذا الحدث.", async () => {
        await post("/api/memory/rollback", { event_id: eventId });
        pushToast(`Rolled back ${eventId}`, "success");
        await loadMemory();
      });
      return;
    }
  });

  drawerScrim.addEventListener("click", closeDrawer);
  modalBackdrop.addEventListener("click", closeConfirm);

  document.addEventListener("submit", (event) => {
    if (event.target.id === "forget-form") {
      event.preventDefault();
      const form = new FormData(event.target);
      const payload = {
        scope: form.get("scope"),
        key: form.get("key"),
        value: form.get("value") || null,
      };
      runConfirmed(`Forget ${payload.key}`, "سيتم حذف المفتاح من الـ durable profile.", async () => {
        await post("/api/memory/forget", payload);
        pushToast(`Forgot ${payload.key}`, "success");
        await loadMemory();
      });
    }
    if (event.target.id === "rollback-form") {
      event.preventDefault();
      const form = new FormData(event.target);
      const payload = { event_id: form.get("event_id") };
      runConfirmed(`Rollback ${payload.event_id}`, "سيتم تنفيذ rollback للحدث المحدد.", async () => {
        await post("/api/memory/rollback", payload);
        pushToast(`Rolled back ${payload.event_id}`, "success");
        await loadMemory();
      });
    }
  });

  window.addEventListener("hashchange", () => {
    setRoute((window.location.hash || "#/skills").replace(/^#\//, ""));
    refreshRoute().catch((error) => pushToast(error.message, "danger"));
  });

  function boot() {
    const rememberedRoute = localStorage.getItem("omega-cockpit:last-route");
    if (!window.location.hash && rememberedRoute) {
      window.location.hash = `#/${rememberedRoute}`;
      return;
    }
    setRoute(state.route);
    get("/api/health")
      .then((health) => {
        state.health = health;
        return refreshRoute();
      })
      .catch((error) => {
        root.innerHTML = emptyState("فشل تحميل الكوكبيت.", "Failed to load cockpit.");
        pushToast(error.message, "danger");
      });
  }

  boot();
})();
