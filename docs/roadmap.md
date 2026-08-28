# Research Roadmap

## Phase 2 — PPO hyper-heuristic with statistical validation

Status: infrastructure complete; long-horizon multi-training-seed study pending.

Deliverables:

- PPO training with reproducible configuration;
- deterministic out-of-sample PPO evaluation;
- raw seed-level result tables;
- bootstrap confidence intervals;
- paired randomization tests and effect sizes;
- decision-latency reporting;
- PPO vs eight fixed dispatching rules.

Completed infrastructure: seed-level paired evaluation, confidence intervals, effect sizes, randomization tests, decision-latency measurement, PPO model adapters, audit manifests, disjoint nominal/stress seed ranges, and real Stable-Baselines3 integration CI.

Exit criterion: a multi-training-seed PPO experiment can make a defensible statement about whether PPO improves a predeclared operational KPI under nominal conditions.

## Phase 3 — Rolling-horizon OR benchmark

Status: in progress.

Current implementation milestone:

- explicit job-machine decision path through the same simulator transition logic used by RL;
- rolling-horizon CP-SAT over released jobs only;
- heterogeneous machine-dependent processing times;
- sequence-dependent initial and inter-job setup transitions;
- priority-weighted tardiness objective with setup/makespan tie breakers;
- fixed online solver budget and measured decision latency;
- paired nominal comparison against all eight dispatching rules.

Next Phase 3 milestones:

- validate the nominal CP-SAT benchmark across a larger seed set;
- add CP-SAT to the predefined distribution-shift suite;
- run three-way PPO vs CP-SAT vs fixed-rule comparisons;
- study horizon length and solver-budget sensitivity;
- optionally add a forecast-aware OR variant as a separately declared information regime.

Compare:

- objective quality;
- feasibility;
- solve/decision time;
- robustness to disruptions;
- value of reoptimization frequency;
- sensitivity to horizon and compute budget.

The goal is not to make RL win. The goal is to identify operating regimes where each approach is preferable.

## Phase 4 — Generalization and stress testing

Status: stress-test infrastructure implemented; learned-policy and OR comparative study pending.

The repository now provides controlled shifts for:

- +20%, +40%, +60% arrival intensity;
- 2x and 4x machine breakdown probability;
- tighter due dates;
- slower machine-speed distributions;
- higher sequence-dependent setup pressure;
- compound operational stress.

The learned policy must be trained under nominal conditions and evaluated without retraining across these scenarios. The OR controller must use only the information explicitly available at each decision epoch. Future simulator extensions will add explicit urgent-order bursts and other event processes rather than approximating them through reward penalties.

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
- selected dispatch rule or OR assignment;
- predicted tardiness risk;
- baseline vs learned-policy vs OR KPI comparison;
- what-if scenarios.

3D visualization is optional. The core industrial-engineering value is the synchronized decision model, not graphics.

## Follow-on project family

After this repository reaches the learned-policy/OR stress-test milestone, the same research architecture will be reused in separate repositories for:

1. joint production and predictive-maintenance scheduling;
2. dynamic EV routing and charging;
3. multi-echelon supply-chain disruption and allocation;
4. adaptive quality inspection.

The shared methodological template is:

**OR baseline + stochastic simulator/digital twin + adaptive policy + paired statistical validation.**
