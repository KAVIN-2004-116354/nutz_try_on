"""FLUX Category-Specific Prompt Engine for Nutz Replacer.

Implements the official 17-category virtual try-on prompt architecture:
- Universal Strict Rules (Identity, Body Proportions, Reference Fidelity, Realism)
- 17 Category-Specific Directive Modules
- Final Global Priority Order and Integrity Enforcement
"""

from typing import Dict, Any, Optional, Tuple

UNIVERSAL_IDENTITY_RULES = (
    "IDENTITY & BODY PRESERVATION (MANDATORY):\n"
    "- Image 1 is the authoritative source for the target person's identity.\n"
    "- Preserve the target person's original face, facial features, eyes, nose, lips and facial structure.\n"
    "- Preserve original hairstyle, hairline, beard, moustache, and natural skin tone.\n"
    "- Never beautify, slim, enlarge, or reshape the target person's body.\n"
    "- Preserve original shoulder width, chest, waist, arms, legs, and anatomical proportions.\n"
    "- Preserve the original body posture, head angle, hand positions, and orientation."
)

UNIVERSAL_REFERENCE_RULES = (
    "GARMENT DESIGN FIDELITY (MANDATORY):\n"
    "- Image 2 is the authoritative source for garment appearance.\n"
    "- Preserve the exact original garment colors, color balance, and saturation.\n"
    "- Preserve all original printed patterns, graphics, floral, geometric, and abstract artwork.\n"
    "- Preserve stripes, checks, polka dots, typography, and their exact spatial arrangements.\n"
    "- Preserve all embroidery, zardozi, zari, lace, ornamental borders, and decorative motifs.\n"
    "- Preserve logos, brand symbols, badges, text, buttons, zippers, collars, and stitching.\n"
    "- Never invent, remove, simplify, recolor, or redesign patterns.\n"
    "- Never convert patterned fabric into plain fabric, or replace with a generic design.\n"
    "- Reference fidelity is more important than creative redesign."
)

UNIVERSAL_REALISM_RULES = (
    "REALISM & FABRIC DRAPING:\n"
    "- Adapt garment geometry realistically to the target person's existing pose and body shape.\n"
    "- Render photorealistic fabric drape, micro-creases, natural tension folds, and contact shadows.\n"
    "- Do not create floating clothing, clipping artifacts, or disconnected body parts.\n"
    "- Only replace intended clothing regions; strictly preserve all protected body parts and background."
)

FINAL_GLOBAL_INSTRUCTIONS = (
    "FINAL GLOBAL INSTRUCTION:\n"
    "The target person must remain the same person as in Image 1.\n"
    "The garment must remain the same garment as in Image 2.\n"
    "PRIORITY ORDER:\n"
    "1. Preserve target identity.\n"
    "2. Preserve original body proportions.\n"
    "3. Preserve exact garment pattern and design.\n"
    "4. Preserve original garment colors and fabric.\n"
    "5. Preserve original pose and anatomy.\n"
    "6. Generate realistic garment fitting and natural folds.\n"
    "7. Preserve all unrelated image regions.\n"
    "NEVER prioritize aesthetic enhancement over reference accuracy.\n"
    "NEVER invent garment details.\n"
    "NEVER alter the original garment pattern.\n"
    "NEVER reshape the target person's body."
)

CATEGORY_CONFIGS: Dict[str, Dict[str, Any]] = {
    "t_shirt": {
        "id": 1,
        "name": "T-Shirt",
        "macro_category": "upper_body",
        "aliases": ["t-shirt", "tshirt", "t_shirt", "tee", "crewneck tee", "graphic tee"],
        "sleeves": "short_sleeves",
        "collar": "round_crew_neck",
        "directive": (
            "CATEGORY 1: T-SHIRT\n"
            "Replace only the target person's upper-body clothing with the exact T-shirt shown in Image 2.\n"
            "Preserve: Original neckline and collar; sleeve length and sleeve construction; original fabric and texture; "
            "exact printed graphics, logos and patterns; original colors and design placement; stitching and garment details.\n"
            "Maintain realistic T-shirt fitting according to the target person's existing body proportions.\n"
            "Do not change the person's face, hairstyle, skin tone, body shape, hands or pose. Do not modify lower-body clothing or background."
        ),
    },
    "inner_vest": {
        "id": 2,
        "name": "Inner Vest / Baniyan",
        "macro_category": "upper_body",
        "aliases": ["vest", "inner vest", "baniyan", "undershirt", "tank top", "singlet", "sleeveless undershirt"],
        "sleeves": "sleeveless",
        "collar": "scoop_neck",
        "directive": (
            "CATEGORY 2: INNER VEST / BANIYAN\n"
            "Replace only the target person's upper-body clothing with the exact inner vest shown in Image 2.\n"
            "Preserve: Sleeveless construction; original neckline; armhole shape; fabric ribbed texture; original colors and patterns; stitching and garment details.\n"
            "Maintain the natural appearance of an inner vest.\n"
            "Do not generate sleeves, jackets, collars or additional clothing layers unless present in the reference.\n"
            "Preserve the target person's identity, body proportions, face and skin tone."
        ),
    },
    "shirt": {
        "id": 3,
        "name": "Shirt",
        "macro_category": "upper_body",
        "aliases": ["shirt", "formal shirt", "dress shirt", "button-down", "button-up", "oxford shirt", "linen shirt", "casual shirt"],
        "sleeves": "long_sleeves",
        "collar": "button_down_collar",
        "directive": (
            "CATEGORY 3: SHIRT\n"
            "Replace only the upper-body clothing with the exact shirt shown in Image 2.\n"
            "Preserve: Collar design; button arrangement; sleeve length; pocket placement; original stripes, checks, prints and embroidery; "
            "exact fabric color and texture; original stitching and design.\n"
            "Maintain realistic shirt fitting, natural folds and correct fabric alignment.\n"
            "Never change the original shirt pattern or button arrangement.\n"
            "Preserve the target person's identity and body proportions."
        ),
    },
    "polo_t_shirt": {
        "id": 4,
        "name": "Polo T-Shirt",
        "macro_category": "upper_body",
        "aliases": ["polo", "polo t-shirt", "polo shirt", "collared tee", "golf shirt"],
        "sleeves": "short_sleeves",
        "collar": "polo_ribbed_collar",
        "directive": (
            "CATEGORY 4: POLO T-SHIRT\n"
            "Replace only the upper-body clothing with the exact polo T-shirt shown in Image 2.\n"
            "Preserve: Polo collar; button placket; sleeve construction and ribbed cuffs; original logo placement; printed patterns and embroidery; exact colors and fabric texture.\n"
            "Maintain realistic polo-shirt fitting.\n"
            "Do not convert the polo into a regular round-neck T-shirt.\n"
            "Preserve the target person's face, skin tone, identity and body proportions."
        ),
    },
    "kurta": {
        "id": 5,
        "name": "Kurta",
        "macro_category": "upper_body",
        "aliases": ["kurta", "kurti", "ethnic kurta", "panjabi", "short kurta", "long kurta"],
        "sleeves": "long_sleeves",
        "collar": "mandarin_bandhgala_collar",
        "directive": (
            "CATEGORY 5: KURTA\n"
            "Replace only the upper-body clothing with the exact kurta shown in Image 2.\n"
            "Preserve: Traditional kurta silhouette; original neckline; front placket and buttons; sleeve length; embroidery and decorative motifs; original fabric and colors; all printed patterns and borders.\n"
            "Preserve the exact embroidery placement and decorative arrangements.\n"
            "Maintain realistic traditional garment fitting extending down past hip line.\n"
            "Do not simplify or redesign the kurta.\n"
            "Preserve the target person's identity and body proportions."
        ),
    },
    "blazer": {
        "id": 6,
        "name": "Blazer / Suit Jacket",
        "macro_category": "upper_body",
        "aliases": ["blazer", "suit jacket", "coat", "formal blazer", "tuxedo jacket", "sports coat"],
        "sleeves": "long_sleeves",
        "collar": "notch_lapel",
        "directive": (
            "CATEGORY 6: BLAZER / SUIT JACKET\n"
            "Replace only the upper-body outer clothing with the exact blazer shown in Image 2.\n"
            "Preserve: Lapel shape; collar construction; button placement; pocket design; original fabric texture; exact color and patterns; stitching and tailoring details.\n"
            "Maintain realistic shoulder alignment and natural blazer fitting.\n"
            "Preserve the existing inner shirt unless the reference explicitly includes a different visible inner layer.\n"
            "Do not modify the target person's face, identity, skin tone or body proportions."
        ),
    },
    "waistcoat": {
        "id": 7,
        "name": "Waistcoat / Nehru Jacket",
        "macro_category": "upper_body",
        "aliases": ["waistcoat", "nehru jacket", "modi jacket", "bandi", "sleeveless jacket", "gilet", "vest coat"],
        "sleeves": "sleeveless",
        "collar": "nehru_mandarin_collar",
        "directive": (
            "CATEGORY 7: WAISTCOAT / NEHRU JACKET\n"
            "Replace the intended upper-body outer garment with the exact waistcoat or Nehru jacket shown in Image 2.\n"
            "Preserve: Sleeveless construction; original collar; button arrangement; front pockets; embroidery and ornamental designs; exact fabric and colors; original pattern placement.\n"
            "Maintain realistic layering over the existing inner garment.\n"
            "Do not generate additional sleeves or change the original design.\n"
            "Preserve identity, body proportions and pose."
        ),
    },
    "hoodie": {
        "id": 8,
        "name": "Hoodie / Sweatshirt",
        "macro_category": "upper_body",
        "aliases": ["hoodie", "sweatshirt", "hooded sweatshirt", "pullover", "fleece hoodie", "zip hoodie"],
        "sleeves": "long_sleeves",
        "collar": "hooded",
        "directive": (
            "CATEGORY 8: HOODIE / SWEATSHIRT\n"
            "Replace only the upper-body clothing with the exact hoodie or sweatshirt shown in Image 2.\n"
            "Preserve: Hood shape; neckline; sleeve construction; cuffs; kangaroo pockets; drawstrings; original graphics and logos; exact patterns, colors and fabric texture.\n"
            "Maintain realistic fabric thickness and natural folds.\n"
            "Do not invent additional graphics or redesign the hoodie.\n"
            "Preserve the target person's identity, face and body proportions."
        ),
    },
    "sherwani": {
        "id": 9,
        "name": "Sherwani",
        "macro_category": "upper_body",
        "aliases": ["sherwani", "groom sherwani", "royal sherwani", "indo-western sherwani"],
        "sleeves": "long_sleeves",
        "collar": "mandarin_embroidered_collar",
        "directive": (
            "CATEGORY 9: SHERWANI\n"
            "Replace the intended upper-body clothing with the exact sherwani shown in Image 2.\n"
            "Preserve: Traditional sherwani silhouette; original collar; front button arrangement; exact embroidery; ornamental motifs; decorative borders; original fabric texture; exact colors and design placement; original garment length extending towards knees.\n"
            "Preserve every visible decorative detail. Do not simplify, regenerate or replace the embroidery with a different pattern.\n"
            "Maintain realistic traditional fitting according to the target person's existing body proportions.\n"
            "Preserve face, hairstyle, skin tone and identity."
        ),
    },
    "achkan": {
        "id": 10,
        "name": "Achkan",
        "macro_category": "upper_body",
        "aliases": ["achkan", "traditional achkan", "angrakha", "long coat achkan"],
        "sleeves": "long_sleeves",
        "collar": "mandarin_closed_collar",
        "directive": (
            "CATEGORY 10: ACHKAN\n"
            "Replace the intended upper-body clothing with the exact achkan shown in Image 2.\n"
            "Preserve: Traditional long silhouette; structured collar; front button arrangement; original fabric; embroidery and decorative patterns; original color combinations; exact garment length and proportions.\n"
            "Maintain realistic traditional tailoring and natural fabric folds.\n"
            "Do not change the original achkan design.\n"
            "Preserve the target person's identity, face and body proportions."
        ),
    },
    "saree": {
        "id": 11,
        "name": "Saree",
        "macro_category": "complex_ethnic",
        "aliases": ["saree", "sari", "banarasi saree", "kanjivaram saree", "silk saree", "chiffon saree"],
        "sleeves": "short_sleeves",
        "collar": "blouse_neckline",
        "directive": (
            "CATEGORY 11: SAREE\n"
            "Dress the target person in the exact saree shown in Image 2.\n"
            "Preserve: Original saree fabric; exact colors; border design; embroidery; printed motifs; decorative patterns; pallu design; original blouse design, if included in the reference; original border width and decorative arrangement.\n"
            "Reproduce traditional saree draping with realistic pleats and natural fabric folds.\n"
            "The pallu must retain its original pattern and decorative details.\n"
            "Do not replace the saree with a gown, skirt or generic dress. Never invent new embroidery or change the original saree pattern.\n"
            "Preserve the target person's face, hairstyle, skin tone, identity and body proportions."
        ),
    },
    "lehenga": {
        "id": 12,
        "name": "Lehenga",
        "macro_category": "complex_ethnic",
        "aliases": ["lehenga", "lehenga choli", "ghagra", "chaniya choli", "bridal lehenga"],
        "sleeves": "elbow_sleeves",
        "collar": "choli_neckline",
        "directive": (
            "CATEGORY 12: LEHENGA\n"
            "Dress the target person in the exact lehenga outfit shown in Image 2.\n"
            "Preserve: Original skirt silhouette; skirt flare and length; blouse design; dupatta design; embroidery; decorative motifs; original colors; fabric texture; borders and ornamental details.\n"
            "Maintain realistic traditional lehenga construction.\n"
            "Preserve the exact embroidery arrangement and pattern placement.\n"
            "Do not simplify or redesign the outfit.\n"
            "Preserve the target person's face, identity, skin tone and body proportions."
        ),
    },
    "jeans": {
        "id": 13,
        "name": "Jeans",
        "macro_category": "lower_body",
        "aliases": ["jeans", "denim jeans", "denim pants", "ripped jeans", "skinny jeans", "straight jeans"],
        "sleeves": "not_applicable",
        "collar": "not_applicable",
        "directive": (
            "CATEGORY 13: JEANS\n"
            "Replace only the lower-body clothing with the exact jeans shown in Image 2.\n"
            "Preserve: Denim color; original wash and fading; waistband; pocket arrangement; stitching; original cut and fit; ripped details, if present; decorative patterns and logos.\n"
            "Maintain realistic denim texture and natural folds.\n"
            "Do not change the upper-body clothing.\n"
            "Preserve the target person's original body proportions, identity and pose."
        ),
    },
    "formal_trousers": {
        "id": 14,
        "name": "Formal Trousers",
        "macro_category": "lower_body",
        "aliases": ["trousers", "formal trousers", "slacks", "chinos", "suit pants", "dress pants"],
        "sleeves": "not_applicable",
        "collar": "not_applicable",
        "directive": (
            "CATEGORY 14: FORMAL TROUSERS\n"
            "Replace only the lower-body clothing with the exact formal trousers shown in Image 2.\n"
            "Preserve: Original color; waistband; pleats; pocket arrangement; fabric texture; stitching; original cut and silhouette; decorative details and patterns.\n"
            "Maintain realistic formal trouser fitting.\n"
            "Do not change upper-body clothing or body proportions.\n"
            "Preserve the target person's original identity and pose."
        ),
    },
    "shorts": {
        "id": 15,
        "name": "Shorts",
        "macro_category": "lower_body",
        "aliases": ["shorts", "bermuda shorts", "cargo shorts", "denim shorts", "running shorts"],
        "sleeves": "not_applicable",
        "collar": "not_applicable",
        "directive": (
            "CATEGORY 15: SHORTS\n"
            "Replace only the lower-body clothing with the exact shorts shown in Image 2.\n"
            "Preserve: Original length; waistband; pocket placement; fabric texture; original colors; printed patterns; logos and stitching; original design.\n"
            "Maintain realistic fitting according to the target person's existing body proportions.\n"
            "Do not modify upper-body clothing, face or identity."
        ),
    },
    "western_dress": {
        "id": 16,
        "name": "Western Dress / Gown",
        "macro_category": "full_body",
        "aliases": ["dress", "gown", "western dress", "evening dress", "evening gown", "maxi dress", "cocktail dress", "anarkali suit", "anarkali"],
        "sleeves": "long_sleeves",
        "collar": "dress_neckline",
        "directive": (
            "CATEGORY 16: WESTERN DRESS / GOWN\n"
            "Dress the target person in the exact dress or gown shown in Image 2.\n"
            "Preserve: Original neckline; sleeve design; waistline; dress silhouette; skirt length; fabric texture; original colors; printed patterns; embroidery and decorative elements; original design and construction.\n"
            "Maintain realistic dress fitting and natural fabric folds.\n"
            "Do not redesign the dress or change its original pattern.\n"
            "Preserve the target person's identity, face, hairstyle, skin tone and body proportions."
        ),
    },
    "dhoti": {
        "id": 17,
        "name": "Dhoti",
        "macro_category": "lower_body",
        "aliases": ["dhoti", "veshti", "mundu", "panche", "dhotar"],
        "sleeves": "not_applicable",
        "collar": "not_applicable",
        "directive": (
            "CATEGORY 17: DHOTI\n"
            "Replace only the lower-body clothing with the exact dhoti shown in Image 2.\n"
            "Preserve: Traditional dhoti construction; original draping style; pleats and folds; border design; fabric texture; original colors; decorative patterns; exact length and arrangement.\n"
            "Maintain realistic traditional dhoti draping.\n"
            "Do not convert the dhoti into trousers, jeans or a generic skirt.\n"
            "Preserve the target person's upper-body clothing, face, identity, body proportions and pose."
        ),
    },
}


def normalize_category(category_or_name: str) -> str:
    """Normalizes any freeform garment name or category string into one of the 17 canonical IDs."""
    if not category_or_name:
        return "t_shirt"
    cleaned = category_or_name.lower().replace("-", " ").replace("_", " ").strip()

    # Exact key match
    if category_or_name in CATEGORY_CONFIGS:
        return category_or_name

    # Alias matching
    for cat_id, cfg in CATEGORY_CONFIGS.items():
        for alias in cfg["aliases"]:
            if alias in cleaned:
                return cat_id

    # Fallback heuristics
    if any(w in cleaned for w in ["anarkali", "gown", "dress", "maxi", "frock"]):
        return "western_dress"
    if any(w in cleaned for w in ["saree", "sari"]):
        return "saree"
    if any(w in cleaned for w in ["lehenga", "ghagra", "chaniya"]):
        return "lehenga"
    if any(w in cleaned for w in ["kurta", "kurti"]):
        return "kurta"
    if any(w in cleaned for w in ["sherwani"]):
        return "sherwani"
    if any(w in cleaned for w in ["achkan", "angrakha"]):
        return "achkan"
    if any(w in cleaned for w in ["blazer", "suit", "jacket", "coat", "tuxedo"]):
        return "blazer"
    if any(w in cleaned for w in ["vest", "baniyan", "tank"]):
        return "inner_vest"
    if any(w in cleaned for w in ["polo"]):
        return "polo_t_shirt"
    if any(w in cleaned for w in ["shirt", "oxford"]):
        return "shirt"
    if any(w in cleaned for w in ["hoodie", "sweatshirt"]):
        return "hoodie"
    if any(w in cleaned for w in ["waistcoat", "nehru"]):
        return "waistcoat"
    if any(w in cleaned for w in ["jean", "denim"]):
        return "jeans"
    if any(w in cleaned for w in ["trouser", "pant", "chino", "slack"]):
        return "formal_trousers"
    if any(w in cleaned for w in ["short"]):
        return "shorts"
    if any(w in cleaned for w in ["dhoti", "veshti", "mundu"]):
        return "dhoti"

    return "t_shirt"


def get_category_config(category_or_name: str) -> Dict[str, Any]:
    """Returns the category configuration for the given input."""
    canonical = normalize_category(category_or_name)
    return CATEGORY_CONFIGS.get(canonical, CATEGORY_CONFIGS["t_shirt"])


def build_flux_category_prompt(
    category_or_name: str,
    garment_attributes: Optional[Dict[str, Any]] = None,
    user_prompt: Optional[str] = None,
) -> str:
    """
    Constructs the authoritative, category-specific FLUX Virtual Try-On prompt.
    Synthesizes:
    1. Universal Strict Rules (Identity, Anatomy, Reference Fidelity)
    2. Category-Specific Transformation Directives
    3. Visual attributes extracted from Image 2
    4. Final Global Priority & Integrity Instructions
    """
    cat_key = normalize_category(category_or_name)
    cat_cfg = CATEGORY_CONFIGS[cat_key]

    attr_desc = ""
    if garment_attributes:
        color = garment_attributes.get("primary_color") or ""
        sec_color = garment_attributes.get("secondary_color") or ""
        fabric = garment_attributes.get("fabric") or ""
        pattern = garment_attributes.get("pattern") or ""
        details = garment_attributes.get("construction_details") or []

        parts = []
        if color:
            parts.append(f"color: {color}" + (f" with {sec_color}" if sec_color and sec_color != "neutral" else ""))
        if fabric:
            parts.append(f"fabric: {fabric}")
        if pattern and pattern != "solid":
            parts.append(f"pattern/embroidery: {pattern}")
        if details:
            parts.append(f"details: {', '.join(details[:3])}")

        if parts:
            attr_desc = f"\nREFERENCE GARMENT VISUAL ATTRIBUTES (IMAGE 2):\n" + "; ".join(parts) + ".\n"

    user_directive = ""
    if user_prompt and user_prompt.strip():
        user_directive = f"\nSPECIFIC STYLING INSTRUCTION:\n{user_prompt.strip()}\n"

    # Assemble complete prompt structured for FLUX-DEV-012 inpainting
    prompt = (
        f"FLUX VIRTUAL TRY-ON — {cat_cfg['name'].upper()} SYNTHESIS\n\n"
        f"{UNIVERSAL_IDENTITY_RULES}\n\n"
        f"{UNIVERSAL_REFERENCE_RULES}\n\n"
        f"{cat_cfg['directive']}\n"
        f"{attr_desc}"
        f"{user_directive}\n"
        f"{UNIVERSAL_REALISM_RULES}\n\n"
        f"{FINAL_GLOBAL_INSTRUCTIONS}\n\n"
        f"8k resolution, photorealistic masterpiece, pristine studio illumination, flawless edge blending."
    )

    return prompt
