"""Plot previously saved PCA results; no fit/transform or raw-data access."""
from pathlib import Path
import csv
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

root = Path('/home/hongyi-home-lab/neuro_science/outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906')
metrics_path = root / 'v8b-v9-cebra-final-20260905T224554Z/v8b/v8b_regularization_metrics.csv'
pca_dir = root / 'v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms'
with metrics_path.open(newline='') as f:
    rows = [r for r in csv.DictReader(f) if r['representation'] in ('pca_cellspace_3', 'pca_cellspace_8') and float(r['C']) == 1.0]
assert len(rows) == 12
lookup = {(int(r['pca_dim']), int(r['seed']), r['split']): r for r in rows}
assert len(lookup) == 12
fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.6))
colors = ['#236494', '#dc7c24', '#298568']
for seed in range(3):
    with np.load(pca_dir / f'train_only_pca_seed{seed}.npz', allow_pickle=False) as data:
        ratios = data['pca_cellspace_8_explained_variance_ratio']
        assert ratios.shape == (8,) and np.all(ratios >= 0)
        curve = 100 * np.cumsum(ratios)
        for dim in (3, 8):
            expected = 100 * float(lookup[(dim, seed, 'train')]['pca_explained_variance_sum'])
            assert abs(float(curve[dim-1]) - expected) < 0.0001
        axes[0].plot(range(1, 9), curve, 'o-', color=colors[seed], label=f'Assembly seed {seed}', alpha=0.85)
axes[0].set(xlabel='Number of principal components retained', ylabel='Training standardized-count variance retained (%)', ylim=(0, 100), xticks=range(1, 9), title='A. PCA compression—not route accuracy')
axes[0].axvline(3, color='#777', linestyle=':', linewidth=1)
axes[0].axvline(8, color='#777', linestyle=':', linewidth=1)
axes[0].annotate('3 PCs: about 21%', (3, 21.5), (1.3, 40), arrowprops={'arrowstyle': '->', 'color': '#555'})
axes[0].annotate('8 PCs: about 45%', (8, 45), (4.7, 68), arrowprops={'arrowstyle': '->', 'color': '#555'})
axes[0].legend(loc='upper left', fontsize=8)
keys = [(dim, seed) for dim in (3, 8) for seed in range(3)]
x = np.arange(6)
train = [100 * float(lookup[(d, s, 'train')]['balanced_accuracy']) for d, s in keys]
validation = [100 * float(lookup[(d, s, 'validation')]['balanced_accuracy']) for d, s in keys]
assert train == [100.0] * 6
axes[1].bar(x-0.18, train, 0.36, label='Training', color='#bcc9d3')
bars = axes[1].bar(x+0.18, validation, 0.36, label='Validation', color='#236494')
for bar, value in zip(bars, validation, strict=True):
    axes[1].text(bar.get_x()+bar.get_width()/2, value+1.4, f'{value:.1f}', ha='center', fontsize=9)
axes[1].axhline(50, linestyle='--', color='#444', linewidth=1, label='Balanced chance baseline')
axes[1].set(xticks=x, xticklabels=[f'PCA-{d}\nseed {s}' for d,s in keys], ylim=(0, 118), ylabel='Whole-cue balanced accuracy (%)', title='B. Logistic classifier: training vs validation')
axes[1].legend(loc='upper center', fontsize=8, ncol=2)
for ax in axes:
    ax.spines[['right', 'top']].set_visible(False)
    ax.grid(axis='y', alpha=0.15)
    ax.set_axisbelow(True)
fig.suptitle('Saved PCA + logistic regression results | 29 cells, ten 100 ms bins, C = 1', fontsize=13)
fig.text(0.5, 0.02, 'Same three assembly seeds; not independent biological replications. Plotted from saved results only—no retraining.', ha='center', fontsize=9)
fig.tight_layout(rect=(0, 0.055, 1, 0.95))
output = Path('/tmp/pi-teach/place195-pca-explained.png')
fig.savefig(output, dpi=170)
plt.close(fig)
html = Path('/tmp/pi-teach/place195-pca-explained.html')
html.write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; base-uri 'none'"><title>PCA: compression versus prediction</title><style>body{font:17px/1.6 system-ui;color:#173047;max-width:1400px;margin:30px auto;padding:0 24px}img{width:100%;height:auto}h1,h2{line-height:1.2}.note{background:#eef4fa;padding:14px}a{color:#126098}</style><h1>PCA: compression versus prediction</h1><p>Existing primary 29-cell results, not a new fit. Each cue bin is compressed to 3 or 8 components; ten projected bins become 30 or 80 logistic-regression inputs.</p><img src="place195-pca-explained.png" alt="Left: cumulative training variance retained rises from roughly eight percent with one component to forty-five percent with eight. Right: all training accuracies are one hundred percent, but validation is highly variable and usually near or below fifty percent."><p><strong>Left:</strong> PCA retains about 21% or 45% of standardized training-count variation. This is not percent of route information or brain activity explained.</p><p><strong>Right:</strong> the supervised readout fits its training pseudorows perfectly, but validation is unstable. Seeds resample the same source pools; they are not three biological replications.</p><div class="note">PCA has no saved epoch-by-epoch training-loss curve here: it is a matrix-decomposition fit. The C=1 logistic classifiers each recorded seven solver iterations in the V8b diagnostics. The original test is not pristine; these are development-validation results on label-conditioned pseudopopulations.</div><p><a href="place195-pca-explained.png">Open full-size figure</a> · <a href="place195-audit/v7-code.html#L354">PCA/readout code</a> · <a href="place195-pca-metrics.csv.txt">Saved training/validation metric table</a></p></html>''')
# Publish only the relevant saved metric rows, not the source observations.
with Path('/tmp/pi-teach/place195-pca-metrics.csv.txt').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
assert output.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
print(json.dumps({'figure': str(output), 'html': str(html), 'saved_metric_rows': len(rows), 'model_fits': 0}, indent=2))
