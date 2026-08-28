# ruff: noqa: I001
"""Distribution-shift experiment orchestration."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from dmdtrl import experiments
from dmdtrl.env import EnvConfig
from dmdtrl.policies import DispatchPolicy, load_ppo_policy
from dmdtrl.research import DEFAULT_COMPARISON_METRICS, fixed_policies
from dmdtrl.scenarios import Scenario, select_scenarios


def evaluate_scenarios(
    policies: list[DispatchPolicy],
    seeds: list[int],
    scenarios: list[Scenario],
    base_config: EnvConfig | None = None,
    *,
    n_bootstrap: int = 5_000,
) -> tuple[list[dict[str, float | int | str]], list[dict[str, float | int | str]]]:
    if not scenarios:
        raise ValueError("at least one stress scenario is required")
    raw_rows: list[dict[str, float | int | str]] = []
    summary_rows: list[dict[str, float | int | str]] = []
    base = base_config or EnvConfig()

    for scenario_index, scenario in enumerate(scenarios):
        config = scenario.apply(base)
        scenario_rows = experiments.evaluate_policies(policies, seeds, config)
        for row in scenario_rows:
            raw_rows.append({"scenario": scenario.name, **row})

        summaries = experiments.summarize_runs(
            scenario_rows,
            n_bootstrap=n_bootstrap,
            seed=30_000 + scenario_index * 10_000,
        )
        for row in summaries:
            summary_rows.append(
                {
                    "scenario": scenario.name,
                    "scenario_description": scenario.description,
                    **row,
                }
            )
    return raw_rows, summary_rows


def compare_candidate_across_scenarios(
    raw_rows: list[dict[str, float | int | str]],
    *,
    candidate: str,
    baselines: list[str],
    metrics: tuple[str, ...] = DEFAULT_COMPARISON_METRICS,
    n_bootstrap: int = 5_000,
    n_permutations: int = 10_000,
) -> list[dict[str, float | int | str]]:
    grouped: dict[str, list[dict[str, float | int | str]]] = defaultdict(list)
    for row in raw_rows:
        grouped[str(row["scenario"])].append(row)

    results: list[dict[str, float | int | str]] = []
    for scenario_index, (scenario, rows) in enumerate(sorted(grouped.items())):
        comparisons = experiments.compare_candidate_to_baselines(
            rows,
            candidate=candidate,
            baselines=baselines,
            metrics=metrics,
            n_bootstrap=n_bootstrap,
            n_permutations=n_permutations,
            seed=40_000 + scenario_index * 10_000,
        )
        for row in comparisons:
            results.append({"scenario": scenario, **row})
    return results


def main() -> None:  # pragma: no cover - exercised by CI smoke test
    from dmdtrl.dispatch import DispatchRule

    parser = argparse.ArgumentParser(
        description="Evaluate scheduling policies under controlled distribution shifts."
    )
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--seed-start", type=int, default=30_000)
    parser.add_argument("--scenario", action="append", dest="scenarios", default=None)
    parser.add_argument("--model", type=Path, default=None)
    parser.add_argument("--bootstrap", type=int, default=5_000)
    parser.add_argument("--permutations", type=int, default=10_000)
    parser.add_argument("--raw-output", type=Path, default=Path("results/stress_runs.csv"))
    parser.add_argument("--summary-output", type=Path, default=Path("results/stress_summary.csv"))
    parser.add_argument(
        "--comparisons-output",
        type=Path,
        default=Path("results/stress_ppo_comparisons.csv"),
    )
    args = parser.parse_args()

    if args.seeds <= 0:
        parser.error("--seeds must be positive")
    if args.seed_start < 0:
        parser.error("--seed-start must be non-negative")

    try:
        scenarios = select_scenarios(args.scenarios)
    except ValueError as exc:
        parser.error(str(exc))

    policies = list(fixed_policies())
    if args.model is not None:
        policies.append(load_ppo_policy(args.model))
    seeds = list(range(args.seed_start, args.seed_start + args.seeds))

    raw_rows, summary_rows = evaluate_scenarios(
        policies,
        seeds,
        scenarios,
        n_bootstrap=args.bootstrap,
    )
    experiments.write_csv(raw_rows, args.raw_output)
    experiments.write_csv(summary_rows, args.summary_output)

    print("Stress-test weighted-tardiness leaders:")
    for scenario in scenarios:
        candidates = [row for row in summary_rows if row["scenario"] == scenario.name]
        best = min(candidates, key=lambda item: float(item["weighted_tardiness_mean"]))
        print(
            f"  {scenario.name:<20} {str(best['policy']):<24} "
            f"WTT={float(best['weighted_tardiness_mean']):.3f}"
        )

    if args.model is not None:
        comparisons = compare_candidate_across_scenarios(
            raw_rows,
            candidate="PPO",
            baselines=[rule.name for rule in DispatchRule],
            n_bootstrap=args.bootstrap,
            n_permutations=args.permutations,
        )
        experiments.write_csv(comparisons, args.comparisons_output)
        print(f"Paired stress comparisons saved to {args.comparisons_output}")

    print(f"Raw stress runs saved to {args.raw_output}")
    print(f"Stress summaries saved to {args.summary_output}")


if __name__ == "__main__":  # pragma: no cover
    main()
