# Dynamic Manufacturing Digital Twin with Reinforcement Learning

A research-oriented industrial engineering / operations research project for **dynamic production scheduling under uncertainty**.

The repository implements an event-driven manufacturing digital twin and formulates real-time dispatching as a reinforcement-learning hyper-heuristic. Instead of assigning an RL action to every `(job, machine)` pair, the agent selects a dispatching policy at each decision epoch. This keeps the action space fixed while allowing the policy to adapt to stochastic arrivals, heterogeneous machines, sequence-dependent setups, due-date pressure, and random breakdowns.

A rolling-horizon CP-SAT controller provides a classical operations-research comparator using the same simulator transitions and online information boundary.

> Current model scope: dynamic heterogeneous parallel-machine scheduling. It is not yet a full job-shop or flexible job-shop model; multi-operation routing and precedence constraints are a later research phase.

## Research question

> Under what levels of demand variability and operational disruption does an adaptive RL hyper-heuristic provide material value over fixed dispatching rules and rolling-horizon optimization?

The project is intentionally structured around **benchmarking, stress testing, reproducible training, OR comparison, and statistical validation**, not training reward alone.

## Current v0.5 scope

The digital twin and research harness include:

- stochastic job arrivals;
- heterogeneous parallel machines;
- sequence-dependent family changeovers;
- random machine breakdown/repair delays;
- job priorities and due dates;
- quality-risk attributes;
- event-driven scheduling decisions;
- fourteen bounded operational state features;
- eight deterministic dispatching rules;
- PPO hyper-heuristic training;
- machine-readable PPO training manifests;
- explicit nominal/stress test seed separation;
- deterministic learned-policy evaluation adapters;
- rolling-horizon CP-SAT job-machine optimization;
- released-job-only OR information boundaries;
- sequence-dependent setup transitions inside the CP-SAT plan;
- common-random-number experiments;
- raw seed-level KPI output;
- bootstrap confidence intervals;
- paired randomization tests;
- paired effect sizes and probability of superiority;
- online decision-latency measurement;
- controlled distribution-shift scenarios;
- compound operational stress testing;
- multi-version CI plus a separate real RL integration workflow.

## RL formulation

### State

A 14-dimensional normalized vector summarizes the current operational state:

1. queue length;
2. queued workload;
3. mean waiting time;
4. urgent-job ratio;
5. same-family setup opportunity;
6. mean slack pressure;
7. overdue-job ratio;
8. mean queued processing time;
9. processing-time dispersion;
10. mean quality risk;
11. machine utilization;
12. episode time progress;
13. completion ratio;
14. setup/disruption load.

### Action

The agent selects one dispatching rule:

1. FIFO;
2. highest priority first;
3. earliest due date (EDD);
4. shortest processing time (SPT);
5. same family first;
6. minimum setup;
7. critical ratio;
8. weighted composite heuristic.

This is a **hyper-heuristic RL** design. It avoids a variable and mostly infeasible job-ID action space.

### Reward

The incremental reward combines:

- completion reward;
- on-time completion bonus;
- waiting-time penalty;
- priority-weighted tardiness penalty;
- setup-time penalty;
- breakdown/repair penalty;
- quality-risk penalty.

Reward is a training mechanism. Scientific conclusions are based on operational KPIs.

## OR / IE performance metrics

Experiments report:

- makespan;
- mean waiting time;
- total tardiness;
- priority-weighted tardiness;
- setup time;
- repair/disruption time;
- on-time completion rate;
- machine utilization;
- mean processed quality risk;
- mean online decision latency.

## Installation

Core simulation and research harness:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev,analysis]"
```

For PPO training/evaluation:

```bash
pip install -e ".[rl,dev,analysis]"
```

For rolling-horizon CP-SAT benchmarking:

```bash
pip install -e ".[or,dev,analysis]"
```

## Run the tests

```bash
pytest
ruff check src tests
```

## Benchmark fixed dispatching rules

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

The command writes the Stable-Baselines3 model and a JSON manifest containing the full PPO configuration, `EnvConfig`, training time, GitHub run metadata when available, Python/platform information, and package versions.

See [`docs/ppo_reproducibility.md`](docs/ppo_reproducibility.md) for the experiment contract.

## Research-grade nominal evaluation

Nominal final-test seeds default to the disjoint `20000+` range:

```bash
dmdtrl-research \
  --model models/ppo_dispatcher.zip \
  --seeds 100 \
  --seed-start 20000 \
  --raw-output results/nominal_runs.csv \
  --summary-output results/nominal_summary.csv \
  --comparisons-output results/nominal_ppo_comparisons.csv
```

For every candidate-vs-baseline KPI comparison, the harness reports:

- candidate and baseline means;
- paired mean improvement, oriented so positive favors the candidate;
- bootstrap 95% confidence interval;
- percent improvement relative to the baseline mean;
- two-sided paired randomization p-value;
- Cohen's dz paired effect size;
- probability of superiority;
- number of paired stochastic seeds.

## Rolling-horizon CP-SAT benchmark

The OR controller sees only jobs that have already been released and machines that are currently available. It does not inspect future arrivals or future breakdown realizations.

At every decision epoch it builds a bounded CP-SAT plan, models heterogeneous machine processing times and sequence-dependent family setups, executes only the first assignment, and replans.

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

The benchmark uses the same seed-level KPI schema and paired statistical comparison machinery as the PPO research harness. Online solve latency is included as a first-class metric.

See [`docs/or_baseline.md`](docs/or_baseline.md) for the information boundary, CP-SAT formulation, objective hierarchy, and current limitations.

## Distribution-shift stress testing

Stress seeds default to a separate `30000+` range. Built-in scenarios include:

- nominal conditions;
- +20%, +40%, and +60% arrival intensity;
- 2x and 4x breakdown probability;
- 15% tighter due-date allowances;
- 10% slower machine-speed distributions;
- 2x sequence-dependent setup time;
- a compound severe scenario combining demand, failure, due-date, speed, and setup pressure.

```bash
dmdtrl-stress \
  --model models/ppo_dispatcher.zip \
  --seeds 100 \
  --seed-start 30000 \
  --raw-output results/stress_runs.csv \
  --summary-output results/stress_summary.csv \
  --comparisons-output results/stress_ppo_comparisons.csv
```

The PPO model is evaluated without retraining. The objective is a **robustness profile**, not one calibrated leaderboard score. CP-SAT integration into the same stress matrix is the next Phase 3 milestone.

## GitHub Actions

Two workflows serve different purposes:

- `CI` — Python 3.10/3.11/3.12 lint, unit/integration tests, coverage, research/stress/CP-SAT CLI smoke tests;
- `RL Smoke` — Python 3.11 with Stable-Baselines3/PyTorch, short PPO training, nominal learned-policy evaluation, distribution-shift evaluation, manifest validation, and uploaded experiment artifacts.

The short model generated by `RL Smoke` is only an integration test and must not be interpreted as evidence that PPO is operationally superior.

## Repository structure

```text
.
├── .github/workflows/
│   ├── ci.yml
│   └── rl-smoke.yml
├── docs/
│   ├── or_baseline.md
│   ├── ppo_reproducibility.md
│   ├── research_protocol.md
│   ├── roadmap.md
│   └── stress_scenarios.md
├── src/dmdtrl/
│   ├── dispatch.py
│   ├── env.py
│   ├── evaluate.py
│   ├── experiments.py
│   ├── generator.py
│   ├── models.py
│   ├── or_benchmark.py
│   ├── or_experiments.py
│   ├── or_policy.py
│   ├── policies.py
│   ├── research.py
│   ├── scenarios.py
│   ├── statistics.py
│   ├── stress.py
│   └── train.py
├── tests/
├── pyproject.toml
└── README.md
```

## Research phases

### Phase 1 — validated simulation + deterministic baselines

Complete. Event logic, dispatching rules, reproducibility tests, and baseline benchmarking are implemented.

### Phase 2 — PPO hyper-heuristic + statistical validation

Infrastructure is complete. Reproducible training, manifest generation, nominal/stress seed separation, learned-policy adapters, and paired statistical evaluation are implemented. The remaining scientific milestone is a sufficiently long multi-training-seed PPO study.

### Phase 3 — rolling-horizon optimization

In progress. The first CP-SAT baseline now performs online released-job planning with explicit job-machine assignments, sequence-dependent setup transitions, bounded solve time, and paired nominal evaluation against the eight fixed rules.

Next: integrate CP-SAT into the distribution-shift suite and run matched PPO vs CP-SAT vs fixed-rule comparisons.

### Phase 4 — generalization study

Stress-test infrastructure is implemented. Candidate policies trained only on nominal conditions will be evaluated without retraining across the predefined distribution-shift matrix.

The key scientific output will be the relationship between uncertainty/disruption level and the relative advantage of adaptive and optimization-based policies.

### Phase 5 — true flexible job-shop extension

Introduce multi-operation jobs, precedence constraints, alternative eligible machines, routing decisions, and variable feasible action sets. Candidate methods include action-masked PPO and graph-based state representations.

### Phase 6 — live decision-twin layer

Expose current twin state and recommended actions through an API/dashboard suitable for simulated or real production data.

## Scientific protocol

See [`docs/research_protocol.md`](docs/research_protocol.md), [`docs/ppo_reproducibility.md`](docs/ppo_reproducibility.md), [`docs/or_baseline.md`](docs/or_baseline.md), [`docs/stress_scenarios.md`](docs/stress_scenarios.md), and [`docs/roadmap.md`](docs/roadmap.md).

A learned policy should not be described as superior merely because training reward increases. If a classical OR or dispatching policy is faster, more robust, or operationally better, that is a valid and useful research result.

## License

MIT License. See [LICENSE](LICENSE).
