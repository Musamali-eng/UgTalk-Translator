/**
 * Main JavaScript for VisionLens AI 💖
 * Handles client-side interactions and API calls
 */

// API Configuration
const API_BASE_URL = window.location.origin;

/**
 * Make API request
 * @param {string} endpoint - API endpoint
 * @param {object} data - Request data
 * @returns {Promise} API response
 */
async function apiRequest(endpoint, data = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('💔 API request failed:', error);
        throw error;
    }
}

/**
 * Validate input text
 * @param {string} text - Input text to validate
 * @returns {object} Validation result
 */
function validateInput(text) {
    const errors = [];
    
    if (!text || text.trim().length === 0) {
        errors.push('Input text cannot be empty');
    }
    
    if (text.length > 1000) {
        errors.push('Input text must be less than 1000 characters');
    }
    
    return {
        valid: errors.length === 0,
        errors: errors
    };
}

/**
 * Format prediction result for display
 * @param {object} result - Prediction result
 * @returns {string} Formatted HTML
 */
function formatResult(result) {
    if (!result || !result.sentiment) {
        return '<p class="text-danger">Invalid result format</p>';
    }
    
    const sentimentColors = {
        'positive': 'success',
        'negative': 'danger',
        'neutral': 'warning'
    };
    
    const color = sentimentColors[result.sentiment] || 'secondary';
    const confidence = (result.confidence * 100).toFixed(1);
    
    const emoji = result.sentiment === 'positive' ? '😊' : (result.sentiment === 'negative' ? '😔' : '😐');
    
    return `
        <h5>${emoji} Sentiment: <span class="badge bg-${color}">${result.sentiment.toUpperCase()}</span></h5>
        <p><strong>Confidence:</strong> ${confidence}%</p>
        <p><strong>Score:</strong> ${result.score}</p>
        <hr>
        <p><strong>Positive words found:</strong> ${result.positive_words}</p>
        <p><strong>Negative words found:</strong> ${result.negative_words}</p>
    `;
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    const errorDiv = document.getElementById('error');
    const errorMessage = document.getElementById('errorMessage');
    
    if (errorDiv && errorMessage) {
        errorMessage.textContent = '😅 ' + message;
        errorDiv.classList.remove('d-none');
        
        // Hide after 5 seconds
        setTimeout(() => {
            errorDiv.classList.add('d-none');
        }, 5000);
    }
}

/**
 * Hide error message
 */
function hideError() {
    const errorDiv = document.getElementById('error');
    if (errorDiv) {
        errorDiv.classList.add('d-none');
    }
}

/**
 * Show results
 * @param {object} result - Result to display
 */
function showResults(result) {
    const resultsDiv = document.getElementById('results');
    const resultContent = document.getElementById('resultContent');
    
    if (resultsDiv && resultContent) {
        resultContent.innerHTML = formatResult(result);
        resultsDiv.classList.remove('d-none');
        
        // Scroll to results
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

/**
 * Hide results
 */
function hideResults() {
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.classList.add('d-none');
    }
}

/**
 * Set loading state
 * @param {boolean} loading - Loading state
 */
function setLoading(loading) {
    const predictBtn = document.getElementById('predictBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    
    if (predictBtn && btnText && btnSpinner) {
        predictBtn.disabled = loading;
        
        if (loading) {
            btnText.textContent = '⏳ Analyzing...';
            btnSpinner.classList.remove('d-none');
        } else {
            btnText.textContent = '✨ Analyze Text ✨';
            btnSpinner.classList.add('d-none');
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('💖 VisionLens AI initialized!');
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add input character counter
    const inputText = document.getElementById('inputText');
    if (inputText) {
        inputText.addEventListener('input', function() {
            const maxLength = 1000;
            const currentLength = this.value.length;
            const remaining = maxLength - currentLength;
            console.log(`💬 Characters: ${currentLength}/${maxLength}`);
        });
    }
});

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        validateInput,
        formatResult,
        showError,
        hideError,
        showResults,
        hideResults,
        setLoading
    };
}
