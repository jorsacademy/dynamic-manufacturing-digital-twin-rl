from __future__ import annotations

from pathlib import Path

import pytest

from dmdtrl.fjsp_env import FJSPEnvConfig
from dmdtrl.fjsp_generator import FJSPGeneratorConfig
from dmdtrl.fjsp_hh_train import (
    FJSPHyperHeuristicPPOConfig,
    build_training_manifest,
    model_archive_path,
    validate_operator_contract,
)
from dmdtrl.fjsp_hyperheuristic_env import FlexibleJobShopHyperHeuristicEnv
from dmdtrl.fjsp_operators import FJSPOperator


def _env_config() -> FJSPEnvConfig:
    return FJSPEnvConfig(
        generator=FJSPGeneratorConfig(
            n_jobs=5,
            n_machines=3,
            n_families=3,
            operations_min=2,
            operations_max=3,
            eligible_machines_min=1,
            eligible_machines_max=2,
        ),
        default_setup_time=0.5,
    )


def test_training_config_validation_and_archive_path() -> None:
    config = FJSPHyperHeuristicPPOConfig(total_timesteps=1_000, n_steps=256, batch_size=64)
    config.validate()
    assert model_archive_path("model") == Path("model.zip")
    assert model_archive_path("model.zip") == Path("model.zip")

    with pytest.raises(ValueError, match="divisible"):
        FJSPHyperHeuristicPPOConfig(n_steps=250, batch_size=64).validate()


def test_operator_contract_completes_episode() -> None:
    env = FlexibleJobShopHyperHeuristicEnv(_env_config())
    contract = validate_operator_contract(env, seed=40030)
    assert contract["operator_action_count"] == len(FJSPOperator)
    assert contract["validated_decisions"] > 0


def test_training_manifest_declares_action_abstraction_and_seed_embargo() -> None:
    training = FJSPHyperHeuristicPPOConfig(
        total_timesteps=4_096,
        seed=801,
        n_steps=256,
        batch_size=64,
    )
    manifest = build_training_manifest(
        training_config=training,
        env_config=_env_config(),
        model_path=Path("artifacts/fjsp_hh_ppo.zip"),
        training_seconds=1.25,
        operator_contract={
            "validated_decisions": 12,
            "operator_action_count": len(FJSPOperator),
        },
    )

    assert manifest["algorithm"] == "PPO"
    assert manifest["controller"] == "FJSP_HYPER_HEURISTIC"
    assert manifest["operator_contract"]["operator_action_count"] == len(FJSPOperator)
    assert len(manifest["operator_names"]) == len(FJSPOperator)
    assert manifest["phase5_seed_policy"]["development_evaluation"] == "40000-40999"
    assert "embargoed" in manifest["phase5_seed_policy"]["final"]
