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
    # strap types and adjustability (binary flags)
    "headstrap",
    "adjustable_headstrap",
    "earloops",
    "adjustable_earloops",
    # mask styles
    "boat",
    "duckbill",
    "cup",
    "bifold",
    "bifold+gasket",
    # generic mask ids (allow sparse one-hots like mask_id_1, mask_id_2, ...)
]

@dataclass
class FeatureConfig:
    numerical: List[str]
    binary: List[str]


def split_feature_types(feature_names: List[str]) -> FeatureConfig:
    numerical = []
    binary = []
    for name in feature_names:
        if name.startswith("mask_id_"):
            binary.append(name)
        elif name in {
            "headstrap",
            "adjustable_headstrap",
            "earloops",
            "adjustable_earloops",
            "boat",
            "duckbill",
            "cup",
            "bifold",
            "bifold+gasket",
        }:
            binary.append(name)
        else:
            numerical.append(name)
    return FeatureConfig(numerical=numerical, binary=binary)
