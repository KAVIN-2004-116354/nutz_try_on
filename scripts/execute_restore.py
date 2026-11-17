import shutil
from pathlib import Path

scripts_dir = Path("/home/lenovo/try_on/scripts")
src_dir = Path("/home/lenovo/try_on/nutz-replacer/src")

# 1. Navbar.tsx
shutil.copy(scripts_dir / "backup_navbar_1119.tsx", src_dir / "components/Navbar.tsx")
print("Restored Navbar.tsx")

# 2. GenerationHistory.tsx
hist_content = (scripts_dir / "backup_history_1151.tsx").read_text(encoding="utf-8")
hist_content = hist_content.replace(
    "import { History, Download, Eye, Clock, Trash2, Cpu, Sparkles } from 'lucide-react';",
    "import { History, Download, Eye, Clock, Trash2, Cpu } from 'lucide-react';"
)
(src_dir / "components/GenerationHistory.tsx").write_text(hist_content, encoding="utf-8")
print("Restored GenerationHistory.tsx")

# 3. presets.ts
presets_content = """import { SamplePreset } from './types';

export const SAMPLE_PERSONS: SamplePreset[] = [
  {
    id: 'p-fem-1',
    name: 'Ananya (Editorial Model)',
    category: 'Female Model',
    gender: 'women',
    imageUrl: '/studio/assets/sample_person_female.jpg',
    promptHint: 'Full-length fashion portrait of Indian female model Ananya with natural posture and studio lighting',
  },
  {
    id: 'p-men-clean',
    name: 'Kabir (Clean Look)',
    category: 'Male Model',
    gender: 'men',
    imageUrl: '/studio/assets/sample_men_clean.jpg',
    promptHint: 'Clean-shaven attractive Indian male model standing in neutral studio pose',
  },
  {
    id: 'p-men-beard',
    name: 'Aarav (Bearded Look)',
    category: 'Male Model',
    gender: 'men',
    imageUrl: '/studio/assets/sample_men_beard.jpg',
    promptHint: 'Attractive Indian male model with groomed beard in studio portrait lighting',
  },
  {
    id: 'p-men-smile',
    name: 'Rohan (Casual Look)',
    category: 'Male Model',
    gender: 'men',
    imageUrl: '/studio/assets/sample_men_smile.jpg',
    promptHint: 'Casual smiling Indian male model standing forward facing',
  },
];

export const SAMPLE_GARMENTS: SamplePreset[] = [
  {
    id: 'g-anarkali',
    name: 'Emerald Silk Anarkali Suit',
    category: 'Ethnic Wear',
    gender: 'women',
    imageUrl: '/studio/assets/sample_anarkali_dress.jpg',
    promptHint: 'Exquisite emerald green silk Indian anarkali dress with intricate gold zardozi embroidery, dupatta, and matching chudidar',
  },
  {
    id: 'g-blazer',
    name: 'Tailored Navy Wool Blazer',
    category: 'Formal Wear',
    gender: 'men',
    imageUrl: '/studio/assets/sample_navy_blazer.jpg',
    promptHint: 'Formal tailored Italian navy blue wool blazer over crisp white dress shirt',
  },
  {
    id: 'g-black-tee',
    name: 'Essential Minimalist Black Tee',
    category: 'Casual Wear',
    gender: 'men',
    imageUrl: '/studio/assets/sample_black_tshirt.jpg',
    promptHint: 'Modern minimalist premium black cotton crew-neck t-shirt with clean tailored drape',
  },
  {
    id: 'g-emerald-shirt',
    name: 'Pastel Mint Printed Casual Shirt',
    category: 'Casual Wear',
    gender: 'men',
    imageUrl: '/studio/assets/sample_emerald_shirt.jpg',
    promptHint: 'Casual light mint pastel green button-down shirt with all-over printed micro character motifs and spread collar',
  },
  {
    id: 'g-denim',
    name: 'Vintage Selvedge Denim Jacket',
    category: 'Outerwear',
    gender: 'men',
    imageUrl: '/studio/assets/sample_denim_jacket.jpg',
    promptHint: 'Classic vintage indigo blue denim trucker jacket over white tee',
  },
];

export interface CategorySpec {
  id: number;
  key: string;
  name: string;
  macroCategory: 'upper_body' | 'lower_body' | 'full_body' | 'complex_ethnic';
  directiveSummary: string;
}

export const FLUX_17_CATEGORIES: CategorySpec[] = [
  { id: 1, key: 't_shirt', name: 'T-Shirt', macroCategory: 'upper_body', directiveSummary: 'Preserve neckline, collar, sleeve length, printed graphics, original colors.' },
  { id: 2, key: 'inner_vest', name: 'Inner Vest / Baniyan', macroCategory: 'upper_body', directiveSummary: 'Strictly sleeveless, armhole shape, ribbed texture, no jackets/collars.' },
  { id: 3, key: 'shirt', name: 'Shirt', macroCategory: 'upper_body', directiveSummary: 'Collar design, button arrangement, pocket placement, stripes/checks.' },
  { id: 4, key: 'polo_t_shirt', name: 'Polo T-Shirt', macroCategory: 'upper_body', directiveSummary: 'Polo collar, button placket, sleeve construction, logo placement.' },
  { id: 5, key: 'kurta', name: 'Kurta', macroCategory: 'upper_body', directiveSummary: 'Traditional silhouette, front placket, embroidery, knee/thigh length.' },
  { id: 6, key: 'blazer', name: 'Blazer / Suit Jacket', macroCategory: 'upper_body', directiveSummary: 'Lapel shape, collar construction, buttons, preserve inner shirt.' },
  { id: 7, key: 'waistcoat', name: 'Waistcoat / Nehru Jacket', macroCategory: 'upper_body', directiveSummary: 'Sleeveless outer layer, Nehru collar, button placket, ornamental motifs.' },
  { id: 8, key: 'hoodie', name: 'Hoodie / Sweatshirt', macroCategory: 'upper_body', directiveSummary: 'Hood shape, cuffs, kangaroo pockets, drawstrings, graphics.' },
  { id: 9, key: 'sherwani', name: 'Sherwani', macroCategory: 'upper_body', directiveSummary: 'Traditional long silhouette, ornate embroidery, decorative borders, mandarin collar.' },
  { id: 10, key: 'achkan', name: 'Achkan', macroCategory: 'upper_body', directiveSummary: 'Structured collar, traditional long silhouette, front buttons, embroidery.' },
  { id: 11, key: 'saree', name: 'Saree', macroCategory: 'complex_ethnic', directiveSummary: 'Traditional drape, realistic pleats, border, pallu pattern, blouse.' },
  { id: 12, key: 'lehenga', name: 'Lehenga', macroCategory: 'complex_ethnic', directiveSummary: 'Flared skirt, choli blouse, dupatta drape, intricate zardozi embroidery.' },
  { id: 13, key: 'jeans', name: 'Jeans', macroCategory: 'lower_body', directiveSummary: 'Denim wash, fading, waistband, pocket stitching, cut and fit.' },
  { id: 14, key: 'formal_trousers', name: 'Formal Trousers', macroCategory: 'lower_body', directiveSummary: 'Tailored fit, pleats, waistband, pocket arrangement, fabric texture.' },
  { id: 15, key: 'shorts', name: 'Shorts', macroCategory: 'lower_body', directiveSummary: 'Above/at knee length, waistband, pocket placement, protect upper body.' },
  { id: 16, key: 'western_dress', name: 'Western Dress / Gown', macroCategory: 'full_body', directiveSummary: 'Neckline, sleeve design, waistline, dress silhouette, flared hemline.' },
  { id: 17, key: 'dhoti', name: 'Dhoti', macroCategory: 'lower_body', directiveSummary: 'Traditional dhoti draping, pleats and folds, decorative border.' },
];
"""
(src_dir / "presets.ts").write_text(presets_content, encoding="utf-8")
print("Restored presets.ts")

# 4. App.tsx
app_content = (scripts_dir / "app_backup_1167.tsx").read_text(encoding="utf-8")
app_content = app_content.replace(
    "const [customPrompt, setCustomPrompt] = useState<string>(\n    SAMPLE_GARMENTS[0].promptHint || ''\n  );",
    "const [customPrompt, setCustomPrompt] = useState<string>('');"
)
(src_dir / "App.tsx").write_text(app_content, encoding="utf-8")
print("Restored App.tsx")

# 5. Clean up temporary test components in components/
for extra in ["PhotoUploadSection.tsx", "GarmentCatalogSection.tsx", "ChosenGarmentsSection.tsx", "ResultSection.tsx"]:
    p = src_dir / "components" / extra
    if p.exists():
        p.unlink()
        print(f"Removed temporary {extra}")

# 6. index.html
index_html = Path("/home/lenovo/try_on/nutz-replacer/index.html")
index_content = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23a855f7'><path d='M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5'/></svg>" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Nutz Atelier — Haute Couture FLUX-DEV-012 Virtual Try-On Studio</title>
    <meta name="description" content="Haute Couture AI Virtual Try-On Studio powered exclusively by FLUX-DEV-012 on Nutz Railway Cloud." />
    <!-- Google Fonts: Inter (UI/Controls) + Playfair Display (Editorial Luxury Serif) + JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400;1,600&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  </head>
  <body class="bg-studio-950 text-slate-100 antialiased selection:bg-purple-900 selection:text-amber-200">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""
index_html.write_text(index_content, encoding="utf-8")
print("Restored index.html")
