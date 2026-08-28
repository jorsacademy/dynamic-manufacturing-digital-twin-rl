# Research Roadmap

## Phase 2 — PPO hyper-heuristic with statistical validation

Status: infrastructure complete; long-horizon multi-training-seed study is the next major workload.

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

Status: **operating point frozen for final evaluation.**

Completed milestones:

- explicit job-machine decisions through the same simulator transition logic used by RL;
- released-job-only rolling-horizon CP-SAT;
- heterogeneous machine-dependent processing times;
- sequence-dependent initial and inter-job setups;
- strictly primary priority-weighted tardiness objective;
- bounded online solve time and measured decision latency;
- deterministic emergency fallback for solver `UNKNOWN` timeouts, with fallback-rate reporting;
- paired nominal comparison against all eight fixed rules;
- CP-SAT integration into every predefined distribution-shift scenario;
- scenario-local paired CP-SAT comparisons;
- matched PPO / CP-SAT / fixed-rule stress tables;
- horizon × solver-budget sensitivity grid;
- seed-level sensitivity results and bootstrap summaries;
- WTT/latency Pareto-front identification;
- paired comparison of each sensitivity point against a declared reference configuration;
- validation-only operating-point selector with complete-grid and solver-reliability checks;
- 30-seed OR Validation campaign on seeds `10000–10029`;
- uploaded validation raw/summary/comparison/manifest artifact with verified SHA-256;
- frozen CP-SAT operating point committed in `configs/cpsat_operating_point.json`.

### Frozen OR operating point

The 30-seed 3×3 validation sweep selected:

- horizon: **8 released jobs**;
- solver budget: **100 ms per decision**;
- validation mean priority-weighted tardiness: **72.5101**;
- validation mean decision latency: **21.4080 ms**;
- validation mean solver fallback rate: **0.00%**.

The best reliable Pareto WTT was 72.5101 and the predeclared 2% acceptance threshold was 73.9603. H8 / 50 ms achieved WTT 74.138 and therefore fell outside the declared tolerance despite its lower latency. H8 / 100 ms was consequently the only acceptable Pareto configuration.

Relative to the declared H12 / 100 ms reference, H8 / 100 ms showed a 5.59% lower mean WTT on validation seeds, but the paired 95% interval crossed zero and the paired randomization p-value was about 0.225. This is model-selection evidence, not a claim of statistically established superiority.

Phase 3 freeze rule: **H=8 and 0.10 s must remain unchanged for nominal `20000+` and stress `30000+` final-test experiments.**

A forecast-aware OR variant may be added later only as a separately declared information regime; it must not replace or retune the frozen comparator after final-test inspection.

## Phase 4 — Generalization and full comparative experiment

Status: comparative infrastructure implemented; full experimental campaign pending after PPO model selection is frozen.

Controlled shifts currently include:

- +20%, +40%, +60% arrival intensity;
- 2x and 4x machine breakdown probability;
- tighter due dates;
- slower machine-speed distributions;
- higher sequence-dependent setup pressure;
- compound operational stress.

Before the final campaign:

1. **CP-SAT operating point: complete and frozen at H=8 / 100 ms.**
2. train PPO for a scientifically adequate horizon across multiple independent training seeds;
3. select/freeze PPO settings using validation data only;
4. evaluate PPO, frozen CP-SAT, and fixed rules on common nominal and stress final-test seeds.

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
