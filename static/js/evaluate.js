// evaluate.js - JavaScript za stran evalvacije sej

// Ikone scenarijev
const SCENARIO_ICONS = {
    calm: "😊",
    confused: "🤔",
    distracted: "👀",
    stressed: "😰",
    critical: "🚨"
};

const SCENARIO_NAMES = {
    calm: "Mirna seja",
    confused: "Pogosto zmeden",
    distracted: "Odvrača pozornost",
    stressed: "Pod stresom",
    critical: "Kritična seja"
};

let sessions = [];
let selectedSessionId = null;

// Naloži seje
async function loadSessions() {
    try {
        const response = await fetch('/api/all-sessions');
        sessions = await response.json();
        renderSessionList();
    } catch (err) {
        console.error('Napaka pri nalaganju sej:', err);
        document.getElementById('session-list').innerHTML = 
            '<p class="error-text">Napaka pri nalaganju sej.</p>';
    }
}

function renderSessionList() {
    const list = document.getElementById('session-list');
    
    if (sessions.length === 0) {
        list.innerHTML = '<p class="empty-text">Ni preteklih sej.</p>';
        return;
    }
    
    list.innerHTML = sessions.map(s => `
        <div class="session-item ${selectedSessionId === s.id ? 'selected' : ''}" 
             onclick="selectSession(${s.id})">
            <div class="session-main">
                <div class="session-info">
                    <span class="session-id">Seja #${s.id}</span>
                    <span class="session-date">${formatDate(s.started_at)}</span>
                </div>
                <div class="session-scenario-badge" title="${SCENARIO_NAMES[s.scenario_type] || 'Neznano'}">
                    ${SCENARIO_ICONS[s.scenario_type] || '❓'}
                </div>
            </div>
            <div class="session-stats">
                <div class="session-stat">
                    <div class="session-stat-value">${s.step_count}</div>
                    <div class="session-stat-label">Korakov</div>
                </div>
                <div class="session-stat">
                    <div class="session-stat-value">${s.escalation_count}</div>
                    <div class="session-stat-label">Eskalacij</div>
                </div>
                <div class="session-stat">
                    <div class="session-stat-value">${s.scenario_confidence}%</div>
                    <div class="session-stat-label">Ujemanje</div>
                </div>
            </div>
            <div class="session-badges">
                <span class="${s.completed ? 'completed-badge' : 'incomplete-badge'}">
                    ${s.completed ? '✓' : '...'}
                </span>
                ${s.has_evaluation ? '<span class="eval-badge">⭐</span>' : ''}
            </div>
        </div>
    `).join('');
}

async function selectSession(sessionId) {
    selectedSessionId = sessionId;
    renderSessionList();
    
    // Naloži podrobnosti
    try {
        const response = await fetch(`/api/session/${sessionId}`);
        const data = await response.json();
        displaySessionDetails(data);
    } catch (err) {
        console.error('Napaka pri nalaganju podrobnosti:', err);
    }
}

function displaySessionDetails(data) {
    document.getElementById('no-selection').classList.add('hidden');
    document.getElementById('session-details').classList.remove('hidden');
    
    const { session, interactions, statistics, functional_evaluation } = data;
    
    // FUNKCIONALNA EVALVACIJA
    if (functional_evaluation) {
        const scenario = functional_evaluation.scenario_classification;
        const fsmMetrics = functional_evaluation.fsm_metrics;
        
        // Scenarij badge
        document.getElementById('scenario-icon').textContent = scenario?.icon || '❓';
        document.getElementById('scenario-name').textContent = scenario?.name || 'Neznano';
        document.getElementById('scenario-confidence').textContent = `${functional_evaluation.confidence}% ujemanje`;
        document.getElementById('scenario-description').textContent = scenario?.description || '';
        
        // Nastavi barvo glede na scenarij
        const badge = document.getElementById('scenario-badge');
        badge.className = 'scenario-badge scenario-' + (scenario?.id || 'unknown');
        
        // FSM metrike
        document.getElementById('fsm-linearity').textContent = fsmMetrics.linearity_score + '%';
        document.getElementById('fsm-efficiency').textContent = fsmMetrics.efficiency_score + '%';
        document.getElementById('fsm-forward').textContent = fsmMetrics.forward_progress;
        document.getElementById('fsm-backward').textContent = fsmMetrics.backward_moves;
        
        // Progress bari
        document.getElementById('fsm-linearity-bar').style.width = fsmMetrics.linearity_score + '%';
        document.getElementById('fsm-efficiency-bar').style.width = fsmMetrics.efficiency_score + '%';
        
        // Povzetek
        document.getElementById('summary-text').textContent = functional_evaluation.summary;
    }
    
    // Osnovne metrike
    document.getElementById('metric-steps').textContent = statistics.step_count;
    document.getElementById('metric-positive').textContent = statistics.positive_interactions;
    document.getElementById('metric-escalations').textContent = statistics.total_escalations;
    document.getElementById('metric-duration').textContent = formatDuration(session.started_at, session.ended_at);
    document.getElementById('metric-ratio').textContent = Math.round(statistics.positive_ratio * 100) + '%';
    document.getElementById('metric-triggers').textContent = statistics.unique_triggers;
    
    // Uporabniška evalvacija
    if (session.rating_supportive !== null) {
        document.getElementById('user-evaluation').classList.remove('hidden');
        document.getElementById('no-evaluation').classList.add('hidden');
        document.getElementById('rating-supportive').innerHTML = renderStars(session.rating_supportive);
        document.getElementById('rating-understandable').innerHTML = renderStars(session.rating_understandable);
        document.getElementById('rating-non-intrusive').innerHTML = renderStars(session.rating_non_intrusive);
    } else {
        document.getElementById('user-evaluation').classList.add('hidden');
        document.getElementById('no-evaluation').classList.remove('hidden');
    }
    
    // Potek seje
    const traceBody = document.getElementById('trace-body');
    traceBody.innerHTML = interactions.map((i, idx) => `
        <tr>
            <td>${idx + 1}</td>
            <td>${i.trigger}</td>
            <td>${i.inferred_intent || '-'}</td>
            <td>
                <span class="state-badge ${i.state_after === 'S4_FEEDBACK' ? 'final' : ''}">
                    ${i.state_after}
                </span>
            </td>
            <td>${i.escalation_count}</td>
        </tr>
    `).join('');
    
    // Povzetek naslov
    const summary = document.getElementById('eval-summary');
    const summaryTitle = document.getElementById('summary-title');
    
    if (session.completed) {
        summary.classList.remove('failed');
        summaryTitle.textContent = '📊 Povzetek evalvacije';
    } else {
        summary.classList.add('failed');
        summaryTitle.textContent = '⚠️ Seja ni bila zaključena';
    }
}

function renderStars(rating) {
    if (rating === null || rating === undefined) return '-';
    const filled = '★'.repeat(rating);
    const empty = '☆'.repeat(5 - rating);
    return `<span class="stars">${filled}${empty}</span> <span class="rating-num">(${rating}/5)</span>`;
}

function formatDate(isoString) {
    if (!isoString) return '-';
    return new Date(isoString).toLocaleString('sl-SI', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDuration(start, end) {
    if (!start || !end) return '-';
    const ms = new Date(end) - new Date(start);
    const seconds = Math.floor(ms / 1000);
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
}

// Inicializacija ob nalaganju strani
document.addEventListener('DOMContentLoaded', loadSessions);

