// ============================================
// THUMBNAIL BUDDY - INFINITE CANVAS
// Figma-like experience for thumbnail generation
// ============================================

// Global State
const state = {
    topic: '',
    pov: '',
    selectedThumbnails: [], // Max 2
    allThumbnails: null,
    currentView: 'canvas', // 'canvas' or 'grid'
    
    // Canvas state
    canvas: {
        scale: 1,
        translateX: 0,
        translateY: 0,
        isDragging: false,
        startX: 0,
        startY: 0,
        velocityX: 0,
        velocityY: 0,
        lastX: 0,
        lastY: 0,
        targetScale: 1,
        animationFrame: null,
    },
    
    // Analysis results
    analyses: [],
    currentStep: 0, // For breakdown panel
    breakdownExpanded: false, // Track if breakdown panel is expanded
};

// Configuration
const CONFIG = {
    MIN_SCALE: 0.1,
    MAX_SCALE: 5,
    SCALE_STEP: 0.08,  // Reduced from 0.15 for slower zoom
    CANVAS_PADDING: 60,
    CATEGORY_SPACING: 60,
    ZOOM_SMOOTH_FACTOR: 0.08,  // Reduced from 0.1 for smoother zoom
    PAN_INERTIA: 0.92,
    MIN_VELOCITY: 0.5,
    WHEEL_SENSITIVITY: 0.002,  // Control wheel zoom speed
};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    console.log('🎨 Initializing Thumbnail Buddy...');
    
    // Load stats
    await loadStats();
    
    // Setup event listeners
    setupInputListeners();
    setupUploadListeners();
    setupCanvasControls();
    setupViewToggle();
    setupBreakdownPanel();
    
    // Load thumbnails into canvas
    await loadCanvasData();
    
    // Initialize canvas
    initializeCanvas();
    
    console.log('✅ App initialized successfully!');
}

// ============================================
// STATS & API
// ============================================

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        // Update UI
        document.getElementById('thumbnail-count').textContent = data.thumbnail_count;
        
        const openaiDot = document.getElementById('openai-dot');
        const googleDot = document.getElementById('google-dot');
        
        if (data.openai_configured) {
            openaiDot.classList.add('active');
        }
        if (data.google_configured) {
            googleDot.classList.add('active');
        }
        
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadCanvasData() {
    showCanvasLoading();
    
    try {
        const response = await fetch('/api/all-thumbnails');
        const data = await response.json();
        
        state.allThumbnails = data;
        renderCanvasContent(data);
        renderGridContent(data);
        
        hideCanvasLoading();
        
    } catch (error) {
        console.error('Error loading thumbnails:', error);
        hideCanvasLoading();
    }
}

// ============================================
// INPUT HANDLERS
// ============================================

function setupInputListeners() {
    const topicInput = document.getElementById('topic');
    const povInput = document.getElementById('pov');
    const generateBtn = document.getElementById('generate-btn');
    const clearSelectionBtn = document.getElementById('clear-selection-btn');
    
    // Update state on input
    topicInput.addEventListener('input', (e) => {
        state.topic = e.target.value.trim();
        updateGenerateButton();
    });
    
    povInput.addEventListener('input', (e) => {
        state.pov = e.target.value.trim();
    });
    
    // Generate button
    generateBtn.addEventListener('click', startGenerationFlow);
    
    // Clear selection
    clearSelectionBtn.addEventListener('click', clearAllSelections);
}

function updateGenerateButton() {
    const generateBtn = document.getElementById('generate-btn');
    const hasInput = state.topic.length > 0;
    const hasSelection = state.selectedThumbnails.length > 0;
    
    generateBtn.disabled = !(hasInput && hasSelection);
}

// ============================================
// UPLOAD FUNCTIONALITY
// ============================================

let uploadFiles = [];

function setupUploadListeners() {
    const dropzone = document.getElementById('upload-dropzone');
    const fileInput = document.getElementById('upload-input');
    const uploadBtn = document.getElementById('upload-btn');
    const categorySelect = document.getElementById('upload-category');
    
    // Click to browse
    dropzone.addEventListener('click', () => {
        fileInput.click();
    });
    
    // File selection
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
    
    // Drag and drop
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('drag-over');
    });
    
    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('drag-over');
    });
    
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('drag-over');
        handleFiles(e.dataTransfer.files);
    });
    
    // Upload button
    uploadBtn.addEventListener('click', () => {
        const category = categorySelect.value;
        if (!category) {
            showToast('Please select a category', 'error');
            return;
        }
        if (uploadFiles.length === 0) {
            showToast('Please select files to upload', 'error');
            return;
        }
        uploadThumbnails(category);
    });
    
    // Category selection
    categorySelect.addEventListener('change', updateUploadButton);
}

function handleFiles(files) {
    uploadFiles = Array.from(files).filter(file => {
        return file.type.startsWith('image/');
    });
    
    if (uploadFiles.length === 0) {
        showToast('Please select valid image files', 'error');
        return;
    }
    
    displayUploadPreview();
    updateUploadButton();
}

function displayUploadPreview() {
    const previewContainer = document.getElementById('upload-preview');
    previewContainer.innerHTML = '';
    
    if (uploadFiles.length === 0) {
        previewContainer.style.display = 'none';
        return;
    }
    
    previewContainer.style.display = 'block';
    
    uploadFiles.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'upload-preview-item';
        
        const thumb = document.createElement('img');
        thumb.className = 'upload-preview-thumb';
        thumb.src = URL.createObjectURL(file);
        
        const info = document.createElement('div');
        info.className = 'upload-preview-info';
        
        const name = document.createElement('div');
        name.className = 'upload-preview-name';
        name.textContent = file.name;
        
        const size = document.createElement('div');
        size.className = 'upload-preview-size';
        size.textContent = formatFileSize(file.size);
        
        info.appendChild(name);
        info.appendChild(size);
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'upload-preview-remove';
        removeBtn.textContent = '×';
        removeBtn.onclick = () => {
            uploadFiles.splice(index, 1);
            displayUploadPreview();
            updateUploadButton();
        };
        
        item.appendChild(thumb);
        item.appendChild(info);
        item.appendChild(removeBtn);
        
        previewContainer.appendChild(item);
    });
}

function updateUploadButton() {
    const uploadBtn = document.getElementById('upload-btn');
    const categorySelect = document.getElementById('upload-category');
    const fileCount = document.getElementById('upload-file-count');
    
    fileCount.textContent = uploadFiles.length;
    uploadBtn.disabled = uploadFiles.length === 0 || !categorySelect.value;
}

async function uploadThumbnails(category) {
    const uploadBtn = document.getElementById('upload-btn');
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span class="btn-icon">⏳</span> Uploading...';
    
    showLoadingOverlay('Uploading thumbnails...');
    
    try {
        const formData = new FormData();
        formData.append('category', category);
        
        uploadFiles.forEach((file, index) => {
            formData.append('thumbnails', file);
        });
        
        const response = await fetch('/api/upload-thumbnails', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast(`Successfully uploaded ${result.uploaded} thumbnail(s)!`, 'success');
            
            // Clear upload state
            uploadFiles = [];
            document.getElementById('upload-input').value = '';
            document.getElementById('upload-category').value = '';
            displayUploadPreview();
            updateUploadButton();
            
            // Reload canvas to show new thumbnails
            await loadCanvasData();
            await loadStats();
            
            hideLoadingOverlay();
        } else {
            throw new Error(result.error || 'Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showToast(`Upload failed: ${error.message}`, 'error');
        hideLoadingOverlay();
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = '<span class="btn-icon">⬆</span> Upload <span id="upload-file-count">0</span> file(s)';
    }
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function clearAllSelections() {
    state.selectedThumbnails = [];
    updateSelectionUI();
    
    // Remove selection styling from all thumbnails
    document.querySelectorAll('.canvas-thumb, .grid-thumb').forEach(thumb => {
        thumb.classList.remove('selected');
    });
}

// ============================================
// CANVAS RENDERING
// ============================================

function renderCanvasContent(data) {
    const canvasContent = document.getElementById('canvas-content');
    canvasContent.innerHTML = '';
    
    if (!data || !data.categorized) {
        canvasContent.innerHTML = '<p style="color: var(--text-secondary); padding: 40px;">No thumbnails found</p>';
        return;
    }
    
    let yOffset = 0;
    
    // Render each category
    Object.keys(data.categorized).forEach((category, catIndex) => {
        const thumbnails = data.categorized[category];
        
        const categorySection = document.createElement('div');
        categorySection.className = 'canvas-category';
        categorySection.style.marginBottom = CONFIG.CATEGORY_SPACING + 'px';
        
        // Category header with pill
        const header = document.createElement('div');
        header.className = 'category-header';
        header.innerHTML = `
            <div class="category-pill">
                ${category.replace(/_/g, ' ')}
                <span class="category-count">${thumbnails.length}</span>
            </div>
        `;
        categorySection.appendChild(header);
        
        // Thumbnails grid
        const grid = document.createElement('div');
        grid.className = 'category-thumbnails';
        
        thumbnails.forEach((thumb, idx) => {
            const thumbElement = createCanvasThumbnail(thumb, category);
            grid.appendChild(thumbElement);
        });
        
        categorySection.appendChild(grid);
        canvasContent.appendChild(categorySection);
    });
}

function createCanvasThumbnail(thumbnail, category) {
    const div = document.createElement('div');
    div.className = 'canvas-thumb';
    div.dataset.path = thumbnail.path;
    div.dataset.url = thumbnail.url;
    div.dataset.filename = thumbnail.filename;
    div.dataset.category = category;
    
    div.innerHTML = `
        <img src="${thumbnail.url}" alt="${thumbnail.filename}" loading="lazy">
        <div class="canvas-thumb-overlay">
            <div class="canvas-thumb-name">${thumbnail.filename}</div>
        </div>
    `;
    
    // Click to select
    div.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleThumbnailSelection(div);
    });
    
    return div;
}

function toggleThumbnailSelection(thumbElement) {
    const path = thumbElement.dataset.path;
    const url = thumbElement.dataset.url;
    const filename = thumbElement.dataset.filename;
    const category = thumbElement.dataset.category;
    
    // Check if already selected
    const existingIndex = state.selectedThumbnails.findIndex(t => t.path === path);
    
    if (existingIndex >= 0) {
        // Deselect
        state.selectedThumbnails.splice(existingIndex, 1);
        thumbElement.classList.remove('selected');
    } else {
        // Check max limit
        if (state.selectedThumbnails.length >= 2) {
            showToast('Maximum 2 thumbnails can be selected', 'warning');
            return;
        }
        
        // Select
        state.selectedThumbnails.push({ path, url, filename, category });
        thumbElement.classList.add('selected');
    }
    
    // Update UI
    updateSelectionUI();
    updateGenerateButton();
}

function updateSelectionUI() {
    const preview = document.getElementById('selection-preview');
    const countSpan = document.getElementById('selected-count');
    const clearBtn = document.getElementById('clear-selection-btn');
    
    countSpan.textContent = state.selectedThumbnails.length;
    
    if (state.selectedThumbnails.length === 0) {
        preview.innerHTML = `
            <div class="empty-selection">
                <span class="empty-icon">⬚</span>
                <p>Select 1-2 thumbnails from the canvas</p>
            </div>
        `;
        clearBtn.style.display = 'none';
    } else {
        preview.innerHTML = state.selectedThumbnails.map((thumb, index) => `
            <div class="selected-thumb">
                <img src="${thumb.url}" alt="${thumb.filename}">
                <div class="thumb-name">${thumb.filename}</div>
                <button class="remove-btn" onclick="removeSelection(${index})">×</button>
            </div>
        `).join('');
        clearBtn.style.display = 'block';
    }
}

function removeSelection(index) {
    const removed = state.selectedThumbnails[index];
    state.selectedThumbnails.splice(index, 1);
    
    // Remove selection styling
    const thumbElement = document.querySelector(`[data-path="${removed.path}"]`);
    if (thumbElement) {
        thumbElement.classList.remove('selected');
    }
    
    updateSelectionUI();
    updateGenerateButton();
}

// Make removeSelection global
window.removeSelection = removeSelection;

// ============================================
// INFINITE CANVAS - PAN & ZOOM
// ============================================

function initializeCanvas() {
    const container = document.getElementById('canvas-container');
    const viewport = document.getElementById('canvas-viewport');
    
    // Mouse wheel zoom
    container.addEventListener('wheel', handleWheel, { passive: false });
    
    // Pan with mouse drag
    container.addEventListener('mousedown', startPan);
    container.addEventListener('mousemove', pan);
    container.addEventListener('mouseup', endPan);
    container.addEventListener('mouseleave', endPan);
    
    // Touch support
    container.addEventListener('touchstart', handleTouchStart, { passive: false });
    container.addEventListener('touchmove', handleTouchMove, { passive: false });
    container.addEventListener('touchend', endPan);
    
    // Initial transform
    updateCanvasTransform();
}

function handleWheel(e) {
    e.preventDefault();
    
    const container = document.getElementById('canvas-container');
    const rect = container.getBoundingClientRect();
    
    // Mouse position relative to container
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    // Calculate zoom delta based on wheel movement with reduced sensitivity
    const wheelDelta = -e.deltaY * CONFIG.WHEEL_SENSITIVITY;
    const delta = wheelDelta * state.canvas.targetScale; // Scale relative to current zoom
    
    state.canvas.targetScale = Math.min(Math.max(state.canvas.targetScale + delta, CONFIG.MIN_SCALE), CONFIG.MAX_SCALE);
    
    // Animate to target scale
    animateZoom(mouseX, mouseY);
}

function startPan(e) {
    if (e.target.closest('.canvas-thumb')) return; // Don't pan when clicking thumbnail
    
    state.canvas.isDragging = true;
    state.canvas.startX = e.clientX - state.canvas.translateX;
    state.canvas.startY = e.clientY - state.canvas.translateY;
    state.canvas.lastX = e.clientX;
    state.canvas.lastY = e.clientY;
    state.canvas.velocityX = 0;
    state.canvas.velocityY = 0;
    
    document.getElementById('canvas-container').style.cursor = 'grabbing';
}

function pan(e) {
    if (!state.canvas.isDragging) return;
    
    e.preventDefault();
    
    // Calculate velocity for momentum
    state.canvas.velocityX = e.clientX - state.canvas.lastX;
    state.canvas.velocityY = e.clientY - state.canvas.lastY;
    
    state.canvas.translateX = e.clientX - state.canvas.startX;
    state.canvas.translateY = e.clientY - state.canvas.startY;
    
    state.canvas.lastX = e.clientX;
    state.canvas.lastY = e.clientY;
    
    updateCanvasTransform();
}

function endPan() {
    if (state.canvas.isDragging) {
        state.canvas.isDragging = false;
        // Apply momentum/inertia
        applyMomentum();
    }
    document.getElementById('canvas-container').style.cursor = 'grab';
}

function handleTouchStart(e) {
    if (e.touches.length === 1) {
        const touch = e.touches[0];
        state.canvas.isDragging = true;
        state.canvas.startX = touch.clientX - state.canvas.translateX;
        state.canvas.startY = touch.clientY - state.canvas.translateY;
    }
}

function handleTouchMove(e) {
    if (!state.canvas.isDragging || e.touches.length !== 1) return;
    
    e.preventDefault();
    const touch = e.touches[0];
    state.canvas.translateX = touch.clientX - state.canvas.startX;
    state.canvas.translateY = touch.clientY - state.canvas.startY;
    
    updateCanvasTransform();
}

function updateCanvasTransform() {
    const viewport = document.getElementById('canvas-viewport');
    viewport.style.transform = `translate(${state.canvas.translateX}px, ${state.canvas.translateY}px) scale(${state.canvas.scale})`;
}

function updateZoomLevel() {
    document.getElementById('zoom-level').textContent = Math.round(state.canvas.scale * 100) + '%';
}

function animateZoom(mouseX, mouseY) {
    if (state.canvas.animationFrame) {
        cancelAnimationFrame(state.canvas.animationFrame);
    }
    
    function animate() {
        const diff = state.canvas.targetScale - state.canvas.scale;
        
        if (Math.abs(diff) > 0.001) {
            // Smooth interpolation
            const scaleDiff = 1 + (diff * CONFIG.ZOOM_SMOOTH_FACTOR);
            
            // Zoom towards mouse/center
            state.canvas.translateX = mouseX - (mouseX - state.canvas.translateX) * scaleDiff;
            state.canvas.translateY = mouseY - (mouseY - state.canvas.translateY) * scaleDiff;
            state.canvas.scale += diff * CONFIG.ZOOM_SMOOTH_FACTOR;
            
            updateCanvasTransform();
            updateZoomLevel();
            
            state.canvas.animationFrame = requestAnimationFrame(animate);
        } else {
            state.canvas.scale = state.canvas.targetScale;
            updateCanvasTransform();
            updateZoomLevel();
        }
    }
    
    animate();
}

function applyMomentum() {
    if (Math.abs(state.canvas.velocityX) < CONFIG.MIN_VELOCITY && 
        Math.abs(state.canvas.velocityY) < CONFIG.MIN_VELOCITY) {
        return;
    }
    
    function animate() {
        // Apply inertia
        state.canvas.velocityX *= CONFIG.PAN_INERTIA;
        state.canvas.velocityY *= CONFIG.PAN_INERTIA;
        
        state.canvas.translateX += state.canvas.velocityX;
        state.canvas.translateY += state.canvas.velocityY;
        
        updateCanvasTransform();
        
        // Continue if still moving
        if (Math.abs(state.canvas.velocityX) > CONFIG.MIN_VELOCITY || 
            Math.abs(state.canvas.velocityY) > CONFIG.MIN_VELOCITY) {
            requestAnimationFrame(animate);
        }
    }
    
    animate();
}

// ============================================
// ZOOM CONTROLS
// ============================================

function setupCanvasControls() {
    document.getElementById('zoom-in').addEventListener('click', zoomIn);
    document.getElementById('zoom-out').addEventListener('click', zoomOut);
    document.getElementById('zoom-fit').addEventListener('click', fitToView);
    
    // Search
    const searchInput = document.getElementById('search-canvas');
    searchInput.addEventListener('input', handleCanvasSearch);
}

function zoomIn() {
    const container = document.getElementById('canvas-container');
    const rect = container.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    state.canvas.targetScale = Math.min(state.canvas.targetScale + CONFIG.SCALE_STEP, CONFIG.MAX_SCALE);
    animateZoom(centerX, centerY);
}

function zoomOut() {
    const container = document.getElementById('canvas-container');
    const rect = container.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    state.canvas.targetScale = Math.max(state.canvas.targetScale - CONFIG.SCALE_STEP, CONFIG.MIN_SCALE);
    animateZoom(centerX, centerY);
}

function fitToView() {
    // Smooth transition to default view
    state.canvas.targetScale = 1;
    
    function animate() {
        const scaleDiff = state.canvas.targetScale - state.canvas.scale;
        const translateXDiff = -state.canvas.translateX;
        const translateYDiff = -state.canvas.translateY;
        
        if (Math.abs(scaleDiff) > 0.01 || Math.abs(translateXDiff) > 1 || Math.abs(translateYDiff) > 1) {
            state.canvas.scale += scaleDiff * 0.15;
            state.canvas.translateX += translateXDiff * 0.15;
            state.canvas.translateY += translateYDiff * 0.15;
            
            updateCanvasTransform();
            updateZoomLevel();
            
            requestAnimationFrame(animate);
        } else {
            state.canvas.scale = 1;
            state.canvas.translateX = 0;
            state.canvas.translateY = 0;
            updateCanvasTransform();
            updateZoomLevel();
        }
    }
    
    animate();
}

function handleCanvasSearch(e) {
    const query = e.target.value.toLowerCase().trim();
    const thumbs = document.querySelectorAll('.canvas-thumb');
    
    thumbs.forEach(thumb => {
        const filename = thumb.dataset.filename.toLowerCase();
        const category = thumb.dataset.category.toLowerCase();
        
        if (query === '' || filename.includes(query) || category.includes(query)) {
            thumb.style.display = '';
        } else {
            thumb.style.display = 'none';
        }
    });
}

// ============================================
// GRID VIEW
// ============================================

function setupViewToggle() {
    const canvasBtn = document.getElementById('canvas-view-btn');
    const gridBtn = document.getElementById('grid-view-btn');
    
    canvasBtn.addEventListener('click', () => switchView('canvas'));
    gridBtn.addEventListener('click', () => switchView('grid'));
}

function switchView(view) {
    state.currentView = view;
    
    const canvasBtn = document.getElementById('canvas-view-btn');
    const gridBtn = document.getElementById('grid-view-btn');
    const canvasContainer = document.getElementById('canvas-container');
    const gridContainer = document.getElementById('grid-container');
    
    if (view === 'canvas') {
        canvasBtn.classList.add('active');
        gridBtn.classList.remove('active');
        canvasContainer.style.display = 'block';
        gridContainer.style.display = 'none';
    } else {
        gridBtn.classList.add('active');
        canvasBtn.classList.remove('active');
        gridContainer.style.display = 'block';
        canvasContainer.style.display = 'none';
    }
}

function renderGridContent(data) {
    const gridContent = document.getElementById('grid-content');
    const gridPills = document.getElementById('grid-category-pills');
    
    gridContent.innerHTML = '';
    gridPills.innerHTML = '<button class="category-pill active" data-category="all">All</button>';
    
    if (!data || !data.categorized) return;
    
    // Add category pills
    Object.keys(data.categorized).forEach(category => {
        const pill = document.createElement('button');
        pill.className = 'category-pill';
        pill.dataset.category = category;
        pill.textContent = category.replace(/_/g, ' ');
        pill.addEventListener('click', () => filterGrid(category));
        gridPills.appendChild(pill);
    });
    
    // Add "All" button handler
    gridPills.querySelector('[data-category="all"]').addEventListener('click', () => filterGrid('all'));
    
    // Render all thumbnails
    renderGridThumbnails('all', data);
}

function filterGrid(category) {
    // Update active pill
    document.querySelectorAll('#grid-category-pills .category-pill').forEach(pill => {
        pill.classList.remove('active');
        if (pill.dataset.category === category) {
            pill.classList.add('active');
        }
    });
    
    renderGridThumbnails(category, state.allThumbnails);
}

function renderGridThumbnails(category, data) {
    const gridContent = document.getElementById('grid-content');
    gridContent.innerHTML = '';
    
    let thumbnails = [];
    
    if (category === 'all') {
        Object.values(data.categorized).forEach(cats => {
            thumbnails.push(...cats);
        });
    } else {
        thumbnails = data.categorized[category] || [];
    }
    
    thumbnails.forEach(thumb => {
        const div = document.createElement('div');
        div.className = 'grid-thumb';
        div.dataset.path = thumb.path;
        div.dataset.url = thumb.url;
        div.dataset.filename = thumb.filename;
        
        div.innerHTML = `<img src="${thumb.url}" alt="${thumb.filename}" loading="lazy">`;
        
        div.addEventListener('click', () => toggleThumbnailSelection(div));
        
        // Check if already selected
        if (state.selectedThumbnails.find(t => t.path === thumb.path)) {
            div.classList.add('selected');
        }
        
        gridContent.appendChild(div);
    });
}

// ============================================
// GENERATION FLOW
// ============================================

async function startGenerationFlow() {
    if (!state.topic || state.selectedThumbnails.length === 0) {
        showToast('Please enter a topic and select at least 1 thumbnail', 'error');
        return;
    }
    
    // Reset state
    state.analyses = [];
    state.currentStep = 0;
    
    // Open breakdown panel
    openBreakdownPanel();
    
    // Show selected thumbnails
    showBreakdownStep1();
    
    // Start analysis
    await analyzeSelectedThumbnails();
}

function setupBreakdownPanel() {
    const closeBtn = document.getElementById('close-breakdown');
    const expandBtn = document.getElementById('expand-breakdown');
    
    closeBtn.addEventListener('click', closeBreakdownPanel);
    expandBtn.addEventListener('click', toggleBreakdownExpansion);
}

function openBreakdownPanel() {
    document.getElementById('breakdown-panel').classList.add('open');
}

function closeBreakdownPanel() {
    const panel = document.getElementById('breakdown-panel');
    const expandBtn = document.getElementById('expand-breakdown');
    const rightPanel = document.querySelector('.right-panel');
    
    panel.classList.remove('open');
    panel.classList.remove('expanded');
    expandBtn.classList.remove('active');
    rightPanel.classList.remove('breakdown-expanded');
    
    // Reset label
    const label = expandBtn.querySelector('.expand-label');
    if (label) label.textContent = 'Wide';
    
    state.breakdownExpanded = false;
}

function toggleBreakdownExpansion() {
    const panel = document.getElementById('breakdown-panel');
    const expandBtn = document.getElementById('expand-breakdown');
    const rightPanel = document.querySelector('.right-panel');
    const label = expandBtn.querySelector('.expand-label');
    
    state.breakdownExpanded = !state.breakdownExpanded;
    
    if (state.breakdownExpanded) {
        panel.classList.add('expanded');
        expandBtn.classList.add('active');
        rightPanel.classList.add('breakdown-expanded');
        expandBtn.title = 'Switch to Normal View';
        if (label) label.textContent = 'Normal';
    } else {
        panel.classList.remove('expanded');
        expandBtn.classList.remove('active');
        rightPanel.classList.remove('breakdown-expanded');
        expandBtn.title = 'Switch to Wide View';
        if (label) label.textContent = 'Wide';
    }
}

function showBreakdownStep1() {
    // Show selected references
    const selectedRefs = document.getElementById('breakdown-selected');
    selectedRefs.innerHTML = state.selectedThumbnails.map(thumb => `
        <div class="breakdown-thumb">
            <img src="${thumb.url}" alt="${thumb.filename}">
            <div class="breakdown-thumb-info">
                <span>${thumb.filename}</span>
            </div>
        </div>
    `).join('');
    
    document.getElementById('breakdown-step-1').style.display = 'block';
    updateProgressIndicator(1);
}

async function analyzeSelectedThumbnails() {
    showLoadingOverlay('Analyzing thumbnails with GPT-4 Vision...');
    
    try {
        for (let i = 0; i < state.selectedThumbnails.length; i++) {
            const thumb = state.selectedThumbnails[i];
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thumbnail_path: thumb.path,
                    topic: state.topic,
                    pov: state.pov || null
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Analysis response:', data); // Debug log
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Validate analysis structure
            if (!data.analysis || typeof data.analysis !== 'object') {
                throw new Error('Invalid analysis response structure');
            }
            
            state.analyses.push({
                thumbnail: thumb,
                analysis: data.analysis
            });
        }
        
        hideLoadingOverlay();
        showBreakdownStep2();
        showBreakdownStep3();
        showBreakdownStep4();
        
    } catch (error) {
        console.error('Error analyzing:', error);
        hideLoadingOverlay();
        showToast('Error analyzing thumbnails: ' + error.message, 'error');
        closeBreakdownPanel();
    }
}

function showBreakdownStep2() {
    const analysisContent = document.getElementById('breakdown-analysis');
    analysisContent.innerHTML = '';
    
    state.analyses.forEach((item, index) => {
        if (!item || !item.analysis) {
            console.error('Invalid analysis item:', item);
            return;
        }
        
        const analysis = item.analysis.current_analysis || {};
        
        // Create section for this thumbnail
        const thumbnailSection = document.createElement('div');
        thumbnailSection.style.marginBottom = '24px';
        thumbnailSection.style.padding = '16px';
        thumbnailSection.style.background = 'var(--bg-elevated)';
        thumbnailSection.style.borderRadius = 'var(--radius-md)';
        thumbnailSection.style.border = '1px solid var(--border-default)';
        
        const header = document.createElement('h4');
        header.style.color = 'var(--accent-primary)';
        header.style.marginBottom = '16px';
        header.style.display = 'flex';
        header.style.alignItems = 'center';
        header.style.gap = '8px';
        header.innerHTML = `
            <span style="background: var(--accent-primary); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem;">${index + 1}</span>
            Current Analysis - ${item.thumbnail.filename}
        `;
        thumbnailSection.appendChild(header);
        
        // Add thumbnail preview
        const thumbPreview = document.createElement('div');
        thumbPreview.style.marginBottom = '16px';
        thumbPreview.innerHTML = `<img src="${item.thumbnail.url}" style="width: 100%; border-radius: 8px; max-height: 120px; object-fit: cover;">`;
        thumbnailSection.appendChild(thumbPreview);
        
        // Add analysis items - check if analysis is not empty
        if (analysis && typeof analysis === 'object' && Object.keys(analysis).length > 0) {
            Object.entries(analysis).forEach(([key, value]) => {
                const div = document.createElement('div');
                div.className = 'analysis-item';
                div.innerHTML = `
                    <div class="analysis-label">${key.replace(/_/g, ' ')}</div>
                    <div class="analysis-value">${value || 'N/A'}</div>
                `;
                thumbnailSection.appendChild(div);
            });
        } else {
            // Show placeholder if no analysis data
            const noDataDiv = document.createElement('div');
            noDataDiv.style.color = 'var(--text-secondary)';
            noDataDiv.style.padding = '20px';
            noDataDiv.style.textAlign = 'center';
            noDataDiv.textContent = 'No analysis data available';
            thumbnailSection.appendChild(noDataDiv);
        }
        
        analysisContent.appendChild(thumbnailSection);
    });
    
    document.getElementById('breakdown-step-2').style.display = 'block';
    updateProgressIndicator(2);
}

function showBreakdownStep3() {
    const modificationsContent = document.getElementById('breakdown-modifications');
    modificationsContent.innerHTML = '';
    
    state.analyses.forEach((item, index) => {
        if (!item || !item.analysis) {
            console.error('Invalid analysis item:', item);
            return;
        }
        
        const modifications = item.analysis.suggested_modifications || {};
        
        // Create section for this thumbnail
        const thumbnailSection = document.createElement('div');
        thumbnailSection.style.marginBottom = '24px';
        thumbnailSection.style.padding = '16px';
        thumbnailSection.style.background = 'var(--bg-elevated)';
        thumbnailSection.style.borderRadius = 'var(--radius-md)';
        thumbnailSection.style.border = '1px solid var(--border-default)';
        
        const header = document.createElement('h4');
        header.style.color = 'var(--accent-primary)';
        header.style.marginBottom = '16px';
        header.style.display = 'flex';
        header.style.alignItems = 'center';
        header.style.gap = '8px';
        header.innerHTML = `
            <span style="background: var(--accent-primary); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem;">${index + 1}</span>
            Suggested Changes - ${item.thumbnail.filename}
        `;
        thumbnailSection.appendChild(header);
        
        // Add thumbnail preview
        const thumbPreview = document.createElement('div');
        thumbPreview.style.marginBottom = '16px';
        thumbPreview.innerHTML = `<img src="${item.thumbnail.url}" style="width: 100%; border-radius: 8px; max-height: 120px; object-fit: cover;">`;
        thumbnailSection.appendChild(thumbPreview);
        
        // Add modification items - check if modifications is not empty
        if (modifications && typeof modifications === 'object' && Object.keys(modifications).length > 0) {
            Object.entries(modifications).forEach(([key, value]) => {
                const div = document.createElement('div');
                div.className = 'analysis-item';
                div.innerHTML = `
                    <div class="analysis-label">${key.replace(/_/g, ' ')}</div>
                    <div class="analysis-value">${value || 'N/A'}</div>
                `;
                thumbnailSection.appendChild(div);
            });
        } else {
            // Show placeholder if no modification data
            const noDataDiv = document.createElement('div');
            noDataDiv.style.color = 'var(--text-secondary)';
            noDataDiv.style.padding = '20px';
            noDataDiv.style.textAlign = 'center';
            noDataDiv.textContent = 'No modification suggestions available';
            thumbnailSection.appendChild(noDataDiv);
        }
        
        modificationsContent.appendChild(thumbnailSection);
    });
    
    document.getElementById('breakdown-step-3').style.display = 'block';
    updateProgressIndicator(3);
}

function showBreakdownStep4() {
    const generationContent = document.getElementById('breakdown-generation');
    generationContent.innerHTML = '';
    
    // Create separate generation section for each selected thumbnail
    state.analyses.forEach((item, index) => {
        const prompt = item.analysis.generation_prompt || '';
        
        const generationSection = document.createElement('div');
        generationSection.style.marginBottom = '24px';
        generationSection.style.padding = '16px';
        generationSection.style.background = 'var(--bg-elevated)';
        generationSection.style.borderRadius = 'var(--radius-md)';
        generationSection.style.border = '1px solid var(--border-default)';
        
        generationSection.innerHTML = `
            <h4 style="color: var(--accent-primary); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <span style="background: var(--accent-primary); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem;">${index + 1}</span>
                ${item.thumbnail.filename}
            </h4>
            
            <div style="margin-bottom: 12px;">
                <img src="${item.thumbnail.url}" style="width: 100%; border-radius: 8px; max-height: 120px; object-fit: cover;">
            </div>
            
            <div style="margin-bottom: 12px;">
                <label style="display: block; font-size: 0.8rem; font-weight: 500; color: var(--text-secondary); margin-bottom: 8px;">Service</label>
                <select id="generation-service-${index}" class="select-field">
                    <option value="gemini">🍌 Gemini 2.0 Flash Pro (Nano Banana Pro)</option>
                    <option value="dalle">🎨 DALL-E 3</option>
                </select>
            </div>
            
            <div style="margin-bottom: 12px;">
                <label style="display: block; font-size: 0.8rem; font-weight: 500; color: var(--text-secondary); margin-bottom: 8px;">Edit Prompt</label>
                <textarea id="generation-prompt-${index}" class="prompt-textarea" rows="4" style="width: 100%; padding: 12px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: var(--radius-sm); color: var(--text-primary); font-family: inherit; font-size: 0.85rem; resize: vertical;">${prompt}</textarea>
            </div>
            
            <button class="btn-generate-final" id="final-generate-btn-${index}" style="width: 100%;">
                <span class="btn-icon">⚡</span>
                Generate Thumbnail ${index + 1}
            </button>
            
            <div id="generation-result-${index}" style="margin-top: 16px; display: none;"></div>
        `;
        
        generationContent.appendChild(generationSection);
        
        // Setup button handler
        setTimeout(() => {
            document.getElementById(`final-generate-btn-${index}`).onclick = () => generateSingleThumbnailFromBreakdown(index);
        }, 100);
    });
    
    document.getElementById('breakdown-step-4').style.display = 'block';
    updateProgressIndicator(4);
}

async function generateSingleThumbnailFromBreakdown(index) {
    const item = state.analyses[index];
    
    if (!item || !item.thumbnail) {
        showToast('Invalid thumbnail data', 'error');
        return;
    }
    
    const service = document.getElementById(`generation-service-${index}`).value;
    const prompt = document.getElementById(`generation-prompt-${index}`).value.trim();
    
    if (!prompt) {
        showToast('Please provide a generation prompt', 'error');
        return;
    }
    
    const serviceName = service === 'gemini' ? 'Gemini 2.0 Flash Pro' : 'DALL-E 3';
    showLoadingOverlay(`Generating thumbnail ${index + 1} with ${serviceName}...`);
    
    // Disable button during generation
    const btn = document.getElementById(`final-generate-btn-${index}`);
    btn.disabled = true;
    btn.innerHTML = '<span class="btn-icon">⏳</span> Generating...';
    
    try {
        // Get reference image path (might be undefined/null)
        const referencePath = item.thumbnail && item.thumbnail.path ? item.thumbnail.path : null;
        
        console.log('Generating with:', {
            prompt: prompt.substring(0, 50) + '...',
            service: service,
            topic: `${state.topic}_${index + 1}`,
            reference_image: referencePath
        });
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: prompt,
                service: service,
                topic: `${state.topic}_${index + 1}`,
                reference_image: referencePath
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Server error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Generation response:', data); // Debug log
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        if (!data.url) {
            throw new Error('No URL returned from server');
        }
        
        hideLoadingOverlay();
        
        // Show result for this specific thumbnail
        const resultDiv = document.getElementById(`generation-result-${index}`);
        resultDiv.style.display = 'block';
        
        // Ensure URL starts with /
        const imageUrl = data.url.startsWith('/') ? data.url : '/' + data.url;
        const cacheBuster = Date.now();
        
        // Create a new image element with proper loading
        const img = new Image();
        img.onload = function() {
            resultDiv.innerHTML = `
                <div style="padding: 16px; background: var(--bg-tertiary); border-radius: var(--radius-md); border: 2px solid var(--success);">
                    <h4 style="color: var(--success); margin-bottom: 12px;">✓ Generated Successfully!</h4>
                    <img src="${imageUrl}?t=${cacheBuster}" alt="Generated Thumbnail" style="width: 100%; height: auto; border-radius: 8px; margin-bottom: 12px; display: block;">
                    <button onclick="downloadThumbnail('${imageUrl}', '${state.topic}_${index + 1}.png')" class="btn-download" style="display: block; width: 100%; text-align: center; padding: 12px; background: var(--success); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">
                        📥 Download Thumbnail ${index + 1}
                    </button>
                </div>
            `;
        };
        img.onerror = function() {
            console.error('Image load error for:', imageUrl);
            resultDiv.innerHTML = `
                <div style="padding: 16px; background: var(--bg-tertiary); border-radius: var(--radius-md); border: 2px solid var(--error);">
                    <h4 style="color: var(--error); margin-bottom: 12px;">⚠️ Image Load Error</h4>
                    <p style="color: var(--text-secondary); margin-bottom: 12px;">Generated but couldn't display. File saved to server. Try downloading:</p>
                    <button onclick="downloadThumbnail('${imageUrl}', '${state.topic}_${index + 1}.png')" class="btn-download" style="display: block; width: 100%; text-align: center; padding: 12px; background: var(--success); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">
                        📥 Download Thumbnail ${index + 1}
                    </button>
                    <p style="color: var(--text-muted); font-size: 0.75rem; margin-top: 8px;">Path: ${data.path || imageUrl}</p>
                </div>
            `;
        };
        img.src = `${imageUrl}?t=${cacheBuster}`;
        
        // Update button
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">✓</span> Generated!';
        btn.style.background = 'var(--success)';
        
        // Update stats
        loadStats();
        
        // If all thumbnails generated, show step 5
        checkAllGenerated();
        
    } catch (error) {
        console.error('Error generating:', error);
        hideLoadingOverlay();
        showToast('Error generating thumbnail: ' + error.message, 'error');
        
        // Re-enable button
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">⚡</span> Generate Thumbnail ' + (index + 1);
    }
}

function checkAllGenerated() {
    // Check if all thumbnails have been generated
    let allGenerated = true;
    for (let i = 0; i < state.analyses.length; i++) {
        const resultDiv = document.getElementById(`generation-result-${i}`);
        if (!resultDiv || resultDiv.style.display === 'none') {
            allGenerated = false;
            break;
        }
    }
    
    if (allGenerated) {
        document.getElementById('breakdown-step-5').style.display = 'block';
        const resultContent = document.getElementById('breakdown-result');
        resultContent.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <h3 style="color: var(--success); margin-bottom: 16px;">🎉 All Thumbnails Generated!</h3>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">
                    Generated ${state.analyses.length} thumbnail${state.analyses.length > 1 ? 's' : ''} successfully. Scroll up to download each one.
                </p>
                <button class="btn-download" onclick="closeBreakdownPanel(); clearAllSelections();" style="width: 100%; padding: 12px; background: var(--accent-primary); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">
                    ✨ Create Another Set
                </button>
            </div>
        `;
        updateProgressIndicator(5);
    }
}

function updateProgressIndicator(step) {
    document.querySelectorAll('.progress-step').forEach((el, index) => {
        const stepNum = parseInt(el.dataset.step);
        
        if (stepNum < step) {
            el.classList.add('completed');
            el.classList.remove('active');
        } else if (stepNum === step) {
            el.classList.add('active');
            el.classList.remove('completed');
        } else {
            el.classList.remove('active', 'completed');
        }
    });
}

// ============================================
// UI UTILITIES
// ============================================

function showCanvasLoading() {
    document.getElementById('canvas-loading').classList.remove('hidden');
}

function hideCanvasLoading() {
    document.getElementById('canvas-loading').classList.add('hidden');
}

function showLoadingOverlay(text) {
    document.getElementById('loading-text').textContent = text;
    document.getElementById('loading-overlay').classList.add('active');
}

function hideLoadingOverlay() {
    document.getElementById('loading-overlay').classList.remove('active');
}

function showToast(message, type = 'info') {
    // Simple alert for now - you can enhance this with a custom toast
    alert(message);
}

// ============================================
// DOWNLOAD HELPER
// ============================================

function downloadThumbnail(url, filename) {
    // Extract just the filename from the URL
    const urlParts = url.split('/');
    const fileFromUrl = urlParts[urlParts.length - 1].split('?')[0]; // Remove query params
    
    // Use the download endpoint
    const downloadUrl = `/download/${fileFromUrl}`;
    
    // Create a temporary link and trigger download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ============================================
// EXPORTS (for inline onclick handlers)
// ============================================

window.removeSelection = removeSelection;
window.downloadThumbnail = downloadThumbnail;
