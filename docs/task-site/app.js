const state = {
  tasks: [],
  selectedId: "",
  query: "",
};

const els = {
  taskList: document.querySelector("#taskList"),
  taskCount: document.querySelector("#taskCount"),
  detail: document.querySelector("#detail"),
  searchInput: document.querySelector("#searchInput"),
};

const text = (value, fallback = "不明") => {
  if (typeof value !== "string") return fallback;
  const trimmed = value.trim();
  return trimmed ? trimmed : fallback;
};

const list = (items) => {
  if (!Array.isArray(items) || items.length === 0) {
    return '<p class="summary">なし</p>';
  }
  return `<ul class="list">${items.map((item) => `<li>${escapeHtml(text(item))}</li>`).join("")}</ul>`;
};

const escapeHtml = (value) =>
  String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

const judgementClass = (value) => {
  if (value === "OK" || value === "完了") return "ok";
  if (value === "修正が必要" || value === "要確認") return "warn";
  return "";
};

const reviewLabel = (kind) => {
  const labels = {
    "test-cases": "Test Cases Review",
    "test-code": "Test Code Review",
    "public-check": "Public Check",
  };
  return labels[kind] || text(kind);
};

const taskMatches = (task) => {
  const query = state.query.toLowerCase();
  if (!query) return true;
  return JSON.stringify(task).toLowerCase().includes(query);
};

const renderTaskList = () => {
  const filtered = state.tasks.filter(taskMatches);
  els.taskCount.textContent = String(filtered.length);
  els.taskList.innerHTML = filtered
    .map(
      (task) => `
        <button class="task-button ${task.task_id === state.selectedId ? "active" : ""}" data-task-id="${escapeHtml(task.task_id)}">
          <strong>${escapeHtml(task.task_id)}</strong>
          <span>${escapeHtml(text(task.title))}</span>
        </button>
      `,
    )
    .join("");
};

const renderDetail = () => {
  const task = state.tasks.find((item) => item.task_id === state.selectedId);
  if (!task) {
    els.detail.innerHTML = `
      <div class="empty">
        <h2>No task selected</h2>
        <p>Generate task summaries, then select a task from the list.</p>
      </div>
    `;
    return;
  }

  const changePlan = task.change_plan || {};
  const implementation = task.implementation || {};
  const reviews = Array.isArray(task.reviews) ? task.reviews : [];
  const artifacts = Array.isArray(task.artifacts) ? task.artifacts : [];

  els.detail.innerHTML = `
    <article>
      <section class="hero">
        <div class="hero-row">
          <span class="badge">${escapeHtml(task.task_id)}</span>
          <span class="badge ${judgementClass(task.status)}">${escapeHtml(text(task.status))}</span>
          <span class="badge">${escapeHtml(text(task.updated_at))}</span>
        </div>
        <h2>${escapeHtml(text(task.title))}</h2>
        <p class="summary">${escapeHtml(text(task.summary))}</p>
      </section>

      <section class="section">
        <h2>Change Plan</h2>
        <div class="grid">
          <div>
            <h3>Background</h3>
            <p>${escapeHtml(text(changePlan.background))}</p>
          </div>
          <div>
            <h3>Goal</h3>
            <p>${escapeHtml(text(changePlan.goal))}</p>
          </div>
          <div>
            <h3>Scope</h3>
            ${list(changePlan.scope)}
          </div>
          <div>
            <h3>Out Of Scope</h3>
            ${list(changePlan.out_of_scope)}
          </div>
        </div>
      </section>

      <section class="section">
        <h2>Reviews</h2>
        ${
          reviews.length
            ? reviews
                .map(
                  (review) => `
                    <div class="review">
                      <div class="review-title">
                        <h3>${escapeHtml(reviewLabel(review.kind))}</h3>
                        <span class="badge ${judgementClass(review.judgement)}">${escapeHtml(text(review.judgement))}</span>
                      </div>
                      <p class="summary">${escapeHtml(text(review.file, ""))}</p>
                      ${list(review.findings)}
                      <p>${escapeHtml(text(review.result))}</p>
                    </div>
                  `,
                )
                .join("")
            : '<p class="summary">レビュー情報なし</p>'
        }
      </section>

      <section class="section">
        <h2>Implementation</h2>
        <div class="grid">
          <div>
            <h3>Tests</h3>
            ${list(implementation.tests)}
          </div>
          <div>
            <h3>Samples</h3>
            ${list(implementation.samples)}
          </div>
          <div>
            <h3>App</h3>
            ${list(implementation.app)}
          </div>
          <div>
            <h3>Verification</h3>
            ${list(implementation.verification)}
          </div>
        </div>
      </section>

      <section class="section">
        <h2>Artifacts</h2>
        <ul class="path-list">
          ${artifacts
            .map(
              (artifact) => `
                <li>
                  <a href="../../${escapeHtml(artifact.path)}" target="_blank" rel="noreferrer">
                    ${escapeHtml(text(artifact.label))}<br>
                    <small>${escapeHtml(text(artifact.path, ""))}</small>
                  </a>
                </li>
              `,
            )
            .join("")}
        </ul>
      </section>
    </article>
  `;
};

const loadTasks = async () => {
  const manifestResponse = await fetch("data/manifest.json", { cache: "no-store" });
  if (!manifestResponse.ok) throw new Error("manifest.json could not be loaded");
  const manifest = await manifestResponse.json();
  const entries = Array.isArray(manifest.tasks) ? manifest.tasks : [];
  const tasks = await Promise.all(
    entries.map(async (entry) => {
      const response = await fetch(entry.file, { cache: "no-store" });
      if (!response.ok) throw new Error(`${entry.file} could not be loaded`);
      return response.json();
    }),
  );
  state.tasks = tasks.sort((a, b) => String(a.task_id).localeCompare(String(b.task_id)));
  state.selectedId = state.tasks[0]?.task_id || "";
  renderTaskList();
  renderDetail();
};

els.taskList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-task-id]");
  if (!button) return;
  state.selectedId = button.dataset.taskId;
  renderTaskList();
  renderDetail();
});

els.searchInput.addEventListener("input", (event) => {
  state.query = event.target.value;
  const visible = state.tasks.filter(taskMatches);
  if (!visible.some((task) => task.task_id === state.selectedId)) {
    state.selectedId = visible[0]?.task_id || "";
  }
  renderTaskList();
  renderDetail();
});

loadTasks().catch((error) => {
  els.detail.innerHTML = `
    <div class="empty">
      <h2>Task data is not ready</h2>
      <p>${escapeHtml(error.message)}</p>
      <p>Run scripts/80-update-task-site.sh, then serve docs/task-site from a local web server.</p>
    </div>
  `;
});
