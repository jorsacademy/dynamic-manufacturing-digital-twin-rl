# Dynamic Manufacturing Digital Twin with Reinforcement Learning

A research-oriented industrial engineering / operations research project for **dynamic production scheduling under uncertainty**.

The repository implements an event-driven manufacturing digital twin and compares three online scheduling controller classes: fixed dispatching rules, a PPO hyper-heuristic, and rolling-horizon CP-SAT optimization. All controllers share the same simulator transitions and are evaluated with common random seeds.

> Current scope: dynamic heterogeneous parallel-machine scheduling. A true flexible job-shop representation with multi-operation routing and precedence constraints is a later phase.

## Research question

> Under what levels of demand variability and operational disruption does an adaptive RL hyper-heuristic provide material value over fixed dispatching rules and rolling-horizon optimization, after accounting for online decision latency and controller reliability?

The repository is built around reproducibility, paired benchmarking, model-selection discipline, and disjoint validation/final-test data—not training reward alone.

## Current v0.9 scope

Implemented research infrastructure includes:

- stochastic arrivals, heterogeneous machines, sequence-dependent setups, breakdown/repair delays, priorities, due dates, and quality risk;
- fourteen normalized operational state features and eight deterministic dispatching rules;
- PPO hyper-heuristic training with audit manifests;
- rolling-horizon CP-SAT with explicit job-machine assignments and released-job-only information;
- deterministic timeout fallback plus measured solver fallback/success rates;
- CP-SAT horizon × solve-budget sensitivity analysis;
- completed 30-seed OR validation campaign and a frozen CP-SAT operating point;
- long-horizon multi-training-seed PPO validation design;
- seed-level KPIs, bootstrap confidence intervals, paired randomization tests, effect sizes, and probability of superiority;
- nominal and distribution-shift evaluation harnesses;
- Python 3.10/3.11/3.12 CI, RL integration smoke tests, OR Validation, and PPO Validation workflows.

Seed regimes are deliberately separated:

- training randomness: below `10000`;
- validation/model selection: `10000–19999`;
- nominal final test: `20000+`;
- stress final test: `30000+`.

## Controller formulations

### PPO hyper-heuristic

The PPO agent receives a 14-dimensional normalized operational state and selects one of eight dispatching rules: FIFO, highest priority, EDD, SPT, same-family-first, minimum setup, critical ratio, or a weighted composite rule.

The RL action therefore selects a dispatching heuristic rather than an arbitrary job-machine pair. This keeps the action space fixed and feasible while allowing the policy to adapt its scheduling logic to current shop conditions.

### Rolling-horizon CP-SAT

At each decision epoch CP-SAT sees only jobs already released into the queue and machines currently available. It cannot inspect future arrivals, breakdown realizations, or repair durations.

The optimizer plans a bounded released-job horizon with machine-dependent processing durations and sequence-dependent setups, executes only the first assignment, and replans. Priority-weighted tardiness is the primary objective.

If the online budget expires with solver status `UNKNOWN`, a deterministic one-step feasible assignment keeps the plant moving and the fallback is recorded. `INFEASIBLE` and model-invalid states remain hard failures.

## Frozen CP-SAT operating point

The completed validation campaign used seeds `10000–10029` and evaluated 3 horizons × 3 solve budgets. The predeclared selection rule required Pareto optimality in weighted tardiness/latency, at most 1% mean fallback, WTT within 2% of the best reliable Pareto point, then minimum latency.

Frozen final-evaluation configuration:

- horizon: **8 released jobs**;
- solve budget: **100 ms per decision**;
- validation mean weighted tardiness: **72.5101**;
- validation mean decision latency: **21.4080 ms**;
- validation mean fallback rate: **0.00%**.

The frozen provenance is stored in [`configs/cpsat_operating_point.json`](configs/cpsat_operating_point.json). This configuration will not be retuned after PPO results are observed.

## PPO multi-training-seed validation

The next research gate is defined in [`configs/ppo_validation_campaign.json`](configs/ppo_validation_campaign.json).

Five independent PPO models are trained with identical hyperparameters:

- training seeds: `101, 202, 303, 404, 505`;
- `150,000` timesteps per member;
- common validation seeds: `10000–10029`.

The research result will **not** cherry-pick the best training seed. All five learned policies remain part of the later scientific evaluation. A single representative model is selected only for deployment/demo continuity using a predeclared median-role rule: choose the training run whose validation WTT mean is closest to the median across all five runs.

See [`docs/ppo_multiseed.md`](docs/ppo_multiseed.md).

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

## Train one reproducible PPO member

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

## Aggregate a PPO validation campaign

After all declared PPO members and their validation outputs are present under `artifacts/seed_<TRAINING_SEED>/`:

```bash
dmdtrl-ppo-campaign \
  --config configs/ppo_validation_campaign.json \
  --artifacts-root artifacts \
  --runs-output campaign/ppo_validation_runs.csv \
  --summary-output campaign/ppo_training_seed_summary.csv \
  --manifest-output campaign/ppo_validation_manifest.json
```

The validator verifies training manifests, SHA-256 hashes model artifacts, enforces complete common validation seeds, and refuses validation/final-test leakage.

## Nominal final evaluation

Final PPO evaluation must not begin until the PPO validation campaign is reviewed and frozen. Final nominal seeds begin at `20000`.

Frozen CP-SAT command:

```bash
dmdtrl-or \
  --seeds 100 \
  --seed-start 20000 \
  --horizon 8 \
  --solver-seconds 0.10 \
  --raw-output results/or_runs.csv \
  --summary-output results/or_summary.csv \
  --comparisons-output results/cpsat_comparisons.csv
```

For PPO, the final campaign will evaluate all declared training-seed realizations rather than only the representative model.

## Distribution-shift evaluation

Built-in scenarios include +20/+40/+60% arrival intensity, 2×/4× breakdown probability, tighter due dates, slower machines, increased setup pressure, and compound stress.

The full final matrix will use frozen PPO settings, frozen CP-SAT `H=8 / 100 ms`, common `30000+` stress seeds, and direct PPO-vs-CP-SAT/fixed-rule comparisons.

## GitHub Actions

- `CI`: Python 3.10/3.11/3.12 lint, tests, coverage, research smoke, stress smoke, CP-SAT smoke, and sensitivity smoke.
- `RL Smoke`: short Stable-Baselines3 training/inference integration test; not policy-quality evidence.
- `OR Validation`: completed 30-seed CP-SAT validation campaign with reliability gating and artifacts.
- `PPO Validation`: five independent `150k`-step PPO trainings, common 30-seed validation, per-member artifacts, and aggregate campaign manifest.

## Research phases

1. **Validated simulator + deterministic baselines:** complete.
2. **Rolling-horizon OR baseline and operating-point freeze:** complete; frozen at **H=8 / 100 ms**.
3. **PPO hyper-heuristic validation:** multi-training-seed long-horizon campaign in progress.
4. **Full nominal + stress comparative experiment:** next after PPO freeze.
5. **True flexible job-shop extension:** planned.
6. **Decision-twin service/dashboard layer:** planned.

See [`docs/roadmap.md`](docs/roadmap.md).

## Scientific principle

A learned policy is not superior because training reward rises, and an optimizer is not superior because it solves a mathematical model. Operational KPIs, online compute cost, solver reliability, training-seed variability, robustness, and paired out-of-sample evidence determine the conclusion. A fixed heuristic winning in some regime is a valid result.

## License

MIT License. See [LICENSE](LICENSE).
