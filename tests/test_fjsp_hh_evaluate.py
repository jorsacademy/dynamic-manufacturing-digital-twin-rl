from __future__ import annotations

from collections import defaultdict

import numpy as np
import pytest

from dmdtrl.fjsp_generator import FJSPGeneratorConfig
from dmdtrl.fjsp_hh_evaluate import (
    FJSPHyperHeuristicDevelopmentConfig,
    evaluate_development_panel,
)
from dmdtrl.fjsp_operators import FJSPOperator
from dmdtrl.fjsp_optimization import FJSPCPSATConfig


class FixedOperatorModel:
    def __init__(self, operator: FJSPOperator) -> None:
        self.operator = operator

    def predict(self, observation, deterministic: bool = True):  # noqa: ANN001, ANN201
        assert deterministic
        assert observation is not None
        return np.asarray(int(self.operator)), None


def _generator() -> FJSPGeneratorConfig:
    return FJSPGeneratorConfig(
        n_jobs=5,
        n_machines=3,
        n_families=3,
        operations_min=2,
        operations_max=3,
        eligible_machines_min=1,
        eligible_machines_max=2,
    )


def test_development_seed_boundary_rejects_validation_access() -> None:
    FJSPHyperHeuristicDevelopmentConfig(seeds=2, seed_start=40000).validate()
    with pytest.raises(ValueError, match="41000"):
        FJSPHyperHeuristicDevelopmentConfig(seeds=2, seed_start=40999).validate()
    with pytest.raises(ValueError, match="40000"):
        FJSPHyperHeuristicDevelopmentConfig(seeds=1, seed_start=39999).validate()


def test_development_panel_uses_common_instances_for_all_controllers() -> None:
    evaluation = FJSPHyperHeuristicDevelopmentConfig(
        seeds=2,
        seed_start=40040,
        default_setup_time=0.5,
        bootstrap=100,
        permutations=100,
    )
    rows = evaluate_development_panel(
        evaluation,
        generator_config=_generator(),
        cpsat_config=FJSPCPSATConfig(job_horizon=4, solver_seconds=0.05),
        ppo_model=FixedOperatorModel(FJSPOperator.EARLIEST_DUE_DATE),
    )

    expected_policies = {operator.name for operator in FJSPOperator}
    expected_policies.update({"ROLLING_HORIZON_CPSAT", "PPO_HYPER_HEURISTIC"})
    assert len(rows) == 2 * len(expected_policies)
    assert {str(row["policy"]) for row in rows} == expected_policies
    assert {int(row["seed"]) for row in rows} == {40040, 40041}
    assert {str(row["seed_regime"]) for row in rows} == {"development"}

    by_seed: dict[int, list[dict[str, float | int | str]]] = defaultdict(list)
    for row in rows:
        by_seed[int(row["seed"])].append(row)
    for seed_rows in by_seed.values():
        assert len(seed_rows) == len(expected_policies)
        assert len({str(row["instance_sha256"]) for row in seed_rows}) == 1

    ppo_rows = [row for row in rows if row["policy"] == "PPO_HYPER_HEURISTIC"]
    assert all(float(row["unique_operator_fraction"]) > 0.0 for row in ppo_rows)
    assert all(float(row["mean_underlying_feasible_actions"]) >= 1.0 for row in ppo_rows)
