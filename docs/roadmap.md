# Research Roadmap

## Phase 2 — PPO hyper-heuristic with statistical validation

Status: infrastructure complete; long-horizon multi-training-seed study pending.

Completed infrastructure:

- reproducible PPO configuration and audit manifests;
- deterministic out-of-sample evaluation;
- disjoint training, validation, nominal-test, and stress-test seed regimes;
- raw seed-level KPI tables;
- bootstrap confidence intervals;
- paired randomization tests and effect sizes;
- probability of superiority;
- online decision-latency reporting;
- real Stable-Baselines3 integration CI.

Exit criterion: a multi-training-seed PPO experiment can make a defensible statement about whether PPO improves a predeclared operational KPI under nominal conditions.

## Phase 3 — Rolling-horizon OR benchmark

Status: operating-point validation campaign in progress.

Completed milestones:

- explicit job-machine decisions through the same simulator transition logic used by RL;
- released-job-only rolling-horizon CP-SAT;
- heterogeneous machine-dependent processing times;
- sequence-dependent initial and inter-job setups;
- strictly primary priority-weighted tardiness objective;
- bounded online solve time and measured decision latency;
- paired nominal comparison against all eight fixed rules;
- CP-SAT integration into every predefined distribution-shift scenario;
- scenario-local paired CP-SAT comparisons;
- matched PPO / CP-SAT / fixed-rule stress tables;
- horizon × solver-budget sensitivity grid;
- seed-level sensitivity results and bootstrap summaries;
- WTT/latency Pareto-front identification;
- paired comparison of each sensitivity point against a declared reference configuration;
- validation-only operating-point selector with complete-grid seed checks;
- dedicated 30-seed OR Validation workflow with uploaded raw, summary, comparison, and freeze artifacts.

Current Phase 3 sequence:

1. run the 30-seed validation sensitivity campaign on seeds `10000–10029`;
2. apply the predeclared Pareto + 2% WTT-tolerance latency selection rule;
3. review and freeze one CP-SAT horizon/budget operating point;
4. keep that configuration unchanged for all nominal `20000+` and stress `30000+` final-test experiments;
5. optionally add a forecast-aware OR variant later as a separately declared information regime.

The comparison must report objective quality, feasibility, decision time, robustness, and compute-budget sensitivity. The goal is not to make RL win; it is to identify operating regimes where each controller class is preferable.

## Phase 4 — Generalization and full comparative experiment

Status: comparative infrastructure implemented; full experimental campaign pending.

Controlled shifts currently include:

- +20%, +40%, +60% arrival intensity;
- 2x and 4x machine breakdown probability;
- tighter due dates;
- slower machine-speed distributions;
- higher sequence-dependent setup pressure;
- compound operational stress.

Before the final campaign:

1. freeze the CP-SAT operating point using validation seeds;
2. train PPO for a scientifically adequate horizon across multiple independent training seeds;
3. freeze PPO training/model-selection settings without using final test seeds;
4. evaluate PPO, frozen CP-SAT, and fixed rules on common nominal and stress test seeds.

Primary output: response surfaces showing how operational performance and decision latency change with uncertainty/disruption level, including direct paired PPO-vs-CP-SAT comparisons and each controller's advantage over the strongest fixed-rule comparator.

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

After the learned-policy/OR comparative milestone, the same architecture can be reused for:

1. joint production and predictive-maintenance scheduling;
2. dynamic EV routing and charging;
3. multi-echelon supply-chain disruption and allocation;
4. adaptive quality inspection.

The shared methodological template is:

**OR baseline + stochastic simulator/digital twin + adaptive policy + paired statistical validation.**
