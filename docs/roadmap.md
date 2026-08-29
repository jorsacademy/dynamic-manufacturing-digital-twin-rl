# Research Roadmap

## Phase 1 — Validated simulator and deterministic baselines

Status: **complete.**

Delivered:

- event-driven dynamic manufacturing simulator;
- stochastic arrivals, heterogeneous machines, sequence-dependent setups, failures/repairs, priorities, due dates, and quality risk;
- eight deterministic dispatching rules;
- operational KPI definitions and reproducible common-random-number evaluation;
- unit/integration tests and multi-version CI.

## Phase 2 — Rolling-horizon OR benchmark

Status: **complete and frozen.**

Delivered:

- released-job-only rolling-horizon CP-SAT;
- explicit job-machine assignment decisions through the same simulator transition logic used by RL;
- machine-dependent processing times and sequence-dependent setup transitions;
- bounded online solve time and measured decision latency;
- deterministic feasible fallback for solver `UNKNOWN` timeouts;
- solver reliability reporting;
- horizon × solver-budget sensitivity analysis;
- 30-seed validation campaign on `10000–10029`;
- reliability-gated operating-point selection;
- frozen H=8 / 100 ms provenance in `configs/cpsat_operating_point.json`.

Frozen OR operating point:

- horizon: **8 released jobs**;
- solve budget: **100 ms**;
- validation WTT: **72.5101**;
- mean decision latency: **21.4080 ms**;
- fallback rate: **0.00%**.

## Phase 3 — PPO hyper-heuristic multi-seed validation

Status: **complete and frozen.**

Delivered:

- Stable-Baselines3 PPO hyper-heuristic over eight dispatching rules;
- reproducible training manifests with runtime/package metadata;
- five independent 150,000-timestep training runs (`101, 202, 303, 404, 505`);
- common validation seeds `10000–10029`;
- bootstrap confidence intervals, paired tests, effect sizes, and probability of superiority;
- model/manifests SHA-256 verification;
- training-seed dispersion reporting;
- representative-model selection that does not cherry-pick the best seed;
- frozen validation provenance in `configs/ppo_validation_freeze.json`.

Validation WTT by training seed:

- seed 101: **77.0644**;
- seed 202: **83.4609**;
- seed 303: **73.8590**;
- seed 404: **72.9942**;
- seed 505: **83.2213**.

Scientific rule: final PPO claims retain all five training-seed realizations.

## Phase 4 — Full nominal and distribution-shift comparison

Status: **complete; final evidence frozen.**

Final campaign design:

- all five frozen PPO training-seed realizations;
- frozen CP-SAT H=8 / 100 ms;
- all eight fixed dispatching rules;
- nominal seeds `20000–20099`;
- nine OOD scenarios with common seeds `30000–30099`;
- priority-weighted tardiness as primary KPI;
- paired environment-seed comparisons;
- hierarchical bootstrap over PPO training-seed and environment-seed uncertainty;
- Holm correction across the twenty primary WTT tests;
- no controller or scenario retuning after final-test access.

Final result:

- `WEIGHTED_COMPOSITE` has lower mean WTT than the five-training-seed PPO mean in **10/10 scenarios**;
- PPO robustly beats frozen CP-SAT on WTT only under `compound_stress` after hierarchical training-seed uncertainty is retained;
- the same compound-stress regime is still won by `WEIGHTED_COMPOSITE`, so it is not an overall RL advantage;
- PPO training-seed WTT dispersion grows from **7.3307** nominally to **86.0259** under compound stress;
- PPO seed 303 is outcome-equivalent to `WEIGHTED_COMPOSITE` across all 1,000 final scenario-seed episodes, and seed 202 is outcome-equivalent to `MINIMUM_SETUP` / `SAME_FAMILY_FIRST` across all 1,000 episodes.

Scientific conclusion: the current parallel-machine state/action/reward formulation does not justify PPO complexity over the strongest fixed dispatching rule. This negative result is retained rather than tuned away.

Evidence:

- `docs/final_comparative_results.md`;
- `results/final_comparative/`;
- GitHub Actions final artifact `9712700007`.

## Phase 5 — True flexible job-shop and stronger adaptivity test

Status: **next manufacturing research phase.**

The current environment is a dynamic heterogeneous parallel-machine model. The next extension should introduce structural reasons for adaptive decision-making rather than retune PPO against locked final seeds.

Planned model upgrades:

- multi-operation jobs;
- precedence constraints;
- alternative eligible machines per operation;
- operation-dependent processing times;
- routing decisions;
- dynamic feasible action sets;
- richer family-to-family setup matrices;
- urgent-order bursts;
- explicitly pre-generated exogenous disruption plans;
- explicit physical completion events and completion-timed reward/KPI accounting;
- productive-utilization versus occupancy separation.

Planned RL/diagnostic upgrades:

- action/rule-selection trace logging;
- policy entropy and heuristic-switching diagnostics;
- action-masked PPO for dynamic feasibility;
- graph/attention state encoders if the FJSP structure warrants them;
- comparison with strong rolling-horizon OR and neighborhood-search baselines.

The locked Phase-4 final seeds remain untouched. Phase 5 receives new development/validation/final seed partitions.

## Phase 6 — Decision-twin service layer

Expose synchronized simulator state, KPIs, controller recommendations, and scenario controls through an API/dashboard.

Target capabilities:

- current WIP and queue state;
- machine/disruption state;
- selected RL rule or OR assignment;
- predicted tardiness risk;
- controller KPI/latency comparison;
- what-if scenario controls.

3D visualization remains optional. The core value is the synchronized decision model and closed-loop recommendation layer.

## Portfolio projects after this flagship

Follow-on repositories will use the same research-grade pattern—strong OR/control baseline, stochastic simulator or digital twin, adaptive policy, CI, and paired evaluation—while covering different IE/OR problem classes.

Planned sequence:

1. **Joint Production + Maintenance Decision Twin** — machine degradation, predictive-maintenance timing, queues, due-date pressure, failure risk, and rolling-horizon OR versus adaptive/hierarchical policies.
2. **Dynamic EV Routing + Charging Decision Twin** — OR-Tools/ALNS feasibility foundation with dynamic orders, traffic/charging uncertainty, and RL operator or strategy selection.
3. **Multi-Echelon Supply-Chain Decision Twin** — base-stock/stochastic-programming/MPC baselines versus adaptive inventory/allocation policies under nonstationarity and disruption.
4. **Adaptive Quality / Capacity extensions** — only where a distinct decision problem and strong baseline justify a separate project.

The shared portfolio methodology is:

**mathematical/OR baseline + stochastic simulator/digital twin + adaptive policy + compute/reliability accounting + paired out-of-sample validation.**
