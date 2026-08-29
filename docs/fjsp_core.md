# Phase 5: Flexible Job-Shop Core

## Purpose

Phase 4 showed that the PPO hyper-heuristic did not add robust value over the strongest fixed dispatching rule in the dynamic parallel-machine formulation. Phase 5 therefore changes the scheduling problem structure instead of tuning PPO against locked final-test seeds.

This first Phase-5 increment introduces a separate true flexible job-shop (FJSP) core while preserving the validated v1.0 parallel-machine experiment unchanged.

## Implemented structure

The FJSP model now supports:

- jobs with multiple ordered operations;
- strict operation precedence;
- alternative eligible machines for each operation;
- machine-dependent processing times for each operation;
- dynamic job release times;
- family-dependent sequence setup times;
- event-driven advancement to the next feasible decision epoch;
- explicit `(job, operation, machine)` assignment actions;
- operation-level schedules and job-level tardiness/flow-time metrics.

`FJSPAction(job_id, operation_index, machine_id)` is feasible only when:

1. the job has been released;
2. the requested operation is exactly the job's next unscheduled operation;
3. its predecessor has completed;
4. the selected machine is eligible for that operation; and
5. the machine is available at the current event time.

The simulator advances time only when no feasible assignment exists. This creates a dynamic feasible action set naturally from precedence, routing eligibility, releases, and machine availability.

## Reproducible instance generator

`generate_fjsp_instance` creates seeded stochastic instances with configurable:

- number of jobs and machines;
- operations per job;
- eligible machines per operation;
- release process;
- processing-time range;
- due-date tightness;
- priorities and product families.

Due dates are based on the sum of the fastest eligible processing option for each operation, multiplied by a stochastic due-date factor. This is intentionally simple and will be stress-tested before final experimental use.

## Deterministic baselines

The first core includes two feasibility-preserving direct assignment selectors:

- shortest setup-plus-processing action;
- earliest-due-date action with processing-time tie breaking.

These are scaffolding baselines, not the final strong comparison set. Later Phase-5 increments should add FJSP rolling-horizon CP-SAT / interval scheduling and neighborhood-search baselines before any RL performance claim.

## Deliberate exclusions from this increment

Not yet included:

- breakdowns or stochastic repairs;
- urgent-order burst process;
- pre-generated exogenous disruption plans;
- Gymnasium observation/action interface;
- action masking / Maskable PPO;
- GNN or attention encoder;
- FJSP CP-SAT benchmark;
- physical completion-event queue separate from schedule commitment;
- RL training.

These are intentionally deferred until the core precedence/routing semantics are tested and stable.

## Testing contract

The initial tests verify:

- invalid precedence chains are rejected;
- duplicate machine alternatives are rejected;
- seeded FJSP generation is reproducible;
- operation precedence cannot be bypassed;
- machine eligibility is enforced;
- release times and event advancement work;
- sequence setup time is applied between product families;
- a deterministic greedy policy can complete a generated multi-operation FJSP instance.

## Next Phase-5 increment

The next increment should add a Gymnasium-compatible FJSP decision environment with a fixed-capacity action index and explicit feasibility mask, plus action-trace logging. That environment will be designed for Maskable PPO without allowing invalid job-operation-machine assignments.

The Phase-4 final seeds remain locked and are not reused for Phase-5 model selection.
