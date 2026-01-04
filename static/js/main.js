// main.js - JavaScript for backend calls and UI updates

// ============================================================
// TRIGGER HANDLING
// ============================================================

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

// ============================================================
// SESSION CONTROL
// ============================================================

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

async function forceEnd() {
    hideSuggestEnd();
    
    try {
        const response = await fetch("/force-end", {
            method: "POST",
        });

        if (!response.ok) {
            console.error("Force end error:", await response.text());
            return;
        }

        const data = await response.json();
        updateUI(data);
    } catch (err) {
        console.error("Force end network error:", err);
    }
}

function hideSuggestEnd() {
    const notification = document.getElementById("suggest-end-notification");
    if (notification) {
        notification.classList.add("hidden");
    }
}

// ============================================================
// UI UPDATE
// ============================================================

function updateUI(data) {
    // Update conversation
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
        
        // Dodaj tip sporočila (suggestion)
        if (msg.type) {
            wrapper.classList.add(`${msg.type}-type`);
        }

        const bubble = document.createElement("div");
        bubble.classList.add("message-bubble");
        bubble.textContent = msg.text;
        
        // Dodaj speech act badge, če je na voljo
        if (data.speech_act && msg.sender === "robot" && data.conversation.indexOf(msg) === data.conversation.length - 1) {
            const badge = document.createElement("span");
            badge.classList.add("speech-act-badge");
            badge.textContent = data.speech_act;
            bubble.appendChild(badge);
        }

        wrapper.appendChild(bubble);
        chatBox.appendChild(wrapper);
    });

    // Scroll na dno
    chatBox.scrollTop = chatBox.scrollHeight;

    // Update FSM diagram
    updateFSMDiagram(data.current_state);
    
    // Update current state display
    updateStateDisplay(data.state_info);
    
    // Update statistics
    if (data.statistics) {
        updateStatistics(data.statistics);
    }

    // END notification
    const endNotification = document.getElementById("end-notification");
    if (data.is_final) {
        showEndNotification(data);
    } else {
        endNotification.classList.add("hidden");
    }
    
    // Suggest end notification
    const suggestNotification = document.getElementById("suggest-end-notification");
    if (data.should_suggest_end && !data.is_final) {
        if (suggestNotification) {
            suggestNotification.classList.remove("hidden");
        }
    } else {
        // Skrij obvestilo, če should_suggest_end ni True (npr. ko uporabnik klikne pozitiven trigger)
        if (suggestNotification) {
            suggestNotification.classList.add("hidden");
        }
    }
}

function updateFSMDiagram(currentState) {
    const states = document.querySelectorAll(".fsm-state");
    states.forEach((state) => {
        const stateId = state.getAttribute("data-state");
        if (stateId === currentState) {
            state.classList.add("active");
        } else {
            state.classList.remove("active");
        }
    });
}

function updateStateDisplay(stateInfo) {
    const display = document.getElementById("current-state-display");
    const nameEl = document.getElementById("current-state-name");
    const iconEl = display?.querySelector(".state-display-icon");
    
    if (display && stateInfo) {
        // Remove old color classes
        display.className = display.className.replace(/state-\w+/g, "");
        display.classList.add(`state-${stateInfo.color}`);
        
        if (nameEl) nameEl.textContent = stateInfo.name;
        if (iconEl) iconEl.textContent = stateInfo.icon;
    }
}

function updateStatistics(stats) {
    const elements = {
        "stat-positive": stats.positive_interactions,
        "stat-negative": stats.negative_interactions,
        "stat-escalation": stats.total_escalations,
        "stat-steps": stats.step_count,
        "stat-success": `${stats.success_steps}/5`,
    };
    
    for (const [id, value] of Object.entries(elements)) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    }
    
    // Highlight escalation if high
    const escEl = document.getElementById("stat-escalation");
    if (escEl) {
        if (stats.total_escalations >= 3) {
            escEl.classList.add("warning");
        } else {
            escEl.classList.remove("warning");
        }
    }
}

function showEndNotification(data) {
    const notification = document.getElementById("end-notification");
    const reasonText = document.getElementById("end-reason-text");
    
    // Set reason text
    const reasons = {
        "success_steps": "Odlično! Uspešno si zaključil vse korake vaje. 🎉",
        "max_escalations": "Seja je bila zaključena zaradi preveč težav.",
        "forced": "Seja je bila zaključena na tvojo željo.",
        "": "Trening je bil uspešno zaključen.",
    };
    
    if (reasonText && data.end_reason !== undefined) {
        reasonText.textContent = reasons[data.end_reason] || reasons[""];
    }
    
    // Set final stats
    if (data.statistics) {
        const finalSteps = document.getElementById("final-steps");
        const finalPositive = document.getElementById("final-positive");
        const finalEscalation = document.getElementById("final-escalation");
        
        if (finalSteps) finalSteps.textContent = data.statistics.step_count;
        if (finalPositive) finalPositive.textContent = data.statistics.positive_interactions;
        if (finalEscalation) finalEscalation.textContent = data.statistics.total_escalations;
    }
    
    // Reset star ratings
    resetStarRatings();
    
    notification.classList.remove("hidden");
}

// ============================================================
// EVALUATION (STAR RATING)
// ============================================================

// Shramba ocen
const evaluationRatings = {
    supportive: 0,
    understandable: 0,
    non_intrusive: 0
};

// Inicializacija star rating
document.addEventListener("DOMContentLoaded", () => {
    initStarRatings();
});

function initStarRatings() {
    document.querySelectorAll(".star-rating").forEach(ratingContainer => {
        const question = ratingContainer.dataset.question;
        const stars = ratingContainer.querySelectorAll(".star");
        
        stars.forEach(star => {
            // Hover effect
            star.addEventListener("mouseenter", () => {
                const value = parseInt(star.dataset.value);
                highlightStars(ratingContainer, value);
            });
            
            // Click to select
            star.addEventListener("click", () => {
                const value = parseInt(star.dataset.value);
                evaluationRatings[question] = value;
                selectStars(ratingContainer, value);
            });
        });
        
        // Reset on mouse leave if not selected
        ratingContainer.addEventListener("mouseleave", () => {
            const selectedValue = evaluationRatings[question];
            if (selectedValue > 0) {
                selectStars(ratingContainer, selectedValue);
            } else {
                resetStars(ratingContainer);
            }
        });
    });
}

function highlightStars(container, value) {
    const stars = container.querySelectorAll(".star");
    stars.forEach(star => {
        const starValue = parseInt(star.dataset.value);
        star.textContent = starValue <= value ? "★" : "☆";
        star.classList.toggle("highlighted", starValue <= value);
    });
}

function selectStars(container, value) {
    const stars = container.querySelectorAll(".star");
    stars.forEach(star => {
        const starValue = parseInt(star.dataset.value);
        star.textContent = starValue <= value ? "★" : "☆";
        star.classList.toggle("selected", starValue <= value);
        star.classList.remove("highlighted");
    });
}

function resetStars(container) {
    const stars = container.querySelectorAll(".star");
    stars.forEach(star => {
        star.textContent = "☆";
        star.classList.remove("selected", "highlighted");
    });
}

function resetStarRatings() {
    evaluationRatings.supportive = 0;
    evaluationRatings.understandable = 0;
    evaluationRatings.non_intrusive = 0;
    
    document.querySelectorAll(".star-rating").forEach(container => {
        resetStars(container);
    });
}

async function submitEvaluation() {
    const btn = document.getElementById("submit-eval-btn");
    btn.disabled = true;
    btn.textContent = "Oddajam...";
    
    try {
        const response = await fetch("/api/evaluate-session", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                supportive: evaluationRatings.supportive || null,
                understandable: evaluationRatings.understandable || null,
                non_intrusive: evaluationRatings.non_intrusive || null
            })
        });
        
        if (!response.ok) {
            console.error("Evaluation error:", await response.text());
        }
        
        // Reset in nova seja
        await resetSession();
    } catch (err) {
        console.error("Evaluation network error:", err);
        btn.disabled = false;
        btn.textContent = "Oddaj oceno in začni novo sejo";
    }
}

function skipEvaluation() {
    resetSession();
}
