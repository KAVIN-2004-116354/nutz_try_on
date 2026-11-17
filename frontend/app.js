/**
 * Nutz Try On — Interactive Face Swap & 2D Virtual Fitting Studio
 */

const MODE_UI = {
    flux: {
        supportsAttr: "flux",
        headerBadge: "⚡ Flux.1 Dev Cloud (1024×1024 Photorealistic)",
        generateBtn: "⚡ Generate with Flux.1 Dev",
        stageGenerateBtn: "⚡ Run Flux.1 Dev Try-On (1024×1024)",
        personSectionTitle: "👤 1. Model / Person",
        garmentSectionTitle: "👗 2. Outfit Reference & Styling",
        garmentDropMain: "Upload Outfit / Reference",
        garmentDropSub: "Garment photo, mannequin, or style",
        settingsTitle: "⚡ Flux.1 Dev Cloud Engine",
        stageMainTitle: "Flux.1 Dev Virtual Try-On Stage",
        stageSubText: "1024×1024 Photorealistic Cloud AI Synthesis via Railway Cloud GPU",
        stagePersonBadge: "👤 Model / Person",
        stageTransferText: "Flux.1 Dev Synthesis",
        stageGarmentBadge: "👗 Outfit Reference",
        readyTitle: "Ready for Flux.1 Dev Try-On",
        readyDesc: "Model and garment are selected. Flux.1 Dev will synthesize a 1024×1024 photorealistic try-on result preserving model identity.",
        loadingTitle: "Synthesizing with Flux.1 Dev Cloud...",
        loadingSteps: [
            "Sending to Railway Cloud GPU",
            "Flux.1 Dev 1024×1024 Latent Synthesis",
            "Decoding Photorealistic Masterpiece"
        ],
        compBeforeLabel: "Original Model",
        compAfterLabel: "Flux.1 Dev Try-On",
        dualBeforeTitle: "👤 Before (Original Model)",
        dualAfterTitle: "⚡ After (Flux.1 Dev 1024×1024)",
        dualAfterBadge: "FLUX-DEV-012",
        reTryBtn: "🔄 Try Another Outfit",
        specsTitle: "📋 Garment & Model Specs",
        garmentNotes: "1024×1024 photorealistic latent diffusion synthesis via FLUX-DEV-012 on Railway cloud (~15-25s).",
        tipsTitle: "💡 Flux.1 Dev Pro Tips",
        tipsHtml: [
            "Flux.1 Dev synthesizes photorealistic textures, true fabric draping, and studio illumination.",
            "Use the prompt input to add custom fabrics, gold zardozi embroidery, or distinct color palettes.",
            "All output images are generated at full 1024×1024 resolution on high-end cloud GPUs."
        ]
    },
    face_swap: {
        supportsAttr: "faceswap",
        headerBadge: "✨ Face Swap (InsightFace)",
        generateBtn: "✨ Swap Face",
        stageGenerateBtn: "✨ Swap Face Now",
        personSectionTitle: "👤 1. Your Face Photo",
        garmentSectionTitle: "👗 2. Model / Garment Photo",
        garmentDropMain: "Upload Model / Garment Photo",
        garmentDropSub: "Photo of model wearing the outfit",
        settingsTitle: "⚡ Face Swap Engine",
        stageMainTitle: "Face Swap Studio",
        stageSubText: "Replace Garment Model Face with Your Face",
        stagePersonBadge: "👤 Your Face",
        stageTransferText: "InsightFace Swap",
        stageGarmentBadge: "👗 Garment / Model",
        readyTitle: "Ready for Face Swap",
        readyDesc: "We will place your face cleanly onto the model wearing the outfit.",
        loadingTitle: "Swapping Your Face onto Garment...",
        loadingSteps: [
            "Detect Your Face Landmarks",
            "Locate Garment Model Face",
            "Blend Face Identity & Lighting"
        ],
        compBeforeLabel: "Original Outfit",
        compAfterLabel: "Face Swap Result",
        dualBeforeTitle: "👗 Before (Original Outfit)",
        dualAfterTitle: "✨ After (Face Swapped)",
        dualAfterBadge: "InsightFace",
        reTryBtn: "🔄 Swap Another",
        specsTitle: "📋 Garment / Outfit",
        garmentNotes: "Places your face onto the outfit photo while preserving the garment, background, and pose.",
        tipsTitle: "💡 Face Swap Pro Tips",
        tipsHtml: [
            "Use a clear front-facing photo for your face with good lighting.",
            "Choose a garment photo where a model is wearing the outfit with a visible face.",
            "The outfit fabric, pleats, jewellery, and background remain 100% original."
        ]
    },
    catvton: {
        supportsAttr: "catvton",
        headerBadge: "⚡ CatVTON 2D Inpainting",
        generateBtn: "✨ Generate Try-On",
        stageGenerateBtn: "✨ Generate 2D Try-On",
        personSectionTitle: "👤 1. Person / Model",
        garmentSectionTitle: "👕 2. Garment Reference",
        garmentDropMain: "Upload Garment Image",
        garmentDropSub: "Ghost mannequin or flat lay",
        settingsTitle: "⚙️ 2D Diffusion Settings",
        stageMainTitle: "2D Virtual Fitting Stage",
        stageSubText: "High-Resolution Diffusion Try-On Preview",
        stagePersonBadge: "👤 Target Person",
        stageTransferText: "CatVTON Inpainting",
        stageGarmentBadge: "👕 Garment Reference",
        readyTitle: "Ready for 2D Virtual Try-On",
        readyDesc: "Inputs are configured. Click generate below to synthesize the try-on image.",
        loadingTitle: "Generating 2D Virtual Try-On...",
        loadingSteps: [
            "Upload & Category Masking",
            "SegFormer Clothing Segmentation",
            "CatVTON Diffusion Inpainting"
        ],
        compBeforeLabel: "Original Photo",
        compAfterLabel: "2D Try-On Result",
        dualBeforeTitle: "👤 Before (Original)",
        dualAfterTitle: "✨ After (2D Try-On Result)",
        dualAfterBadge: "CatVTON",
        reTryBtn: "🔄 Try Another Garment",
        specsTitle: "📋 Garment Specs",
        garmentNotes: "Concatenation-conditioned visual conditioning via CatVTON diffusion.",
        tipsTitle: "💡 2D Try-On Pro Tips",
        tipsHtml: [
            "Use clean front-facing portraits with good lighting.",
            "Garment photos with clean white/plain background give the sharpest collar and sleeve transitions.",
            "Balanced 40 steps provides the ideal balance between photorealism and speed."
        ]
    }
};

// Curated 30-item wardrobe (each entry has paired g_XX_model.jpg + g_XX_cloth.jpg)
const EXTRA_GARMENT_CATALOG = [
    ["01", "Indigo Tie-Dye Kurta", "Ethnic Kurta", "full_body"],
    ["02", "Terracotta A-Line Dress", "Midi Dress", "full_body"],
    ["03", "Sage Printed Suit", "Salwar Suit", "full_body"],
    ["04", "Navy Peacock Kurti", "Ethnic Kurti", "full_body"],
    ["05", "Maroon Gold Anarkali", "Festive Wear", "full_body"],
    ["06", "Crimson Silk Anarkali", "Silk Anarkali", "full_body"],
    ["07", "Mustard Chevron Suit", "Kurta Set", "full_body"],
    ["08", "Ivory Pastel Suit", "Dupatta Suit", "full_body"],
    ["09", "White Floral Kurti", "Cotton Kurti", "full_body"],
    ["10", "Espresso Zari Kurta", "Kurta Set", "full_body"],
    ["11", "Midnight Motif Kurti", "Ethnic Kurti", "full_body"],
    ["12", "Purple Bandhani Suit", "Printed Suit", "full_body"],
    ["13", "Coral Floral Kurta", "Casual Kurta", "full_body"],
    ["14", "Obsidian Floral Suit", "Black Ethnic", "full_body"],
    ["15", "Cream Thread Anarkali", "Festive Kurta", "full_body"],
    ["16", "Emerald Striped Knit", "Striped Top", "upper_body"],
    ["17", "Classic Black Tee", "Fitted Top", "upper_body"],
    ["18", "Blush Graphic Tee", "Casual Tee", "upper_body"],
    ["19", "Heather Grey Polo", "Knit Polo", "upper_body"],
    ["20", "Sport Stripe Tee", "Streetwear", "upper_body"],
    ["21", "Colorblock Hoodie", "Casual Top", "upper_body"],
    ["22", "Ivory Botanical Tee", "Graphic Tee", "upper_body"],
    ["23", "Rust Wrap Blouse", "Wrap Top", "upper_body"],
    ["24", "Relaxed Black Knit", "Pullover", "upper_body"],
    ["25", "Silver Sequin Set", "Party Dress", "full_body"],
    ["26", "Tangerine Zip Polo", "Summer Top", "upper_body"],
    ["27", "Blush Ruched Cami", "Tank Top", "upper_body"],
    ["28", "Navy Off-Shoulder Set", "Evening Set", "full_body"],
    ["29", "White Textured Tee", "Classic Tee", "upper_body"],
    ["30", "Dusty Rose Tee", "Soft Tee", "upper_body"]
];

function createGarmentCard(supports, url, name, tag, category, gender = "women") {
    const card = document.createElement("div");
    card.className = "garment-card";
    card.dataset.supports = supports;
    card.dataset.url = url;
    card.dataset.name = name;
    card.dataset.category = category;
    card.dataset.gender = gender;
    if (supports === "catvton") card.style.display = "none";

    const img = document.createElement("img");
    img.src = url;
    img.alt = name;
    img.loading = "lazy";

    const info = document.createElement("div");
    info.className = "info";
    const h4 = document.createElement("h4");
    h4.textContent = name;
    const pill = document.createElement("span");
    pill.className = "cat-pill";
    pill.textContent = tag;

    info.append(h4, pill);
    card.append(img, info);
    return card;
}

function appendGarmentCatalog() {
    const grid = document.getElementById("garment-samples");
    if (!grid) return;
    const frag = document.createDocumentFragment();
    EXTRA_GARMENT_CATALOG.forEach(([num, name, tag, category]) => {
        frag.appendChild(
            createGarmentCard("faceswap", `assets/garments/g_${num}_model.jpg`, name, tag, category)
        );
        frag.appendChild(
            createGarmentCard("catvton", `assets/garments/g_${num}_cloth.jpg`, name, tag, category)
        );
    });
    grid.appendChild(frag);
}

// Application State
const state = {
    engineMode: "flux", // 'flux' (Flux.1 Dev Cloud) | 'catvton' | 'face_swap'
    personUrl: "assets/sample_person_female.jpg",
    personName: "Fashion Model",
    personFile: null,

    garmentUrl: "assets/sample_anarkali_dress.jpg",
    garmentName: "Green Anarkali Dress",
    garmentCategory: "full_body",
    garmentFile: null,

    steps: 40,
    categoryMode: "auto",
    viewMode: "comparison", // 'comparison', 'sidebyside', 'resultonly'

    currentResultSrc: null,
    history: [],
    timerInterval: null,
    stepTimeouts: [],
    startTime: 0,
    comfyuiConnected: false,
    faceswapReady: true
};

// DOM Elements
const dom = {};

window.addEventListener("DOMContentLoaded", () => {
    appendGarmentCatalog();
    cacheDomElements();
    bindEvents();
    initSlider();
    setEngineMode(state.engineMode);
    checkBackendHealth();
    setInterval(checkBackendHealth, 10000);
});

function cacheDomElements() {
    dom.backendStatusDot = document.getElementById("backend-status-dot");
    dom.backendStatusText = document.getElementById("backend-status-text");
    appendMenGarmentCatalog();
    dom.headerModeBadge = document.getElementById("header-mode-badge");
    dom.modeBtns = document.querySelectorAll("#mode-toggle-group .mode-btn");
    dom.genderBtns = document.querySelectorAll("#gender-filter-group .gender-btn");

    dom.btnQuickSample = document.getElementById("btn-quick-sample");
    dom.btnHeaderGenerate = document.getElementById("btn-header-generate");
    dom.btnStageGenerate = document.getElementById("btn-stage-generate");
    dom.btnReTry = document.getElementById("btn-re-try");
    dom.btnDownloadResult = document.getElementById("btn-download-result");

    // Person
    dom.sectionPersonTitle = document.getElementById("section-person-title");
    dom.personSelectionLabel = document.getElementById("person-selection-label");
    dom.personSamples = document.querySelectorAll("#person-samples .sample-card");
    dom.personFileInput = document.getElementById("person-file-input");
    dom.personDropzoneContent = document.getElementById("person-dropzone-content");
    dom.personPreviewWrap = document.getElementById("person-preview-wrap");
    dom.personCustomPreview = document.getElementById("person-custom-preview");
    dom.btnClearPerson = document.getElementById("btn-clear-person");

    // AI Cloud Generator Elements (Flux.1 Dev)
    dom.fluxStatusBadge = document.getElementById("flux-status-badge");
    dom.fluxStatusDot = document.getElementById("flux-status-dot");
    dom.fluxStatusText = document.getElementById("flux-status-text");

    dom.btnToggleAiPerson = document.getElementById("btn-toggle-ai-person");
    dom.aiPersonPanel = document.getElementById("ai-person-panel");
    dom.inputAiPerson = document.getElementById("input-ai-person");
    dom.btnSubmitAiPerson = document.getElementById("btn-submit-ai-person");
    dom.statusAiPerson = document.getElementById("status-ai-person");

    dom.btnToggleAiGarment = document.getElementById("btn-toggle-ai-garment");
    dom.aiGarmentPanel = document.getElementById("ai-garment-panel");
    dom.inputAiGarment = document.getElementById("input-ai-garment");
    dom.btnSubmitAiGarment = document.getElementById("btn-submit-ai-garment");
    dom.statusAiGarment = document.getElementById("status-ai-garment");
    dom.aiPromptChips = document.querySelectorAll(".prompt-chips .chip-btn");

    dom.fluxStylingBox = document.getElementById("flux-styling-box");
    dom.inputFluxPrompt = document.getElementById("input-flux-prompt");

    // Garment
    dom.sectionGarmentTitle = document.getElementById("section-garment-title");
    dom.garmentSelectionLabel = document.getElementById("garment-selection-label");
    dom.garmentSamples = document.querySelectorAll("#garment-samples .garment-card");
    dom.garmentFileInput = document.getElementById("garment-file-input");
    dom.garmentDropzoneContent = document.getElementById("garment-dropzone-content");
    dom.garmentDropzoneMain = document.getElementById("garment-dropzone-main");
    dom.garmentDropzoneSub = document.getElementById("garment-dropzone-sub");
    dom.garmentPreviewWrap = document.getElementById("garment-preview-wrap");
    dom.garmentCustomPreview = document.getElementById("garment-custom-preview");
    dom.btnClearGarment = document.getElementById("btn-clear-garment");

    // Settings controls
    dom.sectionSettingsTitle = document.getElementById("section-settings-title");
    dom.faceswapSettingsNote = document.getElementById("faceswap-settings-note");
    dom.diffusionSettingsBody = document.getElementById("diffusion-settings-body");
    dom.selectCategory = document.getElementById("select-category");
    dom.valCategory = document.getElementById("val-category");
    dom.sliderSteps = document.getElementById("slider-steps");
    dom.valSteps = document.getElementById("val-steps");
    dom.presetBtns = document.querySelectorAll(".preset-btn");

    // Views & Stage Labels
    dom.stageMainTitle = document.getElementById("stage-main-title");
    dom.stageSubText = document.getElementById("stage-sub-text");
    dom.stagePersonBadge = document.getElementById("stage-person-badge");
    dom.stageTransferText = document.getElementById("stage-transfer-text");
    dom.stageGarmentBadge = document.getElementById("stage-garment-badge");
    dom.readyTitle = document.getElementById("ready-title");
    dom.readyDesc = document.getElementById("ready-desc");

    dom.stageInitial = document.getElementById("stage-initial");
    dom.stageLoading = document.getElementById("stage-loading");
    dom.stageFooter = document.getElementById("stage-footer");
    dom.previewPersonImg = document.getElementById("preview-person-img");
    dom.previewPersonName = document.getElementById("preview-person-name");
    dom.previewGarmentImg = document.getElementById("preview-garment-img");
    dom.previewGarmentName = document.getElementById("preview-garment-name");

    // Result Containers
    dom.viewComparison = document.getElementById("view-comparison");
    dom.viewSidebyside = document.getElementById("view-sidebyside");
    dom.viewResultonly = document.getElementById("view-resultonly");
    dom.tabBtns = document.querySelectorAll("#view-mode-tabs .tab-btn");

    // Slider items
    dom.comparisonSlider = document.getElementById("comparison-slider");
    dom.compOverlay = document.getElementById("comp-overlay");
    dom.compHandle = document.getElementById("comp-handle");
    dom.compBeforeImg = document.getElementById("comp-before-img");
    dom.compAfterImg = document.getElementById("comp-after-img");
    dom.compBeforeLabel = document.getElementById("comp-before-label");
    dom.compAfterLabel = document.getElementById("comp-after-label");

    // Dual items
    dom.dualBeforeTitle = document.getElementById("dual-before-title");
    dom.dualAfterTitle = document.getElementById("dual-after-title");
    dom.dualAfterBadge = document.getElementById("dual-after-badge");
    dom.dualBeforeImg = document.getElementById("dual-before-img");
    dom.dualAfterImg = document.getElementById("dual-after-img");
    dom.singleResultImg = document.getElementById("single-result-img");

    // Metrics
    dom.metricLatency = document.getElementById("metric-latency");
    dom.metricCategory = document.getElementById("metric-category");
    dom.metricResolution = document.getElementById("metric-resolution");

    // Specs, Tips & History
    dom.specsSectionTitle = document.getElementById("specs-section-title");
    dom.detailGarmentThumb = document.getElementById("detail-garment-thumb");
    dom.detailGarmentTitle = document.getElementById("detail-garment-title");
    dom.detailGarmentCategory = document.getElementById("detail-garment-category");
    dom.detailGarmentNotes = document.getElementById("detail-garment-notes");
    dom.tipsTitle = document.getElementById("tips-title");
    dom.tipsList = document.getElementById("tips-list");
    dom.historyList = document.getElementById("history-list");
    dom.historyCount = document.getElementById("history-count");
    dom.historyEmpty = document.getElementById("history-empty");

    // Progress loading elements
    dom.loadingTitle = document.getElementById("loading-stage-title");
    dom.loadingDesc = document.getElementById("loading-stage-desc");
    dom.timerTag = document.getElementById("timer-tag");
    dom.pStep1 = document.getElementById("p-step-1");
    dom.pStep2 = document.getElementById("p-step-2");
    dom.pStep3 = document.getElementById("p-step-3");
    dom.pStep1Text = document.getElementById("p-step-1-text");
    dom.pStep2Text = document.getElementById("p-step-2-text");
    dom.pStep3Text = document.getElementById("p-step-3-text");

    // Zoom modal
    dom.zoomModal = document.getElementById("zoom-modal");
    dom.zoomModalImg = document.getElementById("zoom-modal-img");
    dom.btnZoomClose = document.getElementById("btn-zoom-close");
}

function bindEvents() {
    // Workflow Mode Switcher
    dom.modeBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            setEngineMode(btn.dataset.mode);
        });
    });
    // Person selection cards
    dom.personSamples.forEach(card => {
        card.addEventListener("click", () => {
            dom.personSamples.forEach(c => c.classList.remove("active"));
            card.classList.add("active");
            state.personUrl = card.dataset.url;
            state.personName = card.dataset.name;
            state.personFile = null;

            // Clear custom upload preview if any
            dom.personPreviewWrap.style.display = "none";
            dom.personDropzoneContent.style.display = "flex";
            dom.personFileInput.value = "";

            updatePersonPreview();
        });
    });

    // Custom Person Upload
    dom.personFileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            handlePersonFile(e.target.files[0]);
        }
    });

    dom.btnClearPerson.addEventListener("click", (e) => {
        e.stopPropagation();
        state.personFile = null;
        dom.personFileInput.value = "";
        dom.personPreviewWrap.style.display = "none";
        dom.personDropzoneContent.style.display = "flex";

        // Restore first sample
        dom.personSamples[0].click();
    });

    // Garment selection cards
    dom.garmentSamples.forEach(card => {
        card.addEventListener("click", () => {
            dom.garmentSamples.forEach(c => c.classList.remove("active"));
            card.classList.add("active");
            state.garmentUrl = card.dataset.url;
            state.garmentName = card.dataset.name;
            state.garmentCategory = card.dataset.category || "upper_body";
            state.garmentFile = null;

            // Clear custom upload preview
            dom.garmentPreviewWrap.style.display = "none";
            dom.garmentDropzoneContent.style.display = "flex";
            dom.garmentFileInput.value = "";

            updateGarmentPreview();
        });
    });

    // Custom Garment Upload
    dom.garmentFileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            handleGarmentFile(e.target.files[0]);
        }
    });

    dom.btnClearGarment.addEventListener("click", (e) => {
        e.stopPropagation();
        state.garmentFile = null;
        dom.garmentFileInput.value = "";
        dom.garmentPreviewWrap.style.display = "none";
        dom.garmentDropzoneContent.style.display = "flex";

        const compatible = getCompatibleGarmentCards();
        if (compatible.length > 0) compatible[0].click();
    });

    // AI Cloud Generator Actions (Person)
    if (dom.btnToggleAiPerson && dom.aiPersonPanel) {
        dom.btnToggleAiPerson.addEventListener("click", () => {
            const isHidden = dom.aiPersonPanel.style.display === "none";
            dom.aiPersonPanel.style.display = isHidden ? "flex" : "none";
            dom.btnToggleAiPerson.classList.toggle("open", isHidden);
            if (isHidden) dom.inputAiPerson.focus();
        });
    }

    if (dom.btnSubmitAiPerson) {
        dom.btnSubmitAiPerson.addEventListener("click", () => handleCloudGenerate("person"));
    }
    if (dom.inputAiPerson) {
        dom.inputAiPerson.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                handleCloudGenerate("person");
            }
        });
    }

    // AI Cloud Generator Actions (Garment)
    if (dom.btnToggleAiGarment && dom.aiGarmentPanel) {
        dom.btnToggleAiGarment.addEventListener("click", () => {
            const isHidden = dom.aiGarmentPanel.style.display === "none";
            dom.aiGarmentPanel.style.display = isHidden ? "flex" : "none";
            dom.btnToggleAiGarment.classList.toggle("open", isHidden);
            if (isHidden) dom.inputAiGarment.focus();
        });
    }

    if (dom.btnSubmitAiGarment) {
        dom.btnSubmitAiGarment.addEventListener("click", () => handleCloudGenerate("garment"));
    }
    if (dom.inputAiGarment) {
        dom.inputAiGarment.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                handleCloudGenerate("garment");
            }
        });
    }

    // Preset Prompt Chips
    dom.aiPromptChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const target = chip.dataset.target;
            const prompt = chip.dataset.prompt;
            if (target === "person") {
                dom.inputAiPerson.value = prompt;
                handleCloudGenerate("person");
            } else {
                dom.inputAiGarment.value = prompt;
                handleCloudGenerate("garment");
            }
        });
    });

    // Preset Steps Buttons
    dom.presetBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            dom.presetBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            const steps = parseInt(btn.dataset.steps);
            state.steps = steps;
            dom.sliderSteps.value = steps;
            updateStepLabel(steps);
        });
    });

    dom.sliderSteps.addEventListener("input", (e) => {
        const val = parseInt(e.target.value);
        state.steps = val;
        updateStepLabel(val);
        dom.presetBtns.forEach(b => {
            b.classList.toggle("active", parseInt(b.dataset.steps) === val);
        });
    });

    dom.selectCategory.addEventListener("change", (e) => {
        state.categoryMode = e.target.value;
        if (state.categoryMode === "auto") {
            dom.valCategory.innerText = `${state.garmentCategory} (Auto)`;
        } else {
            state.garmentCategory = state.categoryMode;
            dom.valCategory.innerText = `${state.garmentCategory} (Manual)`;
        }
    });

    // View Mode Tabs
    dom.tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            dom.tabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            state.viewMode = btn.dataset.view;
            renderActiveViewMode();
        });
    });

    // Action Triggers
    dom.btnHeaderGenerate.addEventListener("click", triggerGenerate);
    dom.btnStageGenerate.addEventListener("click", triggerGenerate);
    dom.btnReTry.addEventListener("click", () => {
        // Switch back to input preview
        dom.stageInitial.style.display = "flex";
        dom.viewComparison.style.display = "none";
        dom.viewSidebyside.style.display = "none";
        dom.viewResultonly.style.display = "none";
        dom.stageFooter.style.display = "none";
    });

    dom.btnQuickSample.addEventListener("click", loadRandomSampleOutfit);

    // Zoom modal
    dom.singleResultImg.addEventListener("click", () => {
        if (state.currentResultSrc) {
            dom.zoomModalImg.src = state.currentResultSrc;
            dom.zoomModal.classList.add("open");
        }
    });

    dom.btnZoomClose.addEventListener("click", () => dom.zoomModal.classList.remove("open"));
    dom.zoomModal.addEventListener("click", (e) => {
        if (e.target === dom.zoomModal) dom.zoomModal.classList.remove("open");
    });
}

function updateStepLabel(steps) {
    let est = "~8s";
    if (steps > 28) est = "~14s";
    else if (steps > 22) est = "~10s";
    dom.valSteps.innerText = `${steps} steps (${est})`;
}

function handlePersonFile(file) {
    state.personFile = file;
    state.personName = file.name.replace(/\.[^/.]+$/, "");
    dom.personSamples.forEach(c => c.classList.remove("active"));

    const reader = new FileReader();
    reader.onload = (e) => {
        state.personUrl = e.target.result;
        dom.personCustomPreview.src = state.personUrl;
        dom.personDropzoneContent.style.display = "none";
        dom.personPreviewWrap.style.display = "block";
        updatePersonPreview();
    };
    reader.readAsDataURL(file);
}

function handleGarmentFile(file) {
    state.garmentFile = file;
    state.garmentName = file.name.replace(/\.[^/.]+$/, "");
    dom.garmentSamples.forEach(c => c.classList.remove("active"));

    const reader = new FileReader();
    reader.onload = (e) => {
        state.garmentUrl = e.target.result;
        dom.garmentCustomPreview.src = state.garmentUrl;
        dom.garmentDropzoneContent.style.display = "none";
        dom.garmentPreviewWrap.style.display = "block";
        updateGarmentPreview();
        if (state.engineMode === "catvton") {
            autoClassifyGarment(file);
        }
    };
    reader.readAsDataURL(file);
}

async function autoClassifyGarment(file) {
    try {
        const formData = new FormData();
        formData.append("garment_image", file);
        const res = await fetch("/api/v1/classify-garment", { method: "POST", body: formData });
        if (res.ok) {
            const data = await res.json();
            if (data.category) {
                state.garmentCategory = data.category;
                if (state.categoryMode === "auto") {
                    dom.valCategory.innerText = `${data.category} (Detected)`;
                }
            }
        }
    } catch (_) {}
}

function getCompatibleGarmentCards(mode = state.engineMode) {
    if (mode === "flux") {
        // Flux.1 Dev supports all fashion items and catalog entries!
        return Array.from(dom.garmentSamples);
    }
    const supportsAttr = MODE_UI[mode]?.supportsAttr || "catvton";
    return Array.from(dom.garmentSamples).filter(card => {
        const supports = (card.dataset.supports || "catvton").split(/\s+/);
        return supports.includes(supportsAttr);
    });
}

function getBeforeSrc() {
    return state.engineMode === "face_swap" ? state.garmentUrl : state.personUrl;
}

function syncBeforeImages(src = getBeforeSrc()) {
    dom.compBeforeImg.src = src;
    dom.dualBeforeImg.src = src;
}

function setEngineMode(mode) {
    const cfg = MODE_UI[mode] || MODE_UI.flux;
    state.engineMode = MODE_UI[mode] ? mode : "flux";

    dom.modeBtns.forEach(btn => {
        btn.classList.toggle("active", btn.dataset.mode === state.engineMode);
    });

    const isFlux = state.engineMode === "flux";
    const isFaceSwap = state.engineMode === "face_swap";
    dom.faceswapSettingsNote.style.display = isFaceSwap ? "block" : "none";
    dom.diffusionSettingsBody.style.display = (isFaceSwap || isFlux) ? "none" : "block";
    if (dom.fluxStylingBox) {
        dom.fluxStylingBox.style.display = isFlux ? "flex" : "none";
    }

    dom.headerModeBadge.innerText = cfg.headerBadge;
    dom.btnHeaderGenerate.innerText = cfg.generateBtn;
    dom.btnStageGenerate.innerText = cfg.stageGenerateBtn;
    dom.sectionPersonTitle.innerText = cfg.personSectionTitle;
    dom.sectionGarmentTitle.innerText = cfg.garmentSectionTitle;
    dom.garmentDropzoneMain.innerText = cfg.garmentDropMain;
    dom.garmentDropzoneSub.innerText = cfg.garmentDropSub;
    dom.sectionSettingsTitle.innerText = cfg.settingsTitle;
    dom.stageMainTitle.innerText = cfg.stageMainTitle;
    dom.stageSubText.innerText = cfg.stageSubText;
    dom.stagePersonBadge.innerText = cfg.stagePersonBadge;
    dom.stageTransferText.innerText = cfg.stageTransferText;
    dom.stageGarmentBadge.innerText = cfg.stageGarmentBadge;
    dom.readyTitle.innerText = cfg.readyTitle;
    dom.readyDesc.innerText = cfg.readyDesc;
    dom.loadingTitle.innerText = cfg.loadingTitle;
    dom.pStep1Text.innerText = cfg.loadingSteps[0];
    dom.pStep2Text.innerText = cfg.loadingSteps[1];
    dom.pStep3Text.innerText = cfg.loadingSteps[2];
    dom.compBeforeLabel.innerText = cfg.compBeforeLabel;
    dom.compAfterLabel.innerText = cfg.compAfterLabel;
    dom.dualBeforeTitle.innerText = cfg.dualBeforeTitle;
    dom.dualAfterTitle.innerText = cfg.dualAfterTitle;
    dom.dualAfterBadge.innerText = cfg.dualAfterBadge;
    dom.btnReTry.innerText = cfg.reTryBtn;
    dom.specsSectionTitle.innerText = cfg.specsTitle;
    dom.detailGarmentNotes.innerText = cfg.garmentNotes;
    dom.tipsTitle.innerText = cfg.tipsTitle;
    dom.tipsList.innerHTML = cfg.tipsHtml.map(t => `<li>${t}</li>`).join("");

    // Filter garment cards for the active workflow
    const compatibleCards = getCompatibleGarmentCards(state.engineMode);
    const compatibleSet = new Set(compatibleCards);
    dom.garmentSamples.forEach(card => {
        card.style.display = compatibleSet.has(card) ? "" : "none";
    });

    // If user hasn't uploaded a custom garment and active card isn't compatible, select first compatible preset
    if (!state.garmentFile && compatibleCards.length > 0) {
        const activeCard = Array.from(dom.garmentSamples).find(c => c.classList.contains("active"));
        if (!activeCard || !compatibleSet.has(activeCard)) {
            compatibleCards[0].click();
        }
    }

    syncBeforeImages();
    renderHealthBadge();
}

function updatePersonPreview() {
    dom.personSelectionLabel.innerText = state.personName;
    dom.previewPersonImg.src = state.personUrl;
    dom.previewPersonName.innerText = state.personName;
    syncBeforeImages();
}

function updateGarmentPreview() {
    dom.garmentSelectionLabel.innerText = state.garmentName;
    dom.previewGarmentImg.src = state.garmentUrl;
    dom.previewGarmentName.innerText = state.garmentName;

    dom.detailGarmentThumb.src = state.garmentUrl;
    dom.detailGarmentTitle.innerText = state.garmentName;
    dom.detailGarmentCategory.innerText = state.garmentCategory.toUpperCase().replace("_", " ");

    if (state.categoryMode === "auto") {
        dom.valCategory.innerText = `${state.garmentCategory} (Auto)`;
    }

    if (dom.inputFluxPrompt) {
        const hintMap = {
            "Green Anarkali Dress": "Emerald green silk Indian anarkali dress with intricate gold embroidery and matching dupatta",
            "Anarkali Outfit Model": "Traditional royal emerald green bridal anarkali gown with gold zardozi work",
            "Casual Tee Model": "Modern casual heather grey crewneck t-shirt with slim fit denim",
            "Casual Top Model": "Contemporary casual ivory sleeveless summer top",
            "Kurta & Jacket Model": "Traditional cream silk kurta with embroidered nehru jacket",
            "Emerald Oxford Shirt": "Crisp emerald green button-up oxford shirt, clean casual fit",
            "Selvedge Denim Jacket": "Classic vintage indigo blue denim trucker jacket over white tee",
            "Essential Black Tee": "Minimalist premium black cotton crew-neck t-shirt",
            "Tailored Navy Blazer": "Formal tailored navy blue wool blazer over crisp white shirt"
        };
        dom.inputFluxPrompt.value = hintMap[state.garmentName] || `Exquisite designer ${state.garmentName}, perfectly tailored luxury fashion, photorealistic 8k`;
    }

    syncBeforeImages();
}

function loadRandomSampleOutfit() {
    const pIdx = Math.floor(Math.random() * dom.personSamples.length);
    const compatible = getCompatibleGarmentCards();
    const gIdx = Math.floor(Math.random() * compatible.length);
    dom.personSamples[pIdx].click();
    if (compatible[gIdx]) compatible[gIdx].click();
}

// -----------------------------------------------------------------------------
// Interactive Before / After Slider
// -----------------------------------------------------------------------------
function initSlider() {
    let isDragging = false;
    const slider = dom.comparisonSlider;

    function moveDivider(clientX) {
        const rect = slider.getBoundingClientRect();
        let posX = clientX - rect.left;
        posX = Math.max(0, Math.min(posX, rect.width));
        const pct = (posX / rect.width) * 100;

        dom.compOverlay.style.width = `${pct}%`;
        dom.compHandle.style.left = `${pct}%`;
    }

    slider.addEventListener("mousedown", (e) => {
        isDragging = true;
        moveDivider(e.clientX);
    });

    window.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        moveDivider(e.clientX);
    });

    window.addEventListener("mouseup", () => {
        isDragging = false;
    });

    // Touch support
    slider.addEventListener("touchstart", (e) => {
        isDragging = true;
        if (e.touches[0]) moveDivider(e.touches[0].clientX);
    });

    window.addEventListener("touchmove", (e) => {
        if (!isDragging) return;
        if (e.touches[0]) moveDivider(e.touches[0].clientX);
    });

    window.addEventListener("touchend", () => {
        isDragging = false;
    });
}

function renderActiveViewMode() {
    if (!state.currentResultSrc) return;

    dom.stageInitial.style.display = "none";
    dom.viewComparison.style.display = state.viewMode === "comparison" ? "flex" : "none";
    dom.viewSidebyside.style.display = state.viewMode === "sidebyside" ? "flex" : "none";
    dom.viewResultonly.style.display = state.viewMode === "resultonly" ? "flex" : "none";
}

// -----------------------------------------------------------------------------
// Backend Health Polling
// -----------------------------------------------------------------------------
function renderHealthBadge() {
    if (state.engineMode === "face_swap") {
        if (state.faceswapReady) {
            dom.backendStatusDot.className = "status-pulse-dot online";
            dom.backendStatusText.innerText = state.comfyuiConnected
                ? "Face Swap + GPU Ready"
                : "Face Swap Ready";
        } else {
            dom.backendStatusDot.className = "status-pulse-dot";
            dom.backendStatusText.innerText = "Checking Face Swap Engine...";
        }
        return;
    }

    if (state.comfyuiConnected) {
        dom.backendStatusDot.className = "status-pulse-dot online";
        dom.backendStatusText.innerText = "ComfyUI GPU Ready";
    } else {
        dom.backendStatusDot.className = "status-pulse-dot";
        dom.backendStatusText.innerText = "Backend Degraded (Waiting for ComfyUI)";
    }
}

async function checkBackendHealth() {
    try {
        const res = await fetch("/health");
        if (res.ok) {
            const data = await res.json();
            if (data.status === "healthy") {
                state.comfyuiConnected = data.comfyui_backend === "connected";
                state.faceswapReady = Boolean(data.faceswap_ready);
                state.cloudFluxReady = Boolean(data.cloud_flux_ready);
                if (dom.fluxStatusDot && dom.fluxStatusText) {
                    dom.fluxStatusDot.style.background = state.cloudFluxReady ? "#10b981" : "#ef4444";
                    dom.fluxStatusText.innerText = state.cloudFluxReady ? "✨ Flux.1 Cloud API" : "Flux.1 Offline";
                }
                renderHealthBadge();
                return;
            }
        }
    } catch (_) {}
    state.comfyuiConnected = false;
    state.faceswapReady = false;
    renderHealthBadge();
}

// -----------------------------------------------------------------------------
// Cloud Fashion Model & Garment Generation (Flux.1 Dev)
// -----------------------------------------------------------------------------
async function handleCloudGenerate(target) {
    const isPerson = target === "person";
    const inputEl = isPerson ? dom.inputAiPerson : dom.inputAiGarment;
    const btnEl = isPerson ? dom.btnSubmitAiPerson : dom.btnSubmitAiGarment;
    const statusEl = isPerson ? dom.statusAiPerson : dom.statusAiGarment;
    const prompt = inputEl ? inputEl.value.trim() : "";

    if (!prompt) {
        showAiStatus(statusEl, "error", "Please enter a prompt or click a preset chip above.");
        if (inputEl) inputEl.focus();
        return;
    }

    if (btnEl) btnEl.disabled = true;
    const origHtml = btnEl ? btnEl.innerHTML : "";
    if (btnEl) btnEl.innerHTML = `<span class="inner-spin" style="width:12px;height:12px;border:2px solid #fff;border-top-color:transparent;border-radius:50%;display:inline-block;animation:spin 0.8s linear infinite;"></span> Synthesizing...`;
    showAiStatus(statusEl, "info", `✨ Generating via Flux.1 Dev on cloud (~12-18s)...`);

    try {
        const resp = await fetch("/api/v1/generate-cloud-image", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                prompt: prompt,
                target: target,
                size: "1024x1024"
            })
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ detail: "Generation request failed" }));
            throw new Error(err.detail || `HTTP ${resp.status}`);
        }

        const data = await resp.json();
        const imgUrl = data.image_data || data.result_url;

        showAiStatus(statusEl, "success", `✅ Generated in ${data.latency_seconds || 15}s! Active on fitting canvas.`);

        if (isPerson) {
            state.personUrl = imgUrl;
            state.personName = `AI: ${prompt.slice(0, 24)}...`;
            state.personFile = null;

            // Deselect preset cards
            dom.personSamples.forEach(c => c.classList.remove("active"));

            // Show custom preview wrap
            dom.personCustomPreview.src = imgUrl;
            dom.personPreviewWrap.style.display = "block";
            dom.personDropzoneContent.style.display = "none";
            if (dom.personFileInput) dom.personFileInput.value = "";

            updatePersonPreview();
        } else {
            state.garmentUrl = imgUrl;
            state.garmentName = `AI: ${prompt.slice(0, 24)}...`;
            state.garmentCategory = data.category_hint || "upper_body";
            state.garmentFile = null;

            // Deselect preset garment cards
            dom.garmentSamples.forEach(c => c.classList.remove("active"));

            // Show custom preview wrap
            dom.garmentCustomPreview.src = imgUrl;
            dom.garmentPreviewWrap.style.display = "block";
            dom.garmentDropzoneContent.style.display = "none";
            if (dom.garmentFileInput) dom.garmentFileInput.value = "";

            updateGarmentPreview();
        }

        syncBeforeImages();
    } catch (err) {
        showAiStatus(statusEl, "error", `❌ ${err.message}`);
    } finally {
        if (btnEl) {
            btnEl.disabled = false;
            btnEl.innerHTML = origHtml;
        }
    }
}

function showAiStatus(el, type, msg) {
    if (!el) return;
    el.className = `ai-status ${type}`;
    el.innerText = msg;
    el.style.display = "block";
}

function clearStepTimeouts() {
    state.stepTimeouts.forEach(t => clearTimeout(t));
    state.stepTimeouts = [];
}

// -----------------------------------------------------------------------------
// Generation Pipeline (Face Swap, 2D CatVTON, or Flux.1 Dev Cloud)
// -----------------------------------------------------------------------------
async function triggerGenerate() {
    const isFlux = state.engineMode === "flux";
    const isFaceSwap = state.engineMode === "face_swap";
    dom.btnHeaderGenerate.disabled = true;
    dom.btnStageGenerate.disabled = true;
    dom.btnHeaderGenerate.innerText = isFlux
        ? "⏳ Synthesizing (Flux)..."
        : (isFaceSwap ? "⏳ Swapping..." : "⏳ Generating...");

    clearStepTimeouts();
    dom.stageLoading.style.display = "flex";
    setLoadingStep(
        1,
        isFlux
            ? "Preparing inputs and connecting to Railway Cloud GPU..."
            : (isFaceSwap
                ? "Detecting face landmarks in your photo..."
                : "Uploading assets and classifying garment category...")
    );

    state.startTime = performance.now();
    startLoadingTimer();

    try {
        const formData = new FormData();

        // Garment / Model wearing outfit
        if (state.garmentFile) {
            formData.append("garment_image", state.garmentFile);
        } else {
            const resG = await fetch(state.garmentUrl);
            const blobG = await resG.blob();
            const gExt = state.garmentUrl.endsWith(".png") ? "garment.png" : "garment.jpg";
            formData.append("garment_image", blobG, gExt);
        }

        // User face / target person
        if (state.personFile) {
            formData.append("person_image", state.personFile);
        } else {
            const resP = await fetch(state.personUrl);
            const blobP = await resP.blob();
            const pExt = state.personUrl.endsWith(".png") ? "person.png" : "person.jpg";
            formData.append("person_image", blobP, pExt);
        }

        // Engine, Category, Domain & Steps
        formData.append("engine", isFlux ? "flux" : (isFaceSwap ? "face_swap" : "default"));
        formData.append("category", state.garmentCategory);
        formData.append("domain", state.garmentCategory === "full_body" ? "indian_ethnic" : "western");
        formData.append("steps", state.steps.toString());

        if (isFlux) {
            const fluxPrompt = dom.inputFluxPrompt ? dom.inputFluxPrompt.value.trim() : "";
            if (fluxPrompt) {
                formData.append("prompt", fluxPrompt);
            }
            formData.append("garment_desc", state.garmentName);
        }

        if (isFlux) {
            state.stepTimeouts.push(
                setTimeout(() => {
                    setLoadingStep(2, "Submitting to FLUX-DEV-012 Cloud Synthesizer...");
                }, 1200),
                setTimeout(() => {
                    setLoadingStep(3, "Flux.1 Dev 1024×1024 Latent Diffusion in progress (~15-25s)...");
                }, 4000)
            );
        } else {
            state.stepTimeouts.push(
                setTimeout(() => {
                    setLoadingStep(
                        2,
                        isFaceSwap
                            ? "Locating face on the garment model photo..."
                            : "Extracting clothing mask via SegFormer Fashion parser..."
                    );
                }, isFaceSwap ? 450 : 1200),
                setTimeout(() => {
                    setLoadingStep(
                        3,
                        isFaceSwap
                            ? "Blending your identity cleanly into the outfit..."
                            : "Running CatVTON Visual Conditioning Diffusion UNet..."
                    );
                }, isFaceSwap ? 950 : 3200)
            );
        }

        const response = await fetch("/api/v1/try-on", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errText = await response.text();
            let msg = `Server returned HTTP ${response.status}`;
            try {
                const errJson = JSON.parse(errText);
                msg = errJson.detail || msg;
            } catch (_) {}
            throw new Error(msg);
        }

        const contentType = response.headers.get("content-type") || "";
        let finalSrc = "";
        let latencySec = ((performance.now() - state.startTime) / 1000).toFixed(1);
        let detectedCat = isFlux ? "FLUX-DEV-012 (Cloud)" : (isFaceSwap ? "face_swap" : state.garmentCategory);

        if (contentType.includes("application/json")) {
            const jsonResult = await response.json();
            finalSrc = jsonResult.image_data || jsonResult.result_url;
            if (jsonResult.latency_seconds) latencySec = jsonResult.latency_seconds;
            if (jsonResult.model_used) detectedCat = jsonResult.model_used;
            else if (jsonResult.category) detectedCat = jsonResult.category;
        } else {
            const blob = await response.blob();
            finalSrc = URL.createObjectURL(blob);
        }

        clearStepTimeouts();
        stopLoadingTimer();
        dom.stageLoading.style.display = "none";

        const beforeSrc = getBeforeSrc();
        state.currentResultSrc = finalSrc;
        dom.singleResultImg.onload = () => {
            if (dom.singleResultImg.naturalWidth > 0) {
                dom.metricResolution.innerText = `${dom.singleResultImg.naturalWidth} × ${dom.singleResultImg.naturalHeight}`;
            }
        };
        syncBeforeImages(beforeSrc);
        dom.compAfterImg.src = finalSrc;
        dom.dualAfterImg.src = finalSrc;
        dom.singleResultImg.src = finalSrc;

        // Metrics & Footer
        dom.metricLatency.innerText = `${latencySec}s`;
        dom.metricCategory.innerText = detectedCat;
        dom.btnDownloadResult.href = finalSrc;
        dom.stageFooter.style.display = "flex";

        renderActiveViewMode();

        addToHistory({
            personName: state.personName,
            garmentName: state.garmentName,
            beforeSrc,
            resultSrc: finalSrc,
            latency: latencySec,
            categoryLabel: detectedCat,
            time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        });

    } catch (err) {
        clearStepTimeouts();
        stopLoadingTimer();
        dom.stageLoading.style.display = "none";
        const hint = isFaceSwap
            ? "Make sure both photos contain a clear, visible front-facing face."
            : "Please ensure the FastAPI server and ComfyUI GPU backend are running.";
        alert(`${isFaceSwap ? "Face Swap" : "Try-On"} Failed: ${err.message}\n\n${hint}`);
    } finally {
        clearStepTimeouts();
        dom.btnHeaderGenerate.disabled = false;
        dom.btnStageGenerate.disabled = false;
        dom.btnHeaderGenerate.innerText = MODE_UI[state.engineMode].generateBtn;
    }
}

function setLoadingStep(stepNum, desc) {
    dom.loadingDesc.innerText = desc;
    [dom.pStep1, dom.pStep2, dom.pStep3].forEach((el, idx) => {
        el.classList.remove("active", "done");
        if (idx + 1 < stepNum) el.classList.add("done");
        else if (idx + 1 === stepNum) el.classList.add("active");
    });
}

function startLoadingTimer() {
    clearInterval(state.timerInterval);
    dom.timerTag.innerText = "Elapsed: 0.0s";
    state.timerInterval = setInterval(() => {
        const elapsed = ((performance.now() - state.startTime) / 1000).toFixed(1);
        dom.timerTag.innerText = `Elapsed: ${elapsed}s`;
    }, 100);
}

function stopLoadingTimer() {
    clearInterval(state.timerInterval);
}

function addToHistory(item) {
    state.history.unshift(item);
    dom.historyCount.innerText = `${state.history.length} item${state.history.length > 1 ? "s" : ""}`;
    dom.historyEmpty.style.display = "none";

    const el = document.createElement("div");
    el.className = "history-item";
    el.innerHTML = `
        <img src="${item.resultSrc}" alt="Result">
        <div class="history-item-meta">
            <span class="name">${item.garmentName}</span>
            <span class="time">${item.time} &bull; ${item.latency}s</span>
        </div>
    `;

    el.addEventListener("click", () => {
        state.currentResultSrc = item.resultSrc;
        if (item.beforeSrc) syncBeforeImages(item.beforeSrc);
        dom.compAfterImg.src = item.resultSrc;
        dom.dualAfterImg.src = item.resultSrc;
        dom.singleResultImg.src = item.resultSrc;
        if (item.latency) dom.metricLatency.innerText = `${item.latency}s`;
        if (item.categoryLabel) dom.metricCategory.innerText = item.categoryLabel;
        dom.btnDownloadResult.href = item.resultSrc;
        dom.stageFooter.style.display = "flex";
        renderActiveViewMode();
    });

    dom.historyList.prepend(el);
}

// -----------------------------------------------------------------------------
// Men's Ethnic & Western Apparel Catalog + Gender Filter Synchronization
// -----------------------------------------------------------------------------
const MEN_GARMENT_ENTRIES = [
    // Paired Men Ethnic Kurtas (available in both Face Swap & Cloth Try-On)
    ["faceswap", "assets/garments/m_01_model.jpg", "Ivory Chikankari Kurta", "Ethnic Kurta", "full_body"],
    ["catvton", "assets/garments/m_01_cloth.jpg", "Ivory Chikankari Kurta", "Ethnic Kurta", "full_body"],
    ["faceswap", "assets/garments/m_02_model.jpg", "Royal Sapphire Silk Kurta", "Silk Kurta", "full_body"],
    ["catvton", "assets/garments/m_02_cloth.jpg", "Royal Sapphire Silk Kurta", "Silk Kurta", "full_body"],

    // Men Outfit Models (Face / Head Swap)
    ["faceswap", "assets/garments/mm_04.jpg", "Charcoal Printed Kurta", "Ethnic Kurta", "full_body"],
    ["faceswap", "assets/garments/mm_05.jpg", "Sand Chevron Short Kurta", "Ethnic Kurta", "upper_body"],
    ["faceswap", "assets/garments/mm_06.jpg", "Navy Tailored Waistcoat", "Formal Vest", "upper_body"],
    ["faceswap", "assets/garments/mm_07.jpg", "Slate Grey Formal Vest", "Formal Vest", "upper_body"],
    ["faceswap", "assets/garments/mm_08.jpg", "Emerald Tartan Waistcoat", "Tartan Vest", "upper_body"],
    ["faceswap", "assets/garments/mm_09.jpg", "Crimson Check Waistcoat", "Check Vest", "upper_body"],
    ["faceswap", "assets/garments/mm_10.jpg", "Jet Black Formal Shirt", "Button Shirt", "upper_body"],
    ["faceswap", "assets/garments/mm_11.jpg", "Sky Blue Tartan Shirt", "Plaid Shirt", "upper_body"],
    ["faceswap", "assets/garments/mm_12.jpg", "Olive Checkered Shirt", "Flannel Shirt", "upper_body"],
    ["faceswap", "assets/garments/mm_13.jpg", "Espresso Check Shirt", "Button Shirt", "upper_body"],
    ["faceswap", "assets/garments/mm_14.jpg", "Midnight Motorsport Jacket", "Track Jacket", "upper_body"],
    ["faceswap", "assets/garments/mm_15.jpg", "Scarlet Track Jacket", "Track Jacket", "upper_body"],
    ["faceswap", "assets/garments/mm_16.jpg", "Cobalt Windrunner Jacket", "Sport Jacket", "upper_body"],
    ["faceswap", "assets/garments/mm_17.jpg", "Ivory Collegiate Jacket", "Varsity Jacket", "upper_body"],
    ["faceswap", "assets/garments/mm_18.jpg", "Cobalt Fleece Hoodie", "Street Hoodie", "upper_body"],

    // Men Flat-Lay Reference Garments (Cloth Try-On)
    ["catvton", "assets/garments/mc_04.jpg", "Deep Maroon Nehru Jacket", "Nehru Jacket", "upper_body"],
    ["catvton", "assets/garments/m_03_cloth.jpg", "Navy Classic Crew Tee", "Essential Tee", "upper_body"],
    ["catvton", "assets/garments/mc_05.jpg", "Obsidian Collared Shirt", "Button Shirt", "upper_body"],
    ["catvton", "assets/garments/mc_06.jpg", "Navy Crest Utility Shirt", "Casual Shirt", "upper_body"],
    ["catvton", "assets/garments/mc_07.jpg", "Electric Blue Windrunner", "Sport Jacket", "upper_body"],
    ["catvton", "assets/garments/mc_08.jpg", "Crimson Zip Track Jacket", "Track Jacket", "upper_body"],
    ["catvton", "assets/garments/mc_09.jpg", "Heather White Hoodie", "Street Hoodie", "upper_body"],
    ["catvton", "assets/garments/mc_10.jpg", "Jet Black Crew Sweatshirt", "Sweatshirt", "upper_body"],
    ["catvton", "assets/garments/mc_11.jpg", "Burgundy Quarter-Zip Top", "Activewear", "upper_body"],
    ["catvton", "assets/garments/mc_12.jpg", "Graphite Half-Zip Pullover", "Activewear", "upper_body"],
    ["catvton", "assets/garments/mc_13.jpg", "Black Graphic Crew Tee", "Casual Tee", "upper_body"],
    ["catvton", "assets/garments/mc_14.jpg", "Scarlet Collar Polo", "Polo Shirt", "upper_body"],
    ["catvton", "assets/garments/mc_15.jpg", "Charcoal Athletic Tee", "Essential Tee", "upper_body"],
    ["catvton", "assets/garments/mc_16.jpg", "Canary Crewneck Tee", "Essential Tee", "upper_body"],
    ["catvton", "assets/garments/mc_17.jpg", "Lavender Studio Tee", "Essential Tee", "upper_body"]
];

function appendMenGarmentCatalog() {
    const grid = document.getElementById("garment-samples");
    if (!grid || grid.dataset.menCatalogLoaded === "1") return;
    grid.dataset.menCatalogLoaded = "1";

    const firstExtraWomen = grid.querySelector('.garment-card[data-url*="g_01_"]');
    const frag = document.createDocumentFragment();
    MEN_GARMENT_ENTRIES.forEach(([supports, url, name, tag, category]) => {
        frag.appendChild(createGarmentCard(supports, url, name, tag, category, "men"));
    });

    if (firstExtraWomen) {
        grid.insertBefore(frag, firstExtraWomen);
    } else {
        grid.appendChild(frag);
    }
}

function ensureVisibleActiveSelections() {
    const supportsKey = state.engineMode === "face_swap" ? "faceswap" : "catvton";

    if (!state.personFile) {
        const activePerson = document.querySelector("#person-samples .sample-card.active");
        if (!activePerson || activePerson.classList.contains("is-gender-hidden")) {
            const nextPerson = document.querySelector("#person-samples .sample-card:not(.is-gender-hidden)");
            if (nextPerson) nextPerson.click();
        }
    }

    if (!state.garmentFile) {
        const activeGarment = document.querySelector("#garment-samples .garment-card.active");
        const activeMatchesMode = activeGarment && activeGarment.dataset.supports === supportsKey;
        if (!activeGarment || !activeMatchesMode || activeGarment.classList.contains("is-gender-hidden")) {
            const nextGarment = document.querySelector(
                `#garment-samples .garment-card[data-supports="${supportsKey}"]:not(.is-gender-hidden)`
            );
            if (nextGarment) nextGarment.click();
        }
    }
}

function applyGenderFilter(gender) {
    state.genderFilter = gender;
    document.querySelectorAll("#gender-filter-group .gender-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.gender === gender);
    });

    const toggleCard = card => {
        const cardGender = card.dataset.gender || "all";
        const visible = gender === "all" || cardGender === gender || cardGender === "all";
        card.classList.toggle("is-gender-hidden", !visible);
    };

    document.querySelectorAll("#person-samples .sample-card").forEach(toggleCard);
    document.querySelectorAll("#garment-samples .garment-card").forEach(toggleCard);

    ensureVisibleActiveSelections();
}

document.addEventListener("DOMContentLoaded", () => {
    const filterGroup = document.getElementById("gender-filter-group");
    if (filterGroup) {
        filterGroup.addEventListener("click", e => {
            const btn = e.target.closest(".gender-btn");
            if (btn && btn.dataset.gender) {
                applyGenderFilter(btn.dataset.gender);
            }
        });
    }

    const modeGroup = document.getElementById("mode-toggle-group");
    if (modeGroup) {
        modeGroup.addEventListener("click", () => {
            queueMicrotask(ensureVisibleActiveSelections);
        });
    }

    const quickSampleBtn = document.getElementById("btn-quick-sample");
    if (quickSampleBtn) {
        quickSampleBtn.addEventListener("click", () => {
            queueMicrotask(() => {
                if (state.genderFilter && state.genderFilter !== "all") {
                    applyGenderFilter(state.genderFilter);
                }
            });
        });
    }
});
