import { SamplePreset } from './types';

export const SAMPLE_PERSONS: SamplePreset[] = [
  {
    id: 'p-user-studio',
    name: 'Studio Portrait (Namaste)',
    category: 'Male Model',
    gender: 'men',
    imageUrl: '/studio/assets/sample_person_1.jpg',
    promptHint: 'Male portrait standing with hands folded in namaste, studio illumination',
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
    id: 'p-fem-1',
    name: 'Ananya (Editorial Model)',
    category: 'Female Model',
    gender: 'women',
    imageUrl: '/studio/assets/sample_person_female.jpg',
    promptHint: 'Full-length fashion portrait of Indian female model Ananya with natural posture and studio lighting',
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
    id: 'g-emerald-shirt',
    name: 'Pastel Mint Printed Casual Shirt',
    category: 'Upper Body',
    gender: 'men',
    imageUrl: '/studio/assets/sample_emerald_shirt.jpg',
    promptHint: 'Casual light mint pastel green button-down shirt with all-over printed micro character motifs and spread collar',
  },
  {
    id: 'g-blazer',
    name: 'Tailored Navy Wool Blazer',
    category: 'Upper Body',
    gender: 'men',
    imageUrl: '/studio/assets/sample_navy_blazer.jpg',
    promptHint: 'Formal tailored Italian navy blue wool blazer over crisp white dress shirt',
  },
  {
    id: 'g-black-tee',
    name: 'Essential Minimalist Black Tee',
    category: 'Upper Body',
    gender: 'men',
    imageUrl: '/studio/assets/sample_black_tshirt.jpg',
    promptHint: 'Modern minimalist premium black cotton crew-neck t-shirt with clean tailored drape',
  },
  {
    id: 'g-anarkali',
    name: 'Emerald Silk Anarkali Suit',
    category: 'Traditional Wear',
    gender: 'women',
    imageUrl: '/studio/assets/sample_anarkali_dress.jpg',
    promptHint: 'Exquisite emerald green silk Indian anarkali dress with intricate gold zardozi embroidery, dupatta, and matching chudidar',
  },
  {
    id: 'g-denim',
    name: 'Vintage Selvedge Denim Jacket',
    category: 'Upper Body',
    gender: 'men',
    imageUrl: '/studio/assets/sample_denim_jacket.jpg',
    promptHint: 'Classic vintage indigo blue denim trucker jacket over white tee',
  },
];

export interface CategorySpec {
  id: number;
  key: string;
  name: string;
  macroCategory: 'Upper Body' | 'Lower Body' | 'Full Body' | 'Traditional Wear' | 'Dress' | 'Other';
  directiveSummary: string;
}

export const MACRO_CATEGORIES = [
  'Upper Body',
  'Lower Body',
  'Full Body',
  'Dress',
  'Traditional Wear',
  'Other',
] as const;

export const FLUX_17_CATEGORIES: CategorySpec[] = [
  { id: 1, key: 't_shirt', name: 'T-Shirt', macroCategory: 'Upper Body', directiveSummary: 'Preserve neckline, collar, sleeve length, printed graphics, original colors.' },
  { id: 2, key: 'inner_vest', name: 'Inner Vest / Baniyan', macroCategory: 'Upper Body', directiveSummary: 'Strictly sleeveless, armhole shape, ribbed texture, no jackets/collars.' },
  { id: 3, key: 'shirt', name: 'Shirt / Button-Down', macroCategory: 'Upper Body', directiveSummary: 'Collar design, button arrangement, pocket placement, stripes/checks.' },
  { id: 4, key: 'polo_t_shirt', name: 'Polo T-Shirt', macroCategory: 'Upper Body', directiveSummary: 'Polo collar, button placket, sleeve construction, logo placement.' },
  { id: 5, key: 'kurta', name: 'Kurta', macroCategory: 'Traditional Wear', directiveSummary: 'Traditional silhouette, front placket, embroidery, knee/thigh length.' },
  { id: 6, key: 'blazer', name: 'Blazer / Suit Jacket', macroCategory: 'Upper Body', directiveSummary: 'Lapel shape, collar construction, buttons, preserve inner shirt.' },
  { id: 7, key: 'waistcoat', name: 'Waistcoat / Nehru Jacket', macroCategory: 'Traditional Wear', directiveSummary: 'Sleeveless outer layer, Nehru collar, button placket, ornamental motifs.' },
  { id: 8, key: 'hoodie', name: 'Hoodie / Sweatshirt', macroCategory: 'Upper Body', directiveSummary: 'Hood shape, cuffs, kangaroo pockets, drawstrings, graphics.' },
  { id: 9, key: 'sherwani', name: 'Sherwani', macroCategory: 'Traditional Wear', directiveSummary: 'Traditional long silhouette, ornate embroidery, decorative borders, mandarin collar.' },
  { id: 10, key: 'achkan', name: 'Achkan', macroCategory: 'Traditional Wear', directiveSummary: 'Structured collar, traditional long silhouette, front buttons, embroidery.' },
  { id: 11, key: 'saree', name: 'Saree', macroCategory: 'Traditional Wear', directiveSummary: 'Traditional drape, realistic pleats, border, pallu pattern, blouse.' },
  { id: 12, key: 'lehenga', name: 'Lehenga', macroCategory: 'Traditional Wear', directiveSummary: 'Flared skirt, choli blouse, dupatta drape, intricate zardozi embroidery.' },
  { id: 13, key: 'jeans', name: 'Jeans / Denim', macroCategory: 'Lower Body', directiveSummary: 'Denim wash, fading, waistband, pocket stitching, cut and fit.' },
  { id: 14, key: 'formal_trousers', name: 'Formal Trousers', macroCategory: 'Lower Body', directiveSummary: 'Tailored fit, pleats, waistband, pocket arrangement, fabric texture.' },
  { id: 15, key: 'shorts', name: 'Shorts', macroCategory: 'Lower Body', directiveSummary: 'Above/at knee length, waistband, pocket placement, protect upper body.' },
  { id: 16, key: 'western_dress', name: 'Western Dress / Gown', macroCategory: 'Dress', directiveSummary: 'Neckline, sleeve design, waistline, dress silhouette, flared hemline.' },
  { id: 17, key: 'dhoti', name: 'Dhoti', macroCategory: 'Traditional Wear', directiveSummary: 'Traditional dhoti draping, pleats and folds, decorative border.' },
];
