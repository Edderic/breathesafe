from dataclasses import dataclass
from typing import List

# Canonical feature order for the model input
FEATURES: List[str] = [
    # core facial measures
    "face_width",
    "face_length",
    "nose_protrusion",
    "bitragion_subnasale_arc",
    "facial_hair_beard_length_mm",
    "lip_width",
    # mask geometry/context
    "perimeter_mm",
    # adjustability flags remain explicit
    "adjustable_headstrap",
    "adjustable_earloops",
    # categorical columns (mask_id/style/strap_type) will be expanded as one-hots:
    #   mask_id_* , style_* , strap_type_*
]

@dataclass
class FeatureConfig:
    numerical: List[str]
    binary: List[str]


def split_feature_types(feature_names: List[str]) -> FeatureConfig:
    numerical = []
    binary = []
    for name in feature_names:
        if name.startswith("mask_id_") or name.startswith("style_") or name.startswith("strap_type_"):
            binary.append(name)
        elif name in {
            "adjustable_headstrap",
            "adjustable_earloops",
        }:
            binary.append(name)
        else:
            numerical.append(name)
    return FeatureConfig(numerical=numerical, binary=binary)
