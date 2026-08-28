# Distribution-Shift Stress Scenarios

The purpose of this suite is to measure policy robustness outside nominal training-like conditions. A policy is trained or selected under nominal assumptions and then evaluated **without retraining** on controlled shifts.

All policies within a scenario use the same evaluation seeds. Scenario comparisons are therefore paired at the stochastic-seed level.

## Scenario definitions

| Scenario | Operational change |
| --- | --- |
| `nominal` | Base `EnvConfig` |
| `demand_120` | Arrival intensity ×1.20; mean interarrival divided by 1.20 |
| `demand_140` | Arrival intensity ×1.40; mean interarrival divided by 1.40 |
| `demand_160` | Arrival intensity ×1.60; mean interarrival divided by 1.60 |
| `breakdown_2x` | Breakdown probability ×2 |
| `breakdown_4x` | Breakdown probability ×4 |
| `tight_due_085` | Due-date allowance factors ×0.85 |
| `slow_machines_090` | Machine-speed range ×0.90 |
| `setup_2x` | Sequence-dependent setup time ×2 |
| `compound_stress` | Demand ×1.40, breakdown ×3, due-date allowance ×0.85, speed ×0.95, setup ×1.50 |

Breakdown probability is capped at 0.95 so an extreme custom multiplier cannot create an invalid probability.

## Interpretation

The scenarios are controlled interventions, not claims about one specific factory. Their purpose is to create reproducible stress axes and answer questions such as:

- At what demand intensity does a nominally strong dispatching rule begin to fail?
- Does an adaptive policy preserve on-time performance as disruption frequency rises?
- Is a policy's nominal advantage explained only by setup reduction?
- Does the learned policy remain useful when machine capacity shifts away from training conditions?
- Under compound stress, does policy ranking change materially?

## Evaluation protocol

Recommended stress-test seeds begin at 30000 and must remain disjoint from training and nominal model-selection seeds.

For each scenario and policy retain raw seed-level metrics. Report at minimum:

- priority-weighted tardiness;
- on-time completion rate;
- mean waiting time;
- setup time;
- makespan;
- utilization;
- decision latency.

For learned-policy comparisons, report paired confidence intervals, permutation p-values, effect size, probability of superiority, and percent improvement against each baseline.

## Robustness curves

The most important future visualization is not a single leaderboard. It is a response curve such as:

`arrival intensity -> candidate improvement over best classical baseline`

Equivalent curves should be produced for breakdown risk, due-date tightness, and other controlled stress dimensions. A useful RL policy should retain operational value across a meaningful region, rather than winning only at one calibrated point.

## Limitations

The current scenario system modifies parameters already represented by the parallel-machine simulator. It does not yet model:

- correlated machine failures;
- explicit urgent-order burst processes;
- supplier/material shortages;
- operator absenteeism;
- time-varying energy prices;
- multi-operation job routing.

Those effects should be added only with corresponding simulator logic and validation tests; they should not be represented by arbitrary reward penalties.
