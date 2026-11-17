# E-Commerce Merchant Embeddable Widget Validation Report

**Components**: `frontend/widget.js`, `frontend/widget.css`, `frontend/demo_store.html`  
**Purpose**: Drop-in 2D Virtual Try-On SDK for e-commerce platforms (Shopify, WooCommerce, Custom Storefronts)  
**Validation Date**: October 2026  
**Status**: **PASS**

---

## 1. Embed Contract & Architecture

Merchants integrate the virtual try-on capability with a single non-intrusive script tag:

```html
<script 
  src="http://localhost:8000/studio/widget.js" 
  data-product-id="prod_101" 
  data-product-name="Silk Emerald Casual Shirt" 
  data-product-image="http://localhost:8000/studio/assets/sample_emerald_shirt.jpg"
  data-category="upper_body"
  data-api-base="http://localhost:8000">
</script>
```

### SDK Responsibilities:
1. Automatically renders a branded **"Virtual Try-On"** button near the "Add to Cart" button.
2. Injects an isolated modal container using scoped CSS classes to avoid conflicting with existing merchant styles.
3. Allows the shopper to upload their own photo or select a pre-calibrated mannequin model.
4. Auto-detects product garment image and sends the request directly to `/api/v1/try-on`.
5. Displays the resulting try-on image inside the modal with an interactive Before/After comparison slider and a "Buy This Look" CTA.

---

## 2. Storefront Demonstration (`demo_store.html`)

- Served at: `http://localhost:8000/demo` (redirects to `/studio/demo_store.html`).
- Emulates a modern luxury fashion retail store ("MAISON D'ÉLITE").
- Showcases the real user journey:
  1. Customer browses the emerald shirt product page.
  2. Clicks the luxury gold "Try On Virtually" CTA.
  3. Uploads or selects customer photo.
  4. Observes real-time progress bar.
  5. Interacts with the Before/After comparison slider inside the modal.
  6. Closes modal or clicks "Add to Bag".

---

## 3. Cross-Origin (CORS) Verification

FastAPI gateway has full CORS enabled (`allow_origins=["*"]`, `allow_methods=["*"]`, `allow_headers=["*"]`), ensuring merchant domains can seamlessly invoke `POST /api/v1/try-on` without origin blocking.

