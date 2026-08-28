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

Status: **complete and frozen for final evaluation.**

Delivered:

- released-job-only rolling-horizon CP-SAT;
- explicit job-machine assignment decisions through the same simulator transition logic used by RL;
- machine-dependent processing times and sequence-dependent setup transitions;
- primary priority-weighted tardiness objective;
- bounded online solve time and measured decision latency;
- deterministic feasible fallback for solver `UNKNOWN` timeouts;
- solver fallback/success-rate reporting;
- nominal and stress integration;
- horizon × solver-budget sensitivity study;
- 30-seed validation campaign on `10000–10029`;
- complete-grid, reliability-gated operating-point selector;
- independently verified validation artifact;
- frozen configuration in `configs/cpsat_operating_point.json`.

Frozen OR operating point:

- horizon: **8 released jobs**;
- solve budget: **100 ms**;
- validation WTT: **72.5101**;
- mean decision latency: **21.4080 ms**;
- fallback rate: **0.00%**.

Freeze rule: H=8 / 100 ms remains unchanged for nominal `20000+` and stress `30000+` final-test experiments.

## Phase 3 — PPO hyper-heuristic multi-seed validation

Status: **complete and frozen for final evaluation.**

Delivered:

- Stable-Baselines3 PPO hyper-heuristic over eight dispatching rules;
- reproducible training manifests with runtime/package metadata;
- deterministic out-of-sample validation;
- five independent 150,000-timestep training runs (`101, 202, 303, 404, 505`);
- common validation seeds `10000–10029` for every learned policy;
- bootstrap confidence intervals, paired randomization tests, effect sizes, and probability of superiority;
- model/manifests SHA-256 verification;
- aggregate training-seed dispersion reporting;
- independent download and verification of the aggregate GitHub Actions artifact;
- median-role representative-model selection that does not cherry-pick the best PPO seed;
- frozen validation provenance in `configs/ppo_validation_freeze.json`.

Validation WTT by training seed:

- seed 101: **77.0644**;
- seed 202: **83.4609**;
- seed 303: **73.8590**;
- seed 404: **72.9942**;
- seed 505: **83.2213**.

Across the five independent training seeds:

- mean WTT: **78.1200**;
- median WTT: **77.0644**;
- sample standard deviation: **5.0023**;
- minimum: **72.9942**;
- maximum: **83.4609**.

The predeclared median-role representative model is **training seed 101**, with model SHA-256 `a3172d12c59a8585a2ded6ff8e1ae2bbf3287b5ca97d183cf06841e12d6980e3`.

Scientific rule: **final PPO claims retain all five declared training-seed realizations.** Seed 101 is only the representative model for demo/deployment continuity and is not substituted for multi-seed evidence.

See `docs/ppo_multiseed.md` and `docs/ppo_validation_results.md`.

## Phase 4 — Full nominal and distribution-shift comparison

Status: **next active research phase.**

Controllers are now frozen before final-test data are analyzed:

- all five PPO training-seed realizations;
- CP-SAT H=8 / 100 ms;
- all eight fixed dispatching rules.

Nominal final-test regime:

- common seeds beginning at `20000`;
- priority-weighted tardiness as the primary operational KPI;
- decision latency and CP-SAT reliability reported alongside objective quality;
- training-seed variability retained explicitly;
- direct paired controller comparisons on identical stochastic environment seeds.

Stress final-test regime begins at `30000` and includes:

- +20%, +40%, +60% arrival intensity;
- 2× and 4× breakdown probability;
- tighter due dates;
- slower machine speeds;
- increased sequence-dependent setup pressure;
- compound operational stress.

Primary research output: response surfaces identifying the operating regimes in which PPO, rolling-horizon optimization, or simple rules are preferable. The objective is not to force an RL win.

## Phase 5 — True flexible job-shop extension

The current environment is a dynamic heterogeneous parallel-machine model. The next manufacturing research extension introduces:

- multi-operation jobs;
- precedence constraints;
- alternative eligible machines per operation;
- operation-dependent processing times;
- routing decisions;
- dynamic feasible action sets.

Candidate methods:

- action-masked PPO;
- graph neural network state encoders;
- attention/pointer policies;
- RL hyper-heuristics that choose scheduling or neighborhood-search operators.

## Phase 6 — Decision-twin service layer

Expose synchronized simulator state, KPIs, controller recommendations, and scenario controls through an API/dashboard.

Target capabilities:

- current WIP and queue state;
- machine/disruption state;
- selected RL rule or OR assignment;
- predicted tardiness risk;
- PPO/CP-SAT/heuristic KPI comparison;
- what-if scenario controls.

3D visualization remains optional. The core value is the synchronized decision model and closed-loop recommendation layer.

## Portfolio projects after this flagship

The manufacturing scheduler is the first flagship repository, not the only project. Follow-on repositories will use the same research-grade pattern—strong OR/control baseline, stochastic simulator or digital twin, adaptive policy, CI, and paired evaluation—while covering different IE/OR problem classes.

Planned sequence:

1. **Safe Continuous Process Optimization** — injection-molding-style process control using SAC/TD3/PPO versus MPC and Bayesian optimization, with explicit operating constraints and disturbance robustness.
2. **Multi-Echelon Inventory under Nonstationary Demand** — classical base-stock/(s,S)/stochastic-DP baselines versus deep RL under lead-time uncertainty, demand shifts, backlog/lost sales, and multi-product or multi-echelon structure.
3. **Dynamic Vehicle Routing with RL Hyper-Heuristics** — OR-Tools/ALNS foundation with dynamic orders, cancellations, traffic, urgent requests, and RL selection of destroy/repair or local-search operators.
4. **Joint Maintenance + Production Scheduling** — machine degradation, predictive-maintenance timing, queues, due-date pressure, failure risk, and rolling-horizon OR versus adaptive/hierarchical policies.
5. **Real-Time Capacity & Workforce Control** — stochastic queues, service capacity/workforce decisions, forecast uncertainty, and PPO/DQN-style adaptive control against queueing/optimization baselines.

Additional network/safe-RL prototypes will be incorporated only when they add a distinct research contribution; static shortest-path or toy grid-world versions will not be treated as standalone portfolio flagships.

The shared portfolio methodology is:

**mathematical/OR baseline + stochastic simulator/digital twin + adaptive policy + compute/reliability accounting + paired out-of-sample validation.**
