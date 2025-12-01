// main.js - JavaScript for backend calls

// static/js/main.js

async function sendTrigger(trigger) {
    const triggerPanel = document.getElementById("trigger-panel");
    triggerPanel.classList.add("loading");

    try {
        const response = await fetch("/trigger", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ trigger }),
        });

        if (!response.ok) {
            console.error("Trigger error:", await response.text());
            triggerPanel.classList.remove("loading");
            return;
        }

        const data = await response.json();
        updateUI(data);
    } catch (err) {
        console.error("Network error:", err);
    } finally {
        triggerPanel.classList.remove("loading");
    }
}

async function resetSession() {
    try {
        const response = await fetch("/reset", {
            method: "POST",
        });

        if (!response.ok) {
            console.error("Reset error:", await response.text());
            return;
        }

        // po resetu reloadamo stran
        window.location.href = "/";
    } catch (err) {
        console.error("Reset network error:", err);
    }
}

function updateUI(data) {
    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML = "";

    data.conversation.forEach((msg) => {
        const wrapper = document.createElement("div");
        wrapper.classList.add("message");

        if (msg.sender === "robot") {
            wrapper.classList.add("robot-message");
        } else {
            wrapper.classList.add("user-message");
        }

        const bubble = document.createElement("div");
        bubble.classList.add("message-bubble");
        bubble.textContent = msg.text;

        wrapper.appendChild(bubble);
        chatBox.appendChild(wrapper);
    });

    // Scroll na dno
    chatBox.scrollTop = chatBox.scrollHeight;

    // status bar
    document.getElementById("status-state").textContent = data.current_state;
    document.getElementById("status-escalation").textContent = data.escalation;
    document.getElementById("status-steps").textContent = data.step_count;

    // END notification
    const endNotification = document.getElementById("end-notification");
    if (data.is_final) {
        endNotification.classList.remove("hidden");
    } else {
        endNotification.classList.add("hidden");
    }
}
