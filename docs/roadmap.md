# Research Roadmap

## Phase 2 — PPO hyper-heuristic with statistical validation

Status: in progress.

Deliverables:

- PPO training with reproducible configuration;
- deterministic out-of-sample PPO evaluation;
- raw seed-level result tables;
- bootstrap confidence intervals;
- paired randomization tests and effect sizes;
- decision-latency reporting;
- PPO vs eight fixed dispatching rules.

Exit criterion: the evaluation harness can make a defensible statement about whether PPO improves a predeclared operational KPI under nominal conditions.

## Phase 3 — Rolling-horizon OR benchmark

Add CP-SAT or MILP scheduling with a finite look-ahead horizon.

Compare:

- objective quality;
- feasibility;
- solve/decision time;
- robustness to disruptions;
- value of reoptimization frequency.

The goal is not to make RL win. The goal is to identify operating regimes where each approach is preferable.

## Phase 4 — Generalization and stress testing

Train under nominal conditions and test under controlled distribution shifts:

- +20%, +40%, +60% arrival intensity;
- increased machine breakdown probability;
- tighter due dates;
- unseen machine-speed distributions;
- setup-heavy product-family mixes;
- urgent-order bursts.

Primary output: an uncertainty/disruption response surface showing relative policy performance.

## Phase 5 — True flexible job-shop extension

The current environment is a dynamic heterogeneous parallel-machine model. This phase introduces a true FJSP representation:

- multi-operation jobs;
- precedence constraints;
- alternative eligible machines per operation;
- operation-dependent processing times;
- routing decisions;
- variable feasible action sets.

Candidate methods:

- action-masked PPO;
- graph neural network state encoding;
- RL hyper-heuristics that select dispatching/optimization operators.

## Phase 6 — Decision-twin service layer

Expose simulator state, KPIs, policy recommendations, and scenario controls through an API/dashboard.

The service layer should support:

- current WIP and queue state;
- machine availability and disruption state;
- selected dispatch rule;
- predicted tardiness risk;
- baseline vs learned-policy KPI comparison;
- what-if scenarios.

3D visualization is optional. The core industrial-engineering value is the synchronized decision model, not graphics.

## Follow-on project family

After this repository reaches Phase 4, the same research architecture will be reused in separate repositories for:

1. joint production and predictive-maintenance scheduling;
2. dynamic EV routing and charging;
3. multi-echelon supply-chain disruption and allocation;
4. adaptive quality inspection.

The shared methodological template is:

**OR baseline + stochastic simulator/digital twin + adaptive policy + paired statistical validation.**
