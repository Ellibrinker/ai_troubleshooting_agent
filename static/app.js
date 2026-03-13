function loadExample(type) {
    const input = document.getElementById("logInput");
    const sourceInput = document.getElementById("sourceInput");
    const environmentInput = document.getElementById("environmentInput");

    if (type === "error500") {
        input.value = "POST /api/orders returned 500. KeyError user_id in order_service.py";
        sourceInput.value = "orders-service";
        environmentInput.value = "production";
    }

    if (type === "auth401") {
        input.value = "GET /api/profile returned 401 Unauthorized. Token validation failed.";
        sourceInput.value = "auth-service";
        environmentInput.value = "staging";
    }

    if (type === "dbError") {
        input.value = "INSERT INTO users failed. Duplicate key constraint violation in database.";
        sourceInput.value = "users-service";
        environmentInput.value = "production";
    }
}

async function analyzeLog() {
    const logText = document.getElementById("logInput").value;
    const source = document.getElementById("sourceInput").value || "unknown";
    const environment = document.getElementById("environmentInput").value || "unknown";
    const resultBox = document.getElementById("result");

    if (!logText.trim()) {
        resultBox.textContent = "Please enter log text first.";
        return;
    }

    resultBox.textContent = "Analyzing...";

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                log_text: logText,
                source: source,
                environment: environment,
                timestamp: new Date().toISOString()
            })
        });

        const data = await response.json();

        if (!response.ok) {
            resultBox.innerHTML = `<p><strong>Error:</strong> ${data.error || "Request failed."}</p>`;
            return;
        }

        resultBox.innerHTML = `
            <div class="badge-row">
                <span class="badge">Mode: ${data.mode}</span>
                <span class="badge">Category: ${data.category || "general"}</span>
                <span class="badge">Severity: ${data.severity || "medium"}</span>
                <span class="badge">Source: ${data.source || "unknown"}</span>
                <span class="badge">Environment: ${data.environment || "unknown"}</span>
            </div>

            <h3>Summary</h3>
            <p>${data.summary}</p>

            <h3>Probable Causes</h3>
            <ul>
                ${(data.probable_causes || []).map(cause => `<li>${cause}</li>`).join("")}
            </ul>

            <h3>Debugging Steps</h3>
            <ul>
                ${(data.debugging_steps || []).map(step => `<li>${step}</li>`).join("")}
            </ul>

            <h3>Detected Signals</h3>
            <pre>${JSON.stringify(data.signals, null, 2)}</pre>
        `;
    } catch (error) {
        resultBox.textContent = "Request failed: " + error;
    }
}