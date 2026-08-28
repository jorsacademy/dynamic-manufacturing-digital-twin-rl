# Dynamic Manufacturing Digital Twin with Reinforcement Learning

A research-oriented industrial engineering / operations research project for **dynamic production scheduling under uncertainty**.

The repository implements an event-driven manufacturing digital twin and formulates real-time dispatching as a reinforcement-learning hyper-heuristic. Instead of assigning an RL action to every `(job, machine)` pair, the agent selects a dispatching policy at each decision epoch. This keeps the action space fixed while allowing the policy to adapt to stochastic arrivals, heterogeneous machines, sequence-dependent setups, due-date pressure, and random breakdowns.

> Current model scope: dynamic heterogeneous parallel-machine scheduling. It is not yet a full job-shop or flexible job-shop model; multi-operation routing and precedence constraints are a later research phase.

## Research question

> Under what levels of demand variability and operational disruption does an adaptive RL hyper-heuristic provide material value over fixed dispatching rules and, later, rolling-horizon OR methods?

The project is intentionally structured around **benchmarking, stress testing, and statistical validation**, not training reward alone.

## Current v0.3 scope

The digital twin includes:

- stochastic job arrivals;
- heterogeneous parallel machines;
- sequence-dependent family changeovers;
- random machine breakdown/repair delays;
- job priorities and due dates;
- quality-risk attributes;
- event-driven scheduling decisions;
- fourteen bounded operational state features;
- eight deterministic dispatching rules;
- PPO training and deterministic model-evaluation adapters;
- common-random-number experiments;
- raw seed-level KPI output;
- bootstrap confidence intervals;
- paired randomization tests;
- paired effect sizes and probability of superiority;
- online decision-latency measurement;
- controlled distribution-shift scenarios;
- compound operational stress testing;
- automated unit tests and GitHub Actions CI.

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

## Run the tests

```bash
pytest
ruff check src tests
```

## Benchmark fixed dispatching rules

The compact baseline command remains available:

```bash
dmdtrl-baselines --seeds 30 --output results/baselines.csv
```

## Research-grade experiment harness

Run all eight fixed policies on common random seeds and retain seed-level results plus bootstrap confidence intervals:

```bash
dmdtrl-research \
  --seeds 50 \
  --raw-output results/research_runs.csv \
  --summary-output results/research_summary.csv
```

After training PPO, run paired PPO-vs-baseline comparisons on the same stochastic scenarios:

```bash
dmdtrl-research \
  --model models/ppo_dispatcher.zip \
  --seeds 100 \
  --raw-output results/research_runs.csv \
  --summary-output results/research_summary.csv \
  --comparisons-output results/ppo_comparisons.csv
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

## Distribution-shift stress testing

The stress suite evaluates the same policies on controlled out-of-distribution operating conditions. Built-in scenarios include:

- nominal conditions;
- +20%, +40%, and +60% arrival intensity;
- 2x and 4x breakdown probability;
- 15% tighter due-date allowances;
- 10% slower machine-speed distributions;
- 2x sequence-dependent setup time;
- a compound severe scenario combining demand, failure, due-date, speed, and setup pressure.

Run the full stress matrix on fixed policies:

```bash
dmdtrl-stress \
  --seeds 30 \
  --seed-start 30000 \
  --raw-output results/stress_runs.csv \
  --summary-output results/stress_summary.csv
```

Run selected scenarios only:

```bash
dmdtrl-stress \
  --scenario nominal \
  --scenario demand_140 \
  --scenario compound_stress \
  --seeds 50
```

After PPO training, add the learned policy to the same paired stress tests:

```bash
dmdtrl-stress \
  --model models/ppo_dispatcher.zip \
  --seeds 100 \
  --seed-start 30000 \
  --comparisons-output results/stress_ppo_comparisons.csv
```

The objective is to estimate a **robustness profile**, not merely one nominal test score: how quickly each policy degrades as demand, failures, due-date pressure, and processing capacity move away from training-like conditions.

## Train PPO

```bash
dmdtrl-train --steps 150000 --seed 42 --output models/ppo_dispatcher
```

The trained Stable-Baselines3 model is saved as `models/ppo_dispatcher.zip`.

## Repository structure

```text
.
├── .github/workflows/ci.yml
├── docs/
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

Current phase. Evaluate PPO out-of-sample against every fixed dispatching rule using paired stochastic seeds, confidence intervals, effect sizes, and decision latency.

### Phase 3 — rolling-horizon optimization

Add CP-SAT / MILP scheduling baselines and compare solution quality, compute time, and robustness under disturbances.

### Phase 4 — generalization study

Stress-test infrastructure is implemented. The next step is to train candidate policies only on nominal conditions and evaluate them without retraining across the predefined distribution-shift matrix.

The key scientific output will be the relationship between uncertainty/disruption level and the relative advantage of adaptive policies.

### Phase 5 — true flexible job-shop extension

Introduce multi-operation jobs, precedence constraints, alternative eligible machines, routing decisions, and variable feasible action sets. Candidate methods include action-masked PPO and graph-based state representations.

### Phase 6 — live decision-twin layer

Expose current twin state and recommended actions through an API/dashboard suitable for simulated or real production data.

## Scientific protocol

See [`docs/research_protocol.md`](docs/research_protocol.md) for predeclared evaluation standards, [`docs/stress_scenarios.md`](docs/stress_scenarios.md) for the OOD scenario definitions, and [`docs/roadmap.md`](docs/roadmap.md) for the phased research plan.

A learned policy should not be described as superior merely because training reward increases. If a classical OR or dispatching policy is faster, more robust, or operationally better, that is a valid and useful research result.

## License

MIT License. See [LICENSE](LICENSE).
