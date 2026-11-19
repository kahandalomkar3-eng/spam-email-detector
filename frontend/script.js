const samples = {
    spam: "Congratulations! You have won a free vacation package. Click the link now and share your card details to claim it immediately.",
    ham: "Hi team, please review the updated sprint document before our 3 PM check-in. I have attached the latest draft.",
};

const emailText = document.getElementById("emailText");
const analyzeBtn = document.getElementById("analyzeBtn");
const clearBtn = document.getElementById("clearBtn");
const result = document.getElementById("result");
const resultLabel = document.getElementById("resultLabel");
const resultConfidence = document.getElementById("resultConfidence");
const status = document.getElementById("status");

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

function getApiUrl(path) {
    return `${getApiBaseUrl()}${path}`;
}

function setStatus(message, isError = false) {
    status.textContent = message;
    status.style.color = isError ? "var(--spam)" : "var(--text-soft)";
}

function toggleLoading(isLoading) {
    analyzeBtn.disabled = isLoading;
    analyzeBtn.textContent = isLoading ? "Analyzing..." : "Analyze Message";
}

function resetResult() {
    result.classList.add("hidden");
    result.classList.remove("spam", "safe");
    resultLabel.textContent = "";
    resultConfidence.textContent = "";
}

function showResult(label, confidence) {
    const isSpam = label === "spam";

    result.classList.remove("hidden", "spam", "safe");
    result.classList.add(isSpam ? "spam" : "safe");
    resultLabel.textContent = isSpam ? "Spam detected" : "Looks safe";
    resultConfidence.textContent = `Model confidence: ${(confidence * 100).toFixed(1)}%`;
}

async function analyzeMessage() {
    const message = emailText.value.trim();

    if (!message) {
        resetResult();
        setStatus("Paste an email message first so the detector has something to analyze.", true);
        return;
    }

    toggleLoading(true);
    setStatus("Sending the message to the classifier...");

    try {
        const response = await fetch(getApiUrl("/predict"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "The backend could not analyze the message.");
        }

        showResult(data.label, data.confidence);
        setStatus(`Analysis complete and saved to history as #${data.history_id}.`);
    } catch (error) {
        resetResult();
        setStatus(error.message || "Unable to reach the backend.", true);
    } finally {
        toggleLoading(false);
    }
}

analyzeBtn.addEventListener("click", analyzeMessage);

clearBtn.addEventListener("click", () => {
    emailText.value = "";
    resetResult();
    setStatus("Cleared. Paste another email whenever you are ready.");
});

document.querySelectorAll(".sample-chip").forEach((button) => {
    button.addEventListener("click", () => {
        const sampleType = button.dataset.sample;
        emailText.value = samples[sampleType];
        resetResult();
        setStatus(`Loaded a ${sampleType === "spam" ? "spam" : "safe"} sample message.`);
    });
});
