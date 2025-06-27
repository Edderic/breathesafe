import pytest
from ..inference import Factor
import pandas as pd

def test_factor():
    """
    A -> B -> C

    For now, let's assume the factor is a conditional probability table

    A=0  0.7
    A=1  0.3

         B=0,  B=1
    A=0  0.1   0.9
    A=1  0.7   0.3

         C=0,  C=1
    B=0  0.95  0.05
    B=1  0.4   0.6

    Let's say we observe B = 1, and we want to infer the probabilities of A
    P(A | B = 1)

    """

    a = pd.DataFrame(
        [
            { 'A': 0, 'value': 0.7 },
            {'A': 1, 'value': 0.3}
        ]
    )
    #.set_index('A')

    b_given_a = pd.DataFrame(
        [
            {'A': 0, "B": 0, 'value': 0.1},
            {'A': 0, "B": 1, 'value': 0.9},
            {'A': 1, "B": 0, 'value': 0.7},
            {'A': 1, "B": 1, 'value': 0.3},
        ]
    )
    #.groupby(['A', 'B']).apply(lambda r: r['value'])

    c_given_b = pd.DataFrame(
        [
            {'B': 0, "C": 0, 'value': 0.95},
            {'B': 0, "C": 1, 'value': 0.05},
            {'B': 1, "C": 0, 'value': 0.4},
            {'B': 1, "C": 1, 'value': 0.6},
        ]
    )

    factor_a = Factor(a)
    factor_b_given_a = Factor(b_given_a)
    factor_c_given_b = Factor(c_given_b)

    a_b = factor_a.times(factor_b_given_a)
    expected_table = pd.DataFrame(
        [
           {'A': 0,  'B': 0, 'value': 0.07},
           {'A': 0,  'B': 1, 'value': 0.63},
           {'A': 1,  'B': 0, 'value': 0.21},
           {'A': 1,  'B': 1, 'value': 0.09},
        ]
    )

    # Use pandas testing function for DataFrame comparison
    pd.testing.assert_frame_equal(a_b.table, expected_table, check_dtype=False)
