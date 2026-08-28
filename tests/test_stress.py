from dmdtrl.env import EnvConfig
from dmdtrl.research import fixed_policies
from dmdtrl.scenarios import select_scenarios
from dmdtrl.stress import compare_candidate_across_scenarios, evaluate_scenarios


def test_evaluate_scenarios_retains_scenario_and_seed_level_results():
    policies = fixed_policies()[:2]
    scenarios = select_scenarios(["nominal", "demand_120"])
    config = EnvConfig(n_jobs=8, n_machines=2)

    raw_rows, summary_rows = evaluate_scenarios(
        policies,
        [101, 102],
        scenarios,
        config,
        n_bootstrap=100,
    )

    assert len(raw_rows) == 8
    assert len(summary_rows) == 4
    assert {row["scenario"] for row in raw_rows} == {"nominal", "demand_120"}
    assert {row["seed"] for row in raw_rows} == {101, 102}
    assert all("weighted_tardiness_mean" in row for row in summary_rows)


def test_compare_candidate_across_scenarios_keeps_pairing_separate():
    rows = []
    for scenario, penalty in [("nominal", 0.0), ("stress", 10.0)]:
        for seed in range(4):
            rows.append(
                {
                    "scenario": scenario,
                    "policy": "candidate",
                    "seed": seed,
                    "weighted_tardiness": 5.0 + penalty,
                }
            )
            rows.append(
                {
                    "scenario": scenario,
                    "policy": "baseline",
                    "seed": seed,
                    "weighted_tardiness": 8.0 + penalty,
                }
            )

    comparisons = compare_candidate_across_scenarios(
        rows,
        candidate="candidate",
        baselines=["baseline"],
        metrics=("weighted_tardiness",),
        n_bootstrap=100,
        n_permutations=200,
    )

    assert len(comparisons) == 2
    assert {row["scenario"] for row in comparisons} == {"nominal", "stress"}
    assert all(row["mean_improvement"] == 3.0 for row in comparisons)
