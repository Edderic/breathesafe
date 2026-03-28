import sys
import types


fake_pymc = types.ModuleType("pymc")
fake_pymc.__version__ = "test"
sys.modules.setdefault("pymc", fake_pymc)

fake_pymc_sampling = types.ModuleType("pymc.sampling")
sys.modules.setdefault("pymc.sampling", fake_pymc_sampling)

fake_pymc_sampling_jax = types.ModuleType("pymc.sampling.jax")
fake_pymc_sampling_jax.sample_numpyro_nuts = lambda *args, **kwargs: None
sys.modules.setdefault("pymc.sampling.jax", fake_pymc_sampling_jax)

sys.modules.setdefault("arviz", types.ModuleType("arviz"))

fake_sklearn_pipeline = types.ModuleType("mask_recommender.sklearn_pipeline")
fake_sklearn_pipeline.build_sklearn_pipeline = lambda *args, **kwargs: None
sys.modules.setdefault("mask_recommender.sklearn_pipeline", fake_sklearn_pipeline)

from mask_recommender.training import train as train_module
from mask_recommender.training import train_sklearn


def test_training_export_url_defaults_to_internal_endpoint(monkeypatch):
    monkeypatch.delenv("BREATHESAFE_BASE_URL", raising=False)

    assert train_module.training_export_url() == "https://www.breathesafe.xyz/internal/facial_measurements_fit_tests.json"
    assert train_sklearn.training_export_url() == "https://www.breathesafe.xyz/internal/facial_measurements_fit_tests.json"


def test_training_export_headers_uses_internal_token(monkeypatch):
    monkeypatch.setenv("MASK_RECOMMENDER_INTERNAL_API_TOKEN", "internal-secret")

    expected = {"X-Breathesafe-Internal-Token": "internal-secret"}
    assert train_module.training_export_headers() == expected
    assert train_sklearn.training_export_headers() == expected


def test_training_export_headers_omits_header_without_token(monkeypatch):
    monkeypatch.delenv("MASK_RECOMMENDER_INTERNAL_API_TOKEN", raising=False)

    assert train_module.training_export_headers() == {}
    assert train_sklearn.training_export_headers() == {}
