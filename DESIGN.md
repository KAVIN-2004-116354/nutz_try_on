---
name: Nutz Replacer Design System
description: Dedicated AI Virtual Clothing Try-On Platform
colors:
  primary: "#5B3DF0"
  primary-hover: "#4B2EE0"
  primary-light: "#F0EDFD"
  primary-secondary: "#8F77F8"
  neutral-bg: "#F5F4F8"
  surface: "#FFFFFF"
  text-primary: "#171717"
  text-muted: "#64748B"
  text-secondary: "#737373"
  border: "#E8E8EF"
  success: "#16A34A"
  error: "#DC2626"
typography:
  display:
    fontFamily: '"Plus Jakarta Sans", Inter, -apple-system, sans-serif'
    fontSize: "3.5rem"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  headline:
    fontFamily: '"Plus Jakarta Sans", Inter, -apple-system, sans-serif'
    fontSize: "2rem"
    fontWeight: 800
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  title:
    fontFamily: '"Plus Jakarta Sans", Inter, -apple-system, sans-serif'
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: 1.4
  body:
    fontFamily: '"Plus Jakarta Sans", Inter, -apple-system, sans-serif'
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: '"Plus Jakarta Sans", Inter, -apple-system, sans-serif'
    fontSize: "0.8125rem"
    fontWeight: 700
    letterSpacing: "0.05em"
rounded:
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "20px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: "12px 28px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  card-surface:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.xl}"
    padding: "24px"
---

# Design System: Nutz Replacer

## Overview

**Creative North Star: "The Haute-Tech Fitting Atelier"**

Nutz Replacer unites the clarity of modern e-commerce with the precision of high-fashion digital styling. The visual language evokes a luxury fashion studio rather than an algorithmic sandbox. It relies on clean architectural whitespace, solid purposeful typography, restrained deep-purple ink accents, and crisp tactile cards.

The system is calibrated for two distinct production surfaces:
1. **Desktop Studio Canvas (1280px+):** A multi-column workspace with sticky result viewport, side-by-side comparative inspection, and granular category tuning.
2. **Dedicated Mobile Artboard (390 × 844 px):** A mobile-first iPhone layout with touch targets $\ge 44\text{px}$, snap-scrolling tile carousels, 3:4 aspect ratio result stage, and a sticky 56px action bar.

**Key Characteristics:**
- Restrained color economy: 90% light neutrals (`#F5F4F8`, `#FFFFFF`), with `#5B3DF0` reserved for active state and primary actions.
- Zero decorative gradients on text; typography is solid, high-contrast, and legible.
- Strict touch and accessibility floor: WCAG AA contrast $\ge 4.5:1$, touch targets $\ge 44 \times 44\text{px}$, body text $\ge 14\text{px}$.
- SVG-only iconography with zero emoji.

## Colors

The palette balances clean fashion-editorial neutrality with an energetic, authoritative digital violet accent.

### Primary
- **Electric Violet** (`#5B3DF0`): The brand's primary interactive voice. Used for primary CTAs, active selection rings, and progress indicators.
- **Deep Violet Hover** (`#4B2EE0`): Hover and pressed state for primary interactive elements.
- **Violet Wash** (`#F0EDFD`): High-subtlety tint used for active category pills, badge backgrounds, and secondary selections.

### Neutral
- **Primary Ink** (`#171717`): Deep neutral black used for primary headings, logos, and high-emphasis body text.
- **Slate Muted** (`#64748B`): Secondary text, step subtitles, and metadata. Contrast $\ge 4.5:1$ against white.
- **Tertiary Gray** (`#737373`): Captions, micro-copy, and inactive placeholder text.
- **Canvas Gray** (`#F5F4F8`): Global background tone providing soft separation from pure white cards.
- **Pure White** (`#FFFFFF`): Card backgrounds, elevated modals, and button text on primary ink.
- **Hairline Border** (`#E8E8EF`): Crisp 1px structural dividers and card outlines.

### Status & Feedback
- **Emerald Success** (`#16A34A`): Confirmed landmarks, active pipeline checks, and ready badges.
- **Crimson Error** (`#DC2626`): Validation errors, image rejection warnings, and removal actions.

### Named Rules
**The 10% Accent Rule:** The primary accent (`#5B3DF0`) must occupy $\le 10\%$ of any given screen surface. Its rarity signals immediate intent and direction.
**No Gradient Headings:** Headings and text must never use decorative gradient clips; use solid `#171717` or `#5B3DF0`.

## Typography

**Display & Body Font:** Plus Jakarta Sans (fallback: Inter, system-ui, sans-serif)  
**Monospace Font:** JetBrains Mono (fallback: monospace)

Plus Jakarta Sans delivers clean geometric rhythm, generous x-height, and refined legibility across dense dashboard metrics and editorial marketing headers.

### Hierarchy
- **Display** (800 ExtraBold, 3.5rem / 56px, line-height 1.15, -0.02em): Hero headlines and editorial titles.
- **Headline** (800 ExtraBold, 2rem / 32px, line-height 1.25, -0.01em): Section titles and modal headings.
- **Title** (700 Bold, 1.25rem / 20px, line-height 1.4): Card headings and artboard section labels.
- **Body** (400 Regular / 600 SemiBold, 0.875rem / 14px, line-height 1.5): Descriptions, instructions, and list text. Never below 14px for body copy.
- **Label / Tag** (700 Bold, 0.8125rem / 13px, tracking 0.04em): Category chips, status badges, and metadata pills. Never below 13px.

## Layout

- **Desktop Studio Grid:** 12-column responsive layout (`max-w-7xl`, centered with responsive padding `px-4 sm:px-6 lg:px-8`). Two equal 6-column columns for inputs and sticky result stage.
- **Mobile Artboard:** Fixed $390 \times 844\text{px}$ viewport frame with internal safe area scrolling. 16px lateral padding, zero horizontal page overflow.
- **Vertical Spacing Rhythm:** 16px (`gap-4`) between related input cards, 32px (`gap-8`) between major workspace columns, 64px (`py-16`) section rhythm.

## Elevation & Depth

Depth is established primarily through crisp 1px hairline borders (`#E8E8EF`) and soft ambient shadows, avoiding dark skeuomorphic drops.

### Shadow Vocabulary
- **Subtle Layer** (`0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)`): Tonal elevation for badges, small preset tiles, and input controls.
- **Card Ambient** (`0 4px 20px -2px rgba(18, 24, 40, 0.05)`): Applied to all elevated white cards (`rounded-2xl`).
- **Primary CTA Lift** (`0 12px 28px -6px rgba(91, 61, 240, 0.3)`): Soft colored ambient glow giving the primary generation button physical presence.

## Shapes

- **Card Radius:** `rounded-2xl` (16px to 20px) for parent cards and dialog surfaces.
- **Control Radius:** `rounded-xl` (12px) for buttons, inputs, category selectors, and thumbnails.
- **Pill Radius:** `rounded-full` (9999px) for status indicators, active step markers, and filter chips.
- **Aspect Ratios:** Strict 3:4 for portrait person uploads and try-on output; 1:1 or contain for flat-lay garment references.

## Components

### Buttons
- **Primary Action:** 44px–56px height, `bg-[#5B3DF0] text-white`, `rounded-xl`, font weight 700. Shows spinning loader during generation.
- **Secondary / Action:** Minimum 44px height/width, `bg-[#F5F4F8] text-[#171717] border border-[#E8E8EF]`, hover `bg-gray-200`.
- **Destructive:** Minimum 44px height/width, `text-[#DC2626] bg-white border border-[#E8E8EF]`, hover `bg-red-50`.

### Upload Cards
- **Dropzone:** Dashed 2px border, transition to `#5B3DF0` on drag-over, generous click target with clear file type and 20MB limit indicators.
- **Active Preview State:** Split layout with 72×92px or 112×144px thumbnail, readiness badge, title, resolution tag, and Replace/Remove button pair.

### Before/After Split Slider
- **Viewport:** Dual-image overlay with clamped percentage clip-path.
- **Handle:** Vertical divider with centered 28px circular grip (`⟷`) with hover and drag states.
- **Touch Area:** Full 44px tall range slider beneath the image on mobile artboards for frictionless thumb scrubbing.

## Do's and Don'ts

### Do
- Always maintain $\ge 44 \times 44\text{px}$ touch targets on interactive mobile controls.
- Always preserve the target person's original facial features, skin tone, hair, and posture.
- Condition try-on directly on the garment reference image via dual-panel spatial diffusion.
- Use semantic HTML tags (`<button>`, `<main>`, `<header>`, `<nav>`, `<section>`).
- Use solid text colors with high contrast.

### Don't
- Do NOT use gradient text (`bg-clip-text text-transparent`) on headings or labels.
- Do NOT use emoji in the UI; use Lucide-React SVG icons.
- Do NOT drop garment patterns or revert to generic text-only prompting.
- Do NOT allow horizontal scroll on mobile artboards or responsive mobile layouts.
- Do NOT use font sizes below 14px for body content or below 13px for labels.
