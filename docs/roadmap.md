# Research Roadmap

## Phase 2 — PPO hyper-heuristic with statistical validation

Status: infrastructure complete; long-horizon multi-training-seed study pending.

Completed infrastructure:

- reproducible PPO configuration and audit manifests;
- deterministic out-of-sample evaluation;
- disjoint training, nominal-test, and stress-test seed regimes;
- raw seed-level KPI tables;
- bootstrap confidence intervals;
- paired randomization tests and effect sizes;
- probability of superiority;
- online decision-latency reporting;
- real Stable-Baselines3 integration CI.

Exit criterion: a multi-training-seed PPO experiment can make a defensible statement about whether PPO improves a predeclared operational KPI under nominal conditions.

## Phase 3 — Rolling-horizon OR benchmark

Status: in progress; nominal and distribution-shift infrastructure implemented.

Completed milestones:

- explicit job-machine decision path through the same simulator transition logic used by RL;
- rolling-horizon CP-SAT over released jobs only;
- heterogeneous machine-dependent processing times;
- sequence-dependent initial and inter-job setup transitions;
- strictly primary priority-weighted tardiness objective with setup/makespan tie breakers;
- fixed online solver budget and measured decision latency;
- paired nominal comparison against all eight dispatching rules;
- CP-SAT integration into the predefined distribution-shift suite;
- scenario-local paired CP-SAT vs fixed-rule comparisons;
- matched stress tables that can contain PPO, CP-SAT, and all fixed rules on identical seeds.

Next Phase 3 milestones:

- horizon-length sensitivity study;
- solver-budget sensitivity study;
- larger-seed nominal and stress benchmarks;
- direct PPO vs CP-SAT operating-region analysis after long-horizon PPO training;
- optionally add a forecast-aware OR variant as a separately declared information regime.

The comparison must report objective quality, feasibility, decision time, robustness, and compute-budget sensitivity. The goal is not to make RL win; it is to identify operating regimes where each controller class is preferable.

## Phase 4 — Generalization and stress testing

Status: comparative infrastructure implemented; full experimental campaign pending.

Controlled shifts currently include:

- +20%, +40%, +60% arrival intensity;
- 2x and 4x machine breakdown probability;
- tighter due dates;
- slower machine-speed distributions;
- higher sequence-dependent setup pressure;
- compound operational stress.

PPO must be trained under nominal conditions and evaluated without retraining. CP-SAT must use only the information available at each decision epoch. All controllers are evaluated on common random seeds within each scenario.

Primary output: response surfaces showing how operational performance and decision latency change with uncertainty/disruption level, including the paired advantage of PPO and CP-SAT over the strongest fixed-rule comparator.

## Phase 5 — True flexible job-shop extension

The current environment is a dynamic heterogeneous parallel-machine model. This phase introduces a true FJSP representation:

- multi-operation jobs;
- precedence constraints;
- alternative eligible machines per operation;
- operation-dependent processing times;
- routing decisions;
- variable feasible action sets.

Candidate methods include action-masked PPO, graph neural network state encoding, and hyper-heuristics that select dispatching or optimization operators.

## Phase 6 — Decision-twin service layer

Expose simulator state, KPIs, policy recommendations, and scenario controls through an API/dashboard.

The service layer should support current WIP, machine/disruption state, selected dispatch rule or OR assignment, predicted tardiness risk, controller KPI comparison, and what-if scenarios.

3D visualization is optional. The core industrial-engineering value is the synchronized decision model, not graphics.

## Follow-on project family

After the learned-policy/OR stress-test milestone, the same architecture can be reused for:

1. joint production and predictive-maintenance scheduling;
2. dynamic EV routing and charging;
3. multi-echelon supply-chain disruption and allocation;
4. adaptive quality inspection.

The shared methodological template is:

**OR baseline + stochastic simulator/digital twin + adaptive policy + paired statistical validation.**
