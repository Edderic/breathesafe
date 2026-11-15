"""Check which feature recipes can personalize relative mask rankings."""
import numpy as np
import pandas as pd
import pytest

from mask_recommender.scripts.fixed_range_models import CONFIG
from mask_recommender.scripts.simple_fixed_range_comparison import SimpleFixedRangeClassifier


@pytest.mark.parametrize('arm', ['traditional_direct', 'traditional_pca3'])
def test_only_interaction_recipes_support_face_dependent_mask_comparisons(arm):
    rng = np.random.default_rng(11)
    people = pd.DataFrame({'user_id': range(5)})
    for column, (lower, upper) in CONFIG['ranges'].items():
        if column != 'mask_perimeter_mm':
            people[column] = lower+(upper-lower)*rng.uniform(.3, .7, 5)
    frame = pd.DataFrame([dict(user_id=user, mask_id=mask+1, fit_family_id=mask+1,
        style='Bifold' if mask < 2 else 'Cup', strap_type='Headstrap',
        mask_perimeter_mm=250.+mask*70., qlft_pass_normalized=float((user+mask)%3 == 0))
        for user in range(5) for mask in range(3)])
    # Two people, each evaluated with the same two masks. A nonzero difference
    # of mask contrasts means the representation permits personalized ranking.
    pair = frame.loc[((frame.user_id == 0) | (frame.user_id == 1)) & (frame.mask_id <= 2)]
    for recipe in ['linear_additive', 'quadratic_additive', 'shared_perimeter_interactions', 'full_interactions']:
        model = SimpleFixedRangeClassifier(arm, recipe).fit(frame, people)
        x = model.design(pair, people).toarray()
        contrast = x[0]-x[1]-x[2]+x[3]
        if recipe.endswith('additive'):
            np.testing.assert_allclose(contrast, 0., atol=1e-12)
        else:
            assert np.abs(contrast).max() > 1e-5
        assert model.classifier.n_features_in_ < (150 if arm == 'traditional_direct' else 90)
