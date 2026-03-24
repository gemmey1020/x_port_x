(() => {
  const BOOT = window.OMEGA_BOOTSTRAP || {};
  const ROUTES = new Set(["skills", "memory", "artifacts", "runtime"]);
  const state = {
    route: normalizeRoute((window.location.hash || "#/skills").replace(/^#\//, "") || "skills"),
    health: BOOT.health || BOOT,
    session: BOOT.session || null,
    skills: null,
    audit: null,
    memory: null,
    artifacts: null,
    runtime: null,
    runtimeLedger: null,
    modalConfirm: null,
    toasts: [],
    ui: {
      artifactQuery: "",
      artifactFamily: "all",
      artifactSort: "recent",
    },
  };

  const root = document.getElementById("app-root");
  const drawer = document.getElementById("detail-drawer");
  const drawerScrim = document.getElementById("drawer-scrim");
  const modalLayer = document.getElementById("modal-layer");
  const modalBackdrop = document.getElementById("modal-backdrop");
  const toastStack = document.getElementById("toast-stack");
  const sessionLockSlot = document.getElementById("session-lock-slot");
  const sidebarSession = document.getElementById("sidebar-session");
  const sidebarOverview = document.getElementById("sidebar-overview");

  function normalizeRoute(route) {
    return ROUTES.has(route) ? route : "skills";
  }

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

  function prettyPath(path) {
    return `<span class="path-label">${escapeHtml(path)}</span>`;
  }

  function emptyState(ar, en) {
    return `<div class="empty-state">${bi(ar, en)}</div>`;
  }

  function formatDate(value) {
    if (!value) return "-";
    return String(value).replace("T", " ").replace("+00:00", " UTC").replace("Z", " UTC");
  }

  function formatSize(bytes) {
    const size = Number(bytes || 0);
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
    return `${(size / (1024 * 1024)).toFixed(2)} MB`;
  }

  function jsonRequest(path, options = {}) {
    const init = { ...options };
    init.headers = { ...(init.headers || {}) };
    if (init.body && !(init.body instanceof FormData)) {
      init.headers["Content-Type"] = "application/json";
    }
    return fetch(path, init).then(async (response) => {
      const payload = await response.json();
      if (!response.ok || !payload.ok) {
        throw new Error(payload?.error?.message || `Request failed: ${response.status}`);
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
    state.route = normalizeRoute(route);
    localStorage.setItem("omega-cockpit:last-route", state.route);
    updateNav();
  }

  function updateNav() {
    document.querySelectorAll(".route-anchor").forEach((anchor) => {
      const route = (anchor.getAttribute("href") || "").replace(/^#\//, "");
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
    }, 4200);
  }

  function renderToasts() {
    toastStack.innerHTML = state.toasts
      .map((toast) => `<div class="toast toast--${escapeHtml(toast.tone)}">${escapeHtml(toast.message)}</div>`)
      .join("");
  }

  function openDrawer(html) {
    drawer.innerHTML = `<div class="detail-drawer__panel">${html}</div>`;
    drawer.classList.add("is-open");
    drawerScrim.classList.add("is-open");
  }

  function closeDrawer() {
    drawer.classList.remove("is-open");
    drawerScrim.classList.remove("is-open");
    drawer.innerHTML = "";
  }

  function openModal(html) {
    modalBackdrop.classList.add("is-open");
    modalLayer.classList.add("is-open");
    modalLayer.innerHTML = html;
  }

  function closeModal() {
    state.modalConfirm = null;
    modalBackdrop.classList.remove("is-open");
    modalLayer.classList.remove("is-open");
    modalLayer.innerHTML = "";
  }

  function openConfirm({ title, body, onConfirm }) {
    state.modalConfirm = onConfirm;
    openModal(`
      <div class="modal-card">
        <div class="surface-header">
          <p class="section-kicker">${bi("تأكيد التنفيذ", "Confirm action")}</p>
          <h3>${escapeHtml(title)}</h3>
          <p class="muted-copy">${escapeHtml(body)}</p>
        </div>
        <div class="action-row">
          <button class="action-button is-danger" data-action="cancel-modal">${bi("إلغاء", "Cancel")}</button>
          <button class="action-button is-accent" data-action="run-confirm">${bi("نفّذ", "Run")}</button>
        </div>
      </div>
    `);
  }

  function openUnlockModal(message = "") {
    openModal(`
      <div class="modal-card">
        <div class="surface-header">
          <p class="section-kicker">${bi("Admin unlock", "Admin unlock")}</p>
          <h3>${bi("افتح جلسة الكتابة المؤقتة", "Unlock the temporary write session")}</h3>
          <p class="muted-copy">${escapeHtml(message || "Mutating actions need the local admin passcode.")}</p>
        </div>
        <form id="unlock-form" class="field-grid">
          <div class="field">
            <label>${bi("كلمة المرور المحلية", "Local passcode")}</label>
            <input type="password" name="passcode" autocomplete="current-password" required>
          </div>
          <div class="action-row">
            <button class="action-button is-danger" type="button" data-action="cancel-modal">${bi("إلغاء", "Cancel")}</button>
            <button class="action-button is-accent" type="submit">${bi("افتح الجلسة", "Unlock session")}</button>
          </div>
        </form>
      </div>
    `);
  }

  function passcodeConfigured() {
    return Boolean(state.session && state.session.passcode_configured);
  }

  function canMutate() {
    return Boolean(state.session && state.session.writes_available);
  }

  function mutationDisabledAttr() {
    return passcodeConfigured() ? "" : " disabled";
  }

  function ensureMutationAccess() {
    if (!passcodeConfigured()) {
      pushToast("Admin passcode is not configured. Writes are disabled.", "danger");
      return false;
    }
    if (!canMutate()) {
      openUnlockModal("الأفعال التنفيذية تحتاج فتح session محلية مؤقتة قبل المتابعة.");
      return false;
    }
    return true;
  }

  function kvList(items) {
    if (!items.length) return emptyState("لا توجد بيانات.", "No data.");
    return `<ul class="fact-list">${items.map(([key, value]) => `<li><span>${escapeHtml(key)}</span><span>${escapeHtml(value)}</span></li>`).join("")}</ul>`;
  }

  function reportList(items, emptyAr = "لا توجد عناصر.", emptyEn = "No items.") {
    if (!items.length) return emptyState(emptyAr, emptyEn);
    return `<ul class="report-list">${items.map((item) => `<li>${item}</li>`).join("")}</ul>`;
  }

  function summaryCard(value, ar, en) {
    return `
      <article class="summary-panel">
        <div class="summary-panel__value">${escapeHtml(value)}</div>
        <div class="summary-panel__label">${bi(ar, en)}</div>
      </article>
    `;
  }

  function surfaceShell({ kickerAr, kickerEn, titleAr, titleEn, descAr, descEn, actionsHtml = "", summaryHtml = "", contentHtml = "" }) {
    return `
      <section class="route-shell">
        <div class="route-shell__head">
          <div class="route-shell__intro">
            <p class="section-kicker">${bi(kickerAr, kickerEn)}</p>
            <h2>${bi(titleAr, titleEn)}</h2>
            <p class="muted-copy">${bi(descAr, descEn)}</p>
          </div>
          <div class="route-shell__actions">${actionsHtml}</div>
        </div>
        ${summaryHtml ? `<div class="summary-band">${summaryHtml}</div>` : ""}
        ${contentHtml}
      </section>
    `;
  }

  function renderTopSessionSlot() {
    if (!sessionLockSlot || !state.session) return;
    const toneClass = !passcodeConfigured() ? " lock-chip--disabled" : canMutate() ? " lock-chip--armed" : " lock-chip--locked";
    const label = !passcodeConfigured()
      ? bi("passcode غير مضبوطة", "Passcode missing")
      : canMutate()
        ? bi("الجلسة مفتوحة", "Session armed")
        : bi("الجلسة مقفولة", "Session locked");
    const actionButton = !passcodeConfigured()
      ? `<button class="action-button" disabled>${bi("الكتابة معطلة", "Writes disabled")}</button>`
      : canMutate()
        ? `<button class="action-button is-danger" data-action="lock-session">${bi("اقفل الجلسة", "Lock session")}</button>`
        : `<button class="action-button is-accent" data-action="unlock-session">${bi("افتح الجلسة", "Unlock session")}</button>`;
    sessionLockSlot.innerHTML = `<span class="lock-chip${toneClass}">${label}</span>${actionButton}`;
  }

  function renderSidebarPanels() {
    if (!sidebarSession || !sidebarOverview || !state.session) return;
    sidebarSession.innerHTML = `
      <p class="section-kicker">${bi("Access state", "Access state")}</p>
      <h3>${bi("قفل التنفيذ", "Mutation gate")}</h3>
      ${kvList([
        ["mode", String(state.session.mode || "mutations-only")],
        ["passcode_configured", String(state.session.passcode_configured)],
        ["writes_available", String(state.session.writes_available)],
        ["lock_reason", String(state.session.lock_reason || "-")],
        ["unlock_count", String(state.session.unlock_count || 0)],
      ])}
      <p class="command-note">${bi("القراءة مفتوحة محليًا، والكتابة فقط هي التي تحتاج unlock.", "Reads stay open locally; only writes need unlock.")}</p>
    `;

    let overviewTitle = bi("ملخص السطح", "Surface summary");
    let overviewBody = kvList([
      ["workspace_root", String(state.health.workspace_root || "-")],
      ["output_dir", String(state.health.output_dir || "-")],
    ]);

    if (state.route === "skills" && state.audit) {
      const summary = state.audit.summary || {};
      overviewTitle = bi("ملخص المهارات", "Skills summary");
      overviewBody = kvList([
        ["live_total", String(summary.live_total || 0)],
        ["missing_from_catalog", String(summary.missing_from_catalog || 0)],
        ["metadata_drift", String(summary.metadata_drift || 0)],
        ["stale_docs", String(summary.stale_docs || 0)],
      ]);
    } else if (state.route === "memory" && state.memory) {
      overviewTitle = bi("ملخص الميموري", "Memory summary");
      overviewBody = kvList([
        ["pending_total", String(state.memory.analytics?.pending_total || 0)],
        ["older_than_72h", String(state.memory.analytics?.age_bands?.["72h+"] || 0)],
        ["doctor_issues", String((state.memory.doctor?.issues || []).length)],
        ["resolved_project", String(state.memory.doctor?.resolved_project || "-")],
      ]);
    } else if (state.route === "artifacts" && state.artifacts) {
      const summary = state.artifacts.summary || {};
      overviewTitle = bi("ملخص الـ artifacts", "Artifacts summary");
      overviewBody = kvList([
        ["total_html", String(summary.total_html || 0)],
        ["with_pdf_companion", String(summary.with_pdf_companion || 0)],
        ["with_qa_companion", String(summary.with_qa_companion || 0)],
        ["report_total", String(summary.report_total || 0)],
      ]);
    } else if (state.route === "runtime" && state.runtime) {
      overviewTitle = bi("ملخص الـ runtime", "Runtime summary");
      overviewBody = kvList([
        ["implementation_report_present", String(state.runtime.runtime?.implementation_report_present || false)],
        ["recent_exports_total", String(state.runtime.runtime?.recent_exports_total || 0)],
        ["recent_mutations_total", String(state.runtime.runtime?.recent_mutations_total || 0)],
        ["passcode_env", String(state.runtime.runtime?.passcode_env || "-")],
      ]);
    }

    sidebarOverview.innerHTML = `
      <p class="section-kicker">${bi("Deck telemetry", "Deck telemetry")}</p>
      <h3>${overviewTitle}</h3>
      ${overviewBody}
    `;
  }

  function updateChrome() {
    renderTopSessionSlot();
    renderSidebarPanels();
    updateNav();
  }

  function skillRow(skill) {
    return `
      <article class="stream-row">
        <div class="stream-row__headline">
          <div>
            <div class="stream-row__title">${escapeHtml(skill.display_name)}</div>
            <div class="stream-row__subtitle">${escapeHtml(skill.source_path)}</div>
          </div>
          <div class="stream-row__meta">
            ${codeTag(skill.skill_id)}
            ${codeTag(skill.invoke)}
            ${inlineTag(skill.scope === "system" ? "system" : "top-level", skill.scope, skill.scope === "top-level" ? "accent" : "")}
          </div>
        </div>
        <p class="muted-copy">${escapeHtml(skill.description || "")}</p>
        <div class="stream-row__actions">
          <button class="action-button is-accent" data-action="skill-detail" data-skill-key="${escapeHtml(skill.skill_key)}">${bi("تفاصيل", "Details")}</button>
          <button class="action-button" data-action="copy-text" data-value="${escapeHtml(skill.invoke)}">${bi("انسخ invoke", "Copy invoke")}</button>
        </div>
      </article>
    `;
  }

  function renderSkillsSurface() {
    if (!state.skills || !state.audit) {
      return emptyState("جاري تحميل المهارات الحية...", "Loading live skills...");
    }
    const skills = state.skills.skills || [];
    const audit = state.audit;
    const summary = audit.summary || {};
    const topLevel = skills.filter((skill) => skill.scope === "top-level");
    const system = skills.filter((skill) => skill.scope === "system");
    const actions = `
      <button class="action-button" data-action="refresh-skills">${bi("تحديث", "Refresh")}</button>
      <button class="action-button is-accent"${mutationDisabledAttr()} data-action="export-surface" data-surface="skills-review">${bi("تصدير HTML", "Export HTML")}</button>
    `;
    const summaryHtml = [
      summaryCard(summary.live_total || 0, "إجمالي live", "Live total"),
      summaryCard(summary.missing_from_catalog || 0, "خارج الكتالوج", "Missing in catalog"),
      summaryCard(summary.metadata_drift || 0, "metadata drift", "Metadata drift"),
      summaryCard(summary.stale_docs || 0, "docs stale", "Stale docs"),
    ].join("");
    const contentHtml = `
      <div class="stream-grid">
        <article class="stream-panel">
          <h3>${bi("Open findings", "Open findings")}</h3>
          ${reportList((audit.missing_from_catalog || []).slice(0, 8).map((item) => `${codeTag(item.skill_key)} ${prettyPath(item.source_path)}`))}
        </article>
        <article class="stream-panel">
          <h3>${bi("Stale docs", "Stale docs")}</h3>
          ${reportList((audit.stale_docs || []).slice(0, 8).map((item) => `${codeTag(item.skill_key)} ${escapeHtml(item.doc_path || "-")}`))}
        </article>
      </div>
      <article class="stream-panel">
        <h3>${bi("Top-level skills", "Top-level skills")}</h3>
        <div class="surface-stream">${topLevel.map(skillRow).join("")}</div>
      </article>
      <article class="stream-panel">
        <h3>${bi("System skills", "System skills")}</h3>
        <div class="surface-stream">${system.map(skillRow).join("")}</div>
      </article>
    `;
    return surfaceShell({
      kickerAr: "Skill Review",
      kickerEn: "Skill Review",
      titleAr: "مراجعة حية للمصدر الفعلي للمهارات",
      titleEn: "Live review of the actual skill source",
      descAr: "هذه الصفحة readonly بالكامل، والحقيقة فيها تأتي من ~/.codex/skills لا من الأرشيف.",
      descEn: "This page stays fully readonly and its truth comes from ~/.codex/skills, not from archived artifacts.",
      actionsHtml: actions,
      summaryHtml,
      contentHtml,
    });
  }

  function mutationActionButton(labelAr, labelEn, action, value, tone = "") {
    const toneClass = tone ? ` is-${tone}` : "";
    const disabled = mutationDisabledAttr();
    return `<button class="action-button${toneClass}"${disabled} data-action="${escapeHtml(action)}" data-value="${escapeHtml(value)}">${bi(labelAr, labelEn)}</button>`;
  }

  function renderCandidateRow(item, allowPromote) {
    const rawValue = item.normalized_value ?? item.normalized_value_json ?? item.value ?? "";
    const actions = [];
    if (allowPromote) {
      actions.push(`<button class="action-button is-accent"${mutationDisabledAttr()} data-action="promote-candidate" data-candidate-id="${escapeHtml(item.candidate_id)}">${bi("ترقية", "Promote")}</button>`);
    }
    actions.push(`<button class="action-button is-danger"${mutationDisabledAttr()} data-action="reject-candidate" data-candidate-id="${escapeHtml(item.candidate_id)}">${bi("رفض", "Reject")}</button>`);
    return `
      <article class="stream-row">
        <div class="stream-row__headline">
          <div>
            <div class="stream-row__title">${escapeHtml(item.normalized_key)}</div>
            <div class="stream-row__subtitle">${escapeHtml(item.candidate_id)}</div>
          </div>
          <div class="stream-row__meta">
            ${inlineTag(item.confidence, "confidence", "accent")}
            ${inlineTag(item.created_at || "-", "created_at")}
          </div>
        </div>
        <p class="muted-copy">${escapeHtml(JSON.stringify(rawValue, null, 0))}</p>
        <div class="stream-row__actions">${actions.join("")}</div>
      </article>
    `;
  }

  function renderQueue(queue) {
    const disabled = mutationDisabledAttr();
    return `
      <article class="stream-row">
        <div class="stream-row__headline">
          <div>
            <div class="stream-row__title">${bi(queue.label_ar, queue.label_en)}</div>
            <div class="stream-row__subtitle">${bi(queue.description_ar, queue.description_en)}</div>
          </div>
          <div class="stream-row__meta">
            ${codeTag(queue.id)}
            ${inlineTag(queue.total, "items", queue.total ? "accent" : "")}
            ${inlineTag(queue.actionable_total, "actionable", queue.actionable_total ? "accent" : "")}
          </div>
        </div>
        ${kvList([
          ["recommended_action", String(queue.recommended_action || "-")],
          ["total", String(queue.total || 0)],
          ["actionable_total", String(queue.actionable_total || 0)],
        ])}
        <div class="stream-row__actions">
          <button class="action-button" data-action="preview-cleanup">${bi("تحديث الـ preview", "Refresh preview")}</button>
          ${queue.actionable_total ? `<button class="action-button is-danger"${disabled} data-action="execute-queue" data-queue-id="${escapeHtml(queue.id)}">${bi("تنفيذ التنضيف", "Execute cleanup")}</button>` : ""}
        </div>
      </article>
    `;
  }

  function renderMemorySurface() {
    if (!state.memory) {
      return emptyState("جاري تحميل الميموري...", "Loading memory...");
    }
    const { doctor, inspect, triage, suggest, analytics, history, tokenCost, cleanup } = state.memory;
    const summaryHtml = [
      summaryCard((doctor.issues || []).length, "doctor issues", "Doctor issues"),
      summaryCard(triage.summary?.pending_total || 0, "pending", "Pending"),
      summaryCard(triage.summary?.promotable_total || 0, "promotable", "Promotable"),
      summaryCard(analytics.age_bands?.["72h+"] || 0, "older than 72h", "Older than 72h"),
    ].join("");
    const actions = `
      <button class="action-button" data-action="refresh-memory">${bi("تحديث", "Refresh")}</button>
      <button class="action-button is-accent"${mutationDisabledAttr()} data-action="export-surface" data-surface="memory">${bi("تصدير HTML", "Export HTML")}</button>
      <button class="action-button"${mutationDisabledAttr()} data-action="backfill-memory">${bi("Backfill", "Backfill")}</button>
    `;
    const tokenItems = (tokenCost.commands || [])
      .filter((item) => !item.error)
      .map((item) => `<code>${escapeHtml(item.command)}</code> — ${escapeHtml(item.approx_tokens_low)}..${escapeHtml(item.approx_tokens_high)} tokens`);
    const historyItems = (history.items || []).map(
      (item) => `
        <article class="stream-row">
          <div class="stream-row__headline">
            <div>
              <div class="stream-row__title">${escapeHtml(item.event_type)}</div>
              <div class="stream-row__subtitle">${escapeHtml(item.event_id)}</div>
            </div>
            <div class="stream-row__meta">${inlineTag(formatDate(item.created_at), "timestamp")}</div>
          </div>
          <div class="stream-row__actions">
            <button class="action-button"${mutationDisabledAttr()} data-action="rollback-event" data-event-id="${escapeHtml(item.event_id)}">${bi("Rollback", "Rollback")}</button>
          </div>
        </article>
      `
    );
    const promotable = triage.promotable || [];
    const contentHtml = `
      <div class="stream-grid">
        <article class="stream-panel">
          <h3>${bi("Doctor + analytics", "Doctor + analytics")}</h3>
          ${kvList([
            ["memory_root", String(doctor.memory_root || "-")],
            ["state_db", String(doctor.state_db || "-")],
            ["resolved_project", String(doctor.resolved_project || "-")],
            ["pending_total", String(analytics.pending_total || 0)],
          ])}
        </article>
        <article class="stream-panel">
          <h3>${bi("Token cost", "Token cost")}</h3>
          ${reportList(tokenItems)}
        </article>
      </div>
      <article class="stream-panel">
        <h3>${bi("Promotable candidates", "Promotable candidates")}</h3>
        <div class="surface-stream">${promotable.length ? promotable.map((item) => renderCandidateRow(item, true)).join("") : emptyState("لا توجد عناصر promotable حاليًا.", "No promotable items right now.")}</div>
      </article>
      <article class="stream-panel">
        <h3>${bi("Suggest sample", "Suggest sample")}</h3>
        <div class="surface-stream">${(suggest || []).slice(0, 8).map((item) => renderCandidateRow(item, false)).join("")}</div>
      </article>
      <article class="stream-panel">
        <h3>${bi("Smart cleanup queues", "Smart cleanup queues")}</h3>
        <div class="surface-stream">${(cleanup.queues || []).map(renderQueue).join("")}</div>
      </article>
      <div class="stream-grid">
        <article class="stream-panel">
          <h3>${bi("Mutation history", "Mutation history")}</h3>
          <div class="surface-stream">${historyItems.join("")}</div>
        </article>
        <article class="stream-panel">
          <h3>${bi("Inspect snapshot", "Inspect snapshot")}</h3>
          <pre class="code-block">${escapeHtml(JSON.stringify({
            user_profile: inspect.user_profile || {},
            project_profile: inspect.project_profile || {},
          }, null, 2))}</pre>
        </article>
      </div>
      <div class="stream-grid">
        <article class="operator-frame">
          <h3>${bi("Forget key", "Forget key")}</h3>
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
              <button class="action-button is-danger"${mutationDisabledAttr()} type="submit">${bi("نفّذ forget", "Run forget")}</button>
            </div>
          </form>
        </article>
        <article class="operator-frame">
          <h3>${bi("Manual rollback", "Manual rollback")}</h3>
          <form id="rollback-form" class="field-grid">
            <div class="field">
              <label>${bi("event id", "event id")}</label>
              <input name="event_id" placeholder="mem-evt-...">
            </div>
            <div class="action-row">
              <button class="action-button"${mutationDisabledAttr()} type="submit">${bi("نفّذ rollback", "Run rollback")}</button>
            </div>
          </form>
        </article>
      </div>
    `;
    return surfaceShell({
      kickerAr: "Memory Control",
      kickerEn: "Memory Control",
      titleAr: "سطح التنفيذ الوحيدة داخل الكوكبيت",
      titleEn: "The only execution surface inside the cockpit",
      descAr: "القراءة متاحة دائمًا محليًا، لكن الأفعال التي تغيّر الحالة تحتاج unlock مؤقتة.",
      descEn: "Reads stay available locally, but state-changing actions require a temporary unlock.",
      actionsHtml: actions,
      summaryHtml,
      contentHtml,
    });
  }

  function filterArtifacts(items) {
    let filtered = [...items];
    if (state.ui.artifactQuery) {
      const q = state.ui.artifactQuery.toLowerCase();
      filtered = filtered.filter((item) => item.artifact_name.toLowerCase().includes(q) || item.family_id.toLowerCase().includes(q));
    }
    if (state.ui.artifactFamily !== "all") {
      filtered = filtered.filter((item) => item.family_id === state.ui.artifactFamily);
    }
    if (state.ui.artifactSort === "name") {
      filtered.sort((a, b) => a.artifact_name.localeCompare(b.artifact_name));
    } else if (state.ui.artifactSort === "size") {
      filtered.sort((a, b) => (b.size_bytes || 0) - (a.size_bytes || 0));
    } else {
      filtered.sort((a, b) => String(b.modified_at || "").localeCompare(String(a.modified_at || "")));
    }
    return filtered;
  }

  function renderArtifactRow(item) {
    return `
      <article class="stream-row">
        <div class="stream-row__headline">
          <div>
            <div class="stream-row__title">${escapeHtml(item.artifact_name)}</div>
            <div class="stream-row__subtitle">${escapeHtml(item.absolute_path)}</div>
          </div>
          <div class="stream-row__meta">
            ${inlineTag(item.family_label_ar, item.family_label_en, item.family_id === "omega-hud" ? "accent" : "")}
            ${item.is_legacy ? inlineTag("legacy", "legacy") : ""}
            ${item.is_report ? inlineTag("report", "report", "accent") : ""}
          </div>
        </div>
        ${kvList([
          ["modified_at", formatDate(item.modified_at)],
          ["size", formatSize(item.size_bytes)],
          ["public_path", item.public_path],
        ])}
        <div class="stream-row__actions">
          <a class="action-button is-accent" href="${escapeHtml(item.public_path)}" target="_blank" rel="noreferrer">${bi("افتح", "Open")}</a>
          <button class="action-button" data-action="artifact-detail" data-artifact-name="${escapeHtml(item.artifact_name)}">${bi("تفاصيل", "Details")}</button>
          <button class="action-button" data-action="copy-text" data-value="${escapeHtml(item.absolute_path)}">${bi("انسخ المسار", "Copy path")}</button>
        </div>
      </article>
    `;
  }

  function renderArtifactsSurface() {
    if (!state.artifacts) {
      return emptyState("جاري فهرسة الـ artifacts...", "Indexing artifacts...");
    }
    const summary = state.artifacts.summary || {};
    const items = filterArtifacts(state.artifacts.items || []);
    const actions = `
      <button class="action-button" data-action="refresh-artifacts">${bi("تحديث", "Refresh")}</button>
      <button class="action-button is-accent"${mutationDisabledAttr()} data-action="export-surface" data-surface="artifacts">${bi("تصدير HTML", "Export HTML")}</button>
    `;
    const summaryHtml = [
      summaryCard(summary.total_html || 0, "html files", "HTML files"),
      summaryCard(summary.with_pdf_companion || 0, "with pdf", "With PDF"),
      summaryCard(summary.with_qa_companion || 0, "with qa", "With QA"),
      summaryCard(summary.report_total || 0, "reports", "Reports"),
    ].join("");
    const contentHtml = `
      <article class="operator-frame">
        <div class="field-inline">
          <input class="search-input" type="search" data-artifact-input="query" placeholder="omega-hud" value="${escapeHtml(state.ui.artifactQuery)}">
          <select class="search-input" data-artifact-input="family">
            <option value="all"${state.ui.artifactFamily === "all" ? " selected" : ""}>all families</option>
            <option value="omega-hud"${state.ui.artifactFamily === "omega-hud" ? " selected" : ""}>omega-hud</option>
            <option value="omega-planning"${state.ui.artifactFamily === "omega-planning" ? " selected" : ""}>omega-planning</option>
            <option value="omega-memory"${state.ui.artifactFamily === "omega-memory" ? " selected" : ""}>omega-memory</option>
            <option value="omega-skills"${state.ui.artifactFamily === "omega-skills" ? " selected" : ""}>omega-skills</option>
            <option value="omega-admin-report"${state.ui.artifactFamily === "omega-admin-report" ? " selected" : ""}>omega-admin-report</option>
            <option value="other"${state.ui.artifactFamily === "other" ? " selected" : ""}>other</option>
          </select>
          <select class="search-input" data-artifact-input="sort">
            <option value="recent"${state.ui.artifactSort === "recent" ? " selected" : ""}>recent</option>
            <option value="name"${state.ui.artifactSort === "name" ? " selected" : ""}>name</option>
            <option value="size"${state.ui.artifactSort === "size" ? " selected" : ""}>size</option>
          </select>
        </div>
      </article>
      <article class="stream-panel">
        <h3>${bi("Artifact index", "Artifact index")}</h3>
        <div class="surface-stream">${items.length ? items.map(renderArtifactRow).join("") : emptyState("لا توجد عناصر تطابق الفلتر.", "No artifacts match the current filter.")}</div>
      </article>
    `;
    return surfaceShell({
      kickerAr: "Artifacts Hub",
      kickerEn: "Artifacts Hub",
      titleAr: "فهرس حي لملفات output/html",
      titleEn: "A live index for output/html files",
      descAr: "الصفحة تعرض الـ snapshots المحلية والـ reports والـ companions من غير ما تعتبرها source of truth.",
      descEn: "This page shows local snapshots, reports, and companions without treating them as source of truth.",
      actionsHtml: actions,
      summaryHtml,
      contentHtml,
    });
  }

  function renderRuntimeSurface() {
    if (!state.runtime || !state.runtimeLedger) {
      return emptyState("جاري تحميل الـ runtime...", "Loading runtime...");
    }
    const summaryHtml = [
      summaryCard(state.runtime.session?.passcode_configured ? "yes" : "no", "passcode configured", "Passcode configured"),
      summaryCard(state.runtime.session?.writes_available ? "armed" : "locked", "write state", "Write state"),
      summaryCard(state.runtime.runtime?.recent_exports_total || 0, "exports", "Exports"),
      summaryCard(state.runtime.runtime?.recent_mutations_total || 0, "mutations", "Mutations"),
    ].join("");
    const actions = `
      <button class="action-button" data-action="refresh-runtime">${bi("تحديث", "Refresh")}</button>
      <button class="action-button is-accent"${mutationDisabledAttr()} data-action="export-surface" data-surface="runtime">${bi("تصدير HTML", "Export HTML")}</button>
    `;
    const notices = (state.runtime.notices || []).map((item) => `${codeTag(item.probe)} ${escapeHtml(item.message)}`);
    const exportRows = (state.runtimeLedger.exports || []).map((item) => `${codeTag(item.surface_id)} ${escapeHtml(item.artifact_name)} — ${escapeHtml(item.status)}`);
    const mutationRows = (state.runtimeLedger.mutations || []).map((item) => `${codeTag(item.action)} ${escapeHtml(item.status)} — ${escapeHtml(item.message || "")}`);
    const contentHtml = `
      <div class="stream-grid">
        <article class="stream-panel">
          <h3>${bi("Health + session", "Health + session")}</h3>
          ${kvList([
            ["workspace_root", String(state.runtime.health?.workspace_root || "-")],
            ["host", String(state.runtime.health?.host || "-")],
            ["port", String(state.runtime.health?.port || "-")],
            ["lock_reason", String(state.runtime.session?.lock_reason || "-")],
          ])}
        </article>
        <article class="stream-panel">
          <h3>${bi("Latency snapshot", "Latency snapshot")}</h3>
          ${kvList([
            ["skills_scan", `${state.runtime.latencies_ms?.skills_scan || 0} ms`],
            ["memory_doctor", `${state.runtime.latencies_ms?.memory_doctor || 0} ms`],
            ["memory_analytics", `${state.runtime.latencies_ms?.memory_analytics || 0} ms`],
            ["artifacts_index", `${state.runtime.latencies_ms?.artifacts_index || 0} ms`],
          ])}
        </article>
      </div>
      <div class="stream-grid">
        <article class="stream-panel">
          <h3>${bi("Runtime notices", "Runtime notices")}</h3>
          ${reportList(notices)}
        </article>
        <article class="stream-panel">
          <h3>${bi("System roll-up", "System roll-up")}</h3>
          ${kvList([
            ["live_skills", String(state.runtime.skills?.summary?.live_total || 0)],
            ["pending_memory", String(state.runtime.memory?.summary?.pending_total || 0)],
            ["older_than_72h", String(state.runtime.memory?.summary?.older_than_72h || 0)],
            ["artifacts_total", String(state.runtime.artifacts?.summary?.total_html || 0)],
          ])}
        </article>
      </div>
      <div class="stream-grid">
        <article class="stream-panel">
          <h3>${bi("Recent exports", "Recent exports")}</h3>
          ${reportList(exportRows)}
        </article>
        <article class="stream-panel">
          <h3>${bi("Recent mutation attempts", "Recent mutation attempts")}</h3>
          ${reportList(mutationRows)}
        </article>
      </div>
    `;
    return surfaceShell({
      kickerAr: "Runtime",
      kickerEn: "Runtime",
      titleAr: "لوحة تشخيص وتشغيل للكوكبيت الإدارية",
      titleEn: "A diagnostic and operational panel for the admin cockpit",
      descAr: "هذه الصفحة read-only وتجمع health, gate state, latencies, والـ ledgers في مكان واحد.",
      descEn: "This page stays read-only and gathers health, gate state, latencies, and ledgers in one place.",
      actionsHtml: actions,
      summaryHtml,
      contentHtml,
    });
  }

  function render() {
    if (state.route === "memory") {
      root.innerHTML = renderMemorySurface();
    } else if (state.route === "artifacts") {
      root.innerHTML = renderArtifactsSurface();
    } else if (state.route === "runtime") {
      root.innerHTML = renderRuntimeSurface();
    } else {
      root.innerHTML = renderSkillsSurface();
    }
    updateChrome();
  }

  function loadSession() {
    return get("/api/session/state").then((session) => {
      state.session = session;
      updateChrome();
      return session;
    });
  }

  function loadSkills() {
    return Promise.all([get("/api/skills/live"), get("/api/skills/audit"), loadSession()]).then(([skills, audit]) => {
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
      loadSession(),
    ]).then(([doctor, inspect, triage, suggest, analytics, history, tokenCost, cleanup]) => {
      state.memory = { doctor, inspect, triage, suggest, analytics, history, tokenCost, cleanup };
      render();
    });
  }

  function loadArtifacts() {
    return Promise.all([get("/api/artifacts/index"), loadSession()]).then(([artifacts]) => {
      state.artifacts = artifacts;
      render();
    });
  }

  function loadRuntime() {
    return Promise.all([get("/api/runtime/overview"), get("/api/runtime/ledger"), loadSession()]).then(([overview, ledger]) => {
      state.runtime = overview;
      state.runtimeLedger = ledger;
      render();
    });
  }

  function refreshRoute() {
    if (state.route === "memory") return loadMemory();
    if (state.route === "artifacts") return loadArtifacts();
    if (state.route === "runtime") return loadRuntime();
    return loadSkills();
  }

  function showSkillDetail(skillKey) {
    get(`/api/skills/${encodeURIComponent(skillKey)}`).then((detail) => {
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

  function showArtifactDetail(name) {
    get(`/api/artifacts/${encodeURIComponent(name)}`).then((detail) => {
      openDrawer(`
        <div class="surface-header">
          <p class="section-kicker">${bi("Artifact detail", "Artifact detail")}</p>
          <h3>${escapeHtml(detail.artifact_name)}</h3>
          <div class="action-row">
            <button class="action-button" data-action="close-drawer">${bi("إغلاق", "Close")}</button>
            <a class="action-button is-accent" href="${escapeHtml(detail.public_path)}" target="_blank" rel="noreferrer">${bi("افتح", "Open")}</a>
          </div>
        </div>
        ${kvList([
          ["family_id", detail.family_id],
          ["absolute_path", detail.absolute_path],
          ["public_path", detail.public_path],
          ["modified_at", formatDate(detail.modified_at)],
          ["size_bytes", String(detail.size_bytes)],
          ["pdf_companion", String(detail.pdf_companion || "-")],
          ["qa_companion", String(detail.qa_companion || "-")],
        ])}
      `);
    }).catch((error) => pushToast(error.message, "danger"));
  }

  function runConfirmed(title, body, action) {
    if (!ensureMutationAccess()) return;
    openConfirm({
      title,
      body,
      onConfirm: async () => {
        try {
          closeModal();
          await action();
        } catch (error) {
          pushToast(error.message, "danger");
          await loadSession();
          render();
        }
      },
    });
  }

  async function handleExport(surface) {
    if (!ensureMutationAccess()) return;
    const result = await post(`/api/export/${surface}`, {});
    pushToast(`Exported ${result.output_path}`, "success");
    if (state.route === "artifacts" || state.route === "runtime") {
      await refreshRoute();
    } else {
      await loadSession();
      updateChrome();
    }
  }

  document.addEventListener("click", (event) => {
    const target = event.target.closest("[data-action]");
    if (!target) return;
    const action = target.getAttribute("data-action");

    if (action === "close-drawer") {
      closeDrawer();
      return;
    }
    if (action === "cancel-modal") {
      closeModal();
      return;
    }
    if (action === "run-confirm" && state.modalConfirm) {
      state.modalConfirm();
      return;
    }
    if (action === "unlock-session") {
      openUnlockModal();
      return;
    }
    if (action === "lock-session") {
      post("/api/session/lock", {}).then(async () => {
        pushToast("Admin session locked", "success");
        await loadSession();
        render();
      }).catch((error) => pushToast(error.message, "danger"));
      return;
    }
    if (action === "skill-detail") {
      showSkillDetail(target.getAttribute("data-skill-key") || "");
      return;
    }
    if (action === "artifact-detail") {
      showArtifactDetail(target.getAttribute("data-artifact-name") || "");
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
    if (action === "refresh-artifacts") {
      loadArtifacts().catch((error) => pushToast(error.message, "danger"));
      return;
    }
    if (action === "refresh-runtime") {
      loadRuntime().catch((error) => pushToast(error.message, "danger"));
      return;
    }
    if (action === "export-surface") {
      handleExport(target.getAttribute("data-surface") || "").catch((error) => pushToast(error.message, "danger"));
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
      const candidateId = target.getAttribute("data-candidate-id") || "";
      runConfirmed(`Promote ${candidateId}`, "سيتم ترقية الـ candidate إلى durable memory.", async () => {
        await post("/api/memory/promote", { candidate_id: candidateId });
        pushToast(`Promoted ${candidateId}`, "success");
        await loadMemory();
      });
      return;
    }
    if (action === "reject-candidate") {
      const candidateId = target.getAttribute("data-candidate-id") || "";
      runConfirmed(`Reject ${candidateId}`, "سيتم رفض الـ candidate وإبقاؤه خارج durable memory.", async () => {
        await post("/api/memory/reject", { candidate_id: candidateId, reason: "omega-cockpit-admin-v2 manual reject" });
        pushToast(`Rejected ${candidateId}`, "success");
        await loadMemory();
      });
      return;
    }
    if (action === "execute-queue") {
      const queueId = target.getAttribute("data-queue-id") || "";
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
      const eventId = target.getAttribute("data-event-id") || "";
      runConfirmed(`Rollback ${eventId}`, "سيتم استرجاع الحالة من الـ snapshot المرتبط بهذا الحدث.", async () => {
        await post("/api/memory/rollback", { event_id: eventId });
        pushToast(`Rolled back ${eventId}`, "success");
        await loadMemory();
      });
    }
  });

  drawerScrim.addEventListener("click", closeDrawer);
  modalBackdrop.addEventListener("click", closeModal);

  document.addEventListener("submit", (event) => {
    if (event.target.id === "unlock-form") {
      event.preventDefault();
      const form = new FormData(event.target);
      post("/api/session/unlock", { passcode: form.get("passcode") }).then(async () => {
        closeModal();
        pushToast("Admin session unlocked", "success");
        await loadSession();
        render();
      }).catch((error) => pushToast(error.message, "danger"));
      return;
    }
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
      return;
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

  document.addEventListener("input", (event) => {
    const target = event.target;
    if (target.matches("[data-artifact-input='query']")) {
      state.ui.artifactQuery = target.value;
      render();
    }
  });

  document.addEventListener("change", (event) => {
    const target = event.target;
    if (target.matches("[data-artifact-input='family']")) {
      state.ui.artifactFamily = target.value;
      render();
    }
    if (target.matches("[data-artifact-input='sort']")) {
      state.ui.artifactSort = target.value;
      render();
    }
  });

  window.addEventListener("hashchange", () => {
    setRoute((window.location.hash || "#/skills").replace(/^#\//, ""));
    refreshRoute().catch((error) => pushToast(error.message, "danger"));
  });

  function boot() {
    const rememberedRoute = localStorage.getItem("omega-cockpit:last-route");
    if (!window.location.hash && rememberedRoute) {
      window.location.hash = `#/${normalizeRoute(rememberedRoute)}`;
      return;
    }
    setRoute(state.route);
    refreshRoute().catch((error) => {
      root.innerHTML = emptyState("فشل تحميل الكوكبيت.", "Failed to load cockpit.");
      pushToast(error.message, "danger");
    });
  }

  boot();
})();
