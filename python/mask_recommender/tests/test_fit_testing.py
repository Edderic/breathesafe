import os
import sys

module_path = os.path.abspath(os.path.join('./python/mask_recommender'))
if module_path not in sys.path:
    sys.path.append(module_path)

import pytest
from fit_testing import find_air_delivery_rate_filtered

def test_find_air_delivery_rate_filtered_n99():
    """
    Passing in c_ambient of 1000, and the filtration efficiency matches the
    ff_n99 value exactly, we should get that the clean air delivery rate is
    exactly the air delivery rate.
    """
    clean_air_delivery_rate = find_air_delivery_rate_filtered(
        c_ambient=1000,
        filtration_efficiency=0.99,
        c_mask=None,
        ff_n99=100,
        air_delivery_rate=6000,
    )

    assert clean_air_delivery_rate == 6000

def test_find_air_delivery_rate_filtered_n99_without_c_ambient():
    """
    Passing in c_ambient of 1000, and the filtration efficiency matches the
    ff_n99 value exactly, we should get that the clean air delivery rate is
    exactly the air delivery rate.
    """
    clean_air_delivery_rate = find_air_delivery_rate_filtered(
        c_ambient=None,
        filtration_efficiency=0.99,
        c_mask=None,
        ff_n99=100,
        air_delivery_rate=6000,
    )

    assert clean_air_delivery_rate == 6000

def test_find_air_delivery_rate_filtered_n99_without_c_ambient_ff_n99_25():
    """
    Passing in no_c_ambient, and the filtration efficiency is 99%
    but the ff_n99 is only 25, we should get a value less than 6000
    """
    clean_air_delivery_rate = find_air_delivery_rate_filtered(
        c_ambient=None,
        filtration_efficiency=0.99,
        c_mask=None,
        ff_n99=25,
        air_delivery_rate=6000,
    )

    assert abs(clean_air_delivery_rate - 5818) < 1

def test_find_air_delivery_rate_filtered_n99_without_c_ambient_ff_n99_25_some_other_c_ambient():
    """
    Just like
    test_find_air_delivery_rate_filtered_n99_without_c_ambient_ff_n99_25 but
    c_ambient is set to some arbitrary number. It should not make a difference.

    """
    clean_air_delivery_rate = find_air_delivery_rate_filtered(
        c_ambient=1234,
        filtration_efficiency=0.99,
        c_mask=None,
        ff_n99=25,
        air_delivery_rate=6000,
    )

    assert abs(clean_air_delivery_rate - 5818) < 1

def test_find_air_delivery_rate_filtered_n99_without_c_ambient_ff_n99_25_some_other_c_ambient_2():
    """
    Just like
    test_find_air_delivery_rate_filtered_n99_without_c_ambient_ff_n99_25 but
    c_ambient is set to some arbitrary number. It should not make a difference.

    """
    clean_air_delivery_rate = find_air_delivery_rate_filtered(
        c_ambient=4321,
        filtration_efficiency=0.99,
        c_mask=None,
        ff_n99=25,
        air_delivery_rate=6000,
    )

    assert abs(clean_air_delivery_rate - 5818) < 1
