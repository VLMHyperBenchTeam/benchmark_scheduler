from benchmark_scheduler.user_config_reader import UserConfigReader


if __name__ == "__main__":
    config_path = "data/user_config.csv"
    vlm_base_path = "data/vlm_base.csv"

    user_cfg_reader = UserConfigReader(config_path, vlm_base_path)
    bench_run_cfgs = user_cfg_reader.read_user_config()

    for bench_run_cfg in bench_run_cfgs:
        print(bench_run_cfg)
