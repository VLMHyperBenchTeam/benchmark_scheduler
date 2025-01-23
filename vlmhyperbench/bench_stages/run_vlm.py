import os
import time

import torch
from tqdm import tqdm


if __name__ == "__main__":
    # Имя файла, в который будем записывать данные
    filename = "data/task1_output.txt"

    os.system("nvidia-smi")
    print("torch.__version__", torch.__version__)
    print("torch.cuda.is_available()", torch.cuda.is_available())
    print("torch.cuda.current_device()", torch.cuda.current_device())
    print("torch.cuda.device_count()", torch.cuda.current_device())
    print("torch.cuda.get_device_name(0)", torch.cuda.get_device_name(0))
    
    token = os.getenv("HUGGING_FACE_TOKEN")
    if token:
        print(f"Токен Hugging Face: {token}")
    else:
        print("Токен Hugging Face не найден.")

    with open(filename, "w") as file:
        for i in tqdm(range(5), desc="Processing", unit="iteration"):
            line = i
            file.write(f"{i}\n")
            print(f"\nResult: {line}")
            file.flush()

            # Ждем одну секунду
            time.sleep(1)
