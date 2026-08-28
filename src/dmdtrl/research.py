from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_COMPARISON_METRICS = (
    "weighted_tardiness",
    "mean_waiting_time",
    "total_setup_time",
    "on_time_rate",
    "utilization",
    "makespan",
    "mean_decision_time_ms",
)


def fixed_policies():
    from dmdtrl.dispatch import DispatchRule
    from dmdtrl.policies import FixedActionPolicy

    return [FixedActionPolicy(int(rule), rule.name) for rule in DispatchRule]


def main() -> None:  # pragma: no cover - CLI smoke-tested in GitHub Actions
    from dmdtrl import experiments
    from dmdtrl.dispatch import DispatchRule
    from dmdtrl.env import EnvConfig
    from dmdtrl.policies import load_ppo_policy

    parser = argparse.ArgumentParser(
        description="Run seed-level scheduling experiments with statistical comparisons."
    )
    parser.add_argument("--seeds", type=int, default=50, help="Number of common random seeds.")
    parser.add_argument("--model", type=Path, default=None, help="Optional Stable-Baselines3 PPO model.")
    parser.add_argument("--raw-output", type=Path, default=Path("results/research_runs.csv"))
    parser.add_argument("--summary-output", type=Path, default=Path("results/research_summary.csv"))
    parser.add_argument(
        "--comparisons-output", type=Path, default=Path("results/ppo_comparisons.csv")
    )
    parser.add_argument("--bootstrap", type=int, default=5_000)
    parser.add_argument("--permutations", type=int, default=10_000)
    args = parser.parse_args()

    if args.seeds <= 0:
        parser.error("--seeds must be positive")
    policies = fixed_policies()
    if args.model is not None:
        policies.append(load_ppo_policy(args.model))

    rows = experiments.evaluate_policies(policies, range(args.seeds), EnvConfig())
    summaries = experiments.summarize_runs(rows, n_bootstrap=args.bootstrap)
    experiments.write_csv(rows, args.raw_output)
    experiments.write_csv(summaries, args.summary_output)

    print("Weighted-tardiness ranking (lower is better):")
    for row in sorted(summaries, key=lambda item: float(item["weighted_tardiness_mean"])):
        print(
            f"  {row['policy']:<24} "
            f"mean={float(row['weighted_tardiness_mean']):.3f} "
            f"95% CI=[{float(row['weighted_tardiness_ci_low']):.3f}, "
            f"{float(row['weighted_tardiness_ci_high']):.3f}]"
        )

    if args.model is not None:
        baselines = [rule.name for rule in DispatchRule]
        comparisons = experiments.compare_candidate_to_baselines(
            rows,
            candidate="PPO",
            baselines=baselines,
            metrics=DEFAULT_COMPARISON_METRICS,
            n_bootstrap=args.bootstrap,
            n_permutations=args.permutations,
        )
        experiments.write_csv(comparisons, args.comparisons_output)
        print(f"Paired PPO comparisons saved to {args.comparisons_output}")

    print(f"Seed-level runs saved to {args.raw_output}")
    print(f"Statistical summaries saved to {args.summary_output}")


if __name__ == "__main__":  # pragma: no cover
    main()
