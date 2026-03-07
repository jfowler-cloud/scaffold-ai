"""Tests for shared config module."""
import importlib

import shared.config as cfg


def test_app_config_defaults():
    importlib.reload(cfg)
    assert cfg.app_config.deployment_tier == "testing"
    assert cfg.app_config.aws_region == "us-east-1"


def test_model_id_defaults_to_haiku():
    importlib.reload(cfg)
    assert "haiku" in cfg.app_config.model_id.lower()


def test_model_id_override(monkeypatch):
    monkeypatch.setenv("BEDROCK_MODEL_ID", "custom-model")
    importlib.reload(cfg)
    assert cfg.AppConfig().model_id == "custom-model"
