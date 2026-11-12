"""Local paired experiment on a private prepared training-frame snapshot; no network or uploads."""
import argparse
import json
from html import escape
from pathlib import Path

import pandas as pd
import torch

from mask_recommender import train
from mask_recommender.probability_evaluation import evaluate_probabilities


def compare(frame, epochs=200, learning_rate=0.01, seed=42):
    results = {}
    predictions = {}
    for variant in ['none', 'latent_nose_v1']:
        metadata = train._custom_lr_category_metadata(frame)
        metadata['nose_model'] = variant
        rows = []
        cv = train._cross_validate_custom_lr(
            frame, metadata, epochs, learning_rate, False,
            random_seed=seed, prediction_sink=rows)
        observed = [row for row in rows if row['nose_mm_observed']]
        measured_quality = evaluate_probabilities(
            [r['label'] for r in observed], [r['probability'] for r in observed],
            user_ids=[r['user_id'] for r in observed],
            baseline_probabilities=[r['training_positive_rate'] for r in observed]) if observed else None
        # Save a final full-data model separately from the held-out scores.
        torch.manual_seed(seed + 10000)
        indices = torch.arange(len(frame))
        fit = train.train_custom_lr_with_split(
            frame, indices, indices, metadata, epochs=epochs, learning_rate=learning_rate)
        results[variant] = {
            'cross_validation': cv, 'measured_nose_subset': measured_quality,
            'nose_parameters': train._nose_parameter_report(fit['params'], metadata, frame),
        }
        predictions[variant] = {'rows': rows, 'params': fit['params'], 'metadata': metadata}
    keys = lambda rows: [(r['fold'], r['user_id'], r['fit_test_id'], r['mask_id'], r['label']) for r in rows]
    if keys(predictions['none']['rows']) != keys(predictions['latent_nose_v1']['rows']):
        raise RuntimeError('Paired evaluation observations differ')
    return results, predictions


def write_review(report, output):
    sections = []
    for title, key in [('Mixed measured and imputed inputs', 'variants'),
                       ('Trained only on measured ARKit inputs', 'observed_only_training_variants')]:
        rows = []
        for variant, result in report[key].items():
            evaluation = result['cross_validation']['probability_evaluation']
            m = evaluation['at_0_5']
            rows.append(f"<tr><td>{escape(variant)}</td><td>{evaluation['sample_count']} / {evaluation['user_count']}</td>"
                        f"<td>{evaluation['quality']['log_loss']:.3f}</td><td>{m['precision']:.1%}</td>"
                        f"<td>{m['recall']:.1%}</td><td>{m['f1']:.3f}</td></tr>")
        sections.append(f"<h2>{title}</h2><table><tr><th>Model</th><th>Tests / people</th>"
                        "<th>Log loss ↓</th><th>Precision</th><th>Recall</th><th>F1</th></tr>" + ''.join(rows) + '</table>')
    nose = report['variants']['latent_nose_v1']['nose_parameters']
    families = sorted(nose['families'], key=lambda r: -r['training_rows'])
    rows = ''.join(f"<tr><td>{escape(str(r['fit_family']))}</td><td>{escape(str(r['style']))}</td>"
                   f"<td>{r['effective_preferred_nose_mm']:.1f}</td><td>{r['training_rows']}</td>"
                   f"<td>{r['training_people']}</td><td>{r['positive_rows']}</td></tr>" for r in families)
    page = ("<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
            "<title>Nose-distance model comparison</title><style>body{font:17px system-ui;max-width:1100px;margin:40px auto;padding:20px;color:#243b46}"
            "table{border-collapse:collapse;width:100%;font-size:15px}th,td{padding:10px;border-bottom:1px solid #ddd;text-align:left}"
            "aside{padding:16px;background:#fff2d5}p{line-height:1.5}</style><h1>Observed nose distance + latent mask nose preference</h1>"
            "<p>Local research comparison. Fixed 50% cutoff throughout these tables. Live model unchanged.</p>"
            f"<p>{escape(report['method'])}</p>" + ''.join(sections) +
            "<aside>The gain on mixed inputs did not reproduce in measured-only training. Both models still have poor log loss. "
            "These are exploratory results, not independent validation.</aside>"
            f"<p>{escape(report['limitations'])}</p><h2>Final full-data effective mask preferences</h2>"
            "<p>These values are learned from fit labels, not measured mask dimensions. Extreme values and sparse/all-fail families "
            "indicate weak identification. This table comes from the final mixed-input model, not held-out predictions.</p>"
            "<table><tr><th>Fit family</th><th>Style</th><th>Effective nose mm</th><th>Training tests</th>"
            "<th>People</th><th>Positive labels</th></tr>" + rows +
            "</table><p><a href='comparison.json'>Download full aggregate comparison JSON</a></p></html>")
    (output / 'comparison.html').write_text(page)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path, help='Private training_frame.json from local training')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    frame = pd.read_json(args.frame, orient='table')
    results, predictions = compare(frame)
    measured_frame = frame.loc[frame['nose_mm_observed']].reset_index(drop=True)
    measured_results, measured_predictions = compare(measured_frame) if measured_frame['user_id'].nunique() >= 2 else ({}, {})
    args.output.mkdir(parents=True, exist_ok=True)
    report = {
        'method': 'Same prepared rows, five grouped-user folds, seed 42, Adam, 200 epochs, learning rate 0.01, no class reweighting.',
        'limitations': 'Exploratory single-seed comparison. Inherited global ARKit imputation is not refit inside folds. Observed-only scores are a subgroup of mixed-input training. Learned centers are effective fit parameters, not physical measurements.',
        'variants': results,
        'observed_only_training_variants': measured_results,
    }
    (args.output / 'comparison.json').write_text(json.dumps(train._json_finite(report), indent=2, allow_nan=False))
    predictions.update({f'observed_only_{name}': value for name, value in measured_predictions.items()})
    for variant, artifacts in predictions.items():
        folder = args.output / variant
        folder.mkdir(exist_ok=True)
        torch.save(artifacts['params'], folder / 'custom_model_params.pt')
        (folder / 'custom_model_metadata.json').write_text(json.dumps(artifacts['metadata'], indent=2))
        (folder / 'out_of_fold_predictions.json').write_text(json.dumps(artifacts['rows'], indent=2))
    write_review(report, args.output)
    print(args.output / 'comparison.html')


if __name__ == '__main__':
    main()
