from __future__ import annotations

import argparse
from pathlib import Path

from dmdtrl.env import DynamicManufacturingEnv, EnvConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Train PPO as a dispatching hyper-heuristic.")
    parser.add_argument("--steps", type=int, default=150_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("models/ppo_dispatcher"))
    args = parser.parse_args()

    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.env_checker import check_env
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise SystemExit('Install RL dependencies with: pip install -e ".[rl]"') from exc

    env = DynamicManufacturingEnv(EnvConfig())
    check_env(env, warn=True)
    model = PPO(
        "MlpPolicy",
        env,
        seed=args.seed,
        verbose=1,
        learning_rate=3e-4,
        n_steps=1024,
        batch_size=128,
        gamma=0.99,
        gae_lambda=0.95,
        ent_coef=0.01,
        policy_kwargs={"net_arch": [128, 128]},
    )
    model.learn(total_timesteps=args.steps)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(args.output))
    print(f"Saved PPO model to {args.output}.zip")


if __name__ == "__main__":
    main()
