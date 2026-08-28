# CP-SAT Operating-Point Selection and Freeze

## Purpose

The CP-SAT horizon and online solve budget are model-selection choices. They must be selected before nominal final-test seeds (`20000+`) or stress final-test seeds (`30000+`) are analyzed.

The repository therefore reserves `10000–19999` for validation/model selection and provides a deterministic selection rule through `dmdtrl-or-select`.

## Validation campaign

The `OR Validation` GitHub Actions workflow runs the full nominal sensitivity grid on 30 common-random-number seeds:

- validation seeds: `10000–10029`;
- horizons: 4, 8, 12 released jobs;
- solve budgets: 20, 50, 100 ms per decision;
- bootstrap replicates: 2,000;
- paired randomization permutations: 5,000.

The workflow retains:

- raw seed-level sensitivity runs;
- bootstrap summary table;
- paired comparisons against the declared H=12 / 100 ms reference;
- the selected operating-point JSON manifest.

## Selection rule

The selector first restricts attention to Pareto-optimal configurations in mean priority-weighted tardiness and measured mean online decision latency.

Let `WTT_best` be the lowest mean weighted tardiness on the validation Pareto set. With the predeclared default tolerance of 2%, a Pareto configuration is quality-acceptable when:

`WTT <= WTT_best × 1.02`

Among those acceptable configurations, select the one with the lowest measured mean decision latency. Remaining ties are broken deterministically by:

1. lower weighted tardiness;
2. lower solver budget;
3. smaller horizon;
4. policy identifier.

This rule deliberately does not choose the lowest observed WTT at any compute cost. It selects a low-latency operating point whose validation quality is practically indistinguishable under the declared tolerance.

## Data-integrity checks

`dmdtrl-or-select` refuses to create a manifest unless:

- validation seed count is positive;
- every seed is at least 10000 and strictly below 20000;
- at least two sensitivity configurations are present;
- every configuration contains the complete declared validation seed set;
- every summary row contains the required sensitivity fields;
- operational numeric values are finite and valid;
- at least one Pareto-optimal configuration is present.

These checks prevent partial grid runs or final-test leakage from silently determining the OR configuration.

## Freeze manifest

The generated JSON records:

- selected horizon and solver budget;
- validation WTT and latency;
- quality tolerance and threshold;
- Pareto and acceptable-candidate counts;
- validation seed range;
- raw and summary source files;
- Git commit SHA when running in GitHub Actions;
- the exact textual selection rule.

After the validation campaign is reviewed, the selected horizon/budget should be frozen and reused unchanged for nominal final-test and stress-test experiments.

## Scientific boundary

The validation artifact is model-selection evidence, not final performance evidence. Final claims must come from disjoint `20000+` nominal and `30000+` stress seeds after both CP-SAT and PPO settings are frozen.
