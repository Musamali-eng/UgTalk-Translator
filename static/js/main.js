/**
 * Main JavaScript for VisionLens AI 💖
 * Handles client-side interactions and API calls
 */

const API_BASE_URL = window.location.origin;

/**
 * Save text analysis to localStorage history
 */
function saveTextHistory(analysis) {
    let history = JSON.parse(localStorage.getItem('visionlens-history') || '[]');
    history.unshift({
        type: 'text-analysis',
        model: analysis.model_used || '',
        label: analysis.prediction?.sentiment || analysis.prediction?.category || analysis.prediction?.is_spam !== undefined ? (analysis.prediction.is_spam ? 'Spam' : 'Not Spam') : 'Unknown',
        input: analysis.input || '',
        time: new Date().toLocaleString()
    });
    if (history.length > 50) history = history.slice(0, 50);
    localStorage.setItem('visionlens-history', JSON.stringify(history));
}

/**
 * Save translation to localStorage history
 */
function saveTranslationHistory(translation) {
    let history = JSON.parse(localStorage.getItem('visionlens-translation-history') || '[]');
    history.unshift({
        type: 'translation',
        original: translation.original || '',
        translation: translation.translation || '',
        language: translation.target_language || '',
        confidence: translation.confidence ? (translation.confidence * 100).toFixed(1) : '100',
        time: new Date().toLocaleString()
    });
    if (history.length > 50) history = history.slice(0, 50);
    localStorage.setItem('visionlens-translation-history', JSON.stringify(history));
}

// ============================================================
// TEXT ANALYSIS FORM HANDLER
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    const predictionForm = document.getElementById('predictionForm');
    const inputText = document.getElementById('inputText');
    const modelSelect = document.getElementById('modelSelect');
    const predictBtn = document.getElementById('predictBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const resultsDiv = document.getElementById('results');
    const resultContent = document.getElementById('resultContent');
    const imageForm = document.getElementById('imageForm');
    const imageFile = document.getElementById('imageFile');
    const imageBtn = document.getElementById('imageBtn');
    const imageResults = document.getElementById('imageResults');
    const imageResultContent = document.getElementById('imageResultContent');
    const errorDiv = document.getElementById('error');
    const errorMessage = document.getElementById('errorMessage');
    const clearBtn = document.getElementById('clearBtn');

    console.log('💖 VisionLens AI initialized!');

    // ---- TEXT ANALYSIS ----
    if (predictionForm) {
        predictionForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const text = inputText.value.trim();
            if (!text) {
                showErrorFn('Please enter some text to analyze!');
                return;
            }
            if (text.length > 1000) {
                showErrorFn('Text must be less than 1000 characters!');
                return;
            }

            const model = modelSelect.value;

            // Loading state
            predictBtn.disabled = true;
            btnText.textContent = '⏳ Analyzing...';
            btnSpinner.classList.remove('d-none');
            hideErrorFn();
            hideResultsFn();
            hideImageResultsFn();

            try {
                const response = await fetch(API_BASE_URL + '/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text, model: model })
                });

                const data = await response.json();

                if (data.success && data.result && data.result.success) {
                    const analysis = data.result;
                    showResultsFn(analysis, model);
                    saveTextHistory(analysis);
                } else {
                    showErrorFn(data.error || data.result?.error || 'Analysis failed. Please try again.');
                }
            } catch (err) {
                showErrorFn('Network error: ' + err.message);
            } finally {
                predictBtn.disabled = false;
                btnText.textContent = '✨ Analyze Text ✨';
                btnSpinner.classList.add('d-none');
            }
        });
    }

    // ---- CLEAR BUTTON ----
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            inputText.value = '';
            hideResultsFn();
            hideErrorFn();
            hideImageResultsFn();
            inputText.focus();
        });
    }

    // ---- IMAGE ANALYSIS ----
    if (imageForm) {
        imageForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const file = imageFile.files[0];
            if (!file) {
                showErrorFn('Please select an image to analyze!');
                return;
            }

            // Loading
            imageBtn.disabled = true;
            imageBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';
            hideErrorFn();
            hideResultsFn();
            hideImageResultsFn();

            try {
                const formData = new FormData();
                formData.append('image', file);

                const response = await fetch(API_BASE_URL + '/analyze-image', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success && data.result) {
                    showImageResultsFn(data.result);
                } else {
                    showErrorFn(data.error || 'Image analysis failed. Try a different image.');
                }
            } catch (err) {
                showErrorFn('Network error: ' + err.message);
            } finally {
                imageBtn.disabled = false;
                imageBtn.innerHTML = '🖼️ Analyze Image';
            }
        });
    }

    // ---- HELPER FUNCTIONS ----
    function showResultsFn(analysis, modelName) {
        if (!resultsDiv || !resultContent) return;

        const pred = analysis.prediction || {};
        let html = '';

        if (modelName === 'sentiment_analysis') {
            const sentiment = pred.sentiment || 'unknown';
            const confidence = pred.confidence ? (pred.confidence * 100).toFixed(1) : 'N/A';
            const score = pred.score !== undefined ? pred.score : 'N/A';
            const colors = { positive: 'success', negative: 'danger', neutral: 'warning' };
            const color = colors[sentiment] || 'secondary';
            const emojis = { positive: '😊', negative: '😔', neutral: '😐' };
            const emoji = emojis[sentiment] || '🤔';

            html = `
                <div class="mb-3">
                    <h5>${emoji} Sentiment: <span class="badge bg-${color}">${sentiment.toUpperCase()}</span></h5>
                    <p><strong>Confidence:</strong> ${confidence}%</p>
                    <p><strong>Score:</strong> ${score}</p>
                </div>
                <div class="progress" style="height: 10px;">
                    <div class="progress-bar bg-${color}" style="width: ${confidence}%"></div>
                </div>
                <p class="mt-2 small text-muted">Model: ${analysis.model_used || 'Sentiment Analysis'}</p>
            `;
        } else if (modelName === 'text_classification') {
            const category = pred.category || 'unknown';
            const confidence = pred.confidence ? (pred.confidence * 100).toFixed(1) : 'N/A';
            const explanation = pred.explanation || '';

            html = `
                <div class="mb-3">
                    <h5>📂 Category: <span class="badge bg-info">${category.toUpperCase()}</span></h5>
                    <p><strong>Confidence:</strong> ${confidence}%</p>
                    ${explanation ? `<p class="text-muted">${explanation}</p>` : ''}
                </div>
                <div class="progress" style="height: 10px;">
                    <div class="progress-bar bg-info" style="width: ${confidence}%"></div>
                </div>
                <p class="mt-2 small text-muted">Model: ${analysis.model_used || 'Text Classification'}</p>
            `;
        } else if (modelName === 'spam_detection') {
            const isSpam = pred.is_spam;
            const confidence = pred.confidence ? (pred.confidence * 100).toFixed(1) : 'N/A';
            const spamScore = pred.spam_score !== undefined ? (pred.spam_score * 100).toFixed(1) : 'N/A';

            if (isSpam) {
                html = `
                    <div class="mb-3">
                        <h5>🚫 Spam Detected! <span class="badge bg-danger">SPAM</span></h5>
                        <p><strong>Spam Score:</strong> ${spamScore}%</p>
                        <p><strong>Confidence:</strong> ${confidence}%</p>
                        <div class="alert alert-danger mt-2 p-2">⚠️ This message appears to be spam!</div>
                    </div>
                `;
            } else {
                html = `
                    <div class="mb-3">
                        <h5>✅ Not Spam <span class="badge bg-success">SAFE</span></h5>
                        <p><strong>Spam Score:</strong> ${spamScore}%</p>
                        <p><strong>Confidence:</strong> ${confidence}%</p>
                        <div class="alert alert-success mt-2 p-2">✅ This message looks safe!</div>
                    </div>
                `;
            }
            html += `<p class="mt-2 small text-muted">Model: ${analysis.model_used || 'Spam Detection'}</p>`;
        } else {
            html = '<p class="text-danger">Unknown model type.</p>';
        }

        html += `<hr><p class="small text-muted">Input: ${analysis.input || ''}</p>`;
        resultContent.innerHTML = html;
        resultsDiv.classList.remove('d-none');
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function hideResultsFn() {
        if (resultsDiv) resultsDiv.classList.add('d-none');
    }

    function showImageResultsFn(result) {
        if (!imageResults || !imageResultContent) return;

        const top = result.top_prediction || {};
        const predictions = result.predictions || [];
        const model = result.model || 'Image Model';

        let html = `
            <div class="mb-3">
                <h5>🖼️ Prediction: <span class="badge bg-primary">${top.label || 'Unknown'}</span></h5>
                <p><strong>Confidence:</strong> ${top.confidence ? (top.confidence * 100).toFixed(1) + '%' : 'N/A'}</p>
                ${result.description ? `<p class="text-muted">${result.description}</p>` : ''}
            </div>
            <div class="progress" style="height: 10px;">
                <div class="progress-bar bg-primary" style="width: ${top.confidence ? (top.confidence * 100).toFixed(1) : 0}%"></div>
            </div>
        `;

        if (predictions.length > 1) {
            html += '<hr><h6>All Predictions:</h6><div class="list-group list-group-flush">';
            predictions.forEach(function(p, i) {
                const pct = (p.confidence * 100).toFixed(1);
                html += `<div class="list-group-item d-flex justify-content-between align-items-center">
                    <span>${p.label}</span>
                    <span class="badge bg-primary rounded-pill">${pct}%</span>
                </div>`;
            });
            html += '</div>';
        }

        html += `<p class="mt-2 small text-muted">Model: ${model}</p>`;
        imageResultContent.innerHTML = html;
        imageResults.classList.remove('d-none');
        imageResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function hideImageResultsFn() {
        if (imageResults) imageResults.classList.add('d-none');
    }

    function showErrorFn(message) {
        if (errorDiv && errorMessage) {
            errorMessage.textContent = '😅 ' + message;
            errorDiv.classList.remove('d-none');
            setTimeout(function() { errorDiv.classList.add('d-none'); }, 8000);
        }
    }

    function hideErrorFn() {
        if (errorDiv) errorDiv.classList.add('d-none');
    }

    // ---- CHARACTER COUNTER ----
    if (inputText) {
        inputText.addEventListener('input', function() {
            const len = this.value.length;
            const formText = this.nextElementSibling;
            if (formText) {
                formText.textContent = len + ' / 1000 characters';
                formText.style.color = len > 900 ? '#dc3545' : '#6c757d';
            }
        });
    }
});