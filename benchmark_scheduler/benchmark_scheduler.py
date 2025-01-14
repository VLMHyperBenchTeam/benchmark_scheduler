import docker


def run_container(
    image_name,
    host_dir,
    container_dir,
    script_path,
    packages_to_install=None,
    use_gpu=False,
    keep_container=False,
):
    """Запускает Docker-контейнер, монтирует папку, устанавливает пакеты,
    подключает GPU (если нужно) и выполняет Python-скрипт.
    Вывод контейнера, включая tqdm, отображается в реальном времени.

    Args:
        image_name (str): Имя Docker-образа.
        host_dir (str): Путь к папке на хосте, которую нужно примонтировать.
        container_dir (str): Путь внутри контейнера, куда будет примонтирована папка.
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

    # Определение volumes для монтирования папки
    volumes = {
        host_dir: {"bind": container_dir, "mode": "rw"}  # 'rw' - чтение и запись
    }

    # Формирование команды для установки пакетов и запуска скрипта
    install_cmd = (
        f"pip install {' '.join(packages_to_install)}" if packages_to_install else ""
    )
    scrypt_run_cmd = f"python -u {script_path}"
    interactive_shell_cmd = "exec bash" if keep_container else ""
    
    command = [install_cmd, scrypt_run_cmd, interactive_shell_cmd]
    command = list(filter(lambda x: x != '', command))
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

    # Остановка контейнера, если keep_container=False
    if not keep_container:
        container.remove(force=True)
        print(f"Контейнер {container.id} удален.")
    else:
        print(f"Контейнер {container.id} оставлен запущенным.")
        print(
            f"Для подключения к контейнеру выполните: docker exec -it {container.id} bash"
        )
