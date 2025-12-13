// Letter Banner Generator - Frontend JavaScript

class BannerGenerator {
    constructor() {
        this.currentJobId = null;
        this.pollInterval = null;
        this.colorPalettes = {};
        this.models = {};
        this.selectedModel = 'gemini-3-pro-image-preview';
        this.currentLetterImages = [];
        this.themeVariations = null;
        this.currentEditingLetter = null;
        
        this.init();
    }

    async init() {
        console.log('🎨 Letter Banner Generator initialized');
        
        // Load color palettes and models
        await this.loadColorPalettes();
        await this.loadModels();
        
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

    async loadModels() {
        try {
            const response = await fetch('/api/models');
            const data = await response.json();
            this.models = data.models;
            this.selectedModel = data.default_model;
            console.log('✅ Models loaded:', Object.keys(this.models));
        } catch (error) {
            console.error('❌ Failed to load models:', error);
            // Use default if API fails
            this.models = {
                'gemini-3-pro-image': { cost_per_image: 0.0336 },
                'gpt-image-1': { cost_per_image: 0.17 }
            };
        }
    }

    setupEventListeners() {
        // Form submission
        const form = document.getElementById('banner-form');
        form.addEventListener('submit', (e) => this.handleFormSubmit(e));

        // Name input - generate letter inputs
        const nameInput = document.getElementById('banner-name');
        nameInput.addEventListener('input', (e) => this.handleNameInput(e));

        // Model selection
        const modelSelect = document.getElementById('model-select');
        modelSelect.addEventListener('change', (e) => this.handleModelChange(e));

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

        // Theme mode selection
        const themeModeRadios = document.querySelectorAll('input[name="theme-mode"]');
        themeModeRadios.forEach(radio => {
            radio.addEventListener('change', (e) => this.handleThemeModeChange(e));
        });

        // Generate themes button
        const generateThemesBtn = document.getElementById('generate-themes-btn');
        generateThemesBtn?.addEventListener('click', () => this.generateThemeVariations());

        // Approve and generate PDF button
        const approveBtn = document.getElementById('approve-and-generate-pdf-btn');
        approveBtn?.addEventListener('click', () => this.generateFinalPDF());

        // Back to form from preview
        const backToFormBtn = document.getElementById('back-to-form-btn');
        backToFormBtn?.addEventListener('click', () => this.resetForm());

        // Apply edit button
        const applyEditBtn = document.getElementById('apply-edit-btn');
        applyEditBtn?.addEventListener('click', () => this.applyEdit());

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
        const themeMode = document.querySelector('input[name="theme-mode"]:checked')?.value || 'individual';
        
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

        // Only create individual letter inputs if in Individual Theme mode
        if (themeMode === 'individual') {
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
        } else {
            // In Single Theme mode, just show a message
            lettersContainer.innerHTML = `<p class="helper-text">Using single theme mode. Generate theme ideas to see variations for ${letters.length} letters.</p>`;
        }
        
        // Update cost estimate
        this.updateCostEstimate(letters.length);
    }
    
    handleModelChange(event) {
        this.selectedModel = event.target.value;
        const modelInfo = this.models[this.selectedModel];
        
        // Update model description
        const descriptionElement = document.getElementById('model-description');
        if (descriptionElement && modelInfo) {
            descriptionElement.textContent = modelInfo.description || '';
        }
        
        // Update cost estimate
        const nameInput = document.getElementById('banner-name');
        if (nameInput.value.trim()) {
            const letters = nameInput.value.split('').filter(char => /[A-Z]/i.test(char));
            this.updateCostEstimate(letters.length);
        }
        
        console.log(`🔄 Model changed to: ${this.selectedModel}`);
    }

    updateCostEstimate(letterCount) {
        const costEstimateDiv = document.getElementById('cost-estimate');
        const letterCountSpan = document.getElementById('letter-count');
        const totalCostSpan = document.getElementById('total-cost');
        const costRateSpan = document.getElementById('cost-rate');
        
        if (letterCount > 0) {
            const modelInfo = this.models[this.selectedModel] || { cost_per_image: 0.17 };
            const costPerLetter = modelInfo.cost_per_image;
            const totalCost = letterCount * costPerLetter;
            
            letterCountSpan.textContent = letterCount;
            costRateSpan.textContent = `$${costPerLetter.toFixed(4)} USD`;
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
            // Original palettes
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
            'vibrant orange': '#FF8C00',
            
            // Holiday palette colors
            'deep cranberry red': '#C41E3A',
            'forest green': '#228B22',
            'metallic gold': '#D4AF37',
            'holly berry red': '#C41E3A',
            'rose red': '#E63946',
            'champagne gold': '#F7E7CE',
            'pumpkin orange': '#FF7518',
            'midnight black': '#1A1A1A',
            'deep purple': '#4B0082',
            'bone white': '#F9F6EE',
            'pastel pink': '#FFB3BA',
            'baby blue': '#BAE1FF',
            'lemon yellow': '#FFFFBA',
            'mint green': '#BAFFC9',
            'soft lavender': '#E0BBE4',
            'patriotic red': '#B22234',
            'navy blue': '#000080',
            'steel blue': '#4682B4',
            'emerald green': '#50C878',
            'clover green': '#3A9B3E'
        };
        
        return colorMap[colorName] || '#CCCCCC';
    }

    async handleFormSubmit(event) {
        event.preventDefault();
        
        console.log('🚀 Form submitted');
        
        const formData = this.collectFormData();
        if (!formData) {
            console.log('❌ Form validation failed');
            return;
        }

        console.log('✅ Form data collected:', formData);
        
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
        const modelSelect = document.getElementById('model-select').value;
        const themeMode = document.querySelector('input[name="theme-mode"]:checked').value;
        
        if (!name) {
            this.showError('Please enter a name for your banner');
            return null;
        }

        let letters = [];
        
        if (themeMode === 'single') {
            // Single theme mode - use generated variations
            if (!this.themeVariations || this.themeVariations.length === 0) {
                alert('⚠️ Please click "Generate Theme Ideas" button first to create letter variations!');
                this.showError('Please generate theme ideas first by clicking the "Generate Theme Ideas" button');
                return null;
            }
            
            // Collect variations (user may have edited them)
            const variationInputs = document.querySelectorAll('.variation-theme-input');
            console.log(`Found ${variationInputs.length} variation inputs`);
            console.log(`Have ${this.themeVariations.length} theme variations stored`);
            
            variationInputs.forEach((input, index) => {
                const variation = this.themeVariations[index];
                const theme = input.value.trim();
                
                console.log(`Letter ${variation.letter}: "${theme}"`);
                
                if (theme) {
                    letters.push({
                        letter: variation.letter,
                        object: theme
                    });
                }
            });
            
            console.log(`Collected ${letters.length} letters from variations`);
            
        } else {
            // Individual theme mode - collect from letter inputs
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
        }

        if (letters.length === 0) {
            console.error('No letters collected!');
            this.showError('Please enter at least one letter theme');
            return null;
        }

        console.log(`✅ Returning form data with ${letters.length} letters`);
        
        return {
            name,
            letters,
            color_palette: paletteSelect,
            model: modelSelect
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
        
        // NEW: Show preview section instead of going straight to results
        this.displayLetterPreviews(status);
        this.showSection('preview-section');
        
        // Store status for later PDF generation
        this.completedStatus = status;
    }
    
    displayLetterPreviews(status) {
        const grid = document.getElementById('letters-preview-grid');
        grid.innerHTML = '';
        
        this.currentLetterImages = [];
        
        // Get letter files from status
        const files = status.files || {};
        const totalLetters = status.total_letters;
        
        for (let i = 0; i < totalLetters; i++) {
            const letterKey = `letter_${i}`;
            const letterPath = files[letterKey];
            
            if (!letterPath) continue;
            
            // Extract letter name and theme from filename
            const filename = letterPath.split('/').pop();
            const parts = filename.split('_');
            const letter = parts[1]; // letter_A_theme_timestamp.png
            const themeRaw = parts.slice(2, -1).join(' '); // Join theme parts
            
            // Extract just the first few words of the theme (before any colon or long description)
            const themeShort = themeRaw.split(':')[0].substring(0, 50);
            
            this.currentLetterImages.push({
                index: i,
                letter: letter,
                theme: themeShort,
                fullTheme: themeRaw,
                path: letterPath
            });
            
            // Create preview card with simplified theme display
            const card = document.createElement('div');
            card.className = 'letter-preview-card';
            card.innerHTML = `
                <div class="letter-preview-image">
                    <img src="/api/download/${this.currentJobId}/letter_${i}" alt="Letter ${letter}">
                </div>
                <div class="letter-preview-info">
                    <h3>${letter}</h3>
                    <p class="letter-theme">${themeShort}</p>
                    <button class="edit-letter-btn" data-letter-index="${i}">
                        <i class="fas fa-edit"></i> Edit or Add Details
                    </button>
                </div>
            `;
            
            // Add click handler for edit button
            const editBtn = card.querySelector('.edit-letter-btn');
            editBtn.addEventListener('click', () => this.openEditModal(i));
            
            grid.appendChild(card);
        }
        
        console.log(`✅ Displayed ${this.currentLetterImages.length} letter previews`);
    }
    
    displayCostInfo(costInfo) {
        const costElement = document.getElementById('cost-info');
        if (costElement && costInfo) {
            const modelName = costInfo.model || 'selected model';
            const costHtml = `
                <div class="cost-breakdown">
                    <h4><i class="fas fa-dollar-sign"></i> Generation Cost</h4>
                    <div class="cost-details">
                        <span class="cost-item">Model: <strong>${modelName}</strong></span>
                        <span class="cost-item">Letters generated: <strong>${costInfo.letters_generated}</strong></span>
                        <span class="cost-item">Cost per letter: <strong>$${costInfo.cost_per_letter.toFixed(4)} ${costInfo.currency}</strong></span>
                        <span class="cost-total">Total estimated cost: <strong>$${costInfo.estimated_total_cost.toFixed(2)} ${costInfo.currency}</strong></span>
                    </div>
                    <small class="cost-note">* Estimated cost based on ${modelName} pricing</small>
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

    // Theme mode handling
    handleThemeModeChange(event) {
        const mode = event.target.value;
        const singleThemeSection = document.getElementById('single-theme-section');
        const individualSection = document.getElementById('individual-letters-section');
        
        if (mode === 'single') {
            singleThemeSection.classList.remove('hidden');
            individualSection.classList.add('hidden');
        } else {
            singleThemeSection.classList.add('hidden');
            individualSection.classList.remove('hidden');
        }
        
        // Regenerate letter inputs for the current name
        const nameInput = document.getElementById('banner-name');
        if (nameInput.value.trim()) {
            this.handleNameInput({ target: nameInput });
        }
        
        console.log(`🔄 Theme mode changed to: ${mode}`);
    }

    async generateThemeVariations() {
        const nameInput = document.getElementById('banner-name');
        const themeInput = document.getElementById('single-theme-input');
        const name = nameInput.value.trim();
        const theme = themeInput.value.trim();
        
        if (!name) {
            this.showError('Please enter a name first');
            return;
        }
        
        if (!theme) {
            this.showError('Please enter a theme');
            return;
        }
        
        const generateBtn = document.getElementById('generate-themes-btn');
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating ideas...';
        
        try {
            const response = await fetch('/api/generate-theme-variations', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: name,
                    theme: theme,
                    model: 'gemini-2.0-flash-exp'
                })
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'Failed to generate theme variations');
            }
            
            this.themeVariations = result.variations;
            this.displayThemeVariations(result.variations);
            
        } catch (error) {
            console.error('❌ Failed to generate theme variations:', error);
            this.showError(error.message);
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> Generate Theme Ideas';
        }
    }

    displayThemeVariations(variations) {
        const preview = document.getElementById('theme-variations-preview');
        preview.innerHTML = '<h4>Generated Theme Variations (you can edit these):</h4>';
        
        const container = document.createElement('div');
        container.className = 'theme-variations-container';
        
        variations.forEach((v, index) => {
            const varDiv = document.createElement('div');
            varDiv.className = 'theme-variation-item';
            varDiv.innerHTML = `
                <div class="variation-letter">${v.letter}</div>
                <input 
                    type="text" 
                    class="variation-theme-input" 
                    data-index="${index}"
                    value="${v.theme}"
                    placeholder="Theme for ${v.letter}"
                >
            `;
            container.appendChild(varDiv);
        });
        
        preview.appendChild(container);
        preview.classList.remove('hidden');
        
        console.log('✅ Theme variations displayed');
    }

    // Letter editing
    openEditModal(letterIndex) {
        this.currentEditingLetter = letterIndex;
        const letterInfo = this.currentLetterImages[letterIndex];
        
        if (!letterInfo) {
            this.showError('Letter not found');
            return;
        }
        
        // Set modal content
        document.getElementById('edit-letter-name').textContent = letterInfo.letter;
        document.getElementById('edit-current-image').src = `/api/download/${this.currentJobId}/letter_${letterIndex}`;
        document.getElementById('edit-prompt-input').value = '';
        
        // Show modal
        document.getElementById('edit-modal').classList.remove('hidden');
        
        console.log(`✏️ Opening edit modal for letter ${letterInfo.letter}`);
    }

    async applyEdit() {
        const promptInput = document.getElementById('edit-prompt-input');
        const editPrompt = promptInput.value.trim();
        
        if (!editPrompt) {
            alert('Please enter edit instructions');
            return;
        }
        
        const loadingDiv = document.getElementById('edit-loading');
        const applyBtn = document.getElementById('apply-edit-btn');
        
        loadingDiv.classList.remove('hidden');
        applyBtn.disabled = true;
        
        try {
            const response = await fetch(`/api/edit-letter/${this.currentJobId}/${this.currentEditingLetter}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    edit_prompt: editPrompt,
                    model: this.selectedModel
                })
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'Failed to edit letter');
            }
            
            console.log('✅ Letter edited successfully');
            
            // Close modal
            closeModal('edit-modal');
            
            // Refresh the preview
            const letterCard = document.querySelector(`[data-letter-index="${this.currentEditingLetter}"]`).closest('.letter-preview-card');
            const img = letterCard.querySelector('img');
            img.src = `/api/download/${this.currentJobId}/letter_${this.currentEditingLetter}?t=${Date.now()}`;
            
        } catch (error) {
            console.error('❌ Failed to edit letter:', error);
            alert(`Error editing letter: ${error.message}`);
        } finally {
            loadingDiv.classList.add('hidden');
            applyBtn.disabled = false;
        }
    }

    async generateFinalPDF() {
        const approveBtn = document.getElementById('approve-and-generate-pdf-btn');
        approveBtn.disabled = true;
        approveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating PDF...';
        
        try {
            const response = await fetch(`/api/generate-pdf/${this.currentJobId}`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'Failed to generate PDF');
            }
            
            console.log('✅ PDF generated successfully');
            
            // Show results section with download options
            this.showSection('results-section');
            
            // Display cost info if available
            if (this.completedStatus && this.completedStatus.cost_info) {
                this.displayCostInfo(this.completedStatus.cost_info);
            }
            
        } catch (error) {
            console.error('❌ Failed to generate PDF:', error);
            this.showError(error.message);
        } finally {
            approveBtn.disabled = false;
            approveBtn.innerHTML = '<i class="fas fa-file-pdf"></i> Approve All & Generate PDF';
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
