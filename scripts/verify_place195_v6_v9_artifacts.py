"""Read-only accepted-artifact checks plus eight non-fitting software tests.
Run from /home/hongyi-home-lab/neuro_science with scratch/v6-v9-runtime/bin/python.
Does not inspect the importer/raw data or original test rows, load checkpoints,
refit any model, or modify accepted outputs. Saved reload-parity receipts are
checked; checkpoint reload itself is NOT independently repeated here.
"""
import collections
import csv
import hashlib
import json
from pathlib import Path
import sys
import unittest

import numpy as np
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, brier_score_loss, log_loss, roc_auc_score,
)

repo = Path.cwd()
assert (repo / 'scripts/place195_v8b_v9_cebra.py').is_file(), 'Run from neuro_science'
sys.path.insert(0, str(repo))
root = repo / 'outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906'
final = root / 'v8b-v9-cebra-final-20260905T224554Z'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_rows(path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


md = json.loads((root / 'final_report_manifest.json').read_text())
html = json.loads((root / 'audits/professor-html-validation.json').read_text())
assert digest(repo / md['report_path']) == md['report_sha256']
assert digest(repo / html['report_path']) == html['sha256']
assert md['original_test_pristine'] is False
for name, expected in {
    'place195_v7_v8_neural_experiments.py': '39ed10704d7b3258a4d7109c9c4ce7ddecc5de98d4c11efe66f019d3cb973089',
    'place195_v8b_v9_cebra.py': '737ad148dcc261c3ec1bbbd1ada395b34b47b2b37c5920370d3107c209976f9a',
}.items():
    assert digest(repo / 'scripts' / name) == expected, name
source = root / 'v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/source_level_cue_tensors.npz'
assert digest(source) == '688e3b52f69a872c7aec420da99ebb6f0b80464351ded3813b077cd7ed3cf567'
print('PASS: two reports, two experiment scripts, and primary source tensor hashes')

fits = list((final / 'v9').rglob('fit_info.json'))
assert len(fits) == 52, len(fits)
for path in fits:
    info = json.loads(path.read_text())
    assert info['save_load_max_abs_embedding_diff'] == 0.0, path
    assert len(csv_rows(path.parent / 'loss_trace.csv')) == 1000, path
print('PASS: 52 final fit records, 52,000 saved loss rows, all saved reload receipts zero')

# Independent score calculation from accepted predictions, not copying metric cells.
fields = ('representation', 'dim', 'seed', 'split')
grouped = collections.defaultdict(list)
for row in csv_rows(final / 'v9/v9_cebra_predictions.csv'):
    assert row['split'] in ('train', 'validation')
    grouped[tuple(row[k] for k in fields)].append(row)
metrics = csv_rows(final / 'v9/v9_cebra_metrics.csv')
assert len(grouped) == len(metrics) == 24
for row in metrics:
    key = tuple(row[k] for k in fields)
    predictions = grouped[key]
    assert len(predictions) == 128 and len({r['row'] for r in predictions}) == 128
    assert all(r['true_label'] in ('absent', 'present') and r['pred_label'] in ('absent', 'present') for r in predictions)
    y = np.array([r['true_label'] == 'present' for r in predictions], dtype=int)
    pred = np.array([r['pred_label'] == 'present' for r in predictions], dtype=int)
    prob = np.array([float(r['prob_present']) for r in predictions])
    assert np.isfinite(prob).all() and ((prob >= 0) & (prob <= 1)).all()
    actual = {
        'accuracy': accuracy_score(y, pred),
        'balanced_accuracy': balanced_accuracy_score(y, pred),
        'log_loss': log_loss(y, np.c_[1 - prob, prob], labels=[0, 1]),
        'brier': brier_score_loss(y, prob),
        'auroc': roc_auc_score(y, prob),
    }
    for metric, value in actual.items():
        assert abs(float(row[metric]) - value) < 1e-10, (key, metric, row[metric], value)
print('PASS: all 24 observed CEBRA train/validation metric rows recomputed from predictions')

prefix = 'scripts.test_place195_v8b_v9_cebra.V8bV9CebraTest.'
names = ['scripts.test_place195_v7_v8_neural_experiments'] + [prefix + name for name in (
    'test_flatten_rows_preserves_trial_bins_and_labels',
    'test_time_loader_samples_only_within_trial_offset_one',
    'test_offset1_fast_path_matches_cebra_trial_expansion',
    'test_behavior_loader_samples_matching_labels',
    'test_saved_manifest_has_seven_session_components_per_pseudorow',
)]
suite = unittest.defaultTestLoader.loadTestsFromNames(names)
assert suite.countTestCases() == 8
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)
print('PASS: eight non-fitting tests. This checks implementation/artifact consistency, not biological validity.')
