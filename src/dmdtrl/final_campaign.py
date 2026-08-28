from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any

import numpy as np

FINAL_TEST_SEED_MIN = 20_000
STRESS_TEST_SEED_MIN = 30_000
PPO_AGGREGATE_POLICY = "PPO_TRAINING_SEED_MEAN"
PRIMARY_FIXED_BASELINE = "WEIGHTED_COMPOSITE"
PRIMARY_METRIC = "weighted_tardiness"
AGGREGATE_METRICS = (
    "completed_jobs",
    "makespan",
    "mean_waiting_time",
    "total_tardiness",
    "weighted_tardiness",
    "total_setup_time",
    "total_repair_time",
    "on_time_rate",
    "utilization",
    "mean_quality_risk",
    "mean_decision_time_ms",
)
COMPARISON_METRICS = (
    "weighted_tardiness",
    "mean_waiting_time",
    "total_setup_time",
    "on_time_rate",
    "utilization",
    "makespan",
    "mean_decision_time_ms",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_design(
    design: dict[str, Any],
    ppo_freeze: dict[str, Any],
    cpsat_freeze: dict[str, Any],
) -> dict[str, Any]:
    if design.get("status") != "predeclared_final_test_design":
        raise ValueError("final campaign design must be predeclared")
    if design.get("primary_metric") != PRIMARY_METRIC:
        raise ValueError(f"primary metric must remain {PRIMARY_METRIC}")
    if design.get("primary_fixed_baseline") != PRIMARY_FIXED_BASELINE:
        raise ValueError(f"primary fixed baseline must remain {PRIMARY_FIXED_BASELINE}")
    if ppo_freeze.get("status") != "validation_complete_representative_frozen":
        raise ValueError("PPO validation outcome must be frozen before final testing")
    if cpsat_freeze.get("status") != "frozen_for_final_evaluation":
        raise ValueError("CP-SAT operating point must be frozen before final testing")

    nominal = design.get("nominal")
    stress = design.get("stress")
    if not isinstance(nominal, dict) or not isinstance(stress, dict):
        raise ValueError("nominal and stress final-test designs must be objects")
    nominal_start = int(nominal.get("seed_start", -1))
    nominal_count = int(nominal.get("seed_count", 0))
    stress_start = int(stress.get("seed_start", -1))
    stress_count = int(stress.get("seed_count", 0))
    if nominal_count <= 0 or stress_count <= 0:
        raise ValueError("final-test seed counts must be positive")
    if nominal_start < FINAL_TEST_SEED_MIN:
        raise ValueError("nominal final-test seeds must start at or above 20000")
    if nominal_start + nominal_count > STRESS_TEST_SEED_MIN:
        raise ValueError("nominal final-test seeds must remain below 30000")
    if stress_start < STRESS_TEST_SEED_MIN:
        raise ValueError("stress final-test seeds must start at or above 30000")

    scenarios = [str(name) for name in stress.get("scenarios", [])]
    if not scenarios:
        raise ValueError("at least one stress scenario is required")
    if len(set(scenarios)) != len(scenarios):
        raise ValueError("stress scenarios must be unique")
    if "nominal" in scenarios:
        raise ValueError("nominal must use the dedicated nominal final-test seed range")

    freeze_seeds = [int(member["training_seed"]) for member in ppo_freeze.get("members", [])]
    declared_seeds = [int(seed) for seed in design.get("ppo_training_seeds", [])]
    if declared_seeds != freeze_seeds:
        raise ValueError("final campaign PPO training seeds must exactly match the frozen campaign")
    if len(declared_seeds) < 3:
        raise ValueError("final PPO comparison requires at least three frozen training seeds")

    cpsat = design.get("cpsat")
    if not isinstance(cpsat, dict):
        raise ValueError("cpsat final-test configuration must be an object")
    if int(cpsat.get("horizon", -1)) != int(cpsat_freeze["cpsat_horizon"]):
        raise ValueError("final CP-SAT horizon does not match frozen operating point")
    if not math.isclose(
        float(cpsat.get("solver_seconds", -1.0)),
        float(cpsat_freeze["solver_seconds"]),
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise ValueError("final CP-SAT solve budget does not match frozen operating point")

    if int(design.get("bootstrap", 0)) <= 0 or int(design.get("permutations", 0)) <= 0:
        raise ValueError("bootstrap and permutation counts must be positive")

    return {
        **design,
        "ppo_training_seeds": declared_seeds,
        "nominal": {**nominal, "seed_start": nominal_start, "seed_count": nominal_count},
        "stress": {
            **stress,
            "seed_start": stress_start,
            "seed_count": stress_count,
            "scenarios": scenarios,
        },
    }


def verify_frozen_models(models_root: Path, ppo_freeze: dict[str, Any]) -> dict[int, Path]:
    verified: dict[int, Path] = {}
    for member in ppo_freeze.get("members", []):
        seed = int(member["training_seed"])
        member_dir = models_root / f"seed_{seed}"
        model_path = member_dir / "ppo_dispatcher.zip"
        manifest_path = member_dir / "training_manifest.json"
        if not model_path.exists() or not manifest_path.exists():
            raise ValueError(f"missing frozen PPO artifacts for training seed {seed}")
        model_digest = sha256_file(model_path)
        manifest_digest = sha256_file(manifest_path)
        if model_digest != str(member["model_sha256"]):
            raise ValueError(f"PPO model hash mismatch for training seed {seed}")
        if manifest_digest != str(member["training_manifest_sha256"]):
            raise ValueError(f"PPO training-manifest hash mismatch for training seed {seed}")
        manifest = read_json(manifest_path)
        if int(manifest.get("training_seed", -1)) != seed:
            raise ValueError(f"training manifest seed mismatch for frozen model {seed}")
        verified[seed] = model_path
    if not verified:
        raise ValueError("PPO freeze contains no members")
    return verified


def ppo_policy_name(training_seed: int) -> str:
    return f"PPO_TRAIN_{training_seed}"


def average_ppo_by_environment_seed(
    rows: list[dict[str, Any]],
    training_seeds: list[int],
    *,
    scenario: str,
) -> list[dict[str, Any]]:
    expected_names = {ppo_policy_name(seed) for seed in training_seeds}
    grouped: dict[int, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        policy = str(row.get("policy"))
        if policy not in expected_names:
            continue
        env_seed = int(row["seed"])
        if policy in grouped[env_seed]:
            raise ValueError(f"duplicate PPO row for {policy} and environment seed {env_seed}")
        grouped[env_seed][policy] = row
    if not grouped:
        raise ValueError(f"no PPO rows found for scenario {scenario}")

    result: list[dict[str, Any]] = []
    for env_seed in sorted(grouped):
        members = grouped[env_seed]
        if set(members) != expected_names:
            missing = sorted(expected_names - set(members))
            raise ValueError(
                f"incomplete PPO training-seed panel for scenario {scenario}, "
                f"environment seed {env_seed}: missing {missing}"
            )
        averaged: dict[str, Any] = {
            "scenario": scenario,
            "policy": PPO_AGGREGATE_POLICY,
            "controller_class": "PPO",
            "analysis_role": "training_seed_average",
            "training_seed_count": len(training_seeds),
            "seed": env_seed,
        }
        for metric in AGGREGATE_METRICS:
            values = [float(members[name][metric]) for name in sorted(expected_names)]
            if not all(math.isfinite(value) for value in values):
                raise ValueError(f"non-finite PPO metric {metric} for environment seed {env_seed}")
            averaged[metric] = float(mean(values))
        result.append(averaged)
    return result


def ppo_training_seed_dispersion(
    rows: list[dict[str, Any]],
    training_seeds: list[int],
    *,
    scenario: str,
) -> dict[str, Any]:
    by_policy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        policy = str(row.get("policy"))
        if policy.startswith("PPO_TRAIN_"):
            by_policy[policy].append(row)
    expected_names = [ppo_policy_name(seed) for seed in training_seeds]
    if set(by_policy) != set(expected_names):
        raise ValueError(f"PPO policy set for scenario {scenario} does not match frozen training seeds")
    wtt_means = [
        float(mean(float(row[PRIMARY_METRIC]) for row in by_policy[name])) for name in expected_names
    ]
    latency_means = [
        float(mean(float(row["mean_decision_time_ms"]) for row in by_policy[name]))
        for name in expected_names
    ]
    return {
        "scenario": scenario,
        "n_training_seeds": len(training_seeds),
        "ppo_wtt_training_seed_mean": float(mean(wtt_means)),
        "ppo_wtt_training_seed_median": float(median(wtt_means)),
        "ppo_wtt_training_seed_std": float(stdev(wtt_means)),
        "ppo_wtt_training_seed_min": float(min(wtt_means)),
        "ppo_wtt_training_seed_max": float(max(wtt_means)),
        "ppo_decision_time_ms_training_seed_mean": float(mean(latency_means)),
    }


def hierarchical_ppo_improvement_ci(
    rows: list[dict[str, Any]],
    training_seeds: list[int],
    *,
    baseline: str,
    metric: str = PRIMARY_METRIC,
    direction: str = "min",
    n_bootstrap: int = 5_000,
    seed: int = 123_456,
) -> dict[str, float | int]:
    """Bootstrap both PPO training seeds and environment seeds for the primary effect."""
    if direction not in {"min", "max"}:
        raise ValueError("direction must be 'min' or 'max'")
    if n_bootstrap <= 0:
        raise ValueError("n_bootstrap must be positive")

    ppo_names = [ppo_policy_name(training_seed) for training_seed in training_seeds]
    relevant = {*ppo_names, baseline}
    by_policy: dict[str, dict[int, float]] = defaultdict(dict)
    for row in rows:
        policy = str(row.get("policy"))
        if policy in relevant:
            env_seed = int(row["seed"])
            if env_seed in by_policy[policy]:
                raise ValueError(f"duplicate row for {policy} and environment seed {env_seed}")
            value = float(row[metric])
            if not math.isfinite(value):
                raise ValueError(f"non-finite {metric} for {policy} seed {env_seed}")
            by_policy[policy][env_seed] = value

    if baseline not in by_policy:
        raise ValueError(f"baseline {baseline!r} is absent")
    env_seeds = sorted(by_policy[baseline])
    if not env_seeds:
        raise ValueError("hierarchical comparison requires environment seeds")
    for policy in ppo_names:
        if sorted(by_policy.get(policy, {})) != env_seeds:
            raise ValueError(f"PPO panel for {policy} is not paired with baseline {baseline}")

    baseline_values = np.asarray([by_policy[baseline][s] for s in env_seeds], dtype=float)
    ppo_matrix = np.asarray(
        [[by_policy[policy][s] for s in env_seeds] for policy in ppo_names], dtype=float
    )
    if direction == "min":
        point = float(np.mean(baseline_values) - np.mean(ppo_matrix))
    else:
        point = float(np.mean(ppo_matrix) - np.mean(baseline_values))

    rng = np.random.default_rng(seed)
    boot = np.empty(n_bootstrap, dtype=float)
    offset = 0
    chunk_size = min(500, n_bootstrap)
    while offset < n_bootstrap:
        count = min(chunk_size, n_bootstrap - offset)
        train_idx = rng.integers(0, len(training_seeds), size=(count, len(training_seeds)))
        env_idx = rng.integers(0, len(env_seeds), size=(count, len(env_seeds)))
        baseline_means = np.mean(baseline_values[env_idx], axis=1)
        sampled_ppo = ppo_matrix[train_idx[:, :, None], env_idx[:, None, :]]
        ppo_means = np.mean(sampled_ppo, axis=(1, 2))
        if direction == "min":
            boot[offset : offset + count] = baseline_means - ppo_means
        else:
            boot[offset : offset + count] = ppo_means - baseline_means
        offset += count
    ci_low, ci_high = np.quantile(boot, [0.025, 0.975])
    return {
        "hierarchical_mean_improvement": point,
        "hierarchical_ci_low": float(ci_low),
        "hierarchical_ci_high": float(ci_high),
        "hierarchical_training_seeds": len(training_seeds),
        "hierarchical_environment_seeds": len(env_seeds),
    }


def holm_adjust(p_values: list[float]) -> list[float]:
    if not p_values:
        return []
    if any(not 0.0 <= float(value) <= 1.0 for value in p_values):
        raise ValueError("p-values must be in [0, 1]")
    order = sorted(range(len(p_values)), key=lambda index: p_values[index])
    adjusted = [0.0] * len(p_values)
    running = 0.0
    total = len(p_values)
    for rank, index in enumerate(order):
        candidate = min(1.0, (total - rank) * float(p_values[index]))
        running = max(running, candidate)
        adjusted[index] = running
    return adjusted


def apply_primary_holm(rows: list[dict[str, Any]]) -> None:
    family = [
        row
        for row in rows
        if row.get("analysis") == "ppo_training_seed_average_vs_primary_baseline"
        and row.get("metric") == PRIMARY_METRIC
    ]
    adjusted = holm_adjust([float(row["p_value"]) for row in family])
    for row, value in zip(family, adjusted, strict=True):
        row["primary_hypothesis"] = True
        row["p_value_holm"] = value
    for row in rows:
        row.setdefault("primary_hypothesis", False)
        row.setdefault("p_value_holm", "")


def write_csv(rows: list[dict[str, Any]], output: Path) -> None:
    if not rows:
        raise ValueError("cannot write an empty CSV")
    fields: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                fields.append(key)
                seen.add(key)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _annotate_policy_rows(
    rows: list[dict[str, Any]],
    *,
    scenario: str,
    training_seeds: list[int],
) -> list[dict[str, Any]]:
    ppo_names = {ppo_policy_name(seed): seed for seed in training_seeds}
    annotated: list[dict[str, Any]] = []
    for row in rows:
        policy = str(row["policy"])
        if policy in ppo_names:
            annotated.append(
                {
                    "scenario": scenario,
                    "controller_class": "PPO",
                    "training_seed": ppo_names[policy],
                    **row,
                }
            )
        elif policy == "CP_SAT_RH":
            annotated.append({"scenario": scenario, "controller_class": "CP_SAT", **row})
        else:
            annotated.append({"scenario": scenario, "controller_class": "FIXED_RULE", **row})
    return annotated


def _scenario_comparisons(
    scenario_rows: list[dict[str, Any]],
    training_seeds: list[int],
    *,
    n_bootstrap: int,
    n_permutations: int,
    seed_offset: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    from dmdtrl import experiments
    from dmdtrl.dispatch import DispatchRule

    primary: list[dict[str, Any]] = []
    secondary: list[dict[str, Any]] = []
    scenario = str(scenario_rows[0]["scenario"])

    for baseline_index, baseline in enumerate(("CP_SAT_RH", PRIMARY_FIXED_BASELINE)):
        for metric_index, metric in enumerate(COMPARISON_METRICS):
            result = experiments.paired_comparison(
                scenario_rows,
                candidate=PPO_AGGREGATE_POLICY,
                baseline=baseline,
                metric=metric,
                n_bootstrap=n_bootstrap,
                n_permutations=n_permutations,
                seed=seed_offset + baseline_index * 100 + metric_index,
            )
            row = {
                "scenario": scenario,
                "analysis": "ppo_training_seed_average_vs_primary_baseline",
                **result,
            }
            if metric == PRIMARY_METRIC:
                row.update(
                    hierarchical_ppo_improvement_ci(
                        scenario_rows,
                        training_seeds,
                        baseline=baseline,
                        metric=metric,
                        direction="min",
                        n_bootstrap=n_bootstrap,
                        seed=seed_offset + 1_000 + baseline_index,
                    )
                )
            primary.append(row)

    primary.append(
        {
            "scenario": scenario,
            "analysis": "cpsat_vs_primary_fixed_baseline",
            **experiments.paired_comparison(
                scenario_rows,
                candidate="CP_SAT_RH",
                baseline=PRIMARY_FIXED_BASELINE,
                metric=PRIMARY_METRIC,
                n_bootstrap=n_bootstrap,
                n_permutations=n_permutations,
                seed=seed_offset + 900,
            ),
        }
    )

    all_baselines = [rule.name for rule in DispatchRule] + ["CP_SAT_RH"]
    for model_index, training_seed in enumerate(training_seeds):
        candidate = ppo_policy_name(training_seed)
        comparisons = experiments.compare_candidate_to_baselines(
            scenario_rows,
            candidate=candidate,
            baselines=all_baselines,
            metrics=(PRIMARY_METRIC,),
            n_bootstrap=n_bootstrap,
            n_permutations=n_permutations,
            seed=seed_offset + 2_000 + model_index * 1_000,
        )
        for result in comparisons:
            secondary.append(
                {
                    "scenario": scenario,
                    "analysis": "individual_ppo_model_wtt",
                    "training_seed": training_seed,
                    **result,
                }
            )
    return primary, secondary


def run_campaign(
    design: dict[str, Any],
    ppo_freeze: dict[str, Any],
    cpsat_freeze: dict[str, Any],
    models_root: Path,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    from dmdtrl import experiments
    from dmdtrl.env import EnvConfig
    from dmdtrl.or_experiments import evaluate_cpsat_policy
    from dmdtrl.or_policy import CPSATConfig, RollingHorizonCPSATPolicy
    from dmdtrl.policies import load_ppo_policy
    from dmdtrl.research import fixed_policies
    from dmdtrl.scenarios import SCENARIO_REGISTRY

    verified_models = verify_frozen_models(models_root, ppo_freeze)
    training_seeds = design["ppo_training_seeds"]
    policies = list(fixed_policies())
    for training_seed in training_seeds:
        policies.append(
            load_ppo_policy(
                verified_models[training_seed],
                policy_name=ppo_policy_name(training_seed),
            )
        )
    cpsat = RollingHorizonCPSATPolicy(
        CPSATConfig(
            max_jobs=int(cpsat_freeze["cpsat_horizon"]),
            time_limit_s=float(cpsat_freeze["solver_seconds"]),
        )
    )

    plans: list[tuple[str, list[int], Any]] = [
        (
            "nominal",
            list(
                range(
                    int(design["nominal"]["seed_start"]),
                    int(design["nominal"]["seed_start"])
                    + int(design["nominal"]["seed_count"]),
                )
            ),
            EnvConfig(),
        )
    ]
    for scenario_name in design["stress"]["scenarios"]:
        if scenario_name not in SCENARIO_REGISTRY:
            raise ValueError(f"unknown frozen stress scenario: {scenario_name}")
        plans.append(
            (
                scenario_name,
                list(
                    range(
                        int(design["stress"]["seed_start"]),
                        int(design["stress"]["seed_start"])
                        + int(design["stress"]["seed_count"]),
                    )
                ),
                SCENARIO_REGISTRY[scenario_name].apply(EnvConfig()),
            )
        )

    raw_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    dispersion_rows: list[dict[str, Any]] = []
    primary_comparisons: list[dict[str, Any]] = []
    per_model_comparisons: list[dict[str, Any]] = []

    for scenario_index, (scenario, seeds, env_config) in enumerate(plans):
        executable_rows = experiments.evaluate_policies(policies, seeds, env_config)
        executable_rows.extend(evaluate_cpsat_policy(cpsat, seeds, env_config))
        annotated = _annotate_policy_rows(
            executable_rows,
            scenario=scenario,
            training_seeds=training_seeds,
        )
        aggregate_rows = average_ppo_by_environment_seed(
            annotated,
            training_seeds,
            scenario=scenario,
        )
        scenario_rows = annotated + aggregate_rows
        raw_rows.extend(scenario_rows)

        summaries = experiments.summarize_runs(
            scenario_rows,
            n_bootstrap=int(design["bootstrap"]),
            seed=70_000 + scenario_index * 10_000,
        )
        for summary in summaries:
            summary_rows.append({"scenario": scenario, **summary})
        dispersion_rows.append(
            ppo_training_seed_dispersion(annotated, training_seeds, scenario=scenario)
        )
        primary, secondary = _scenario_comparisons(
            scenario_rows,
            training_seeds,
            n_bootstrap=int(design["bootstrap"]),
            n_permutations=int(design["permutations"]),
            seed_offset=80_000 + scenario_index * 20_000,
        )
        primary_comparisons.extend(primary)
        per_model_comparisons.extend(secondary)

    apply_primary_holm(primary_comparisons)
    return raw_rows, summary_rows, dispersion_rows, primary_comparisons, per_model_comparisons


def build_manifest(
    design: dict[str, Any],
    ppo_freeze: dict[str, Any],
    cpsat_freeze: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "status": "final_test_complete",
        "git_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "primary_metric": PRIMARY_METRIC,
        "primary_fixed_baseline": PRIMARY_FIXED_BASELINE,
        "primary_ppo_analysis_unit": (
            "For each environment seed, average the KPI across the five frozen PPO training-seed "
            "realizations, then perform paired inference across environment seeds. Individual PPO "
            "models are also reported separately. The 5 x N PPO rows are not treated as independent."
        ),
        "primary_uncertainty": (
            "Weighted-tardiness primary comparisons additionally use a hierarchical bootstrap that "
            "resamples both PPO training seeds and environment seeds. Holm correction is applied to "
            "the twenty PPO-vs-primary-baseline WTT tests across ten scenarios."
        ),
        "design": design,
        "ppo_freeze_source": {
            "source_workflow_run_id": ppo_freeze.get("source_workflow_run_id"),
            "representative_training_seed": ppo_freeze.get("representative_model", {}).get(
                "training_seed"
            ),
            "members": [
                {
                    "training_seed": member["training_seed"],
                    "model_sha256": member["model_sha256"],
                }
                for member in ppo_freeze.get("members", [])
            ],
        },
        "cpsat_freeze_source": {
            "horizon": cpsat_freeze["cpsat_horizon"],
            "solver_seconds": cpsat_freeze["solver_seconds"],
            "artifact_sha256": cpsat_freeze.get("provenance", {}).get("artifact_sha256"),
        },
        "no_final_test_tuning": True,
    }


def main() -> None:  # pragma: no cover - exercised by GitHub Actions final campaign
    parser = argparse.ArgumentParser(description="Run the frozen multi-controller final campaign.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--ppo-freeze", type=Path, required=True)
    parser.add_argument("--cpsat-freeze", type=Path, required=True)
    parser.add_argument("--models-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    try:
        ppo_freeze = read_json(args.ppo_freeze)
        cpsat_freeze = read_json(args.cpsat_freeze)
        design = validate_design(read_json(args.config), ppo_freeze, cpsat_freeze)
        outputs = run_campaign(design, ppo_freeze, cpsat_freeze, args.models_root)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        parser.error(str(exc))

    raw, summaries, dispersion, primary, per_model = outputs
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(raw, args.output_dir / "final_runs.csv")
    write_csv(summaries, args.output_dir / "final_policy_summary.csv")
    write_csv(dispersion, args.output_dir / "ppo_training_seed_dispersion.csv")
    write_csv(primary, args.output_dir / "primary_comparisons.csv")
    write_csv(per_model, args.output_dir / "ppo_per_model_comparisons.csv")
    (args.output_dir / "final_campaign_manifest.json").write_text(
        json.dumps(build_manifest(design, ppo_freeze, cpsat_freeze), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("Final weighted-tardiness leaders by scenario (descriptive only):")
    for scenario in ["nominal", *design["stress"]["scenarios"]]:
        candidates = [
            row
            for row in summaries
            if row["scenario"] == scenario
            and row["policy"] in {PPO_AGGREGATE_POLICY, "CP_SAT_RH", PRIMARY_FIXED_BASELINE}
        ]
        leader = min(candidates, key=lambda row: float(row["weighted_tardiness_mean"]))
        print(
            f"  {scenario:<20} {leader['policy']:<24} "
            f"WTT={float(leader['weighted_tardiness_mean']):.3f}"
        )


if __name__ == "__main__":
    main()
