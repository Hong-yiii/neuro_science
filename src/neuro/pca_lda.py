"""Train-only sklearn PCA and SVD-LDA classification; no CEBRA/torch dependency.

Neural tensors use row × unit × bin. Raw features are unit-major; pooled-bin
PCA is fitted across training row/bin vectors and produces time-major features.
LDA here is a supervised classifier, not an unsupervised latent projection.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


def neural_tensor(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values)
    if (
        arr.ndim != 3
        or any(size == 0 for size in arr.shape)
        or not np.isfinite(arr).all()
        or np.iscomplexobj(arr)
    ):
        raise ValueError("finite nonempty row × unit × bin tensor required")
    return arr


def _pooled(values: np.ndarray) -> np.ndarray:
    arr = neural_tensor(values)
    return arr.transpose(0, 2, 1).reshape(-1, arr.shape[1])


def raw_features(values: np.ndarray) -> np.ndarray:
    arr = neural_tensor(values)
    return arr.reshape(arr.shape[0], -1).astype(np.float32)


@dataclass(frozen=True)
class Standardizer:
    scaler: StandardScaler
    shape: tuple[int, int]

    def transform(self, values: np.ndarray) -> np.ndarray:
        arr = neural_tensor(values)
        if arr.shape[1:] != self.shape:
            raise ValueError("unit/bin shape differs from training")
        flat = np.asarray(self.scaler.transform(_pooled(arr)), dtype=np.float32)
        if not np.isfinite(flat).all():
            raise ValueError("nonfinite standardized values")
        return flat.reshape(arr.shape[0], arr.shape[2], arr.shape[1]).transpose(0, 2, 1)


def fit_standardizer(train: np.ndarray) -> Standardizer:
    arr = neural_tensor(train)
    with threadpool_limits(limits=2):
        scaler = StandardScaler().fit(_pooled(arr))
    return Standardizer(scaler, arr.shape[1:])


@dataclass(frozen=True)
class PCAFit:
    standardizer: Standardizer
    pca: PCA
    output_components: int

    def transform(self, values: np.ndarray) -> np.ndarray:
        arr = self.standardizer.transform(values)
        with threadpool_limits(limits=2):
            z = self.pca.transform(_pooled(arr)).astype(np.float32)
        if not np.isfinite(z).all():
            raise ValueError("nonfinite PCA transform")
        # Legacy endpoint padding is opt-in, never an implicit dimension policy.
        z = np.pad(z, ((0, 0), (0, self.output_components - z.shape[1])))
        return z.reshape(arr.shape[0], arr.shape[2], self.output_components).reshape(
            arr.shape[0], -1
        )


def fit_pca(
    train: np.ndarray, *, n_components: int, pad_to: int | None = None
) -> PCAFit:
    standardizer = fit_standardizer(train)
    pooled = _pooled(standardizer.transform(train))
    if (
        isinstance(n_components, bool)
        or not isinstance(n_components, int)
        or not 1 <= n_components <= min(pooled.shape)
    ):
        raise ValueError("n_components exceeds training row/bin or unit support")
    output_components = n_components if pad_to is None else pad_to
    if (
        isinstance(output_components, bool)
        or not isinstance(output_components, int)
        or output_components < n_components
    ):
        raise ValueError("pad_to must be an integer >= n_components")
    if not np.any(pooled):
        raise ValueError("requested PCA components exceed numerical training rank")
    with threadpool_limits(limits=2):
        pca = PCA(n_components=n_components, svd_solver="full", whiten=False).fit(
            pooled
        )
    singular = np.asarray(pca.singular_values_)
    tolerance = max(pooled.shape) * np.finfo(singular.dtype).eps * singular[0]
    if np.count_nonzero(singular > tolerance) < n_components:
        raise ValueError("requested PCA components exceed numerical training rank")
    return PCAFit(standardizer, pca, output_components)


def feature_matrix(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values)
    if (
        arr.ndim != 2
        or any(size == 0 for size in arr.shape)
        or not np.isfinite(arr).all()
        or np.iscomplexobj(arr)
    ):
        raise ValueError("finite nonempty row × feature matrix required")
    return arr


def fit_lda(train_features: np.ndarray, train_targets: np.ndarray):
    """Return sklearn Pipeline(StandardScaler, SVD-LDA); call predict[_proba] on eval.

    Scaling is per flattened readout feature, distinct from pooled-bin encoder/PCA
    normalization. All classes need >=2 training rows; synthetic reuse is not n.
    """
    features = feature_matrix(train_features)
    labels = np.asarray(train_targets)
    if labels.ndim != 1 or len(labels) != len(features):
        raise ValueError("target/feature row mismatch")
    classes, counts = np.unique(labels, return_counts=True)
    if len(classes) < 2 or np.any(counts < 2):
        raise ValueError("LDA requires >=2 classes, each with >=2 training rows")
    model = make_pipeline(StandardScaler(), LinearDiscriminantAnalysis(solver="svd"))
    with threadpool_limits(limits=2):
        model.fit(features, labels)
    return model
