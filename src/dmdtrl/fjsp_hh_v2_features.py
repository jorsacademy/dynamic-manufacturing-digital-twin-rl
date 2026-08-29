from __future__ import annotations

import math

import numpy as np

from dmdtrl.fjsp_models import FJSPAction
from dmdtrl.fjsp_operators import FJSPOperator, select_operator_action
from dmdtrl.fjsp_simulator import FlexibleJobShopSimulator

_EPS = 1e-12

OPERATOR_CANDIDATE_FEATURE_NAMES = (
    "action_slack",
    "processing_duration",
    "setup_duration",
    "job_priority",
    "critical_ratio",
    "projected_weighted_tardiness_risk",
    "remaining_work",
    "machine_cumulative_load",
    "family_match",
    "final_operation",
)


def _remaining_min_processing(
    simulator: FlexibleJobShopSimulator,
    job_id: int,
    *,
    after_current: bool,
) -> float:
    job = simulator.job(job_id)
    next_index = simulator.next_operation[job_id]
    start = next_index + (1 if after_current else 0)
    return float(
        sum(
            min(option.processing_time for option in operation.machine_options)
            for operation in job.operations[start:]
        )
    )


def _instance_scales(simulator: FlexibleJobShopSimulator) -> tuple[float, float, float, float]:
    instance = simulator.instance
    max_processing = max(
        option.processing_time
        for job in instance.jobs
        for operation in job.operations
        for option in operation.machine_options
    )
    time_scale = max(
        max(job.due_date for job in instance.jobs),
        sum(
            min(option.processing_time for option in operation.machine_options)
            for job in instance.jobs
            for operation in job.operations
        )
        / instance.n_machines,
        1.0,
    )
    max_priority = max(job.priority for job in instance.jobs)
    setup_scale = max(
        simulator.default_setup_time,
        max(simulator.setup_times.values(), default=0.0),
        1.0,
    )
    return float(time_scale), float(max_processing), float(max_priority), float(setup_scale)


def operator_candidate_actions(
    simulator: FlexibleJobShopSimulator,
) -> tuple[FJSPAction, ...]:
    """Return the concrete feasible assignment proposed by each frozen operator."""

    if simulator.terminated:
        return ()
    return tuple(select_operator_action(simulator, operator) for operator in FJSPOperator)


def action_candidate_features(
    simulator: FlexibleJobShopSimulator,
    action: FJSPAction,
) -> np.ndarray:
    """Encode one currently feasible assignment with bounded operational features."""

    if action not in simulator.eligible_actions():
        raise ValueError("candidate features require a currently feasible FJSP action")

    job = simulator.job(action.job_id)
    operation = job.operations[action.operation_index]
    machine = simulator.machines[action.machine_id]
    processing = operation.processing_time_on(action.machine_id)
    setup = simulator.setup_time(machine.last_family, job.family)
    remaining_after = _remaining_min_processing(
        simulator,
        action.job_id,
        after_current=True,
    )
    remaining_work = processing + remaining_after
    projected_completion = simulator.current_time + setup + remaining_work
    action_slack = job.due_date - projected_completion
    critical_ratio = (job.due_date - simulator.current_time) / max(remaining_work, _EPS)
    weighted_risk = job.priority * max(0.0, projected_completion - job.due_date)
    machine_load = machine.busy_time + machine.setup_time
    time_scale, max_processing, max_priority, setup_scale = _instance_scales(simulator)
    max_operations = max(len(item.operations) for item in simulator.instance.jobs)
    slack_scale = max(max_processing * max_operations, 1.0)
    risk_scale = max(time_scale * max_priority, 1.0)

    values = np.asarray(
        [
            0.5 + 0.5 * math.tanh(action_slack / slack_scale),
            processing / max(max_processing, _EPS),
            setup / setup_scale,
            job.priority / max(max_priority, _EPS),
            0.5 + 0.5 * math.tanh((critical_ratio - 1.0) / 2.0),
            math.tanh(weighted_risk / risk_scale),
            remaining_work / max(time_scale, remaining_work, 1.0),
            machine_load / max(time_scale, machine_load, 1.0),
            float(machine.last_family is None or machine.last_family == job.family),
            float(action.operation_index == len(job.operations) - 1),
        ],
        dtype=np.float32,
    )
    return np.clip(values, 0.0, 1.0)


def operator_candidate_feature_matrix(
    simulator: FlexibleJobShopSimulator,
) -> np.ndarray:
    """Return one feature row per operator in stable enum order."""

    feature_count = len(OPERATOR_CANDIDATE_FEATURE_NAMES)
    if simulator.terminated:
        return np.zeros((len(FJSPOperator), feature_count), dtype=np.float32)
    rows = [
        action_candidate_features(simulator, select_operator_action(simulator, operator))
        for operator in FJSPOperator
    ]
    return np.stack(rows, axis=0).astype(np.float32, copy=False)
