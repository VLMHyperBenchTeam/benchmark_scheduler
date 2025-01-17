from dataclasses import dataclass
import json


@dataclass
class BenchmarkRunConfig:
    """
    Dataclass для хранения всех параметров запуска бенчмарка для одной модели в рамках одной структуры с полями.

    Attributes:
        dataset (str): Название датасета, на котором будем оценивать работу модели.
        framework (str): Название фреймворка для инференса VLM-моделей (например, "Hugging Face", "vLLM", "SgLang").
        model_name (str): Название VLM-модели, которую будем оценивать на бенчмарке (например, "Qwen2-VL-2B").
        prompt_collection (str): Название csv-файла, содержащего коллекцию промптов для модели,
            которые и будут использованы при бенчмарке модели.
        docker_image (str): Название Docker image, в котором будем проводить бенчмарк модели.
            Если None, то будет использован Docker image из `vlmhyperbench/vlm_base.csv`,
            для запуска указанной модели в указанном фреймворке инференса.
        python_package (str): Название python-пакета с классом нужной VLM-модели.
        module (str): Название модуля в python-пакете с классом нужной VLM-модели.
        class_name (str): Название класса нужной VLM-модели в указанном python-пакете.
        system_prompt (str | None): Название текстового файла, содержащего system prompt,
            который будет передан VLM-модели при ее инициализации. Optional.
            Defaults to None.
        metrics (list[str] | None): Список метрик, которые будем оценивать по ответам модели
            (например, ['WER', 'CER', 'BLEU']). Optional. Defaults to None.
            Если None, то метрики оцениваться не будут и этап 2 будет пропущен.
        only_evaluate_metrics (bool): Если True, то пропускаем этап 1 оценки VLM-модели на датасете
            и сразу переходим к этапу оценки метрик. Optional.
            Defaults to False.
        metrics_aggregators (list[str] | None): Список типов агрегаторов, используя которые рассчитываем метрики
            (например, ["by_id", "by_doc_type", "overall"]). Optional. Defaults to None.
            Если None, то метрики оцениваться не будут и этап 2 будет пропущен.
        filter_doc_class (str | None): Разметка датасета annotation.csv, будет отфильтрована, так чтобы
            в датасете в столбце "doc_class" остались только значения равные заданному. Optional. Defaults to None.
        filter_question_type (str | None): Разметка датасета annotation.csv, будет отфильтрована, так чтобы
            в датасете в столбце "question_type" остались только значения равные заданному. Optional. Defaults to None.
    """

    # Обязательные поля (без значений по умолчанию)
    dataset: str
    framework: str
    model_name: str
    prompt_collection: str
    docker_image: str
    python_package: str
    module: str
    class_name: str

    # Опциональные поля (со значениями по умолчанию)
    system_prompt: str | None = None
    metrics: list[str] | None = None
    only_evaluate_metrics: bool = False
    metrics_aggregators: list[str] | None = None
    filter_doc_class: str | None = None
    filter_question_type: str | None = None

    def to_json(self, file_path: str) -> None:
        """
        Сериализует объект в JSON и сохраняет его в файл.

        Args:
            file_path (str): Путь к файлу, в который будет сохранён JSON.
        """
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(self.__dict__, json_file, indent=4)

    @classmethod
    def from_json(cls, file_path: str) -> "BenchmarkRunConfig":
        """
        Десериализует объект из JSON-файла.

        Args:
            file_path (str): Путь к JSON-файлу, из которого будет загружен объект.

        Returns:
            BenchmarkRunConfig: Экземпляр класса BenchmarkRunConfig, созданный из JSON-файла.
        """
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        return cls(**data)
