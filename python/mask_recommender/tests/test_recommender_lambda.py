import pytest
import json

import os
import sys
module_path = os.path.abspath(os.path.join('.'))
if module_path not in sys.path:
    sys.path.append(module_path)

from recommender_lambda import handler

def test_recommender_lambda():
    event = {
        "bitragion_subnasale_arc": 230,
        "face_width": 137,
        "nose_protrusion": 27,
        "facial_hair_beard_length_mm": 0,
    }

    context = {}

    result = handler(event, context)
    body = json.loads(result['body'])

    assert 'mask_id' in body
    assert 'proba_fit' in body
