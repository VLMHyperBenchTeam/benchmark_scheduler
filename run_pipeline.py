from benchmark_scheduler.benchmark_orchestrator import (
    host_paths_to_abs,
    load_env_vars,
    run_container,
)

if __name__ == "__main__":
    vlm_docker_img = (
        "ghcr.io/vlmhyperbenchteam/qwen2-vl:ubuntu22.04-cu124-torch2.4.0_v0.1.0"
    )
    eval_docker_img = (
        "ghcr.io/vlmhyperbenchteam/qwen2-vl:ubuntu22.04-cu124-torch2.4.0_v0.1.0"
    )

    volumes = {
        "vlmhyperbench/data": "/workspace/data",
        "vlmhyperbench/bench_stages": "/workspace/bench_stages",
        "vlmhyperbench/wheels": "/workspace/wheels",
    }

    environment = load_env_vars()
    volumes = host_paths_to_abs(volumes, current_dir=None)

    run_container(
        vlm_docker_img,
        volumes,
        script_path="/workspace/bench_stages/run_vlm.py",
        packages_to_install=["wheels/benchmark_run_config-0.1.0-py3-none-any.whl"],
        use_gpu=True,
        environment=environment,
    )

    run_container(
        eval_docker_img,
        volumes,
        script_path="/workspace/bench_stages/run_eval.py",
        packages_to_install=None,
    )
