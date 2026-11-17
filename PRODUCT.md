# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

B2B fashion e-commerce retailers, digital apparel studios, fashion buyers, and merchandising teams generating high-volume catalog lookbooks and virtual fitting demonstrations from flat-lay and ghost-mannequin garment photos. Secondary audience includes fashion stylists and individual shoppers evaluating clothing items on target models.

## Product Purpose

NUTZ REPLACER is a dedicated AI-powered virtual clothing try-on platform that transfers real garments onto target models photorealistically. It eliminates the need for expensive physical studio photoshoots by producing virtual try-on renders that preserve 100% of the target individual's facial identity, skin tone, natural hair, body proportions, and pose, while transferring the exact fabric patterns, embroidery, and textures of the source garment.

## Positioning

Dual-Panel Spatial Reference Conditioning on FLUX-DEV-012 with MediaPipe anatomical protection. Unlike generic text-to-image generators or standard inpainting tools that hallucinate clothing from text prompts and lose micro-details, NUTZ REPLACER conditions directly on the real garment pixels via composite dual-panel canvas inpainting ($1536 \times 1024$), leveraging FLUX's global bidirectional spatial self-attention to transfer complex patterns, prints, and textures while keeping anatomical boundaries strictly locked.

## Operating Context

- Web application featuring dual view modes: Desktop High-Resolution Studio Canvas and dedicated Mobile Artboard ($390 \times 844$ iPhone viewport).
- FastAPI backend gateway on `http://127.0.0.1:8000` with static endpoints serving `/replacer`, `/studio`, and `/outputs`.
- Remote cloud GPU inference powered by FLUX-DEV-012 on Railway (`https://nutz-image1284.up.railway.app/v1/images/edits`) executing dual-panel composite canvas inpainting.
- Local fallback/accelerator: Local CatVTON LoRA engine running on NVIDIA GPU for sub-2s instant warp previews.
- Production fashion styling engine: 17 dedicated category configs (Blazer, Oxford Shirt, Denim Jacket, Sherwani, Kurta, Saree, Lehenga, Hoodie, Dress, etc.) with universal identity and pattern preservation constraints.

## Capabilities and Constraints

- **Capabilities:**
  - High-resolution target person image upload with MediaPipe anatomical segmentation (protecting face, hair, neck, and hands).
  - Garment reference image upload (flat-lay, ghost mannequin, hanger, or catalog).
  - Automated garment category detection across 17 structured apparel categories.
  - Dual-panel canvas assembly ($1536 \times 1024$ Lanczos resampling, zero aspect-ratio distortion).
  - Interactive Before/After split comparison slider with draggable touch handle.
  - High-resolution PNG output export and history tracking.
  - Dedicated mobile artboard ($390 \times 844$) with $\ge 44\text{px}$ touch targets, horizontal snap-scrolling sample tiles, and sticky 56px action bar.
- **Constraints:**
  - Production quality try-on strictly requires FLUX-DEV-012; CatVTON is reserved for optional fast local preview.
  - Remote Railway endpoint accepts a single composite image and mask; multiple inputs are achieved through deterministic dual-panel canvas stitching and post-diffusion precision cropping.
  - Universal Identity Protection Rules: Never modify facial features, skin tone, eyes, facial hair, hairstyle, or body posture.
  - Universal Pattern Preservation Rules: Never simplify, blur, or hallucinate patterns; faithfully transfer check scales, embroidery, graphic prints, and motifs.

## Brand Commitments

- **Brand Name:** NUTZ REPLACER
- **Tagline:** "Your Style. Your Identity. Reimagined."
- **Brand Assets:** Official NUTZ acorn emblem and wordmark registered trademark logo (`nutz_logo_white.png`, `nutz_logo_dark.png`, `nutz_logo.jpg` located in `nutz-replacer/public/` and `frontend/assets/`).
- **Aesthetic Direction:** Sophisticated fashion-tech aesthetic combining Shopify e-commerce clarity, Zara minimalist editorial framing, and Apple interface precision.
- **Color Palette:** Deep purple accent `#5B3DF0`, neutral light background `#F5F4F8`, pure white cards `#FFFFFF`, primary text `#171717`, 20px rounded corners.
- **Typography:** Plus Jakarta Sans with clear typographic hierarchy.
- **Icons:** Modern SVG icons only (Lucide-React); zero emoji in user interface.

## Evidence on Hand

- Technical implementation audit: `reports/flux_integration_audit.md`.
- Garment conditioning architecture and verification: `reports/flux_garment_conditioning_implementation.md`.
- Live generated validation assets in `outputs/`:
  - Person reference: `outputs/intelligent_person_seed322079.png`
  - Garment reference: `outputs/intelligent_garment_seed322079.png`
  - Assembled composite canvas: `outputs/intelligent_canvas_seed322079.png`
  - MediaPipe segmentation mask: `outputs/intelligent_mask_seed322079.png`
  - Master try-on output: `outputs/intelligent_tryon_seed322079.png`
- Official brand assets: `nutz-replacer/public/nutz_logo_white.png`, `nutz-replacer/public/nutz_logo_dark.png`.

## Product Principles

- **Identity Lock:** The person's physical identity (face, skin tone, natural hair, pose, anatomy) is inviolable. The model only replaces clothing on the body.
- **Garment Fidelity First:** The garment's visual truth (patterns, needlework, micro-prints, textures) must transfer directly from the reference image without synthetic drift.
- **Clarity Over Clutter:** Clean, deliberate interface with generous whitespace, subtle shadows, and crisp visual hierarchy.
- **Responsive Parity:** Both desktop studio canvas and mobile artboard provide first-class workflows with touch-friendly controls ($\ge 44\text{px}$) and zero horizontal page scroll.

## Accessibility & Inclusion

- WCAG AA compliant color contrast ratio ($\ge 4.5:1$) across all body text, headings, and interactive elements.
- All tappable and clickable touch areas $\ge 44 \times 44\text{px}$.
- Body typography $\ge 14\text{px}$, metadata and small labels $\ge 13\text{px}$.
- Fully keyboard accessible controls with explicit focus rings and semantic HTML markup.
