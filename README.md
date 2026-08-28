# Dynamic Manufacturing Digital Twin with Reinforcement Learning

A research-oriented industrial engineering / operations research project for **dynamic production scheduling under uncertainty**.

The repository implements an event-driven manufacturing digital twin and formulates real-time dispatching as a reinforcement-learning hyper-heuristic. Instead of assigning an RL action to every `(job, machine)` pair, the agent selects a dispatching policy at each decision epoch. This keeps the action space fixed while allowing the policy to adapt to stochastic arrivals, heterogeneous machines, sequence-dependent setups, due-date pressure, and random breakdowns.

## Research question

> Under what levels of demand variability and operational disruption does an adaptive RL hyper-heuristic outperform fixed dispatching rules and, in later phases, rolling-horizon OR methods?

The project is intentionally structured around **benchmarking**, not training reward alone.

## Current v0.1 scope

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
- PPO training entry point;
- common-random-number baseline experiments;
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

## OR / IE performance metrics

Experiments report operational KPIs independently from the RL reward:

- makespan;
- mean waiting time;
- total tardiness;
- priority-weighted tardiness;
- setup time;
- repair/disruption time;
- on-time completion rate;
- machine utilization;
- mean processed quality risk.

## Installation

Core simulation and baselines:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev,analysis]"
```

For PPO training:

```bash
pip install -e ".[rl,dev,analysis]"
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

All policies are evaluated with the same random seeds so that they face comparable synthetic job streams and disruptions.

## Train PPO

```bash
dmdtrl-train --steps 150000 --seed 42 --output models/ppo_dispatcher
```

The trained Stable-Baselines3 model is saved as `models/ppo_dispatcher.zip`.

## Repository structure

```text
.
├── .github/workflows/ci.yml
├── src/dmdtrl/
│   ├── dispatch.py
│   ├── env.py
│   ├── evaluate.py
│   ├── generator.py
│   ├── models.py
│   └── train.py
├── tests/
├── pyproject.toml
└── README.md
```

## Planned research phases

### Phase 1 — validated simulation + deterministic OR baselines

Current phase. Validate event logic and establish reproducible KPI baselines.

### Phase 2 — PPO hyper-heuristic benchmark

Train PPO and evaluate it out-of-sample against every fixed dispatching rule with confidence intervals and paired statistical tests.

### Phase 3 — rolling-horizon optimization

Add CP-SAT / MILP scheduling baselines and compare solution quality, compute time, and robustness under disturbances.

### Phase 4 — generalization study

Train under nominal conditions and test under distribution shifts:

- +20% / +40% arrival intensity;
- elevated breakdown probability;
- unseen machine-speed profiles;
- changed job-family mix;
- tighter due dates.

### Phase 5 — graph representation

Represent the shop floor and waiting jobs as a graph and study GNN-based state encoding or action-masked direct scheduling.

### Phase 6 — live decision-twin layer

Expose current twin state and recommended actions through an API/dashboard suitable for connection to simulated or real production data.

## Scientific use

For credible RL-vs-OR comparisons, future experiments should report multiple random seeds, confidence intervals, out-of-distribution tests, wall-clock decision time, and explicit baseline tuning. A learned policy should not be judged only by cumulative training reward.

## License

MIT License. See [LICENSE](LICENSE).
