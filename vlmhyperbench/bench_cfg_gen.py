import json

# Пример словаря
data = {
    "vlm_base_path": "vlmhyperbench/vlm_base.csv",
    "system_prompts_dir": "vlmhyperbench/SystemPrompts",
    "prompt_collection_dir": "vlmhyperbench/PromptCollection",
    "datasets_dir": "vlmhyperbench/Datasets",
    "cfg_dir": "vlmhyperbench/cfg",
    "models_answers_dir": "vlmhyperbench/ModelsAnswers",
    "models_metrics_dir": "vlmhyperbench/ModelsMetrics",
    "reports": "vlmhyperbench/Reports",
}

# Сохранение словаря в JSON файл
with open('data.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)

# Если нужно сохранить словарь в виде JSON строки
json_string = json.dumps(data, indent=4)
print(json_string)