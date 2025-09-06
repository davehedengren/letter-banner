// Letter Banner Generator - Frontend JavaScript

class BannerGenerator {
    constructor() {
        this.currentJobId = null;
        this.pollInterval = null;
        this.colorPalettes = {};
        
        this.init();
    }

    async init() {
        console.log('🎨 Letter Banner Generator initialized');
        
        // Load color palettes
        await this.loadColorPalettes();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Initialize palette preview
        this.updatePalettePreview();
    }

    async loadColorPalettes() {
        try {
            const response = await fetch('/api/palettes');
            const data = await response.json();
            this.colorPalettes = data.palettes;
            console.log('✅ Color palettes loaded');
        } catch (error) {
            console.error('❌ Failed to load color palettes:', error);
            this.showError('Failed to load color palettes');
        }
    }

    setupEventListeners() {
        // Form submission
        const form = document.getElementById('banner-form');
        form.addEventListener('submit', (e) => this.handleFormSubmit(e));

        // Name input - generate letter inputs
        const nameInput = document.getElementById('banner-name');
        nameInput.addEventListener('input', (e) => this.handleNameInput(e));

        // Color palette selection
        const paletteSelect = document.getElementById('color-palette');
        paletteSelect.addEventListener('change', (e) => this.updatePalettePreview());

        // Action buttons
        const createAnotherBtn = document.getElementById('create-another');
        createAnotherBtn?.addEventListener('click', () => this.resetForm());

        const retryBtn = document.getElementById('retry-btn');
        retryBtn?.addEventListener('click', () => this.resetToForm());

        const cancelBtn = document.getElementById('cancel-btn');
        cancelBtn?.addEventListener('click', () => this.cancelGeneration());

        // Download buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('download-btn') || e.target.closest('.download-btn')) {
                const btn = e.target.classList.contains('download-btn') ? e.target : e.target.closest('.download-btn');
                const fileType = btn.getAttribute('data-file-type');
                this.downloadFile(fileType);
            }
        });
    }

    handleNameInput(event) {
        const name = event.target.value.toUpperCase();
        const lettersContainer = document.getElementById('letters-container');
        
        // Clear existing inputs
        lettersContainer.innerHTML = '';
        
        if (!name.trim()) {
            lettersContainer.innerHTML = '<p class="helper-text">Enter a name above to see letter inputs</p>';
            return;
        }

        // Extract ALL letters (including repeats) with their positions
        const letters = name.split('').filter(char => /[A-Z]/.test(char));
        
        if (letters.length === 0) {
            lettersContainer.innerHTML = '<p class="helper-text">Please enter letters (A-Z)</p>';
            return;
        }

        // Create input for each letter (including repeated letters)
        letters.forEach((letter, index) => {
            const letterDiv = document.createElement('div');
            letterDiv.className = 'letter-input';
            
            // Show position for repeated letters
            const letterCount = letters.filter(l => l === letter).length;
            const letterPosition = letters.slice(0, index + 1).filter(l => l === letter).length;
            const displayLabel = letterCount > 1 ? `${letter} (${letterPosition})` : letter;
            
            letterDiv.innerHTML = `
                <div class="letter-label">${displayLabel}</div>
                <input 
                    type="text" 
                    name="letter-${index}" 
                    data-letter="${letter}"
                    placeholder="What interest should inspire ${letter}? (e.g., hiking, cooking, music)"
                    required
                >
            `;
            lettersContainer.appendChild(letterDiv);
        });

        console.log(`📝 Generated inputs for ${letters.length} letters: ${letters.join('')}`);
        
        // Update cost estimate
        this.updateCostEstimate(letters.length);
    }
    
    updateCostEstimate(letterCount) {
        const costEstimateDiv = document.getElementById('cost-estimate');
        const letterCountSpan = document.getElementById('letter-count');
        const totalCostSpan = document.getElementById('total-cost');
        
        if (letterCount > 0) {
            const costPerLetter = 0.04; // $0.04 per gpt-image-1 generation
            const totalCost = letterCount * costPerLetter;
            
            letterCountSpan.textContent = letterCount;
            totalCostSpan.textContent = `$${totalCost.toFixed(2)} USD`;
            
            costEstimateDiv.classList.remove('hidden');
        } else {
            costEstimateDiv.classList.add('hidden');
        }
    }

    updatePalettePreview() {
        const paletteSelect = document.getElementById('color-palette');
        const preview = document.getElementById('palette-preview');
        const selectedPalette = paletteSelect.value;

        if (!this.colorPalettes[selectedPalette]) {
            preview.innerHTML = '<p class="helper-text">Loading palette...</p>';
            return;
        }

        const palette = this.colorPalettes[selectedPalette];
        
        preview.innerHTML = `
            <div class="palette-info">
                <div class="palette-name">${palette.name}</div>
                <div class="palette-mood">${palette.mood}</div>
            </div>
            <div class="color-swatches">
                ${palette.colors.map(color => 
                    `<div class="color-swatch" style="background-color: ${this.getColorValue(color)}" title="${color}"></div>`
                ).join('')}
            </div>
        `;
    }

    getColorValue(colorName) {
        // Simple color name to hex/color mapping
        const colorMap = {
            'warm beige': '#F5F5DC',
            'deep forest green': '#355E3B',
            'rich brown': '#8B4513',
            'warm orange': '#FF8C00',
            'charcoal black': '#36454F',
            'cream white': '#FFFDD0',
            'deep navy blue': '#000080',
            'seafoam green': '#9FE2BF',
            'sandy beige': '#F5E6D3',
            'coral pink': '#FF7F7F',
            'crisp white': '#FFFFFF',
            'burnt orange': '#CC5500',
            'golden yellow': '#FFD700',
            'deep burgundy red': '#800020',
            'warm chestnut brown': '#954535',
            'cream': '#FFFDD0',
            'soft blush pink': '#FFB6C1',
            'sage green': '#9CAF88',
            'gentle lavender': '#E6E6FA',
            'butter yellow': '#FFFF8D',
            'pure white': '#FFFFFF',
            'charcoal gray': '#36454F',
            'soft slate blue': '#6A7B8B',
            'warm white': '#FAF0E6',
            'deep black': '#000000',
            'terracotta orange': '#E2725B',
            'dusty rose': '#DCAE96',
            'desert sage green': '#BCBF95',
            'warm cream': '#F5F5DC',
            'vibrant electric blue': '#0080FF',
            'bright sunny yellow': '#FFFF00',
            'lime green': '#32CD32',
            'vibrant orange': '#FF8C00'
        };
        
        return colorMap[colorName] || '#CCCCCC';
    }

    async handleFormSubmit(event) {
        event.preventDefault();
        
        const formData = this.collectFormData();
        if (!formData) return;

        console.log('🚀 Starting banner generation:', formData);
        
        // Show loading and switch to progress view
        this.showSection('progress-section');
        this.showLoading('Preparing your banner...');
        
        try {
            const response = await fetch('/api/generate-banner', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'Failed to start generation');
            }

            this.currentJobId = result.job_id;
            console.log(`✅ Generation started with job ID: ${this.currentJobId}`);
            
            this.hideLoading();
            this.startPolling();
            
        } catch (error) {
            console.error('❌ Failed to start generation:', error);
            this.hideLoading();
            this.showError(error.message);
        }
    }

    collectFormData() {
        const name = document.getElementById('banner-name').value.trim();
        const paletteSelect = document.getElementById('color-palette').value;
        
        if (!name) {
            this.showError('Please enter a name for your banner');
            return null;
        }

        // Collect letter inputs
        const letters = [];
        const letterInputs = document.querySelectorAll('input[name^="letter-"]');
        
        for (const input of letterInputs) {
            const letter = input.getAttribute('data-letter');
            const interest = input.value.trim();
            
            if (!interest) {
                this.showError(`Please specify an interest for letter "${letter}"`);
                return null;
            }
            
            letters.push({ letter, object: interest });
        }

        if (letters.length === 0) {
            this.showError('Please enter at least one letter');
            return null;
        }

        return {
            name,
            letters,
            color_palette: paletteSelect
        };
    }

    startPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }

        this.pollInterval = setInterval(() => {
            this.checkJobStatus();
        }, 2000); // Poll every 2 seconds

        // Initial check
        this.checkJobStatus();
    }

    async checkJobStatus() {
        if (!this.currentJobId) return;

        try {
            const response = await fetch(`/api/status/${this.currentJobId}`);
            const status = await response.json();

            if (!response.ok) {
                throw new Error('Failed to check status');
            }

            this.updateProgress(status);

            if (status.status === 'completed') {
                this.handleGenerationComplete(status);
            } else if (status.status === 'failed') {
                this.handleGenerationFailed(status);
            }

        } catch (error) {
            console.error('❌ Failed to check job status:', error);
            // Continue polling - might be temporary network issue
        }
    }

    updateProgress(status) {
        // Update progress bar
        const progressFill = document.getElementById('progress-fill');
        const progressPercentage = document.getElementById('progress-percentage');
        const progressStatus = document.getElementById('progress-status');
        const currentStep = document.getElementById('current-step');
        const completedLetters = document.getElementById('completed-letters');
        const totalLetters = document.getElementById('total-letters');

        if (progressFill) progressFill.style.width = `${status.progress}%`;
        if (progressPercentage) progressPercentage.textContent = `${status.progress}%`;
        if (progressStatus) progressStatus.textContent = status.status.charAt(0).toUpperCase() + status.status.slice(1);
        if (currentStep) currentStep.textContent = status.current_step;
        if (completedLetters) completedLetters.textContent = status.completed_letters;
        if (totalLetters) totalLetters.textContent = status.total_letters;

        console.log(`📊 Progress: ${status.progress}% - ${status.current_step}`);
    }

    handleGenerationComplete(status) {
        console.log('🎉 Banner generation completed!');
        
        this.stopPolling();
        this.showSection('results-section');
        
        // Set up download buttons
        const downloadButtons = document.querySelectorAll('.download-btn');
        downloadButtons.forEach(btn => {
            btn.disabled = false;
        });
        
        // Display cost information if available
        if (status.cost_info) {
            this.displayCostInfo(status.cost_info);
        }
    }
    
    displayCostInfo(costInfo) {
        const costElement = document.getElementById('cost-info');
        if (costElement && costInfo) {
            const costHtml = `
                <div class="cost-breakdown">
                    <h4><i class="fas fa-dollar-sign"></i> Generation Cost</h4>
                    <div class="cost-details">
                        <span class="cost-item">Letters generated: <strong>${costInfo.letters_generated}</strong></span>
                        <span class="cost-item">Cost per letter: <strong>$${costInfo.cost_per_letter.toFixed(2)} ${costInfo.currency}</strong></span>
                        <span class="cost-total">Total estimated cost: <strong>$${costInfo.estimated_total_cost.toFixed(2)} ${costInfo.currency}</strong></span>
                    </div>
                    <small class="cost-note">* Estimated cost based on OpenAI gpt-image-1 pricing</small>
                </div>
            `;
            costElement.innerHTML = costHtml;
            costElement.classList.remove('hidden');
        }
    }

    handleGenerationFailed(status) {
        console.error('❌ Banner generation failed:', status.error_message);
        
        this.stopPolling();
        this.showError(status.error_message || 'Generation failed for unknown reason');
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    async downloadFile(fileType) {
        if (!this.currentJobId) {
            this.showError('No job ID available for download');
            return;
        }

        try {
            console.log(`📥 Downloading ${fileType} file...`);
            
            const response = await fetch(`/api/download/${this.currentJobId}/${fileType}`);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Download failed');
            }

            // Create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = this.getDownloadFilename(fileType);
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            console.log(`✅ ${fileType} downloaded successfully`);

        } catch (error) {
            console.error(`❌ Failed to download ${fileType}:`, error);
            this.showError(`Failed to download ${fileType}: ${error.message}`);
        }
    }

    getDownloadFilename(fileType) {
        const name = document.getElementById('banner-name').value.trim() || 'banner';
        const timestamp = new Date().toISOString().slice(0, 10);
        
        switch (fileType) {
            case 'banner':
                return `${name}_banner_${timestamp}.png`;
            case 'pdf':
                return `${name}_letters_${timestamp}.pdf`;
            default:
                return `${name}_${fileType}_${timestamp}.png`;
        }
    }

    cancelGeneration() {
        console.log('🛑 Cancelling generation...');
        this.stopPolling();
        this.currentJobId = null;
        this.resetToForm();
    }

    resetForm() {
        // Clear form
        document.getElementById('banner-form').reset();
        document.getElementById('letters-container').innerHTML = '<p class="helper-text">Enter a name above to see letter inputs</p>';
        this.updatePalettePreview();
        
        // Reset state
        this.currentJobId = null;
        this.stopPolling();
        
        // Show form
        this.showSection('form-section');
        
        console.log('🔄 Form reset');
    }

    resetToForm() {
        this.showSection('form-section');
    }

    showSection(sectionId) {
        // Hide all sections
        const sections = ['form-section', 'progress-section', 'results-section', 'error-section'];
        sections.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.classList.add('hidden');
        });

        // Show target section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.remove('hidden');
        }
    }

    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('hidden');
            const messageElement = overlay.querySelector('p');
            if (messageElement) messageElement.textContent = message;
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.classList.add('hidden');
    }

    showError(message) {
        console.error('❌ Error:', message);
        
        const errorSection = document.getElementById('error-section');
        const errorMessage = document.getElementById('error-message');
        
        if (errorSection && errorMessage) {
            errorMessage.textContent = message;
            this.showSection('error-section');
        } else {
            // Fallback to alert if error section not found
            alert(`Error: ${message}`);
        }
    }
}

// Modal functions
function showAbout() {
    document.getElementById('about-modal').classList.remove('hidden');
}

function showHelp() {
    document.getElementById('help-modal').classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

// Close modals when clicking outside
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.add('hidden');
    }
});

// Close modals with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal:not(.hidden)');
        openModals.forEach(modal => modal.classList.add('hidden'));
    }
});

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.bannerGenerator = new BannerGenerator();
});

// Handle page refresh/close during generation
window.addEventListener('beforeunload', (e) => {
    if (window.bannerGenerator && window.bannerGenerator.currentJobId && window.bannerGenerator.pollInterval) {
        e.preventDefault();
        e.returnValue = 'Banner generation is in progress. Are you sure you want to leave?';
        return e.returnValue;
    }
});
