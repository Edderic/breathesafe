import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


spec = importlib.util.spec_from_file_location(
    "scheduled_training_handler",
    Path(__file__).resolve().parents[1] / "training" / "lambda_function.py",
)
training = importlib.util.module_from_spec(spec)
spec.loader.exec_module(training)


@pytest.fixture
def trainer(monkeypatch):
    main = Mock()
    monkeypatch.setitem(sys.modules, "train", SimpleNamespace(main=main))
    monkeypatch.setattr(training.os, "makedirs", Mock())
    monkeypatch.setattr(training.os, "environ", {})
    return main


def test_scheduled_failure_raises(trainer):
    trainer.side_effect = RuntimeError("training failed")
    with pytest.raises(RuntimeError, match="training failed"):
        training.handler({"raise_on_error": True}, None)


def test_existing_callers_keep_error_response(trainer):
    trainer.side_effect = RuntimeError("training failed")
    assert training.handler({}, None)["statusCode"] == 500


def test_scheduled_success(trainer):
    trainer.return_value = {"model": "test"}
    response = training.handler({
        "raise_on_error": True,
        "environment": "production",
        "epochs": 200,
        "learning_rate": 0.01,
        "retrain_with_full": True,
    }, None)
    assert response["statusCode"] == 200
    trainer.assert_called_once_with([
        "--epochs", "200", "--learning-rate", "0.01",
        "--model-type", "custom_lr", "--retrain-with-full",
    ])
