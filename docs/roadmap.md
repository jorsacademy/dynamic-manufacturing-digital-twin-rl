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

Completed infrastructure: seed-level paired evaluation, confidence intervals, effect sizes, randomization tests, decision-latency measurement, and PPO model adapters.

Exit criterion: the evaluation harness can make a defensible statement about whether PPO improves a predeclared operational KPI under nominal conditions.

## Phase 3 — Rolling-horizon OR benchmark

Status: planned after the first PPO benchmark.

Add CP-SAT or MILP scheduling with a finite look-ahead horizon.

Compare:

- objective quality;
- feasibility;
- solve/decision time;
- robustness to disruptions;
- value of reoptimization frequency.

The goal is not to make RL win. The goal is to identify operating regimes where each approach is preferable.

## Phase 4 — Generalization and stress testing

Status: stress-test infrastructure implemented; learned-policy study pending.

The repository now provides controlled shifts for:

- +20%, +40%, +60% arrival intensity;
- 2x and 4x machine breakdown probability;
- tighter due dates;
- slower machine-speed distributions;
- higher sequence-dependent setup pressure;
- compound operational stress.

The learned policy must be trained under nominal conditions and evaluated without retraining across these scenarios. Future simulator extensions will add explicit urgent-order bursts and other event processes rather than approximating them through reward penalties.

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

After this repository reaches the learned-policy stress-test milestone, the same research architecture will be reused in separate repositories for:

1. joint production and predictive-maintenance scheduling;
2. dynamic EV routing and charging;
3. multi-echelon supply-chain disruption and allocation;
4. adaptive quality inspection.

The shared methodological template is:

**OR baseline + stochastic simulator/digital twin + adaptive policy + paired statistical validation.**
