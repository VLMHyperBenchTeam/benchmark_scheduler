from benchmark_scheduler.benchmark_orchestrator import host_paths_to_abs


if __name__ == "__main__":
    volumes = {
        "pipeline/data": "/workspace/data",
        "pipeline/bench_stages": "/workspace/bench_stages",
        "pipeline/wheels": "/workspace/wheels",
    }

    result = host_paths_to_abs(volumes, current_dir=None)

    for key in result:
        print(key, result[key])
