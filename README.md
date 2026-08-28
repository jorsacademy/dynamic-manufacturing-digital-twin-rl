# Dynamic Manufacturing Digital Twin with Reinforcement Learning

A research-oriented industrial engineering / operations research project for **dynamic production scheduling under uncertainty**.

The repository implements an event-driven manufacturing digital twin and compares three online scheduling controller classes: fixed dispatching rules, a PPO hyper-heuristic, and rolling-horizon CP-SAT optimization. All controllers share the same simulator transitions and are evaluated with common random seeds.

> Current model scope: dynamic heterogeneous parallel-machine scheduling. It is not yet a full job-shop or flexible job-shop model; multi-operation routing and precedence constraints are a later research phase.

## Research question

> Under what levels of demand variability and operational disruption does an adaptive RL hyper-heuristic provide material value over fixed dispatching rules and rolling-horizon optimization, after accounting for online decision latency?

The project is structured around **benchmarking, stress testing, reproducible training, OR comparison, compute-budget sensitivity, model-selection discipline, and paired statistical validation**, not training reward alone.

## Current v0.8 scope

The digital twin and research harness include:

- stochastic job arrivals and heterogeneous parallel machines;
- sequence-dependent family changeovers and random breakdown/repair delays;
- priorities, due dates, and quality-risk attributes;
- fourteen bounded operational state features and eight deterministic dispatching rules;
- reproducible PPO training with audit manifests;
- rolling-horizon CP-SAT with explicit job-machine decisions;
- released-job-only OR information boundaries;
- machine-dependent processing times and sequence-dependent setup transitions in CP-SAT;
- strictly primary priority-weighted tardiness optimization;
- deterministic feasible fallback on solver `UNKNOWN` timeouts, with solver fallback/success-rate reporting;
- validation/model-selection seeds reserved at `10000+`, nominal final-test seeds at `20000+`, and stress final-test seeds at `30000+`;
- matched PPO / CP-SAT / fixed-rule stress evaluation;
- CP-SAT horizon × solver-budget sensitivity analysis;
- WTT/decision-latency Pareto-front identification;
- deterministic validation-only CP-SAT operating-point selection with reliability gating;
- complete-grid validation checks requiring every configuration to contain the same declared seed set;
- a completed 30-seed OR Validation campaign with independently verified artifacts;
- a frozen CP-SAT final-evaluation configuration in [`configs/cpsat_operating_point.json`](configs/cpsat_operating_point.json);
- seed-level KPI output, bootstrap confidence intervals, paired randomization tests, effect sizes, and probability of superiority;
- Python 3.10/3.11/3.12 CI and a separate real Stable-Baselines3 integration workflow.

## Controller formulations

### PPO hyper-heuristic

The PPO agent receives a 14-dimensional normalized operational state and selects one of eight dispatching rules: FIFO, highest priority, EDD, SPT, same-family-first, minimum setup, critical ratio, or a weighted composite heuristic. Reward is used for training; scientific conclusions use operational KPIs.

### Rolling-horizon CP-SAT

At each decision epoch CP-SAT sees only jobs already released into the queue and machines currently available. It cannot inspect future arrivals, breakdown realizations, or repair durations.

It plans a bounded released-job horizon with machine-dependent processing durations and sequence-dependent setups, executes only the first job-machine assignment, and then replans. Priority-weighted tardiness is lexicographically dominant over setup and makespan tie breakers.

If the declared online budget expires before CP-SAT finds a first feasible solution (`UNKNOWN`), the controller uses a deterministic one-step feasible fallback and records that event. `INFEASIBLE` and model errors remain hard failures. This makes short compute budgets measurable rather than silently misclassifying fallback behavior as successful optimization.

## Operational metrics

Experiments report makespan, mean waiting time, total tardiness, priority-weighted tardiness, setup time, repair/disruption time, on-time completion rate, utilization, mean processed quality risk, mean online decision latency, and—when CP-SAT is used—solver fallback/success rates.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev,analysis]"
```

For the complete comparative stack:

```bash
pip install -e ".[rl,or,dev,analysis]"
```

## Tests

```bash
pytest
ruff check src tests
```

## Train PPO with an audit manifest

```bash
dmdtrl-train \
  --steps 150000 \
  --seed 42 \
  --output models/ppo_dispatcher \
  --metadata models/ppo_dispatcher_manifest.json \
  --device cpu
```

See [`docs/ppo_reproducibility.md`](docs/ppo_reproducibility.md).

## Nominal PPO evaluation

```bash
dmdtrl-research \
  --model models/ppo_dispatcher.zip \
  --seeds 100 \
  --seed-start 20000 \
  --raw-output results/nominal_runs.csv \
  --summary-output results/nominal_summary.csv \
  --comparisons-output results/nominal_ppo_comparisons.csv
```

Final PPO evaluation must not begin until the PPO training/model-selection settings are frozen using non-final data.

## Frozen CP-SAT operating point

The completed 30-seed validation campaign (`10000–10029`) evaluated a 3×3 horizon/solve-budget grid. The predeclared rule required:

1. WTT/latency Pareto optimality;
2. mean solver fallback rate no greater than 1%;
3. WTT within 2% of the best reliable Pareto WTT;
4. lowest measured decision latency among acceptable points.

The frozen result is:

- horizon: **8 released jobs**;
- solver budget: **0.10 s / 100 ms per decision**;
- validation mean weighted tardiness: **72.5101**;
- validation mean decision latency: **21.4080 ms**;
- validation mean solver fallback rate: **0.00%**.

The best reliable Pareto WTT was 72.5101, giving a 2% threshold of 73.9603. H8 / 50 ms produced WTT 74.138, so it was outside the predeclared tolerance despite lower latency. H8 / 100 ms was the only acceptable Pareto configuration.

The artifact was independently checked: 270 raw rows = 9 configurations × 30 complete validation seeds, and the downloaded ZIP SHA-256 matched the workflow digest. The frozen provenance and selection statistics are retained in [`configs/cpsat_operating_point.json`](configs/cpsat_operating_point.json).

Relative to the declared H12 / 100 ms reference, H8 / 100 ms had 5.59% lower mean WTT on validation seeds, but its paired 95% improvement interval crossed zero (`-0.95` to `11.01`) and the paired randomization p-value was approximately 0.225. This is therefore **model-selection evidence, not a statistical superiority claim**.

## Nominal CP-SAT final benchmark

The frozen OR configuration must remain unchanged on nominal final-test seeds:

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

See [`docs/or_baseline.md`](docs/or_baseline.md) and [`docs/or_operating_point.md`](docs/or_operating_point.md).

## Reproduce the CP-SAT validation study

```bash
dmdtrl-or-sensitivity \
  --seeds 30 \
  --seed-start 10000 \
  --horizon 4 \
  --horizon 8 \
  --horizon 12 \
  --solver-seconds 0.02 \
  --solver-seconds 0.05 \
  --solver-seconds 0.10 \
  --reference-horizon 12 \
  --reference-solver-seconds 0.10 \
  --raw-output results/cpsat_validation_runs.csv \
  --summary-output results/cpsat_validation_summary.csv \
  --comparisons-output results/cpsat_validation_comparisons.csv
```

To reproduce the selector:

```bash
dmdtrl-or-select \
  --raw-input results/cpsat_validation_runs.csv \
  --summary-input results/cpsat_validation_summary.csv \
  --output results/cpsat_operating_point.json \
  --quality-tolerance-pct 2.0 \
  --max-fallback-rate-pct 1.0 \
  --validation-seed-start 10000 \
  --validation-seeds 30
```

The selector refuses partial or leaked seed sets. Every sensitivity configuration must contain all declared validation seeds, and the range must remain below final-test seed 20000.

## Matched distribution-shift evaluation

Built-in scenarios include nominal conditions, +20/+40/+60% arrival intensity, 2x/4x breakdown probability, tighter due dates, slower machines, 2x setup duration, and compound stress.

After PPO settings are independently frozen, run the full matrix on disjoint stress seeds using the already frozen OR settings:

```bash
dmdtrl-stress \
  --model models/ppo_dispatcher.zip \
  --include-cpsat \
  --cpsat-horizon 8 \
  --cpsat-solver-seconds 0.10 \
  --seeds 100 \
  --seed-start 30000 \
  --raw-output results/stress_runs.csv \
  --summary-output results/stress_summary.csv \
  --comparisons-output results/stress_ppo_comparisons.csv \
  --cpsat-comparisons-output results/stress_cpsat_comparisons.csv
```

When both optional controllers are present, PPO is compared against CP-SAT and all eight fixed rules. CP-SAT is independently compared against all eight fixed rules. Every comparison remains scenario-local and seed-paired. See [`docs/stress_scenarios.md`](docs/stress_scenarios.md).

## Statistical outputs

Candidate-vs-baseline comparisons report means, paired mean improvement, bootstrap 95% confidence interval, percent improvement, two-sided paired randomization p-value, Cohen's dz effect size, probability of superiority, and paired seed count.

## GitHub Actions

- `CI`: Python 3.10/3.11/3.12 lint, tests, coverage, nominal research smoke, CP-SAT nominal/stress smoke, and a multi-point CP-SAT sensitivity smoke grid on validation seeds.
- `RL Smoke`: Python 3.11 with Stable-Baselines3/PyTorch, short PPO training, nominal/stress inference, manifest validation, and uploaded experiment artifacts.
- `OR Validation`: 30-seed validation-only 3×3 CP-SAT sensitivity campaign, solver-reliability measurement, deterministic operating-point selection, and uploaded raw/summary/comparison/freeze artifacts.

The short PPO model generated by `RL Smoke` and the one-seed sensitivity run generated by `CI` are integration tests only and must not be interpreted as policy-quality evidence.

## Research phases

1. **Validated simulation + deterministic baselines:** complete.
2. **PPO hyper-heuristic + statistical infrastructure:** complete; long-horizon multi-training-seed experiment is next.
3. **Rolling-horizon OR benchmark:** controller, stress integration, sensitivity study, validation campaign, and operating-point freeze are complete. Frozen final-evaluation setting: **H=8 / 100 ms**.
4. **Generalization/full comparative study:** infrastructure implemented; begins after PPO settings are frozen.
5. **True flexible job-shop extension:** planned.
6. **Decision-twin service layer:** planned.

See [`docs/roadmap.md`](docs/roadmap.md) for the detailed sequence.

## Scientific principle

A learned policy is not superior because training reward increases, and an optimizer is not superior because it solves a mathematical model. Operational KPIs, uncertainty, online compute cost, solver reliability, and paired statistical evidence determine the result. If a fixed rule is faster or better in a regime, that is a valid research outcome.

## License

MIT License. See [LICENSE](LICENSE).
