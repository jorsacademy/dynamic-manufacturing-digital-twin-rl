from __future__ import annotations

import json
from pathlib import Path

import pytest

from dmdtrl.fjsp_final import (
    CPSAT_POLICY,
    FINAL_SEED_END,
    FINAL_SEED_START,
    final_seeds,
    validate_final_design,
    validate_final_rows,
)
from dmdtrl.fjsp_operators import OPERATOR_NAMES


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_final_design_matches_frozen_phase5_boundaries() -> None:
    config = _load("configs/fjsp_final_baseline_test.json")
    environment = _load("configs/fjsp_hh_validation_design.json")
    cpsat = _load("configs/fjsp_cpsat_validation_freeze.json")
    decision = _load("configs/fjsp_hh_validation_decision.json")

    validate_final_design(config, environment, cpsat, decision)
    assert final_seeds(config) == list(range(FINAL_SEED_START, FINAL_SEED_END + 1))
    assert config["policies"] == [*OPERATOR_NAMES, CPSAT_POLICY]
    assert config["authorization"]["retuning_after_final_access"] is False
    assert decision["decision"]["promote_to_phase5_final"] is False


def test_final_seed_range_cannot_drift() -> None:
    config = _load("configs/fjsp_final_baseline_test.json")
    config["seed_start"] = 41999
    with pytest.raises(ValueError, match="seed range"):
        final_seeds(config)


def test_rejected_rl_cannot_be_inserted_into_final_panel() -> None:
    config = _load("configs/fjsp_final_baseline_test.json")
    environment = _load("configs/fjsp_hh_validation_design.json")
    cpsat = _load("configs/fjsp_cpsat_validation_freeze.json")
    decision = _load("configs/fjsp_hh_validation_decision.json")
    config["policies"].append("PPO_HYPER_HEURISTIC")
    with pytest.raises(ValueError, match="policy panel drifted"):
        validate_final_design(config, environment, cpsat, decision)


def test_synthetic_final_rows_require_complete_common_instance_panel() -> None:
    config = _load("configs/fjsp_final_baseline_test.json")
    rows = []
    for seed in range(FINAL_SEED_START, FINAL_SEED_END + 1):
        fingerprint = f"instance-{seed}"
        for policy in config["policies"]:
            rows.append(
                {
                    "seed": seed,
                    "seed_regime": "final",
                    "instance_sha256": fingerprint,
                    "policy": policy,
                }
            )
    validate_final_rows(config, rows)

    rows[-1]["instance_sha256"] = "mismatch"
    with pytest.raises(ValueError, match="canonical instance"):
        validate_final_rows(config, rows)
