# Phase-5 Maskable PPO validation

This stage estimates whether a mask-aware learned FJSP dispatcher is robust to training randomness before any Phase-5 final-test instance is accessed.

## Frozen comparison boundary

The rolling-horizon CP-SAT baseline was selected first, independently of the PPO campaign, on seeds `41000-41029`. The frozen operating point is:

- job horizon: `4`;
- online solve budget: `100 ms`;
- one CP-SAT search worker;
- fixed solver random seed;
- validation WTT mean: `25.0983`;
- validation mean decision latency: `25.0964 ms`;
- validation fallback rate: `0%`.

The exact provenance and selection thresholds are stored in `configs/fjsp_cpsat_validation_freeze.json`. The PPO campaign must not retune this baseline.

## Seed separation

Phase-5 uses separate data blocks for separate decisions:

| Role | Seeds |
| --- | --- |
| development/smoke | `40000-40999` |
| CP-SAT tuning | `41000-41029` |
| Maskable PPO validation | `41100-41129` |
| nominal final test, embargoed during selection | `42000-42099` |

The PPO validation workflow asserts that no evaluation row reaches seed `42000`.

## Training design

The campaign trains five independent Maskable PPO realizations with training seeds:

`701, 1701, 2701, 3701, 4701`

Every member uses the same predeclared configuration:

- `150,000` timesteps;
- learning rate `3e-4`;
- rollout length `1024`;
- batch size `128`;
- gamma `0.99`;
- GAE lambda `0.95`;
- entropy coefficient `0.01`;
- two `128`-unit policy/value hidden layers;
- CPU execution.

The FJSP generator remains fixed at 12 jobs, 5 machines, 2-4 operations per job, up to 3 eligible machines per operation, and the current Phase-5 processing/due-date distributions.

## Evaluation architecture

The fixed baseline panel is evaluated once on the 30 PPO validation instances:

1. earliest due date;
2. shortest processing;
3. frozen rolling-horizon CP-SAT.

Each trained PPO member is then evaluated on exactly the same 30 instance seeds using deterministic masked inference. Canonical SHA-256 instance fingerprints must match the baseline panel seed by seed.

This avoids rerunning the wall-clock-bounded CP-SAT solver five times and accidentally treating slightly different solver trajectories as five baseline replications.

## Statistical unit

The 150 PPO validation episodes are not treated as 150 independent algorithm replications.

For each training seed, the evaluator first computes paired WTT differences against each baseline across the 30 common instances. The campaign then summarizes those five training-seed-level mean improvements. Thus the top-level inference unit for learned-policy robustness is the independent training seed.

Artifacts retain:

- per-instance PPO rows;
- one fixed baseline panel;
- per-training-seed WTT and latency summaries;
- per-training-seed paired baseline comparisons;
- across-training-seed bootstrap summaries;
- model and training-manifest SHA-256 hashes;
- exact runtime package versions.

## Representative model

A single representative model is selected only for deployment/demo continuity. It is the training realization whose validation mean WTT is closest to the median across all five members, with latency and seed used only as tie-breakers.

This representative model must not replace the five-training-seed evidence in scientific claims. The best validation member is never selected simply because it is best.

## Next gate

After this campaign is frozen, Phase-5 final nominal evaluation may use seeds `42000-42099`. Final claims must retain all five declared training realizations and compare them against the already frozen CP-SAT operating point and heuristic baselines.
