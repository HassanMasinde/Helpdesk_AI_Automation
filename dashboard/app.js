const STATUS_LABELS = { idle: "Idle", starting: "Starting...", launching: "Launching browser...", logging_in: "Logging in...", checking: "Checking tickets...", processing: "Processing ticket...", sleeping: "Sleeping (monitoring)", stopped: "Stopped" };
const SOURCE_LABELS = { gemini: "Gemini", learned: "Learned", fallback: "Fallback", policy: "Policy", manual: "Manual", redo: "Redo" };
const MODAL_TITLES = { found: "Found tickets", saved: "Saved resolutions", skipped: "Skipped tickets", failed: "Failed tickets" };
const els = Object.fromEntries([
  "statusBadge", "checkBtn", "startBtn", "stopBtn", "controlMsg",
  "statFound", "statSaved", "statSkipped", "statFailed",
  "ticketId", "ticketType", "ticketSubject", "resolution", "sourceTag",
  "log", "lastUpdated", "modal", "modalTitle", "modalBody", "modalClose",
  "searchInput", "dateFrom", "dateTo", "statusFilter", "typeFilter",
  "searchBtn", "clearSearchBtn", "searchMsg", "resultCount", "searchResults",
  "backgroundToggle", "backgroundState"
].map((id) => [id, document.getElementById(id)]));

let latest = null;
let searchTickets = [];
let modalStatus = null;
let modalView = "list";
let modalTicket = null;

function escapeHtml(value) {
  return String(value || "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char]));
}

function badgeClass(state) {
  if (!state.running) return "idle";
  return state.status === "sleeping" ? "sleeping" : "running";
}

function render(snapshot) {
  latest = snapshot;
  const state = snapshot.state;
  els.statusBadge.textContent = STATUS_LABELS[state.status] || state.status;
  els.statusBadge.className = "badge " + badgeClass(state);
  els.checkBtn.disabled = state.running;
  els.startBtn.disabled = state.running;
  els.stopBtn.disabled = !state.running;
  els.backgroundToggle.checked = !!state.background;
  els.backgroundState.textContent = state.background ? "Loyon: Background" : "Loyon: Visible";
  els.backgroundState.className = state.background ? "pill pill-saved" : "pill pill-status";
  els.statFound.textContent = state.counts.found;
  els.statSaved.textContent = state.counts.saved;
  els.statSkipped.textContent = state.counts.skipped;
  els.statFailed.textContent = state.counts.failed;
  if (state.current_ticket) {
    els.ticketId.textContent = "#" + state.current_ticket.id;
    els.ticketType.textContent = state.current_ticket.type || "—";
    els.ticketSubject.textContent = state.current_ticket.subject || "";
  } else {
    els.ticketId.textContent = "—";
    els.ticketType.textContent = "—";
    els.ticketSubject.textContent = "No ticket being processed.";
  }
  if (state.resolution && state.resolution.text) {
    els.resolution.textContent = state.resolution.text;
    els.sourceTag.textContent = SOURCE_LABELS[state.resolution.source] || state.resolution.source || "";
    els.sourceTag.className = state.resolution.source ? "tag tag-" + state.resolution.source : "tag hidden";
  } else {
    els.resolution.textContent = "No resolution yet.";
    els.sourceTag.className = "tag hidden";
  }
  els.lastUpdated.textContent = state.last_updated || "—";
  els.log.innerHTML = (snapshot.log || []).map((entry) => `<div class="log-line"><span class="log-time">${entry.ts}</span><span class="log-msg"></span></div>`).join("");
  [...els.log.querySelectorAll(".log-msg")].forEach((node, index) => { node.textContent = (snapshot.log || [])[index].message; });
  if (state.last_error) { els.searchMsg.textContent = "Error: " + state.last_error; } else if (!state.running) { els.searchMsg.textContent = ""; }
  if (modalStatus && modalView === "list") renderModalList();
}

async function post(path, body) {
  try {
    const res = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : { method: "POST" });
    const data = await res.json();
    els.controlMsg.textContent = data.message || "";
    setTimeout(() => (els.controlMsg.textContent = ""), 4000);
  } catch (error) {
    els.controlMsg.textContent = "Request failed: " + error;
  }
}

async function postJson(path, body) {
  const response = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  return response.json();
}

async function search() {
  els.searchBtn.disabled = true;
  els.searchMsg.textContent = "Opening Chrome and loading tickets...";
  try {
    const response = await fetch("/api/search-tickets", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query: els.searchInput.value, date_from: els.dateFrom.value, date_to: els.dateTo.value, status: els.statusFilter.value, ticket_type: els.typeFilter.value }) });
    const data = await response.json();
    els.searchMsg.textContent = data.message || "";
    if (data.ok) { searchTickets = data.tickets || []; renderSearchResults(); }
  } catch (error) {
    els.searchMsg.textContent = "Search failed: " + error;
  } finally {
    els.searchBtn.disabled = false;
  }
}

function filteredTickets() {
  const query = els.searchInput.value.trim().toLowerCase();
  const status = els.statusFilter.value.toLowerCase();
  const type = els.typeFilter.value;
  return searchTickets.filter((ticket) => {
    const text = `${ticket.id} ${ticket.description || ""} ${ticket.subject || ""}`.toLowerCase();
    return (!query || text.includes(query)) && (!status || (ticket.status || "").toLowerCase().includes(status)) && (!type || ticket.ticket_type === type);
  });
}

function renderSearchResults() {
  const tickets = filteredTickets();
  els.resultCount.textContent = `${tickets.length} matching ticket${tickets.length === 1 ? "" : "s"}`;
  if (!tickets.length) {
    els.searchResults.className = "results empty-state";
    els.searchResults.textContent = searchTickets.length ? "No tickets match the current filters." : "No tickets were loaded for this date range.";
    return;
  }
  els.searchResults.className = "results";
  els.searchResults.innerHTML = tickets.map((ticket) => `
    <article class="ticket-result clickable" data-ticket-id="${escapeHtml(ticket.id)}" role="button" tabindex="0">
      <div class="ticket-result-main">
        <div class="ticket-heading"><strong>#${escapeHtml(ticket.id)}</strong><span class="pill pill-status">${escapeHtml(ticket.status || "Unknown")}</span></div>
        <div class="ticket-meta">${escapeHtml(ticket.ticket_type_label || "Unknown type")} · ${escapeHtml(ticket.created_on || "Unknown date")}</div>
        <p>${escapeHtml(ticket.description || ticket.subject || "No problem description loaded.")}</p>
        <div class="result-resolution"><strong>Resolution</strong><span>${escapeHtml(ticket.resolution || "No resolution currently saved.")}</span></div>
      </div>
      <div class="row-actions"><span class="muted small">Click to view / change</span></div>
    </article>`).join("");
  els.searchResults.querySelectorAll(".ticket-result").forEach((node) => {
    const open = () => { const ticket = searchTickets.find((item) => String(item.id) === node.dataset.ticketId); if (ticket) showDetail(ticket); };
    node.addEventListener("click", open);
    node.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); open(); } });
  });
}

function openModal(status) {
  modalStatus = status;
  modalView = "list";
  modalTicket = null;
  els.modal.classList.remove("hidden");
  renderModalList();
}

function closeModal() {
  modalStatus = null;
  modalView = "list";
  modalTicket = null;
  els.modal.classList.add("hidden");
}

function renderModalList() {
  if (!modalStatus) return;
  const status = modalStatus;
  const tickets = (latest?.tickets || []).filter((ticket) => {
    if (status === "found") return ticket.status === "found" || ticket.status === "processing";
    return ticket.status === status;
  });
  els.modalTitle.textContent = MODAL_TITLES[status] || "Tickets";
  if (!tickets.length) {
    els.modalBody.innerHTML = "<p class='muted'>No tickets to show.</p>";
    return;
  }
  els.modalBody.innerHTML = `<div class="results">${tickets.map((ticket) => `
    <article class="ticket-result clickable" data-ticket-id="${escapeHtml(ticket.id)}" role="button" tabindex="0">
      <div class="ticket-result-main">
        <div class="ticket-heading"><strong>#${escapeHtml(ticket.id)}</strong><span class="pill pill-${escapeHtml(ticket.status || status)}">${escapeHtml(ticket.status || status)}</span></div>
        <p>${escapeHtml(ticket.subject || ticket.description || "No problem description.")}</p>
        ${ticket.reason ? `<div class="ticket-meta">${escapeHtml(ticket.reason)}</div>` : ""}
      </div>
    </article>`).join("")}</div>`;
  els.modalBody.querySelectorAll(".ticket-result").forEach((node) => {
    const open = () => { const ticket = (latest?.tickets || []).find((item) => String(item.id) === node.dataset.ticketId); if (ticket) showDetail(ticket); };
    node.addEventListener("click", open);
    node.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); open(); } });
  });
}

function showDetail(ticket) {
  modalView = "detail";
  modalTicket = { ...ticket };
  els.modal.classList.remove("hidden");
  renderModalDetail();
}

function renderModalDetail() {
  const ticket = modalTicket;
  if (!ticket) return;
  els.modalTitle.textContent = `Ticket #${ticket.id}`;
  els.modalBody.innerHTML = `
    <div class="summary-sheet">
      <div class="summary-grid">
        <div><span class="summary-label">Ticket</span><strong>#${escapeHtml(ticket.id)}</strong></div>
        <div><span class="summary-label">Created</span><strong>${escapeHtml(ticket.created_on || "Unknown")}</strong></div>
        <div><span class="summary-label">Status</span><strong>${escapeHtml(ticket.status || "Unknown")}</strong></div>
        <div><span class="summary-label">Type</span><strong>${escapeHtml(ticket.ticket_type_label || ticket.type || "Unknown")}</strong></div>
      </div>
      <h3>Problem Description</h3>
      <p>${escapeHtml(ticket.description || ticket.subject || "No description available.")}</p>
      <h3>Current Resolution</h3>
      <div class="current-resolution">${escapeHtml(ticket.resolution || "No resolution currently saved.")}</div>
      <div id="detailMessage" class="muted small"></div>
      <div class="row-actions summary-actions">
        <button id="redoBtn" class="btn">Redo Resolution</button>
        <button id="deleteBtn" class="btn btn-danger">Delete Resolution</button>
        <button id="closeDetailBtn" class="btn btn-ghost">Close</button>
      </div>
    </div>`;
  document.getElementById("redoBtn").addEventListener("click", () => redoResolution(ticket));
  document.getElementById("deleteBtn").addEventListener("click", () => deleteResolution(ticket));
  document.getElementById("closeDetailBtn").addEventListener("click", closeDetail);
}

function closeDetail() {
  if (modalStatus) { modalView = "list"; modalTicket = null; renderModalList(); }
  else { closeModal(); }
}

async function redoResolution(ticket) {
  const message = document.getElementById("detailMessage");
  if (message) message.textContent = "Regenerating resolution...";
  const result = await postJson(`/api/tickets/${encodeURIComponent(ticket.id)}/redo`, { created_on: ticket.created_on });
  if (result.ok) {
    ticket.resolution = result.resolution || ticket.resolution;
    if (modalTicket && String(modalTicket.id) === String(ticket.id)) { modalTicket = ticket; renderModalDetail(); }
    syncSearchTickets(ticket);
  }
  const after = document.getElementById("detailMessage");
  if (after) after.textContent = result.message || "";
}

async function deleteResolution(ticket) {
  if (!confirm(`Delete the resolution for ticket #${ticket.id}?`)) return;
  const message = document.getElementById("detailMessage");
  if (message) message.textContent = "Deleting resolution...";
  const result = await postJson(`/api/tickets/${encodeURIComponent(ticket.id)}/resolution`, { text: "", created_on: ticket.created_on });
  if (result.ok) {
    ticket.resolution = "";
    if (modalTicket && String(modalTicket.id) === String(ticket.id)) { modalTicket = ticket; renderModalDetail(); }
    syncSearchTickets(ticket);
  }
  const after = document.getElementById("detailMessage");
  if (after) after.textContent = result.message || "";
}

function syncSearchTickets(ticket) {
  searchTickets = searchTickets.map((item) => String(item.id) === String(ticket.id) ? { ...item, resolution: ticket.resolution } : item);
  if (latest?.tickets) {
    latest.tickets = latest.tickets.map((item) => String(item.id) === String(ticket.id) ? { ...item, resolution: ticket.resolution } : item);
  }
  renderSearchResults();
}

els.checkBtn.addEventListener("click", () => post("/api/check"));
els.startBtn.addEventListener("click", () => post("/api/start"));
els.stopBtn.addEventListener("click", () => post("/api/stop"));
els.backgroundToggle.addEventListener("change", async () => {
  const value = els.backgroundToggle.checked;
  const result = await postJson("/api/background", { background: value });
  els.controlMsg.textContent = result.message || "";
  setTimeout(() => (els.controlMsg.textContent = ""), 4000);
});
els.searchBtn.addEventListener("click", search);
els.searchInput.addEventListener("input", renderSearchResults);
els.statusFilter.addEventListener("change", renderSearchResults);
els.typeFilter.addEventListener("change", renderSearchResults);
els.clearSearchBtn.addEventListener("click", () => {
  els.searchInput.value = "";
  els.dateFrom.value = "";
  els.dateTo.value = "";
  els.statusFilter.value = "";
  els.typeFilter.value = "";
  searchTickets = [];
  els.searchResults.className = "results empty-state";
  els.searchResults.textContent = "Choose a date range and search to retrieve tickets.";
  els.resultCount.textContent = "";
});
els.modalClose.addEventListener("click", closeModal);
els.modal.addEventListener("click", (event) => { if (event.target === els.modal) closeModal(); });
document.querySelectorAll(".stat.clickable").forEach((card) => {
  const open = () => openModal(card.dataset.status);
  card.addEventListener("click", open);
  card.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); open(); } });
});

async function init() {
  try { render(await fetch("/api/status").then((response) => response.json())); } catch (error) { els.searchMsg.textContent = "Could not load status: " + error; }
  const source = new EventSource("/api/events");
  source.onmessage = (event) => { try { render(JSON.parse(event.data)); } catch (_) {} };
}
init();
