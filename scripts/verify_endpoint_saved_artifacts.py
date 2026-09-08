"""Read-only endpoint delivery checks; no fitting, checkpoint loading or raw access.

Requires the saved baseline/study directories and the recorded research runtime.
Only hashes artifacts contained in those directories and recomputes prediction
metrics. Does not repeat original-split/source-assembly/scaler/reload checks.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss


def verify_hashes(root):
    manifest = json.loads((root / 'artifact_hashes.json').read_text())
    for relative, expected in manifest.items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError(f'Artifact escapes allowlisted root: {relative}')
        digest = hashlib.sha256()
        with path.open('rb') as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b''):
                digest.update(block)
        assert digest.hexdigest() == expected, path
    return len(manifest)


def scores(y, pred, prob):
    values = {'accuracy': accuracy_score(y, pred),
              'balanced_accuracy': balanced_accuracy_score(y, pred),
              'macro_f1': f1_score(y, pred, average='macro', zero_division=0)}  # pyright: ignore[reportArgumentType]  # sklearn supports 0; local stub incorrectly says str.
    if prob.size:
        assert np.isfinite(prob).all() and (prob >= 0).all()
        np.testing.assert_allclose(prob.sum(axis=1), 1, atol=1e-6)
        values['log_loss'] = log_loss(y, prob, labels=np.unique(y))
    return values


def check(baseline, study):
    pairs = np.array([(s, g) for s in range(1, 7) for g in range(1, 7) if s != g])
    baseline_hashes = verify_hashes(baseline)
    with (baseline / 'metrics.csv').open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 690
    for row in rows:
        stage = 'observed' if int(row['null_id']) == -1 else f"null_{int(row['null_id']):03d}"
        file = baseline / stage / f"seed{row['seed']}" / row['representation'] / 'decoder.npz'
        assert file.resolve().is_relative_to(baseline.resolve())
        with np.load(file, allow_pickle=False) as data:
            y, prob = data[f"y_{row['split']}"], data[f"prob_{row['split']}"]
            pred = data['classes'][prob.argmax(axis=1)]
        values = {'joint_' + k: v for k, v in scores(y, pred, prob).items()}
        values.update(start_accuracy=accuracy_score(pairs[y, 0], pairs[pred, 0]),
                      goal_accuracy=accuracy_score(pairs[y, 1], pairs[pred, 1]))
        for key, value in values.items():
            assert abs(float(row[key]) - value) < 1e-10, f'{file}: {key}'
    phases = sorted(study.glob('[0-9][0-9]-*/manifest.json'))
    assert len(phases) == 7
    count = hashes = 0
    for manifest in phases:
        assert json.loads(manifest.read_text())['status'] == 'completed'
        phase = manifest.parent
        hashes += verify_hashes(phase)
        for file in sorted(phase.rglob('*_metrics.json')):
            row = json.loads(file.read_text())
            pred_file = file.with_name(file.name.replace('_metrics.json', '_predictions.npz'))
            with np.load(pred_file, allow_pickle=False) as data:
                y, pred, prob = data['y'], data['pred'], data['prob']
            values = scores(y, pred, prob)
            if prob.size:
                np.testing.assert_array_equal(np.unique(y)[prob.argmax(axis=1)], pred)
            else:
                assert row['log_loss'] is None and row['decoder'] == 'svm'
            if row['target'] == 'joint':
                values.update(start_accuracy=accuracy_score(pairs[y, 0], pairs[pred, 0]),
                              goal_accuracy=accuracy_score(pairs[y, 1], pairs[pred, 1]))
            assert row['n_rows'] == len(y)
            for key, value in values.items():
                assert abs(float(row[key]) - value) < 1e-10, f'{file}: {key}'
            count += 1
    receipt = json.loads((study / 'validation.json').read_text())
    assert receipt['status'] == 'passed'
    assert count == receipt['metrics'] == 1618
    assert hashes == receipt['artifact_hashes']
    return {'status': 'passed', 'baseline_hashes': baseline_hashes,
            'baseline_metrics': len(rows), 'study_hashes': hashes, 'study_metrics': count,
            'new_fits': 0, 'checkpoint_loads': 0, 'raw_or_original_split_access': False,
            'scope': 'Saved artifact hashes and prediction metrics only; not biological validity'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('study', type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error('Do not use Python -O; verification requires assertions')
    print(json.dumps(check(args.baseline, args.study), indent=2))
