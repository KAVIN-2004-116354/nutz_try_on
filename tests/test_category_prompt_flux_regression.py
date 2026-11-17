"""Regression Test Suite: Garment Prompt-to-FLUX Pipeline Verification.

Verifies:
1. Negative matching tests (anti-substring collision: dressing, addressing, dressmaker, shortly).
2. All 17 categories normalized accurately from keys, display names, and aliases.
3. Prompt assembly retains Universal Strict Rules, Category Directives, and Final Global Priority Instructions.
4. Primary dual-panel canvas inpainting transmits composite reference canvas and category prompt to mocked HTTP request.
5. Primary fallback (direct inpainting) and secondary fallback (synthesis) retain category directives.
"""

import io
import re
import pytest
from unittest.mock import patch, MagicMock
from PIL import Image

from src.inference.category_prompts import (
    CATEGORY_CONFIGS,
    normalize_category,
    get_category_config,
    build_flux_category_prompt,
    UNIVERSAL_IDENTITY_RULES,
    UNIVERSAL_REFERENCE_RULES,
    FINAL_GLOBAL_INSTRUCTIONS,
)
from src.inference.cloud_generator import (
    build_spatial_canvas_prompt,
    run_flux_tryon,
    create_tryon_canvas,
)


def _create_mock_response():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    import base64
    img = Image.new("RGB", (1536, 1024), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    mock_resp.json.return_value = {"data": [{"b64_json": base64.b64encode(buf.getvalue()).decode()}]}
    return mock_resp


# ==============================================================================
# 1. NEGATIVE SUBSTRING COLLISION TESTS
# ==============================================================================

def test_negative_substring_matching():
    """Proves words containing 'dress', 'short', 'jean' do NOT trigger false positives."""
    negative_cases = [
        ("dressing the model in casual clothes", "t_shirt"),
        ("addressing the audience in studio lighting", "t_shirt"),
        ("dressmaker measuring cloth", "t_shirt"),
        ("shortly after arrival", "t_shirt"),
        ("jeanette modeling luxury apparel", "t_shirt"),
        ("he addressing the crowd", "t_shirt"),
    ]
    for text, expected in negative_cases:
        res = normalize_category(text)
        assert res != "western_dress", f"False positive western_dress on '{text}'"
        assert res != "shorts", f"False positive shorts on '{text}'"
        assert res != "jeans", f"False positive jeans on '{text}'"
        assert res == expected, f"Expected fallback {expected}, got {res} on '{text}'"


# ==============================================================================
# 2. ALL 17 CATEGORIES NORMALIZATION TESTS
# ==============================================================================

def test_all_17_categories_exact_and_alias_normalization():
    """Verifies that all 17 categories normalize from canonical keys and display names."""
    assert len(CATEGORY_CONFIGS) == 17, "Must define exactly 17 categories"

    for cat_key, cfg in CATEGORY_CONFIGS.items():
        # Canonical key
        assert normalize_category(cat_key) == cat_key, f"Failed on canonical key '{cat_key}'"
        # Display name
        assert normalize_category(cfg["name"]) == cat_key, f"Failed on display name '{cfg['name']}'"
        # First alias if available
        if cfg.get("aliases"):
            first_alias = cfg["aliases"][0]
            assert normalize_category(first_alias) == cat_key, f"Failed on alias '{first_alias}'"


# ==============================================================================
# 3. PROMPT CONSTRUCTION HIERARCHY TESTS
# ==============================================================================

def test_all_17_categories_prompt_construction():
    """Verifies that each category's prompt retains Universal Rules, Category Directives, and Priority Order."""
    for cat_key, cfg in CATEGORY_CONFIGS.items():
        cat_id = cfg["id"]
        cat_name = cfg["name"]

        prompt = build_flux_category_prompt(cat_key, user_prompt="custom user styling note")

        # 1. Header
        assert f"FLUX VIRTUAL TRY-ON — {cat_name.upper()} SYNTHESIS" in prompt
        # 2. Universal Identity Rules
        assert "IDENTITY & BODY PRESERVATION (MANDATORY):" in prompt
        assert "Image 1 is the authoritative source for the target person's identity." in prompt
        # 3. Universal Reference Rules
        assert "GARMENT DESIGN FIDELITY (MANDATORY):" in prompt
        assert "Image 2 is the authoritative source for garment appearance." in prompt
        # 4. Exact Category Directive
        assert f"CATEGORY {cat_id}:" in prompt
        # 5. User Styling Directive
        assert "SPECIFIC STYLING INSTRUCTION:" in prompt
        assert "custom user styling note" in prompt
        # 6. Universal Realism Rules
        assert "REALISM & FABRIC DRAPING:" in prompt
        # 7. Final Global Priority Instructions
        assert "FINAL GLOBAL INSTRUCTION:" in prompt
        assert "PRIORITY ORDER:" in prompt


# ==============================================================================
# 4. PRIMARY DUAL-PANEL CANVAS & MOCKED HTTP REQUEST TESTS (ALL 17 CATEGORIES)
# ==============================================================================

@pytest.mark.parametrize("cat_key", list(CATEGORY_CONFIGS.keys()))
def test_mocked_flux_request_all_17_categories(cat_key):
    """Verifies that every category generates correct prompt, composite canvas, and mask at the HTTP layer."""
    cfg = CATEGORY_CONFIGS[cat_key]
    cat_id = cfg["id"]
    cat_name = cfg["name"].upper()

    person_img = Image.new("RGB", (768, 1024), color=(220, 220, 220))
    garment_img = Image.new("RGB", (768, 1024), color=(100, 150, 255))
    mask_img = Image.new("L", (768, 1024), color=255)

    captured_requests = []

    def mock_post(url, headers=None, files=None, data=None, timeout=None):
        captured_requests.append({
            "url": url,
            "data": data,
            "files": files,
        })
        return _create_mock_response()

    with patch("requests.post", side_effect=mock_post):
        res = run_flux_tryon(
            person_img=person_img,
            garment_img=garment_img,
            garment_desc=cat_key,
            category=cat_key,
            mask_img=mask_img,
            use_canvas_conditioning=True,
        )

    assert res["status"] == "success"
    assert len(captured_requests) == 1
    req = captured_requests[0]

    # Verify endpoint URL
    assert "/v1/images/edits" in req["url"]

    # Verify files payload (Composite dual-panel canvas + inpainting mask)
    files = req["files"]
    assert "image" in files, "Must supply composite canvas in 'image'"
    assert "mask" in files, "Must supply composite inpainting mask in 'mask'"

    # Verify composite canvas dimensions (multiples of 32)
    canvas_bytes = files["image"][1]
    canvas_img = Image.open(io.BytesIO(canvas_bytes))
    assert canvas_img.size == (1536, 1024), f"Expected (1536, 1024), got {canvas_img.size}"

    # Verify Prompt contents
    http_prompt = req["data"]["prompt"]
    assert f"FLUX VIRTUAL TRY-ON — {cat_name} DUAL-PANEL SPATIAL REFERENCE TRANSFORMATION" in http_prompt
    assert f"CATEGORY {cat_id}:" in http_prompt
    assert "GARMENT DESIGN FIDELITY (MANDATORY):" in http_prompt
    assert "IDENTITY & ANATOMY PRESERVATION (STRICT):" in http_prompt
    assert "FINAL GLOBAL INSTRUCTION:" in http_prompt
    assert "PRIORITY ORDER:" in http_prompt

    # Ensure anti-override: does not contain false western_dress unless requested
    if cat_key != "western_dress":
        assert "CATEGORY 16: WESTERN DRESS" not in http_prompt


# ==============================================================================
# 5. FALLBACK PATH PRESERVATION TESTS
# ==============================================================================

def test_fallback_path1_preserves_prompt_on_canvas_error():
    """Verifies that if dual-panel canvas editing fails, direct person edit retains category prompt."""
    person_img = Image.new("RGB", (768, 1024), color=(220, 220, 220))
    garment_img = Image.new("RGB", (768, 1024), color=(100, 150, 255))

    call_count = 0
    captured_prompts = []

    def mock_post(url, headers=None, files=None, data=None, timeout=None):
        nonlocal call_count
        call_count += 1
        captured_prompts.append(data.get("prompt", ""))
        if call_count == 1:
            # Simulate canvas edit failure
            mock_err = MagicMock()
            mock_err.status_code = 500
            mock_err.text = "Canvas processing timeout"
            return mock_err
        # Fallback call succeeds
        return _create_mock_response()

    with patch("requests.post", side_effect=mock_post):
        res = run_flux_tryon(
            person_img=person_img,
            garment_img=garment_img,
            category="kurta",
            use_canvas_conditioning=True,
        )

    assert call_count == 2
    # Verify fallback prompt retained Kurta category directives
    fallback_prompt = captured_prompts[1]
    assert "CATEGORY 5: KURTA" in fallback_prompt
    assert "FINAL GLOBAL INSTRUCTION:" in fallback_prompt


def test_fallback_path2_preserves_prompt_on_synthesis_fallback():
    """Verifies that if edit endpoint fails, text synthesis fallback retains full category prompt."""
    person_img = Image.new("RGB", (768, 1024), color=(220, 220, 220))

    captured_urls = []
    captured_prompts = []

    def mock_post(url, headers=None, files=None, data=None, json=None, timeout=None):
        captured_urls.append(url)
        if json and "prompt" in json:
            captured_prompts.append(json["prompt"])
        elif data and "prompt" in data:
            captured_prompts.append(data["prompt"])

        if "/v1/images/edits" in url:
            # Simulate edit endpoint failure
            mock_err = MagicMock()
            mock_err.status_code = 500
            mock_err.text = "Edits endpoint unavailable"
            return mock_err
        # Synthesis endpoint succeeds
        return _create_mock_response()

    with patch("requests.post", side_effect=mock_post):
        res = run_flux_tryon(
            person_img=person_img,
            garment_img=None, # Single image mode
            category="sherwani",
            use_canvas_conditioning=False,
        )

    assert any("/v1/images/generations" in u for u in captured_urls)
    # The generation prompt must NOT be a generic 2-line string; must retain Sherwani directives
    synthesis_prompt = captured_prompts[-1]
    assert "CATEGORY 9: SHERWANI" in synthesis_prompt
    assert "FINAL GLOBAL INSTRUCTION:" in synthesis_prompt


# ==============================================================================
# 6. GATEWAY ENDPOINT INTEGRATION TESTS (FASTAPI CLIENT)
# ==============================================================================

def test_gateway_flux_tryon_endpoint_preserves_category():
    """Verifies that /api/v1/flux-tryon correctly binds the selected category into FLUX."""
    from fastapi.testclient import TestClient
    from src.gateway.app import app

    client = TestClient(app)

    p_img = Image.new("RGB", (768, 1024), color="gray")
    g_img = Image.new("RGB", (768, 1024), color="blue")
    p_buf = io.BytesIO()
    g_buf = io.BytesIO()
    p_img.save(p_buf, format="PNG")
    g_img.save(g_buf, format="PNG")
    p_buf.seek(0)
    g_buf.seek(0)

    captured_prompt = []

    def mock_post(url, headers=None, files=None, data=None, timeout=None):
        if data and "prompt" in data:
            captured_prompt.append(data["prompt"])
        return _create_mock_response()

    with patch("requests.post", side_effect=mock_post):
        response = client.post(
            "/api/v1/flux-tryon",
            files={
                "person_image": ("person.png", p_buf, "image/png"),
                "garment_image": ("garment.png", g_buf, "image/png"),
            },
            data={
                "category": "kurta",
            }
        )

    assert response.status_code == 200
    assert len(captured_prompt) == 1
    prompt = captured_prompt[0]
    assert "CATEGORY 5: KURTA" in prompt
    assert "CATEGORY 16: WESTERN DRESS" not in prompt


def test_gateway_intelligent_tryon_endpoint_enables_canvas_with_garment():
    """Verifies that /api/v1/intelligent-tryon enables dual-panel canvas when garment image is provided."""
    from fastapi.testclient import TestClient
    from src.gateway.app import app

    client = TestClient(app)

    p_img = Image.new("RGB", (768, 1024), color="gray")
    g_img = Image.new("RGB", (768, 1024), color="red")
    p_buf = io.BytesIO()
    g_buf = io.BytesIO()
    p_img.save(p_buf, format="PNG")
    g_img.save(g_buf, format="PNG")
    p_buf.seek(0)
    g_buf.seek(0)

    captured_files = []
    captured_prompts = []

    def mock_post(url, headers=None, files=None, data=None, timeout=None):
        if files:
            captured_files.append(list(files.keys()))
        if data and "prompt" in data:
            captured_prompts.append(data["prompt"])
        return _create_mock_response()

    with patch("requests.post", side_effect=mock_post):
        response = client.post(
            "/api/v1/intelligent-tryon",
            files={
                "person_image": ("person.png", p_buf, "image/png"),
                "garment_image": ("garment.png", g_buf, "image/png"),
            },
            data={
                "category": "blazer",
                "mode": "auto",
            }
        )

    assert response.status_code == 200
    assert len(captured_files) == 1
    assert "image" in captured_files[0]
    assert "mask" in captured_files[0]
    assert "CATEGORY 6: BLAZER" in captured_prompts[0]

