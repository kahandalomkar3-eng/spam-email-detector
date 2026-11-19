const totalCount = document.getElementById("totalCount");
const spamCount = document.getElementById("spamCount");
const hamCount = document.getElementById("hamCount");
const refreshBtn = document.getElementById("refreshBtn");
const exportBtn = document.getElementById("exportBtn");
const historyStatus = document.getElementById("historyStatus");
const emptyState = document.getElementById("emptyState");
const historyTableWrap = document.getElementById("historyTableWrap");
const historyTableBody = document.getElementById("historyTableBody");

function getApiBaseUrl() {
    const isLocalFile = window.location.protocol === "file:";
    const isLocalStaticPreview =
        ["127.0.0.1", "localhost"].includes(window.location.hostname) &&
        window.location.port !== "5000";

    if (isLocalFile || isLocalStaticPreview) {
        return "http://127.0.0.1:5000";
    }

    return window.location.origin;
}

function setHistoryStatus(message, isError = false) {
    historyStatus.textContent = message;
    historyStatus.style.color = isError ? "var(--spam)" : "var(--text-soft)";
}

function formatTimestamp(value) {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}

function createCell(text, className = "") {
    const cell = document.createElement("td");
    cell.textContent = text;

    if (className) {
        cell.className = className;
    }

    return cell;
}

function renderHistory(items) {
    historyTableBody.replaceChildren();

    if (!items.length) {
        emptyState.classList.remove("hidden");
        historyTableWrap.classList.add("hidden");
        return;
    }

    emptyState.classList.add("hidden");
    historyTableWrap.classList.remove("hidden");

    items.forEach((item) => {
        const row = document.createElement("tr");
        const labelCell = document.createElement("td");
        const labelPill = document.createElement("span");
        const confidence = `${(Number(item.confidence) * 100).toFixed(1)}%`;

        labelPill.textContent = item.label === "spam" ? "Spam" : "Safe";
        labelPill.className = `label-pill ${item.label === "spam" ? "spam" : "safe"}`;
        labelCell.appendChild(labelPill);

        row.appendChild(createCell(String(item.id)));
        row.appendChild(createCell(item.message, "message-cell"));
        row.appendChild(labelCell);
        row.appendChild(createCell(confidence));
        row.appendChild(createCell(formatTimestamp(item.created_at)));
        historyTableBody.appendChild(row);
    });
}

function clearHistoryView() {
    historyTableBody.replaceChildren();
    emptyState.classList.add("hidden");
    historyTableWrap.classList.add("hidden");
}

async function loadHistory() {
    refreshBtn.disabled = true;
    setHistoryStatus("Loading saved email history...");

    try {
        const response = await fetch(`${getApiBaseUrl()}/api/history`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to load history.");
        }

        totalCount.textContent = String(data.total ?? 0);
        spamCount.textContent = String(data.spam_count ?? 0);
        hamCount.textContent = String(data.ham_count ?? 0);
        renderHistory(data.items ?? []);
        setHistoryStatus(
            data.total ? `Loaded ${data.total} saved email record(s).` : "No saved emails yet."
        );
    } catch (error) {
        totalCount.textContent = "0";
        spamCount.textContent = "0";
        hamCount.textContent = "0";
        clearHistoryView();
        setHistoryStatus(error.message || "Unable to reach the backend.", true);
    } finally {
        refreshBtn.disabled = false;
    }
}

exportBtn.href = `${getApiBaseUrl()}/api/history/export`;
refreshBtn.addEventListener("click", loadHistory);

loadHistory();
