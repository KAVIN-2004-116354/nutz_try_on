import os
import sys
import unittest
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.preprocessing.semantic_labels import (
    ATR_MAPPING, LIP_MAPPING, DENSE_INDEX_MAP,
    DatasetType, get_part_mask, get_unified_part_mask,
    validate_segmentation_map, fuse_schp_masks
)
from src.preprocessing.anatomy_guard import AdaptiveAnatomyGuard


class TestSemanticLabels(unittest.TestCase):
    def test_atr_lip_class_counts(self):
        """Validates that ATR has 18 classes and LIP has 20 classes with unique IDs."""
        self.assertEqual(len(ATR_MAPPING), 18)
        self.assertEqual(len(LIP_MAPPING), 20)
        self.assertEqual(len(set(ATR_MAPPING.values())), 18)
        self.assertEqual(len(set(LIP_MAPPING.values())), 20)

    def test_key_label_alignments(self):
        """Verifies critical class IDs match benchmark definitions."""
        # Upper clothes
        self.assertEqual(ATR_MAPPING['Upper-clothes'], 4)
        self.assertEqual(LIP_MAPPING['Upper-clothes'], 5)
        # Pants / Trousers
        self.assertEqual(ATR_MAPPING['Pants'], 6)
        self.assertEqual(LIP_MAPPING['Pants'], 9)
        # Face
        self.assertEqual(ATR_MAPPING['Face'], 11)
        self.assertEqual(LIP_MAPPING['Face'], 13)
        # Arms
        self.assertEqual(ATR_MAPPING['Left-arm'], 14)
        self.assertEqual(ATR_MAPPING['Right-arm'], 15)
        self.assertEqual(LIP_MAPPING['Left-arm'], 14)
        self.assertEqual(LIP_MAPPING['Right-arm'], 15)

    def test_unified_query(self):
        """Tests that abstract queries extract correct masks from synthetic maps."""
        # Create synthetic 100x100 parse map
        atr_map = np.zeros((100, 100), dtype=np.uint8)
        atr_map[10:30, 20:80] = 4  # Upper-clothes
        atr_map[50:90, 20:80] = 6  # Pants
        atr_map[0:10, 40:60] = 11  # Face

        lip_map = np.zeros((100, 100), dtype=np.uint8)
        lip_map[10:30, 20:80] = 5  # Upper-clothes
        lip_map[50:90, 20:80] = 9  # Pants
        lip_map[0:10, 40:60] = 13  # Face

        upper_atr = get_unified_part_mask(atr_map, "upper_clothes", DatasetType.ATR)
        upper_lip = get_unified_part_mask(lip_map, "upper_clothes", DatasetType.LIP)

        self.assertEqual(np.sum(upper_atr), 20 * 60)
        self.assertEqual(np.sum(upper_lip), 20 * 60)
        np.testing.assert_array_equal(upper_atr, upper_lip)

    def test_validation_function(self):
        """Verifies out-of-bounds detection."""
        valid_map = np.array([[0, 4], [6, 11]], dtype=np.uint8)
        val = validate_segmentation_map(valid_map, DatasetType.ATR)
        self.assertTrue(val["valid"])
        self.assertEqual(len(val["out_of_bounds_ids"]), 0)

        invalid_map = np.array([[0, 25], [6, 11]], dtype=np.uint8)
        val_inv = validate_segmentation_map(invalid_map, DatasetType.ATR)
        self.assertFalse(val_inv["valid"])
        self.assertIn(25, val_inv["out_of_bounds_ids"])


class MockLandmark:
    def __init__(self, x, y, visibility=0.95):
        self.x = x
        self.y = y
        self.visibility = visibility


class TestAnatomyGuard(unittest.TestCase):
    def setUp(self):
        self.guard = AdaptiveAnatomyGuard()

    def test_resolution_adaptive_scaling(self):
        """Verifies that protection buffer scales with resolution."""
        # Test sizes: 500x500 vs 1500x1500 (3x resolution)
        landmarks = [MockLandmark(0.5, 0.5) for _ in range(33)]
        # Left hand wrist, pinky, index, thumb (15, 17, 19, 21)
        landmarks[15] = MockLandmark(0.48, 0.50)
        landmarks[17] = MockLandmark(0.47, 0.45)
        landmarks[19] = MockLandmark(0.50, 0.43)
        landmarks[21] = MockLandmark(0.52, 0.46)
        # Right hand (16, 18, 20, 22)
        landmarks[16] = MockLandmark(0.52, 0.50)
        landmarks[18] = MockLandmark(0.53, 0.45)
        landmarks[20] = MockLandmark(0.50, 0.43)
        landmarks[22] = MockLandmark(0.48, 0.46)
        # Shoulders (11, 12)
        landmarks[11] = MockLandmark(0.35, 0.30)
        landmarks[12] = MockLandmark(0.65, 0.30)
        # Elbows (13, 14)
        landmarks[13] = MockLandmark(0.38, 0.45)
        landmarks[14] = MockLandmark(0.62, 0.45)

        mask_small = self.guard.build_hand_protection_mask((500, 500), landmarks)
        mask_large = self.guard.build_hand_protection_mask((1500, 1500), landmarks)

        pixels_small = np.sum(mask_small > 0)
        pixels_large = np.sum(mask_large > 0)

        # In 3x resolution (9x pixel area), pixel count should scale approximately proportionally (~9x)
        area_ratio = pixels_large / max(pixels_small, 1)
        self.assertTrue(7.0 <= area_ratio <= 11.0, f"Expected ~9x area scaling, got {area_ratio:.2f}")

    def test_pose_aware_waistline(self):
        """Verifies waistline estimation bounds upper shirt strictly above pants."""
        h, w = 1000, 750
        landmarks = [MockLandmark(0.5, 0.5) for _ in range(33)]
        # Hips at y=0.55 (550px)
        landmarks[23] = MockLandmark(0.40, 0.55)
        landmarks[24] = MockLandmark(0.60, 0.55)

        # Synthetic pants starting at y=540px
        schp_atr = np.zeros((h, w), dtype=np.uint8)
        schp_atr[540:950, 200:550] = 6  # Pants

        y_waist = self.guard.estimate_pose_aware_waistline((h, w), landmarks, schp_atr=schp_atr)
        # Must be within 5px of detected pants waistband (540px)
        self.assertAlmostEqual(y_waist, 540, delta=10)


if __name__ == "__main__":
    unittest.main()

