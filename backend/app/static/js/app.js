// Global State
let currentAnalysis = null;
let currentContractId = null;
let activeClauseId = null;
let sampleContracts = [];

// CUAD 15 Categories
const CUAD_CATEGORIES = [
    "Parties", "Effective Date", "Expiration Date", "Termination", "Notice",
    "Renewal", "Payment", "Penalties", "Indemnification", "Limitation of Liability",
    "Governing Law", "Dispute Resolution", "Assignment", "Obligations", "Confidentiality"
];

// Initialize on DOM Loaded
document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initUploadDropzone();
    initPasteDrawer();
    initFilters();
    loadSampleContracts();
    loadContractHistory();
    populateCategoryFilter();
    setupExportButtons();
});

// Tab Navigation
function initTabs() {
    const navButtons = document.querySelectorAll(".nav-btn");
    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-tab");
            switchTab(targetId);
        });
    });
}

function switchTab(targetId) {
    document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
    document.querySelectorAll(".nav-btn").forEach(el => el.classList.remove("active"));
    
    // Hide processing view if switching away
    document.getElementById("processing-view").style.display = "none";
    
    const targetContent = document.getElementById(targetId);
    if (targetContent) {
        targetContent.style.display = "block";
        targetContent.classList.add("active");
    }
    
    const targetBtn = document.querySelector(`[data-tab="${targetId}"]`);
    if (targetBtn) {
        targetBtn.classList.add("active");
    }
}

function enableNavButtons() {
    document.getElementById("nav-dashboard-btn").disabled = false;
    document.getElementById("nav-analysis-btn").disabled = false;
}

// Upload & Dropzone Handling
function initUploadDropzone() {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("file-input");
    const browseBtn = document.getElementById("browse-btn");

    browseBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files && fileInput.files.length > 0) {
            handleFileUpload(fileInput.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append("file", file);

    startProcessingAnimation(file.name);

    try {
        updateProcessingStep(1, "Uploading & validating document format...");
        const uploadRes = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });

        if (!uploadRes.ok) {
            const err = await uploadRes.json();
            throw new Error(err.detail || "Upload validation failed.");
        }

        const uploadData = await uploadRes.json();
        await runAnalysisPipeline(uploadData.filename, uploadData.full_text, uploadData.pages);
    } catch (err) {
        alert("Upload error: " + err.message);
        switchTab("upload-tab");
    }
}

// Paste Drawer Handling
function initPasteDrawer() {
    const toggleBtn = document.getElementById("paste-toggle-btn");
    const drawer = document.getElementById("paste-drawer");
    const analyzeBtn = document.getElementById("analyze-pasted-btn");
    const clearBtn = document.getElementById("clear-paste-btn");
    const textarea = document.getElementById("pasted-text");

    toggleBtn.addEventListener("click", () => {
        drawer.classList.toggle("open");
    });

    clearBtn.addEventListener("click", () => {
        textarea.value = "";
    });

    analyzeBtn.addEventListener("click", async () => {
        const text = textarea.value.trim();
        if (!text) {
            alert("Please paste contract text first.");
            return;
        }
        startProcessingAnimation("Pasted_Contract.txt");
        await runAnalysisPipeline("Pasted_Contract.txt", text, null);
    });
}

// Load Benchmark Sample Contracts
async function loadSampleContracts() {
    const container = document.getElementById("samples-container");
    try {
        const res = await fetch("/api/samples");
        const samples = await res.json();
        sampleContracts = samples;
        
        container.innerHTML = "";
        samples.forEach(sample => {
            const isRejectTest = sample.key === "academic_paper";
            const item = document.createElement("div");
            item.className = `sample-item ${isRejectTest ? 'reject-test' : 'accept-test'}`;
            item.innerHTML = `
                <div class="sample-info">
                    <h4>
                        ${sample.title}
                        <span class="sample-domain-tag">${sample.domain}</span>
                    </h4>
                    <p>${sample.description}</p>
                </div>
                <button class="sample-run-btn" data-key="${sample.key}">
                    <i class="fa-solid fa-play"></i> Run Test
                </button>
            `;

            item.addEventListener("click", () => runSampleAnalysis(sample));
            container.appendChild(item);
        });
    } catch (err) {
        container.innerHTML = `<p style="color: var(--color-high);">Failed to load samples: ${err.message}</p>`;
    }
}

async function runSampleAnalysis(sample) {
    startProcessingAnimation(sample.filename);
    await runAnalysisPipeline(sample.filename, sample.text, null);
}

// Processing Animation Stepper (Section 2.2 Figure 1)
function startProcessingAnimation(filename) {
    document.querySelectorAll(".tab-content").forEach(el => el.style.display = "none");
    const processingView = document.getElementById("processing-view");
    processingView.style.display = "block";
    document.getElementById("processing-filename").textContent = `Analyzing: ${filename}`;

    // Reset steps
    for (let i = 1; i <= 8; i++) {
        const stepEl = document.getElementById(`step-${i}`);
        if (stepEl) {
            stepEl.classList.remove("active", "completed");
        }
        const lineEl = document.getElementById(`line-${i}`);
        if (lineEl) {
            lineEl.classList.remove("completed");
        }
    }
}

function updateProcessingStep(stepNum, statusText) {
    for (let i = 1; i < stepNum; i++) {
        const stepEl = document.getElementById(`step-${i}`);
        if (stepEl) {
            stepEl.classList.remove("active");
            stepEl.classList.add("completed");
        }
        const lineEl = document.getElementById(`line-${i}`);
        if (lineEl) lineEl.classList.add("completed");
    }
    const currentStep = document.getElementById(`step-${stepNum}`);
    if (currentStep) {
        currentStep.classList.add("active");
    }
    document.getElementById("step-status-text").textContent = statusText;
}

// Execute Analysis Pipeline
async function runAnalysisPipeline(filename, text, pages) {
    try {
        updateProcessingStep(1, "Validating file format and extractable text...");
        await delay(300);

        updateProcessingStep(2, "Extracting text and preserving page structures...");
        await delay(300);

        updateProcessingStep(3, "Screening legal domains (Section 4)...");
        await delay(350);

        updateProcessingStep(4, "Segmenting numbered clauses and section headings...");
        await delay(350);

        updateProcessingStep(5, "Classifying into 15 CUAD candidate categories...");
        await delay(350);

        updateProcessingStep(6, "Evaluating rule-based risk triggers & missing clauses...");
        await delay(350);

        updateProcessingStep(7, "Calculating multi-factor hybrid risk score...");
        await delay(350);

        updateProcessingStep(8, "Generating LLM plain-language explanations & evidence...");

        const response = await fetch("/api/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename, text, pages })
        });

        const result = await response.json();

        // Check if Rejected during Domain Screening (Section 4.1)
        if (result.status === "Rejected") {
            showRejectionModal(result);
            return;
        }

        currentAnalysis = result;
        currentContractId = result.contract_id;
        enableNavButtons();
        
        // Render Dashboard & Inspector
        renderDashboard(result);
        renderClauses(result.clauses, result.risks);
        loadContractHistory();

        // Switch to Dashboard
        switchTab("dashboard-tab");
    } catch (err) {
        alert("Pipeline error: " + err.message);
        switchTab("upload-tab");
    }
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Domain Screening Rejection Modal (Section 4.1)
function showRejectionModal(result) {
    const modal = document.getElementById("rejection-modal");
    const title = document.getElementById("modal-rejection-title");
    const msg = document.getElementById("modal-rejection-msg");

    title.textContent = `Document Rejected: ${result.screening.contract_type || "Out of Domain"}`;
    msg.textContent = result.message || "This document does not match supported legal contract domains.";

    modal.style.display = "flex";

    document.getElementById("btn-close-rejection-modal").onclick = () => {
        modal.style.display = "none";
        switchTab("upload-tab");
    };
}

// Render Dashboard View (Section 16.3)
function renderDashboard(data) {
    document.getElementById("dash-filename").textContent = data.filename;
    document.getElementById("dash-domain-tag").innerHTML = `<i class="fa-solid fa-scale-balanced"></i> ${data.screening.domain}`;
    document.getElementById("dash-type-tag").innerHTML = `<i class="fa-solid fa-file-contract"></i> ${data.screening.contract_type}`;
    document.getElementById("dash-conf-tag").innerHTML = `<i class="fa-solid fa-circle-check"></i> ${Math.round(data.screening.confidence * 100)}% Confidence`;

    // Overall Score
    const scoreVal = document.getElementById("dash-overall-score");
    const riskTier = document.getElementById("dash-risk-tier");
    const scoreBar = document.getElementById("dash-score-bar");

    scoreVal.textContent = Math.round(data.overall_score);
    riskTier.textContent = `${data.risk_level.toUpperCase()} RISK`;

    scoreVal.className = `score-value color-${data.risk_level.toLowerCase()}`;
    riskTier.className = `risk-badge badge-${data.risk_level.toLowerCase()}`;
    scoreBar.className = `score-bar-fill fill-${data.risk_level.toLowerCase()}`;
    scoreBar.style.width = `${Math.min(100, Math.max(8, data.overall_score))}%`;

    // Counts
    document.getElementById("dash-count-high").textContent = data.risk_counts.high;
    document.getElementById("dash-count-med").textContent = data.risk_counts.medium;
    document.getElementById("dash-count-low").textContent = data.risk_counts.low;
    document.getElementById("dash-total-clauses").textContent = data.clauses.length;

    // Missing Clauses (Section 10.2)
    const missing = data.missing_analysis;
    document.getElementById("dash-missing-detected").textContent = `${missing.detected_count}/${missing.total_expected}`;
    const missingList = document.getElementById("dash-missing-list");
    missingList.innerHTML = "";

    if (missing.missing_clauses.length === 0) {
        missingList.innerHTML = `
            <div class="missing-item-row" style="color: #10b981;">
                <span><i class="fa-solid fa-check-circle"></i> All standard clauses detected!</span>
            </div>
        `;
        document.getElementById("dash-missing-flag").innerHTML = `<span class="missing-alert-badge" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border-color: rgba(16, 185, 129, 0.3);"><i class="fa-solid fa-circle-check"></i> Complete Checklist</span>`;
    } else {
        document.getElementById("dash-missing-flag").innerHTML = `<span class="missing-alert-badge"><i class="fa-solid fa-circle-exclamation"></i> ${missing.missing_clauses.length} Missing Item(s)</span>`;
        missing.missing_clauses.forEach(m => {
            const row = document.createElement("div");
            row.className = "missing-item-row";
            row.innerHTML = `
                <span class="missing-item-name"><i class="fa-solid fa-triangle-exclamation"></i> ${m.name}</span>
                <span style="font-size: 11px; color: var(--text-muted);">${m.importance}</span>
            `;
            missingList.appendChild(row);
        });
    }

    // Fusion Model Factors (Section 11.3)
    const bd = data.score_breakdown;
    document.getElementById("fusion-rule-val").textContent = bd.rule_score.toFixed(1);
    document.getElementById("fusion-rule-bar").style.width = `${bd.rule_score}%`;
    document.getElementById("fusion-rule-contrib").textContent = `+${bd.rule_contribution.toFixed(1)}`;

    document.getElementById("fusion-ml-val").textContent = bd.ml_score.toFixed(1);
    document.getElementById("fusion-ml-bar").style.width = `${bd.ml_score}%`;
    document.getElementById("fusion-ml-contrib").textContent = `+${bd.ml_contribution.toFixed(1)}`;

    document.getElementById("fusion-llm-val").textContent = bd.llm_score.toFixed(1);
    document.getElementById("fusion-llm-bar").style.width = `${bd.llm_score}%`;
    document.getElementById("fusion-llm-contrib").textContent = `+${bd.llm_contribution.toFixed(1)}`;

    document.getElementById("fusion-missing-val").textContent = bd.missing_score.toFixed(1);
    document.getElementById("fusion-missing-bar").style.width = `${bd.missing_score}%`;
    document.getElementById("fusion-missing-contrib").textContent = `+${bd.missing_contribution.toFixed(1)}`;

    // AI Executive Summary
    document.getElementById("dash-summary-text").textContent = data.summary;
}

// Render Detailed Clause Inspector (Section 16.4)
function renderClauses(clauses, risks) {
    const listScroll = document.getElementById("clause-items-scroll");
    const countSpan = document.getElementById("clause-list-count");
    listScroll.innerHTML = "";

    const riskFilter = document.getElementById("filter-risk").value;
    const catFilter = document.getElementById("filter-category").value;
    const searchText = document.getElementById("search-clauses").value.toLowerCase();

    // Map risks by clause_id
    const riskMap = {};
    risks.forEach(r => {
        if (r.clause_id) {
            if (!riskMap[r.clause_id]) riskMap[r.clause_id] = [];
            riskMap[r.clause_id].push(r);
        }
    });

    let visibleCount = 0;
    let firstVisibleClause = null;

    clauses.forEach((c) => {
        const clauseRisks = riskMap[c.id] || [];
        const maxRiskLevel = clauseRisks.some(r => r.risk_level === "High") ? "High" :
                            (clauseRisks.some(r => r.risk_level === "Medium") ? "Medium" : 
                            (clauseRisks.some(r => r.risk_level === "Low") ? "Low" : "Safe"));

        // Filtering
        if (riskFilter !== "ALL" && maxRiskLevel !== riskFilter) return;
        if (catFilter !== "ALL" && c.clause_type !== catFilter) return;
        if (searchText && !c.text.toLowerCase().includes(searchText) && !c.clause_number.toLowerCase().includes(searchText)) return;

        visibleCount++;
        if (!firstVisibleClause) firstVisibleClause = c;

        const item = document.createElement("div");
        item.className = `clause-nav-item ${activeClauseId === c.id ? 'active' : ''}`;
        item.setAttribute("data-id", c.id);

        const badgeClass = maxRiskLevel === "High" ? "badge-high" : (maxRiskLevel === "Medium" ? "badge-med" : (maxRiskLevel === "Low" ? "badge-low" : ""));
        const badgeLabel = maxRiskLevel === "Safe" ? "Standard" : `${maxRiskLevel} Risk`;

        item.innerHTML = `
            <div class="clause-nav-top">
                <span class="clause-nav-num">${c.clause_number}</span>
                <span class="clause-mini-badge ${badgeClass}">${badgeLabel}</span>
            </div>
            <p class="clause-nav-preview">${c.text}</p>
            <div class="clause-nav-meta">
                <span><i class="fa-solid fa-tag"></i> ${c.clause_type}</span>
                <span>Page ${c.page_number}</span>
            </div>
        `;

        item.addEventListener("click", () => {
            selectClause(c, clauseRisks);
        });

        listScroll.appendChild(item);
    });

    countSpan.textContent = visibleCount;

    // Auto-select first matching clause or active clause
    if (visibleCount > 0) {
        const toSelect = clauses.find(c => c.id === activeClauseId) || firstVisibleClause;
        selectClause(toSelect, riskMap[toSelect.id] || []);
    } else {
        renderEmptyEvidencePlaceholder();
    }
}

function selectClause(clause, clauseRisks) {
    activeClauseId = clause.id;
    document.querySelectorAll(".clause-nav-item").forEach(el => {
        el.classList.toggle("active", el.getAttribute("data-id") === clause.id);
    });

    renderEvidenceChain(clause, clauseRisks);
}

// Render Evidence Chain (Section 11.1 Figure 5)
function renderEvidenceChain(clause, risks) {
    const viewer = document.getElementById("evidence-viewer");
    
    let riskCardsHtml = "";
    if (risks.length > 0) {
        risks.forEach(r => {
            riskCardsHtml += `
                <div class="evidence-quote-box">
                    <strong><i class="fa-solid fa-quote-left"></i> Supporting Evidence Text Span (Page ${r.page_number}):</strong>
                    <div style="margin-top: 6px;">"${highlightEvidence(r.evidence)}"</div>
                </div>

                <div class="analysis-section-box what">
                    <h4><i class="fa-solid fa-file-lines"></i> 1. Plain-Language Explanation (What It Says)</h4>
                    <p>${r.plain_explanation || "Defines standard terms."}</p>
                </div>

                <div class="analysis-section-box why">
                    <h4><i class="fa-solid fa-triangle-exclamation"></i> 2. Risk Detection & Reasoning (Why It Is Risky)</h4>
                    <p>${r.risk_reasoning || r.reason}</p>
                </div>

                <div class="analysis-section-box action">
                    <h4><i class="fa-solid fa-lightbulb"></i> 3. Suggested Review & Mitigation (What to Review)</h4>
                    <p>${r.actionable_advice || r.recommendation}</p>
                </div>
            `;
        });
    } else {
        riskCardsHtml = `
            <div class="analysis-section-box action" style="border-left: 4px solid #10b981;">
                <h4><i class="fa-solid fa-check"></i> Standard Clause Profile</h4>
                <p>No critical one-sided conditions or asymmetric risk rules were triggered for this clause. Clause satisfies baseline commercial fairness standards.</p>
            </div>
        `;
    }

    viewer.innerHTML = `
        <div class="evidence-header">
            <div class="evidence-title">
                <h3>${clause.clause_number}</h3>
                <div class="evidence-sub-tags">
                    <span class="meta-tag"><i class="fa-solid fa-tag"></i> CUAD: ${clause.clause_type}</span>
                    <span class="meta-tag"><i class="fa-solid fa-file"></i> Page ${clause.page_number}</span>
                    <span class="meta-tag confidence"><i class="fa-solid fa-circle-check"></i> ${Math.round(clause.confidence * 100)}% Confidence</span>
                </div>
            </div>
        </div>

        ${riskCardsHtml}

        <div class="full-text-accordion">
            <div class="full-text-header">
                <span>FULL RAW CLAUSE TEXT</span>
                <button class="btn-link" id="copy-clause-text-btn"><i class="fa-solid fa-copy"></i> Copy Text</button>
            </div>
            <pre class="raw-clause-text">${clause.text}</pre>
        </div>
    `;

    document.getElementById("copy-clause-text-btn").onclick = () => {
        navigator.clipboard.writeText(clause.text);
        alert("Clause text copied to clipboard!");
    };
}

function highlightEvidence(evidence) {
    if (!evidence) return "";
    return evidence.replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function renderEmptyEvidencePlaceholder() {
    const viewer = document.getElementById("evidence-viewer");
    viewer.innerHTML = `
        <div class="empty-selection-placeholder">
            <i class="fa-solid fa-filter-circle-xmark"></i>
            <h3>No clauses match filter criteria</h3>
            <p>Try resetting your risk or category filters.</p>
        </div>
    `;
}

// Filter Listeners
function initFilters() {
    document.getElementById("filter-risk").addEventListener("change", () => {
        if (currentAnalysis) renderClauses(currentAnalysis.clauses, currentAnalysis.risks);
    });

    document.getElementById("filter-category").addEventListener("change", () => {
        if (currentAnalysis) renderClauses(currentAnalysis.clauses, currentAnalysis.risks);
    });

    document.getElementById("search-clauses").addEventListener("input", () => {
        if (currentAnalysis) renderClauses(currentAnalysis.clauses, currentAnalysis.risks);
    });

    document.getElementById("btn-view-clauses").addEventListener("click", () => {
        switchTab("analysis-tab");
    });
}

function populateCategoryFilter() {
    const select = document.getElementById("filter-category");
    CUAD_CATEGORIES.forEach(cat => {
        const opt = document.createElement("option");
        opt.value = cat;
        opt.textContent = cat;
        select.appendChild(opt);
    });
}

// Database History (Section 15)
async function loadContractHistory() {
    const tbody = document.getElementById("history-table-body");
    try {
        const res = await fetch("/api/contracts");
        const contracts = await res.json();

        tbody.innerHTML = "";
        if (contracts.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 30px;">No contracts stored in database yet.</td></tr>`;
            return;
        }

        contracts.forEach(c => {
            const tr = document.createElement("tr");
            const dateStr = new Date(c.upload_date).toLocaleDateString() + " " + new Date(c.upload_date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            const badgeClass = c.risk_level === "High" ? "badge-high" : (c.risk_level === "Medium" ? "badge-med" : "badge-low");

            tr.innerHTML = `
                <td><strong>${c.filename}</strong></td>
                <td>${c.contract_type}</td>
                <td>${c.domain}</td>
                <td><span class="meta-tag" style="font-size: 11px;">${c.status.toUpperCase()}</span></td>
                <td><strong>${Math.round(c.overall_score)}/100</strong></td>
                <td><span class="risk-badge ${badgeClass}" style="font-size: 11px; padding: 2px 8px;">${c.risk_level}</span></td>
                <td style="color: var(--text-muted); font-size: 12px;">${dateStr}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="loadSavedContract('${c.id}')"><i class="fa-solid fa-eye"></i></button>
                    <a href="/api/reports/${c.id}/html" target="_blank" class="btn btn-secondary btn-sm"><i class="fa-solid fa-print"></i></a>
                    <button class="btn btn-secondary btn-sm" onclick="deleteSavedContract('${c.id}')"><i class="fa-solid fa-trash" style="color: var(--color-high);"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="8" style="color: var(--color-high);">Error loading history: ${err.message}</td></tr>`;
    }

    document.getElementById("btn-refresh-history").onclick = loadContractHistory;
}

window.loadSavedContract = async function(contractId) {
    try {
        const res = await fetch(`/api/contracts/${contractId}`);
        const data = await res.json();
        
        currentContractId = contractId;
        const c = data.contract;
        const metadata = c.metadata || {};

        currentAnalysis = {
            contract_id: c.id,
            filename: c.filename,
            status: c.status,
            screening: {
                domain: c.domain,
                contract_type: c.contract_type,
                confidence: c.confidence
            },
            summary: c.summary,
            overall_score: c.overall_score,
            risk_level: c.risk_level,
            score_breakdown: metadata.fusion?.score_breakdown || {
                rule_score: 50, ml_score: 50, llm_score: 50, missing_score: 10,
                rule_contribution: 20, ml_contribution: 15, llm_contribution: 10, missing_contribution: 1
            },
            risk_counts: metadata.fusion?.counts || {
                high: data.risks.filter(r => r.risk_level === "High").length,
                medium: data.risks.filter(r => r.risk_level === "Medium").length,
                low: data.risks.filter(r => r.risk_level === "Low").length
            },
            clauses: data.clauses,
            risks: data.risks,
            missing_analysis: metadata.missing_analysis || {
                total_expected: 10, detected_count: 9, missing_clauses: []
            }
        };

        enableNavButtons();
        renderDashboard(currentAnalysis);
        renderClauses(currentAnalysis.clauses, currentAnalysis.risks);
        switchTab("dashboard-tab");
    } catch (err) {
        alert("Failed to load contract: " + err.message);
    }
};

window.deleteSavedContract = async function(contractId) {
    if (!confirm("Are you sure you want to delete this contract from the database?")) return;
    try {
        await fetch(`/api/contracts/${contractId}`, { method: "DELETE" });
        loadContractHistory();
        if (currentContractId === contractId) {
            currentContractId = null;
            currentAnalysis = null;
            document.getElementById("nav-dashboard-btn").disabled = true;
            document.getElementById("nav-analysis-btn").disabled = true;
            switchTab("history-tab");
        }
    } catch (err) {
        alert("Failed to delete: " + err.message);
    }
};

// Export Handlers
function setupExportButtons() {
    document.getElementById("btn-export-pdf").addEventListener("click", () => {
        if (!currentContractId) return;
        window.open(`/api/reports/${currentContractId}/html`, "_blank");
    });

    document.getElementById("btn-export-json").addEventListener("click", () => {
        if (!currentContractId) return;
        window.open(`/api/reports/${currentContractId}/json`, "_blank");
    });
}
