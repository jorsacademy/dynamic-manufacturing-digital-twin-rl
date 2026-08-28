# Dynamic Manufacturing Digital Twin with Reinforcement Learning

A research-oriented industrial engineering / operations research project for **dynamic production scheduling under uncertainty**.

The repository implements an event-driven manufacturing digital twin and compares fixed dispatching rules, a PPO hyper-heuristic, and rolling-horizon CP-SAT optimization on common stochastic realizations.

> Current scope: dynamic heterogeneous parallel-machine scheduling. A true flexible job-shop representation with multi-operation routing and precedence constraints is a later phase.

## Research question

> Under what levels of demand variability and operational disruption does an adaptive RL hyper-heuristic provide material value over fixed dispatching rules and rolling-horizon optimization, after accounting for online decision latency, solver reliability, and RL training-seed variability?

The repository is built around reproducibility, paired benchmarking, model-selection discipline, and disjoint validation/final-test data—not training reward alone.

## Current v0.9 status

Completed research infrastructure includes:

- stochastic arrivals, heterogeneous machines, sequence-dependent setups, breakdown/repair delays, priorities, due dates, and quality risk;
- fourteen normalized operational state features and eight deterministic dispatching rules;
- PPO hyper-heuristic training with audit manifests;
- rolling-horizon CP-SAT with explicit job-machine assignments and released-job-only information;
- deterministic CP-SAT timeout fallback plus measured solver fallback/success rates;
- CP-SAT horizon × solve-budget sensitivity analysis;
- completed 30-seed OR validation campaign and frozen CP-SAT operating point;
- completed five-training-seed, 750,000-total-timestep PPO validation campaign;
- independent artifact/hash verification for both controller families;
- seed-level KPIs, bootstrap confidence intervals, paired randomization tests, effect sizes, and probability of superiority;
- nominal and distribution-shift evaluation harnesses;
- Python 3.10/3.11/3.12 CI, RL Smoke, OR Validation, and PPO Validation workflows.

Seed regimes are deliberately separated:

- training randomness: below `10000`;
- validation/model selection: `10000–19999`;
- nominal final test: `20000+`;
- stress final test: `30000+`.

## Controller formulations

### PPO hyper-heuristic

The PPO agent receives a 14-dimensional normalized operational state and selects one of eight dispatching rules: FIFO, highest priority, EDD, SPT, same-family-first, minimum setup, critical ratio, or a weighted composite rule.

The RL action therefore selects a dispatching heuristic rather than an arbitrary job-machine pair. This keeps the action space fixed and feasible while allowing the policy to adapt its scheduling logic to current shop conditions.

### Rolling-horizon CP-SAT

At each decision epoch CP-SAT sees only jobs already released into the queue and machines currently available. It cannot inspect future arrivals, breakdown realizations, or repair durations.

The optimizer plans a bounded released-job horizon with machine-dependent processing durations and sequence-dependent setups, executes only the first assignment, and replans. Priority-weighted tardiness is the primary objective.

If the online budget expires with solver status `UNKNOWN`, a deterministic one-step feasible assignment keeps the plant moving and the fallback is recorded. `INFEASIBLE` and model-invalid states remain hard failures.

## Frozen CP-SAT operating point

The completed validation campaign used seeds `10000–10029` and evaluated 3 horizons × 3 solve budgets. The predeclared selection rule required Pareto optimality in weighted tardiness/latency, at most 1% mean fallback, WTT within 2% of the best reliable Pareto point, then minimum latency.

Frozen final-evaluation configuration:

- horizon: **8 released jobs**;
- solve budget: **100 ms per decision**;
- validation mean weighted tardiness: **72.5101**;
- validation mean decision latency: **21.4080 ms**;
- validation mean fallback rate: **0.00%**.

The frozen provenance is stored in [`configs/cpsat_operating_point.json`](configs/cpsat_operating_point.json). This configuration will not be retuned after PPO or final-test results are observed.

## Frozen PPO validation campaign

Five independent PPO models were trained under the same hyperparameters for `150,000` timesteps each:

- training seeds: `101, 202, 303, 404, 505`;
- total training: **750,000 timesteps**;
- common validation seeds: `10000–10029`;
- final-test seeds were not used for selection.

Validation mean priority-weighted tardiness by training seed:

| Training seed | WTT | PPO decision latency (ms) |
| ---: | ---: | ---: |
| 101 | 77.0644 | 0.1922 |
| 202 | 83.4609 | 0.2469 |
| 303 | 73.8590 | 0.2763 |
| 404 | 72.9942 | 0.1911 |
| 505 | 83.2213 | 0.1036 |

Across the five learned policies:

- mean WTT: **78.1200**;
- median WTT: **77.0644**;
- training-seed sample standard deviation: **5.0023**;
- minimum WTT: **72.9942**;
- maximum WTT: **83.4609**.

The strongest fixed dispatching rule on the same nominal validation seeds was `WEIGHTED_COMPOSITE` with WTT **73.8590**. Some PPO seeds were competitive, while others were materially worse. The project therefore does not report the best PPO seed as if it represented the algorithm.

The predeclared median-role representative model is **training seed 101**, not the best-performing seed. It exists only for dashboard/demo/service continuity. Final scientific claims retain all five PPO training-seed realizations.

Frozen PPO provenance and artifact hashes are stored in [`configs/ppo_validation_freeze.json`](configs/ppo_validation_freeze.json). See [`docs/ppo_validation_results.md`](docs/ppo_validation_results.md) and [`docs/ppo_multiseed.md`](docs/ppo_multiseed.md).

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[rl,or,dev,analysis]"
```

## Tests

```bash
pytest
ruff check src tests
```

## Reproduce one PPO member

```bash
dmdtrl-train \
  --steps 150000 \
  --seed 101 \
  --output models/ppo_dispatcher \
  --metadata models/ppo_dispatcher_manifest.json \
  --device cpu \
  --quiet
```

See [`docs/ppo_reproducibility.md`](docs/ppo_reproducibility.md).

## Nominal final evaluation

Both adaptive controller families are now frozen before final-test analysis. Nominal final seeds begin at `20000`.

Frozen CP-SAT command:

```bash
dmdtrl-or \
  --seeds 100 \
  --seed-start 20000 \
  --horizon 8 \
  --solver-seconds 0.10 \
  --raw-output results/or_runs.csv \
  --summary-output results/or_summary.csv \
  --comparisons-output results/cpsat_comparisons.csv
```

The final PPO campaign evaluates **all five frozen training-seed realizations**, not only representative seed 101. Statistical analysis preserves training-seed variability instead of treating 500 PPO observations as independent repetitions.

## Distribution-shift evaluation

Built-in scenarios include +20/+40/+60% arrival intensity, 2×/4× breakdown probability, tighter due dates, slower machines, increased setup pressure, and compound stress.

The full final matrix will use frozen PPO models, frozen CP-SAT `H=8 / 100 ms`, common `30000+` stress seeds, and direct paired PPO-vs-CP-SAT/fixed-rule comparisons.

## GitHub Actions

- `CI`: Python 3.10/3.11/3.12 lint, tests, coverage, research smoke, stress smoke, CP-SAT smoke, and sensitivity smoke.
- `RL Smoke`: short Stable-Baselines3 training/inference integration test; not policy-quality evidence.
- `OR Validation`: completed 30-seed CP-SAT validation campaign with reliability gating and artifacts.
- `PPO Validation`: completed five-member long-horizon PPO campaign with common validation seeds, member artifacts, hashes, and aggregate manifest.

## Research phases

1. **Validated simulator + deterministic baselines:** complete.
2. **Rolling-horizon OR baseline and operating-point freeze:** complete; frozen at **H=8 / 100 ms**.
3. **PPO hyper-heuristic multi-seed validation:** complete; five models frozen, representative seed **101**.
4. **Full nominal + stress comparative experiment:** next active phase.
5. **True flexible job-shop extension:** planned.
6. **Decision-twin service/dashboard layer:** planned.

See [`docs/roadmap.md`](docs/roadmap.md).

## Portfolio sequence

This repository is the first flagship, not the whole portfolio. Planned follow-on repositories cover safe continuous process control, multi-echelon inventory, dynamic vehicle routing, joint maintenance/production scheduling, and adaptive capacity/workforce control. Each will use the same research-grade standard: strong OR/control baselines, stochastic simulation, CI, reproducible experiments, and out-of-sample comparisons.

## Scientific principle

A learned policy is not superior because training reward rises, and an optimizer is not superior because it solves a mathematical model. Operational KPIs, online compute cost, solver reliability, training-seed variability, robustness, and paired out-of-sample evidence determine the conclusion. A fixed heuristic winning in some regime is a valid result.

## License

MIT License. See [LICENSE](LICENSE).
