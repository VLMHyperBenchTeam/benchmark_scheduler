import docker


def run_container(image_name, host_dir, container_dir, script_path, packages_to_install=None, use_gpu=False):
    """Запускает Docker-контейнер, монтирует папку, устанавливает пакеты, подключает GPU (если нужно) и выполняет Python-скрипт.
    Вывод контейнера, включая tqdm, отображается в реальном времени.

    Args:
        image_name (str): Имя Docker-образа.
        host_dir (str): Путь к папке на хосте, которую нужно примонтировать.
        container_dir (str): Путь внутри контейнера, куда будет примонтирована папка.
        script_path (str): Путь к Python-скрипту внутри контейнера.
        packages_to_install (list): Список пакетов для установки (например, ["numpy", "pandas"]).
        use_gpu (bool): Флаг, указывающий, нужно ли подключать GPU. По умолчанию False.

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

    # Определение volumes для монтирования папки
    volumes = {
        host_dir: {"bind": container_dir, "mode": "rw"}  # 'rw' - чтение и запись
    }

    # Формирование команды для установки пакетов и запуска скрипта
    if packages_to_install:
        # Если нужно установить пакеты, формируем команду для оболочки
        install_command = f"pip install {' '.join(packages_to_install)}"
        command = f"sh -c '{install_command} && python -u {script_path}'"
    else:
        # Если пакеты не нужно устанавливать, просто запускаем скрипт
        command = f"python -u {script_path}"

    # Запуск контейнера
    container = client.containers.run(
        image_name,
        command=command,  # Команда для выполнения
        detach=True,  # Запуск в фоновом режиме
        stdout=True,
        stderr=True,
        tty=True,  # Включаем псевдотерминал для tqdm
        volumes=volumes,  # Монтируем папку
        device_requests=device_requests,  # Подключаем GPU, если use_gpu=True
    )

    # Чтение вывода контейнера в реальном времени
    print(f"Запущен контейнер с ID: {container.id}")
    try:
        for line in container.attach(stream=True, logs=True):
            print(line.decode("utf-8", errors="replace").strip())
    except KeyboardInterrupt:
        print("Остановлено пользователем.")

    # Остановка контейнера
    container.remove(force=True)
    print(f"Контейнер {container.id} удален.")
