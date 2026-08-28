# Dynamic Manufacturing Digital Twin with Reinforcement Learning

A research-oriented industrial engineering / operations research project for **dynamic production scheduling under uncertainty**.

The repository implements an event-driven manufacturing digital twin and compares three online scheduling controller classes: fixed dispatching rules, a PPO hyper-heuristic, and rolling-horizon CP-SAT optimization. All controllers share the same simulator transitions and are evaluated with common random seeds.

> Current model scope: dynamic heterogeneous parallel-machine scheduling. It is not yet a full job-shop or flexible job-shop model; multi-operation routing and precedence constraints are a later research phase.

## Research question

> Under what levels of demand variability and operational disruption does an adaptive RL hyper-heuristic provide material value over fixed dispatching rules and rolling-horizon optimization, after accounting for online decision latency?

The project is structured around **benchmarking, stress testing, reproducible training, OR comparison, and paired statistical validation**, not training reward alone.

## Current v0.6 scope

The digital twin and research harness include:

- stochastic job arrivals and heterogeneous parallel machines;
- sequence-dependent family changeovers;
- random machine breakdown/repair delays;
- priorities, due dates, and quality-risk attributes;
- fourteen bounded operational state features;
- eight deterministic dispatching rules;
- reproducible PPO hyper-heuristic training with audit manifests;
- rolling-horizon CP-SAT with explicit job-machine decisions;
- released-job-only OR information boundaries;
- machine-dependent processing times and sequence-dependent setup transitions in CP-SAT;
- strictly primary priority-weighted tardiness optimization;
- nominal final-test seeds separated at `20000+`;
- distribution-shift seeds separated at `30000+`;
- matched PPO / CP-SAT / fixed-rule stress evaluation;
- seed-level KPI output, bootstrap confidence intervals, paired randomization tests, effect sizes, and probability of superiority;
- online decision-latency measurement;
- Python 3.10/3.11/3.12 CI and a separate real Stable-Baselines3 integration workflow.

## Controller formulations

### PPO hyper-heuristic

The PPO agent receives a 14-dimensional normalized operational state and selects one of eight dispatching rules: FIFO, highest priority, EDD, SPT, same-family-first, minimum setup, critical ratio, or a weighted composite heuristic.

This fixed action space avoids direct variable job-ID actions. Reward is used only for training; scientific conclusions use operational KPIs.

### Rolling-horizon CP-SAT

At each decision epoch CP-SAT sees only jobs already released into the queue and machines currently available. It cannot inspect future arrivals, breakdown realizations, or repair durations.

It plans a bounded released-job horizon with machine-dependent processing durations and sequence-dependent setups, executes only the first job-machine assignment, and then replans. Priority-weighted tardiness is lexicographically dominant over setup and makespan tie breakers.

## Operational metrics

Experiments report makespan, mean waiting time, total tardiness, priority-weighted tardiness, setup time, repair/disruption time, on-time completion rate, utilization, mean processed quality risk, and mean online decision latency.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev,analysis]"
```

For PPO:

```bash
pip install -e ".[rl,dev,analysis]"
```

For CP-SAT:

```bash
pip install -e ".[or,dev,analysis]"
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

## Fixed-rule benchmark

```bash
dmdtrl-baselines --seeds 30 --output results/baselines.csv
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

The JSON manifest records the full PPO configuration, `EnvConfig`, training time, runtime/package versions, and GitHub run metadata when available. See [`docs/ppo_reproducibility.md`](docs/ppo_reproducibility.md).

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

## Nominal CP-SAT benchmark

```bash
dmdtrl-or \
  --seeds 30 \
  --seed-start 20000 \
  --horizon 12 \
  --solver-seconds 0.10 \
  --raw-output results/or_runs.csv \
  --summary-output results/or_summary.csv \
  --comparisons-output results/cpsat_comparisons.csv
```

See [`docs/or_baseline.md`](docs/or_baseline.md) for the OR information boundary and formulation.

## Matched distribution-shift evaluation

Built-in scenarios include nominal conditions, +20/+40/+60% arrival intensity, 2x/4x breakdown probability, tighter due dates, slower machines, 2x setup duration, and compound stress.

Fixed rules plus CP-SAT:

```bash
dmdtrl-stress \
  --include-cpsat \
  --cpsat-horizon 12 \
  --cpsat-solver-seconds 0.10 \
  --seeds 50 \
  --seed-start 30000 \
  --raw-output results/stress_runs.csv \
  --summary-output results/stress_summary.csv \
  --cpsat-comparisons-output results/stress_cpsat_comparisons.csv
```

Full PPO / CP-SAT / fixed-rule matrix:

```bash
dmdtrl-stress \
  --model models/ppo_dispatcher.zip \
  --include-cpsat \
  --cpsat-horizon 12 \
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

For candidate-vs-baseline KPI comparisons the harness reports candidate and baseline means, paired mean improvement, bootstrap 95% confidence interval, percent improvement, two-sided paired randomization p-value, Cohen's dz effect size, probability of superiority, and number of paired stochastic seeds.

## GitHub Actions

- `CI`: Python 3.10/3.11/3.12 lint, tests, coverage, nominal research smoke, CP-SAT nominal smoke, and distribution-shift smoke with actual OR-Tools solves.
- `RL Smoke`: Python 3.11 with Stable-Baselines3/PyTorch, short PPO training, nominal/stress inference, manifest validation, and uploaded experiment artifacts.

The short PPO model generated by `RL Smoke` is an integration test only and must not be interpreted as policy-quality evidence.

## Research phases

1. **Validated simulation + deterministic baselines:** complete.
2. **PPO hyper-heuristic + statistical infrastructure:** complete; long-horizon multi-training-seed experiment pending.
3. **Rolling-horizon OR benchmark:** nominal and stress integration implemented; horizon/solver-budget sensitivity is next.
4. **Generalization study:** stress infrastructure implemented; full comparative campaign pending.
5. **True flexible job-shop extension:** planned.
6. **Decision-twin service layer:** planned.

See [`docs/roadmap.md`](docs/roadmap.md) for the detailed sequence.

## Scientific principle

A learned policy is not superior because training reward increases, and an optimizer is not superior because it solves a mathematical model. Operational KPIs, uncertainty, online compute cost, and paired statistical evidence determine the result. If a fixed rule is faster or better in a regime, that is a valid research outcome.

## License

MIT License. See [LICENSE](LICENSE).
