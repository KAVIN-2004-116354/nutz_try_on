/**
 * Nutz Try On Embeddable Commercial Widget SDK v2.0
 * Pure 2D Photorealistic Diffusion Fitting Room for E-Commerce Stores (Shopify / WooCommerce / Custom)
 */
(function () {
    const API_BASE = window.location.origin;

    // 1. Inject Stylesheet
    if (!document.getElementById("nutz-widget-css")) {
        const link = document.createElement("link");
        link.id = "nutz-widget-css";
        link.rel = "stylesheet";
        link.href = `${API_BASE}/studio/widget.css`;
        document.head.appendChild(link);
    }

    let activeGarmentUrl = "";
    let activeGarmentName = "";
    let selectedPersonFile = null;
    let selectedPersonSampleUrl = `${API_BASE}/studio/assets/sample_person_modi.png`;
    let isUsingSample = true;

    // 2. Build Modal DOM
    function createModal() {
        if (document.getElementById("nutz-modal-overlay")) return;

        const overlay = document.createElement("div");
        overlay.id = "nutz-modal-overlay";
        overlay.innerHTML = `
            <div class="nutz-modal">
                <div class="nutz-modal-header">
                    <div class="nutz-brand">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#4f46e5" stroke-width="2.2">
                            <path d="M20.38 3.46L16 2 12 5.5 8 2l-4.38 1.46a2 2 0 0 0-1.34 1.84L2 19a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2l-.28-13.7a2 2 0 0 0-1.34-1.84z"/>
                        </svg>
                        Nutz <span>Try On</span>
                        <span class="nutz-chip">2D AI Diffusion</span>
                    </div>

                    <button class="nutz-close-btn" id="nutz-close">&times;</button>
                </div>

                <div class="nutz-modal-body">
                    <div class="nutz-ai-container">
                        <!-- Preview Stage Area -->
                        <div class="nutz-preview-area" id="nutz-preview-area">
                            <!-- Placeholder View -->
                            <div id="nutz-ai-placeholder" class="nutz-placeholder-box">
                                <div class="nutz-placeholder-icons">
                                    <img id="nutz-garment-thumb" src="" alt="Garment Preview">
                                </div>
                                <h3 id="nutz-stage-title">Virtual Fitting Room</h3>
                                <p style="color:#64748b; font-size: 0.88rem; max-width: 320px; text-align:center; margin-top: 4px;">
                                    Select a sample model or upload your photo to preview this garment tailored directly onto you.
                                </p>
                            </div>

                            <!-- Result Image Showcase -->
                            <div id="nutz-result-wrap" style="display:none; width:100%; height:100%; display:none; align-items:center; justify-content:center;">
                                <img id="nutz-ai-result-img" src="" alt="Try-On Result">
                            </div>

                            <!-- Loader Spinner -->
                            <div class="nutz-loader" id="nutz-loader">
                                <div class="nutz-spinner"></div>
                                <span id="nutz-loader-status" style="font-size:0.9rem; color:#4f46e5; font-weight:700;">
                                    Inpainting with CatVTON Diffusion...
                                </span>
                                <span style="font-size:0.75rem; color:#64748b; margin-top:4px;">
                                    SegFormer semantic mask + UNet visual conditioning (~8-12s)
                                </span>
                            </div>
                        </div>

                        <!-- Sidebar Controls -->
                        <div class="nutz-controls-area">
                            <div class="nutz-prod-header">
                                <h4 id="nutz-product-title">Product</h4>
                                <span class="nutz-badge">Upper Body</span>
                            </div>

                            <!-- Quick Sample Model Select -->
                            <div>
                                <label class="nutz-label">1. Choose Model</label>
                                <div class="nutz-sample-row">
                                    <button class="nutz-sample-pill active" id="btn-sample-modi" data-url="${API_BASE}/studio/assets/sample_person_modi.png">
                                        N. Modi
                                    </button>
                                    <button class="nutz-sample-pill" id="btn-sample-model" data-url="${API_BASE}/studio/assets/sample_person_1.jpg">
                                        Studio Model
                                    </button>
                                </div>
                            </div>

                            <!-- Or Custom Upload -->
                            <div>
                                <label class="nutz-label">Or Upload Your Photo</label>
                                <div class="nutz-upload-card" id="nutz-upload-zone">
                                    <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#4f46e5" stroke-width="2">
                                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                                    </svg>
                                    <p style="margin:4px 0 2px 0; font-size:0.82rem; font-weight:700; color:#0f172a;" id="nutz-upload-label">
                                        Upload Portrait
                                    </p>
                                    <span style="font-size:0.7rem; color:#94a3b8;">Front-facing JPG, PNG</span>
                                    <input type="file" id="nutz-person-file" accept="image/*">
                                </div>
                            </div>

                            <!-- Speed / Steps -->
                            <div>
                                <label class="nutz-label">Inference Mode</label>
                                <div class="nutz-speed-select">
                                    <button class="nutz-speed-btn" data-steps="20">⚡ Fast (~8s)</button>
                                    <button class="nutz-speed-btn active" data-steps="25">⚖️ Balanced</button>
                                </div>
                            </div>

                            <!-- Generate Button -->
                            <button class="nutz-btn-generate" id="nutz-generate-btn">
                                ✨ Generate 2D Try-On
                            </button>

                            <!-- Result Action (Download / Add to Cart) -->
                            <div id="nutz-result-actions" style="display:none; flex-direction:column; gap:8px;">
                                <a id="nutz-btn-download" href="#" download="virtual_tryon.png" class="nutz-btn-secondary">
                                    💾 Download Image
                                </a>
                            </div>
                            
                            <div style="margin-top:auto; font-size:0.72rem; color:#94a3b8; text-align:center;">
                                Powered by CatVTON &bull; Zero Server Data Retention
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        // Events
        document.getElementById("nutz-close").addEventListener("click", closeModal);
        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) closeModal();
        });

        // Sample Model toggles
        const sampleModi = document.getElementById("btn-sample-modi");
        const sampleModel = document.getElementById("btn-sample-model");

        sampleModi.addEventListener("click", () => {
            sampleModi.classList.add("active");
            sampleModel.classList.remove("active");
            selectedPersonSampleUrl = sampleModi.dataset.url;
            selectedPersonFile = null;
            isUsingSample = true;
            document.getElementById("nutz-upload-label").innerText = "Upload Portrait";
        });

        sampleModel.addEventListener("click", () => {
            sampleModel.classList.add("active");
            sampleModi.classList.remove("active");
            selectedPersonSampleUrl = sampleModel.dataset.url;
            selectedPersonFile = null;
            isUsingSample = true;
            document.getElementById("nutz-upload-label").innerText = "Upload Portrait";
        });

        // Speed steps
        let currentSteps = 25;
        const speedBtns = overlay.querySelectorAll(".nutz-speed-btn");
        speedBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                speedBtns.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                currentSteps = parseInt(btn.dataset.steps);
            });
        });

        // File Select
        const fileInput = document.getElementById("nutz-person-file");
        fileInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                selectedPersonFile = e.target.files[0];
                isUsingSample = false;
                sampleModi.classList.remove("active");
                sampleModel.classList.remove("active");
                document.getElementById("nutz-upload-label").innerText = `Uploaded: ${selectedPersonFile.name.substring(0, 14)}...`;
            }
        });

        // Generate Action
        document.getElementById("nutz-generate-btn").addEventListener("click", () => generateTryOn(currentSteps));
    }

    function openModal(options = {}) {
        createModal();
        const overlay = document.getElementById("nutz-modal-overlay");
        activeGarmentUrl = options.garmentUrl || "";
        activeGarmentName = options.garmentName || "Featured Garment";

        document.getElementById("nutz-product-title").innerText = activeGarmentName;
        document.getElementById("nutz-garment-thumb").src = activeGarmentUrl;

        // Reset state
        document.getElementById("nutz-result-wrap").style.display = "none";
        document.getElementById("nutz-ai-placeholder").style.display = "flex";
        document.getElementById("nutz-result-actions").style.display = "none";
        document.getElementById("nutz-loader").classList.remove("active");

        overlay.classList.add("open");
    }

    function closeModal() {
        const overlay = document.getElementById("nutz-modal-overlay");
        if (overlay) overlay.classList.remove("open");
    }

    async function generateTryOn(steps = 25) {
        const genBtn = document.getElementById("nutz-generate-btn");
        const loader = document.getElementById("nutz-loader");
        const loaderStatus = document.getElementById("nutz-loader-status");
        const resultImg = document.getElementById("nutz-ai-result-img");
        const resultWrap = document.getElementById("nutz-result-wrap");
        const placeholder = document.getElementById("nutz-ai-placeholder");
        const resultActions = document.getElementById("nutz-result-actions");
        const downloadBtn = document.getElementById("nutz-btn-download");

        genBtn.disabled = true;
        genBtn.innerText = "⏳ Generating...";
        loader.classList.add("active");
        loaderStatus.innerText = "Dispatching CatVTON 2D Try-On...";

        try {
            const formData = new FormData();

            // 1. Fetch Garment Blob
            const garmentRes = await fetch(activeGarmentUrl);
            const garmentBlob = await garmentRes.blob();
            formData.append("garment_image", garmentBlob, "garment.jpg");

            // 2. Fetch Person
            if (selectedPersonFile) {
                formData.append("person_image", selectedPersonFile);
            } else {
                const personRes = await fetch(selectedPersonSampleUrl);
                const personBlob = await personRes.blob();
                formData.append("person_image", personBlob, "person.jpg");
            }

            formData.append("steps", steps.toString());
            formData.append("category", "upper_body");

            loaderStatus.innerText = "Computing SegFormer mask & running diffusion...";

            const response = await fetch(`${API_BASE}/api/v1/try-on`, {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server returned HTTP ${response.status}`);
            }

            const contentType = response.headers.get("content-type") || "";
            let imageSrc = "";

            if (contentType.includes("application/json")) {
                const data = await response.json();
                imageSrc = data.image_data || data.result_url;
            } else {
                const blob = await response.blob();
                imageSrc = URL.createObjectURL(blob);
            }

            resultImg.src = imageSrc;
            downloadBtn.href = imageSrc;

            placeholder.style.display = "none";
            resultWrap.style.display = "flex";
            resultActions.style.display = "flex";

        } catch (err) {
            console.error("Widget error:", err);
            alert(`Virtual Try-On error: ${err.message}\nMake sure the ComfyUI GPU backend is running.`);
        } finally {
            loader.classList.remove("active");
            genBtn.disabled = false;
            genBtn.innerText = "✨ Generate 2D Try-On";
        }
    }

    // 3. Scan DOM for Try-On Trigger Buttons
    function initButtons() {
        document.querySelectorAll("[data-nutz-tryon]").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.preventDefault();
                const garmentUrl = btn.dataset.garmentUrl;
                const garmentName = btn.dataset.garmentName;
                openModal({ garmentUrl, garmentName });
            });
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initButtons);
    } else {
        initButtons();
    }

    window.NutzTryOn = { openModal, closeModal };
})();
