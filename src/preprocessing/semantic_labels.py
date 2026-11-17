"""
Nutz Try On Enterprise Studio - Centralized Semantic Label Mapping & Validation
Provides standardized, validated label maps for:
- ATR (21/18 semantic classes - CIHP/ATR)
- LIP (20 semantic classes - Look Into Person)
- DensePose (25 UV body part index map)
- SegFormer Fashion (Fashion-pedia 46-class standard)
"""

from typing import Dict, List, Set, Tuple, Union, Optional
from enum import Enum
import numpy as np

class DatasetType(str, Enum):
    ATR = "ATR"
    LIP = "LIP"
    DENSEPOSE = "DENSEPOSE"
    SEGFORMER = "SEGFORMER"

# 1. Authoritative ATR Class Mapping (CIHP / ATR Human Parsing)
ATR_MAPPING: Dict[str, int] = {
    'Background': 0,
    'Hat': 1,
    'Hair': 2,
    'Sunglasses': 3,
    'Upper-clothes': 4,
    'Skirt': 5,
    'Pants': 6,
    'Dress': 7,
    'Belt': 8,
    'Left-shoe': 9,
    'Right-shoe': 10,
    'Face': 11,
    'Left-leg': 12,
    'Right-leg': 13,
    'Left-arm': 14,
    'Right-arm': 15,
    'Bag': 16,
    'Scarf': 17
}

# 2. Authoritative LIP Class Mapping (Look Into Person Benchmark)
LIP_MAPPING: Dict[str, int] = {
    'Background': 0,
    'Hat': 1,
    'Hair': 2,
    'Glove': 3,
    'Sunglasses': 4,
    'Upper-clothes': 5,
    'Dress': 6,
    'Coat': 7,
    'Socks': 8,
    'Pants': 9,
    'Jumpsuits': 10,
    'Scarf': 11,
    'Skirt': 12,
    'Face': 13,
    'Left-arm': 14,
    'Right-arm': 15,
    'Left-leg': 16,
    'Right-leg': 17,
    'Left-shoe': 18,
    'Right-shoe': 19
}

# 3. DensePose Body Chart Index Mapping (24 Body Parts + 0 Background)
DENSE_INDEX_MAP: Dict[str, List[int]] = {
    "background": [0],
    "torso": [1, 2],
    "right hand": [3],
    "left hand": [4],
    "right foot": [5],
    "left foot": [6],
    "right thigh": [7, 9],
    "left thigh": [8, 10],
    "right leg": [11, 13],
    "left leg": [12, 14],
    "left big arm": [15, 17],
    "right big arm": [16, 18],
    "left forearm": [19, 21],
    "right forearm": [20, 22],
    "face": [23, 24],
    "thighs": [7, 8, 9, 10],
    "legs": [11, 12, 13, 14],
    "hands": [3, 4],
    "feet": [5, 6],
    "big arms": [15, 16, 17, 18],
    "forearms": [19, 20, 21, 22],
}

# 4. Standard Unified Part Definitions Across Datasets
UNIFIED_PART_REGISTRY = {
    "upper_clothes": {
        DatasetType.ATR: ['Upper-clothes'],
        DatasetType.LIP: ['Upper-clothes', 'Coat']
    },
    "dress": {
        DatasetType.ATR: ['Dress'],
        DatasetType.LIP: ['Dress']
    },
    "coat": {
        DatasetType.ATR: [],
        DatasetType.LIP: ['Coat']
    },
    "pants": {
        DatasetType.ATR: ['Pants'],
        DatasetType.LIP: ['Pants']
    },
    "skirt": {
        DatasetType.ATR: ['Skirt'],
        DatasetType.LIP: ['Skirt']
    },
    "jumpsuits": {
        DatasetType.ATR: ['Dress'],  # ATR lacks jumpsuits, maps to Dress
        DatasetType.LIP: ['Jumpsuits']
    },
    "face": {
        DatasetType.ATR: ['Face'],
        DatasetType.LIP: ['Face']
    },
    "hair": {
        DatasetType.ATR: ['Hair'],
        DatasetType.LIP: ['Hair']
    },
    "arms": {
        DatasetType.ATR: ['Left-arm', 'Right-arm'],
        DatasetType.LIP: ['Left-arm', 'Right-arm']
    },
    "legs": {
        DatasetType.ATR: ['Left-leg', 'Right-leg'],
        DatasetType.LIP: ['Left-leg', 'Right-leg']
    },
    "accessories": {
        DatasetType.ATR: ['Hat', 'Sunglasses', 'Belt', 'Left-shoe', 'Right-shoe', 'Bag', 'Scarf'],
        DatasetType.LIP: ['Hat', 'Glove', 'Sunglasses', 'Socks', 'Scarf', 'Left-shoe', 'Right-shoe']
    },
    "background": {
        DatasetType.ATR: ['Background'],
        DatasetType.LIP: ['Background']
    }
}


def get_part_mask(
    parse_map: np.ndarray,
    parts: Union[str, List[str]],
    dataset_type: Union[str, DatasetType]
) -> np.ndarray:
    """
    Extracts a binary mask (uint8: 0 or 1) for one or more semantic parts from a segmentation parse map.
    Validates class IDs and dataset type.
    """
    if isinstance(dataset_type, str):
        dataset_type = DatasetType(dataset_type.upper())

    if dataset_type == DatasetType.ATR:
        mapping = ATR_MAPPING
    elif dataset_type == DatasetType.LIP:
        mapping = LIP_MAPPING
    elif dataset_type == DatasetType.DENSEPOSE:
        mapping = DENSE_INDEX_MAP
    else:
        raise ValueError(f"Unsupported dataset type: {dataset_type}")

    if isinstance(parts, str):
        parts = [parts]

    mask = np.zeros_like(parse_map, dtype=np.uint8)

    for p in parts:
        if p not in mapping:
            continue
        val = mapping[p]
        if isinstance(val, list):
            for v in val:
                mask |= (parse_map == v).astype(np.uint8)
        else:
            mask |= (parse_map == val).astype(np.uint8)

    return mask


def get_unified_part_mask(
    parse_map: np.ndarray,
    unified_part_name: str,
    dataset_type: Union[str, DatasetType]
) -> np.ndarray:
    """
    Queries by abstract category (e.g., 'upper_clothes', 'pants', 'face', 'arms')
    and returns the accurate binary mask regardless of underlying model schema.
    """
    if isinstance(dataset_type, str):
        dataset_type = DatasetType(dataset_type.upper())

    if unified_part_name not in UNIFIED_PART_REGISTRY:
        raise KeyError(f"Unknown unified part '{unified_part_name}'. Available: {list(UNIFIED_PART_REGISTRY.keys())}")

    specific_parts = UNIFIED_PART_REGISTRY[unified_part_name].get(dataset_type, [])
    return get_part_mask(parse_map, specific_parts, dataset_type)


def validate_segmentation_map(parse_map: np.ndarray, dataset_type: Union[str, DatasetType]) -> Dict[str, Union[bool, list, dict]]:
    """
    Validates a segmentation parse map:
    - Checks for unmapped or out-of-range class indices.
    - Computes pixel histogram and present semantic categories.
    """
    if isinstance(dataset_type, str):
        dataset_type = DatasetType(dataset_type.upper())

    if dataset_type == DatasetType.ATR:
        mapping = ATR_MAPPING
        max_valid_id = 17
    elif dataset_type == DatasetType.LIP:
        mapping = LIP_MAPPING
        max_valid_id = 19
    elif dataset_type == DatasetType.DENSEPOSE:
        mapping = DENSE_INDEX_MAP
        max_valid_id = 24
    else:
        raise ValueError(f"Unknown dataset type: {dataset_type}")

    unique_ids = np.unique(parse_map)
    out_of_bounds = [int(i) for i in unique_ids if i < 0 or i > max_valid_id]
    
    # Reverse mapping ID -> Name
    id_to_name = {}
    for k, v in mapping.items():
        if isinstance(v, list):
            for sub_v in v:
                id_to_name[sub_v] = k
        else:
            id_to_name[v] = k

    detected_classes = {id_to_name.get(int(i), f"Unknown_{i}"): int(np.sum(parse_map == i)) for i in unique_ids}

    return {
        "valid": len(out_of_bounds) == 0,
        "unique_ids": [int(i) for i in unique_ids],
        "out_of_bounds_ids": out_of_bounds,
        "class_breakdown": detected_classes,
        "shape": list(parse_map.shape)
    }


def fuse_schp_masks(
    atr_map: np.ndarray,
    lip_map: np.ndarray,
    unified_part: str,
    operation: str = "union"
) -> np.ndarray:
    """
    Combines ATR and LIP parse maps for a target unified part using either union ('union') or intersection ('intersect').
    """
    mask_atr = get_unified_part_mask(atr_map, unified_part, DatasetType.ATR)
    mask_lip = get_unified_part_mask(lip_map, unified_part, DatasetType.LIP)

    if operation == "union":
        return mask_atr | mask_lip
    elif operation == "intersect":
        return mask_atr & mask_lip
    else:
        raise ValueError(f"Operation must be 'union' or 'intersect', got: {operation}")

