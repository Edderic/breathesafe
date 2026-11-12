import math
import pytest
from mask_recommender.probability_evaluation import evaluate_probabilities, probability_quality, threshold_metrics


def test_confusion_counts_and_precision_recall_use_all_outcomes():
    report=evaluate_probabilities([1,1,0,0],[.9,.4,.7,.1],user_ids=[1,1,2,2])
    row=report['at_0_5']
    assert [row[k] for k in ['true_positive','false_positive','true_negative','false_negative']]==[1,1,1,1]
    assert row['precision']==row['recall']==row['f1']==.5
    assert report['sample_count']==4 and report['user_count']==2
    assert report['quality']['log_loss']==pytest.approx(-sum(map(math.log,[.9,.4,.3,.9]))/4)
    assert report['outcome_scores']['pass']['mean']==pytest.approx(.65)
    assert report['outcome_scores']['fail']['mean']==pytest.approx(.4)
    assert sum(b['pass_count'] for b in report['score_histogram'])==2
    assert sum(b['fail_count'] for b in report['score_histogram'])==2


def test_confident_wrong_scores_cost_more_than_uncertain_scores():
    assert probability_quality([1,0],[.01,.99])['log_loss']>probability_quality([1,0],[.5,.5])['log_loss']
    assert math.isfinite(probability_quality([1,0],[0,1])['log_loss'])
    assert probability_quality([1,0],[1,0])['brier_score']==0


def test_edges_and_calibration_counts_include_zero_and_one_once():
    report=evaluate_probabilities([0,1,0,1],[0,.1,.5,1])
    assert sum(b['sample_count'] for b in report['calibration_bins'])==4
    assert report['score_histogram'][0]['fail_count']==1
    assert report['score_histogram'][-1]['pass_count']==1
    assert threshold_metrics([1],[.5],.5)['true_positive']==1


def test_undefined_metrics_and_single_class_have_no_suggested_threshold():
    assert threshold_metrics([1,0],[.1,.1],.5)['precision'] is None
    assert threshold_metrics([0,0],[.9,.8],.5)['recall'] is None
    assert evaluate_probabilities([1,1],[.9,.8])['exploratory_f1'] is None
    empty=evaluate_probabilities([],[])
    assert not empty['available'] and empty['quality']['log_loss'] is None


def test_user_equal_metrics_reduce_repeat_tester_influence():
    report=evaluate_probabilities([1,1,1,0],[.9,.9,.9,.9],user_ids=[1,1,1,2])
    assert report['quality']['positive_rate']==.75
    assert report['user_equal']['quality']['positive_rate']==pytest.approx(.5)
    assert report['user_equal']['at_0_5']['precision']==pytest.approx(.5)


def test_threshold_choice_is_marked_exploratory_and_no_private_rows_are_exported():
    report=evaluate_probabilities([1,1,0,0],[.4,.3,.2,.1],user_ids=[7,7,8,8],baseline_probabilities=[.5]*4)
    assert report['exploratory_f1']['f1']==1
    assert report['at_0_5']['recall']==0
    assert 'not independently validated' in report['threshold_selection']
    assert report['training_prevalence_baseline']['log_loss']==pytest.approx(math.log(2))
    assert 'user_ids' not in report and 'rows' not in report


@pytest.mark.parametrize('labels,scores', [([1],[float('nan')]),([1],[1.1]),([None],[.5]),([1,0],[.5])])
def test_invalid_inputs_fail_instead_of_silently_changing_denominators(labels,scores):
    with pytest.raises(ValueError):evaluate_probabilities(labels,scores)
