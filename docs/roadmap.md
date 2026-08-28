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

Status: **long-horizon campaign in progress.**

Already implemented:

- Stable-Baselines3 PPO hyper-heuristic over eight dispatching rules;
- reproducible training manifests with runtime/package metadata;
- deterministic out-of-sample evaluation;
- bootstrap confidence intervals, paired randomization tests, effect sizes, and probability of superiority;
- RL Smoke integration workflow;
- explicit disjoint training/validation/final-test seed regimes.

The v0.9 campaign is predeclared in `configs/ppo_validation_campaign.json`:

- five independent training seeds: `101, 202, 303, 404, 505`;
- 150,000 timesteps per training member;
- fixed PPO hyperparameters across all members;
- common validation seeds `10000–10029`;
- model archives and manifests retained as workflow artifacts;
- SHA-256 artifact verification;
- one validation summary row per training seed;
- aggregate training-seed dispersion;
- a representative model selected by median-role WTT, not by best validation performance.

Scientific rule: **final PPO claims aggregate all five declared training seeds.** The representative model exists only for demo/deployment continuity and must not replace multi-seed evidence.

Exit criterion:

1. all five 150k-step trainings complete successfully;
2. every member contains the complete common validation seed set;
3. campaign manifest and artifact hashes are verified;
4. training-seed variability is reviewed;
5. the representative model identity and PPO design are frozen without using `20000+` or `30000+` data.

See `docs/ppo_multiseed.md`.

## Phase 4 — Full nominal and distribution-shift comparison

Status: **next after PPO freeze.**

Controllers:

- all five frozen PPO training-seed realizations;
- frozen CP-SAT H=8 / 100 ms;
- all eight fixed dispatching rules.

Nominal final-test regime:

- common seeds beginning at `20000`;
- priority-weighted tardiness as the primary operational KPI;
- decision latency and reliability reported alongside objective quality;
- paired controller comparisons on identical stochastic realizations.

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
