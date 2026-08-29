# Dynamic Manufacturing Digital Twin with Reinforcement Learning

A research-oriented industrial engineering / operations research project for **dynamic production scheduling under uncertainty**.

The repository implements an event-driven manufacturing digital twin and compares eight fixed dispatching rules, a multi-seed PPO hyper-heuristic, and rolling-horizon CP-SAT optimization on common stochastic realizations.

> Current scope: dynamic heterogeneous parallel-machine scheduling. A true flexible job-shop representation with multi-operation routing and precedence constraints is the next manufacturing research extension.

## Research question

> Under what levels of demand variability and operational disruption does an adaptive RL hyper-heuristic provide material value over fixed dispatching rules and rolling-horizon optimization, after accounting for online decision latency, solver reliability, and RL training-seed variability?

The repository is built around reproducibility, paired benchmarking, model-selection discipline, disjoint validation/final-test data, and willingness to report a negative RL result.

## Current v1.0 status

The complete nominal + distribution-shift comparative campaign is finished.

Research infrastructure includes:

- stochastic arrivals, heterogeneous machines, sequence-dependent setups, breakdown/repair delays, priorities, due dates, and quality risk;
- fourteen normalized operational state features and eight deterministic dispatching rules;
- PPO hyper-heuristic training with reproducibility manifests;
- rolling-horizon CP-SAT with released-job-only information and explicit job-machine assignments;
- deterministic CP-SAT timeout fallback plus measured solver reliability;
- CP-SAT horizon × solve-budget sensitivity analysis and a frozen operating point;
- five independent 150,000-timestep PPO training runs and frozen model hashes;
- independent artifact/hash verification for both adaptive controller families;
- 100-seed nominal and 100-seed-per-scenario final evaluation across nine OOD stress regimes;
- hierarchical bootstrap over PPO training-seed and environment-seed uncertainty;
- paired randomization tests, effect sizes, probability of superiority, and Holm correction;
- Python 3.10/3.11/3.12 CI plus RL, OR-validation, PPO-validation, and final-comparison workflows.

Seed regimes are deliberately separated:

- training randomness: below `10000`;
- validation/model selection: `10000–19999`;
- nominal final test: `20000–20099`;
- stress final test: `30000–30099`.

## Final comparative conclusion

The final experiment does **not** support the claim that PPO adds value over the strongest fixed dispatching rule in the current scheduling formulation.

`WEIGHTED_COMPOSITE` has lower mean priority-weighted tardiness than the five-training-seed PPO mean in **all 10 final scenarios**.

Selected results:

| Scenario | PPO seed-mean WTT | Weighted Composite WTT | CP-SAT WTT |
| --- | ---: | ---: | ---: |
| nominal | 70.7847 | **63.2547** | 69.1594 |
| demand +60% | 547.4742 | **489.9622** | 572.7199 |
| breakdown 4× | 166.9652 | **152.2761** | 166.1493 |
| setup 2× | 195.6319 | **186.9471** | 205.5845 |
| compound stress | 820.9690 | **757.3032** | 896.0073 |

PPO robustly beats the frozen CP-SAT controller on primary weighted tardiness only under `compound_stress` after PPO training-seed uncertainty is retained: **8.37% improvement**, hierarchical 95% interval **[1.1970, 142.0060]**, Holm-adjusted paired p-value **0.0020**. This is not an overall RL win because Weighted Composite is still better in the same regime.

Training-seed instability is material. PPO WTT standard deviation across the five frozen training seeds rises from **7.3307** nominally to **86.0259** under compound stress. One PPO model (seed 303) produces final episode-level KPI vectors exactly identical to `WEIGHTED_COMPOSITE` across all 1,000 scenario-seed episodes, while seed 202 exactly matches `MINIMUM_SETUP` / `SAME_FAMILY_FIRST`. These are outcome-equivalence diagnostics, consistent with policy collapse toward existing heuristics; direct action-trace logging is a planned diagnostic extension.

Full interpretation and evidence: [`docs/final_comparative_results.md`](docs/final_comparative_results.md).

Compact frozen result files: [`results/final_comparative/`](results/final_comparative/).

## Controller formulations

### PPO hyper-heuristic

The PPO agent receives a 14-dimensional normalized operational state and selects one of eight dispatching rules: FIFO, highest priority, EDD, SPT, same-family-first, minimum setup, critical ratio, or a weighted composite rule.

The RL action therefore selects a dispatching heuristic rather than an arbitrary job-machine pair. This keeps the action space fixed and feasible while testing whether state-dependent heuristic switching adds value.

Five frozen PPO models use training seeds `101, 202, 303, 404, 505`, each trained for 150,000 timesteps. Scientific claims retain all five training-seed realizations; the best seed is never substituted for the multi-seed result.

Frozen PPO provenance and hashes are stored in [`configs/ppo_validation_freeze.json`](configs/ppo_validation_freeze.json).

### Rolling-horizon CP-SAT

At each decision epoch CP-SAT sees only jobs already released into the queue and machines currently available. It cannot inspect future arrivals, breakdown realizations, or repair durations.

The optimizer plans a bounded released-job horizon with machine-dependent processing durations and sequence-dependent setups, executes only the first assignment, and replans. Priority-weighted tardiness is the primary objective.

The frozen final configuration is:

- horizon: **8 released jobs**;
- solve budget: **100 ms per decision**;
- validation mean WTT: **72.5101**;
- validation mean decision latency: **21.4080 ms**;
- validation fallback rate: **0.00%**.

Frozen provenance is stored in [`configs/cpsat_operating_point.json`](configs/cpsat_operating_point.json).

## Final-test design

The final campaign used:

- nominal seeds `20000–20099`;
- nine stress scenarios with seeds `30000–30099`;
- all eight fixed rules;
- all five frozen PPO models;
- frozen CP-SAT H=8 / 100 ms;
- 5,000 bootstrap resamples;
- 10,000 paired randomization permutations;
- Holm correction across the 20 primary PPO-vs-Weighted-Composite / PPO-vs-CP-SAT WTT tests.

For primary PPO inference, metrics are first averaged across the five PPO training seeds within each environment seed, then compared pairwise across environment seeds. Weighted-tardiness confidence intervals additionally use a hierarchical bootstrap over both training and environment seeds. The 5 × N PPO rows are not treated as independent observations.

No PPO hyperparameter, training seed, CP-SAT setting, scenario definition, fixed baseline, or final seed range was changed after final-test outcomes were observed.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[rl,or,dev,analysis]"
```

## Tests

```bash
pytest
ruff check src tests
```

## Reproduce one PPO member

```bash
dmdtrl-train \
  --steps 150000 \
  --seed 101 \
  --output models/ppo_dispatcher \
  --metadata models/ppo_dispatcher_manifest.json \
  --device cpu \
  --quiet
```

See [`docs/ppo_reproducibility.md`](docs/ppo_reproducibility.md).

## Distribution-shift scenarios

The final OOD matrix includes:

- +20%, +40%, +60% arrival intensity;
- 2× and 4× breakdown probability;
- tighter due dates;
- slower machines;
- 2× setup pressure;
- compound demand/disruption/due-date/speed/setup stress.

## GitHub Actions

- `CI`: Python 3.10/3.11/3.12 lint, tests, coverage, research smoke, stress smoke, CP-SAT smoke, and sensitivity smoke.
- `RL Smoke`: short Stable-Baselines3 training/inference integration test; not policy-quality evidence.
- `OR Validation`: completed 30-seed CP-SAT validation campaign with reliability gating and artifacts.
- `PPO Validation`: completed five-member long-horizon PPO campaign with common validation seeds, model artifacts, hashes, and aggregate manifest.
- `Final Comparative Campaign`: completed frozen nominal + nine-scenario OOD campaign with completeness, seed-boundary, hash, and artifact gates.

## Research phases

1. **Validated simulator + deterministic baselines:** complete.
2. **Rolling-horizon OR baseline and operating-point freeze:** complete; frozen at **H=8 / 100 ms**.
3. **PPO hyper-heuristic multi-seed validation:** complete; five models frozen.
4. **Full nominal + stress comparative experiment:** **complete**; final evidence frozen.
5. **True flexible job-shop / richer adaptivity extension:** next research phase.
6. **Decision-twin service/dashboard layer:** planned.

See [`docs/roadmap.md`](docs/roadmap.md).

## What the negative result means

The project intentionally does not tune PPO against final seeds or hide unfavorable training seeds. In the current model, a very cheap hand-designed composite rule is difficult to beat and several PPO training realizations converge toward behavior that is operationally indistinguishable from existing heuristics.

That result narrows the next research question. Future RL work should target problem structure where state-dependent adaptation has a credible role: multi-operation routing and precedence, changing machine eligibility, urgent-order bursts, richer family-to-family setups, explicitly pre-generated exogenous disruption plans, and larger dynamic feasible action sets.

## Portfolio sequence

This repository is the first flagship. Planned follow-on repositories cover joint production/maintenance decisions, dynamic EV routing and charging, multi-echelon supply-chain decisions, and other IE/OR decision-twin problems. The shared standard is:

**OR baseline + stochastic simulator/digital twin + adaptive policy + compute/reliability accounting + paired out-of-sample validation.**

## Scientific principle

A learned policy is not superior because training reward rises, and an optimizer is not superior because it solves a mathematical model. Operational KPIs, online compute cost, solver reliability, training-seed variability, robustness, and paired out-of-sample evidence determine the conclusion. A fixed heuristic winning is a valid and useful result.

## License

MIT License. See [LICENSE](LICENSE).
