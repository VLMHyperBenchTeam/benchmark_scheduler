import os
from typing import Dict

import docker

from .benchmark_run_config import BenchmarkRunConfig
from .user_config_reader import UserConfigReader


class BenchmarkOrchestrator:
    def __init__(
        self, config_path: str, vlm_base_path: str = "vlmhyperbench/vlm_base.csv"
    ) -> None:
        user_config_reader = UserConfigReader(config_path, vlm_base_path)
        bench_run_cfgs = user_config_reader.read_user_config()

        self.bench_run_cfgs = bench_run_cfgs

    # def benchmark_run(self, bench_run_cfg: "BenchmarkRunConfig"):
    #     self.run_container(
    #         image_name,
    #         host_dir=host_directory,
    #         container_dir=container_directory,
    #         script_path="/workspace/scripts/writer.py",
    #         packages_to_install=["wheels/benchmark_scheduler-0.1.0-py3-none-any.whl"],
    #         keep_container=True,
    #     )

    #     self.run_container(
    #         image_name,
    #         host_dir=host_directory,
    #         container_dir=container_directory,
    #         script_path="/workspace/scripts/reader.py",
    #         use_gpu=True,
    #         packages_to_install=None,
    #     )

    # # добавляем функцию как @staticmethod класса
    # run_container = staticmethod(run_container)


def host_paths_to_abs(
    volumes: Dict[str, str], current_dir: str | None = None
) -> Dict[str, str]:
    """Добавляет текущую директорию ко всем ключам словаря volumes.

    Если current_dir не указан, используется текущая рабочая директория.

    Args:
        volumes (Dict[str, str]): python dict, где ключи — пути на хосте, а значения — пути внутри контейнера.
        current_dir (str | None, optional): Текущая директория. Если None, используется os.getcwd().
            По умолчанию None.

    Returns:
        Dict[str, str]: Новый словарь, где ключи — абсолютные пути на хосте, а значения — пути внутри контейнера.

    Example:
        volumes = {
            "pipeline/data": "/workspace/data",
            "pipeline/bench_stages": "/workspace/bench_stages",
            "pipeline/wheels": "/workspace/wheels",
        }
        current_dir = "/home/user/project"
        result = add_current_dir_to_volumes(volumes, current_dir)
        print(result)
        # {
        #     "/home/user/project/pipeline/data": "/workspace/data",
        #     "/home/user/project/pipeline/bench_stages": "/workspace/bench_stages",
        #     "/home/user/project/pipeline/wheels": "/workspace/wheels",
        # }
    """
    if current_dir is None:
        current_dir = os.getcwd()

    return {
        os.path.join(current_dir, host_path): container_path
        for host_path, container_path in volumes.items()
    }


def run_container(
    image_name,
    volumes,  # Словарь с путями для монтирования
    script_path,
    packages_to_install=None,
    use_gpu=False,
    keep_container=False,
):
    """Запускает Docker-контейнер, монтирует папки, устанавливает пакеты,
    подключает GPU (если нужно) и выполняет Python-скрипт.
    Вывод контейнера, включая tqdm, отображается в реальном времени.

    Args:
        image_name (str): Имя Docker-образа.
        volumes (dict): Словарь, где ключи — пути на хосте, а значения — пути внутри контейнера.
        script_path (str): Путь к Python-скрипту внутри контейнера.
        packages_to_install (list): Список пакетов для установки (например, ["numpy", "pandas"]).
        use_gpu (bool): Флаг, указывающий, нужно ли подключать GPU. По умолчанию False.
        keep_container (bool): Флаг, указывающий, нужно ли оставлять контейнер запущенным
            после выполнения функции. По умолчанию False.

    Returns:
        None

    Raises:
        Exception: Если произошла ошибка при запуске контейнера или выполнении скрипта.
    """
    # Создание клиента Docker
    client = docker.from_env()

    # Определение запроса на использование GPU (если use_gpu=True)
    device_requests = []
    if use_gpu:
        device_requests = [docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])]

    # Формирование volumes для монтирования папок
    volumes_dict = {
        host_path: {"bind": container_path, "mode": "rw"}  # 'rw' - чтение и запись
        for host_path, container_path in volumes.items()
    }

    # Формирование команды для установки пакетов и запуска скрипта
    install_cmd = (
        f"pip install {' '.join(packages_to_install)}" if packages_to_install else ""
    )
    scrypt_run_cmd = f"python -u {script_path}"
    interactive_shell_cmd = "exec bash" if keep_container else ""

    command = [install_cmd, scrypt_run_cmd, interactive_shell_cmd]
    command = list(filter(lambda x: x != "", command))
    command = " && ".join(command)

    # Объединение всех команд в одну
    command = f"sh -c '{command}'"

    # Вывод команды для отладки
    print(command)

    # Запуск контейнера
    container = client.containers.run(
        image_name,
        command=command,  # Команда для выполнения
        detach=True,  # Запуск в фоновом режиме
        stdout=True,
        stderr=True,
        tty=True,  # Включаем псевдотерминал для tqdm
        volumes=volumes_dict,  # Монтируем папки
        device_requests=device_requests,  # Подключаем GPU, если use_gpu=True
    )

    # Чтение вывода контейнера в реальном времени
    print(f"Запущен контейнер с ID: {container.id}")
    try:
        for line in container.attach(stream=True, logs=True):
            print(line.decode("utf-8", errors="replace").strip())
    except KeyboardInterrupt:
        print("Остановлено пользователем.")

    # Остановка контейнера, если keep_container=False
    if not keep_container:
        container.remove(force=True)
        print(f"Контейнер {container.id} удален.")
    else:
        print(f"Контейнер {container.id} оставлен запущенным.")
        print(
            f"Для подключения к контейнеру выполните: docker exec -it {container.id} bash"
        )
