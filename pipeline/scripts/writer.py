import os
import time

from tqdm import tqdm


if __name__ == "__main__":
    # Имя файла, в который будем записывать данные
    filename = "data/task1_output.txt"

    os.system("nvidia-smi")

    with open(filename, "w") as file:
        for i in tqdm(range(10), desc="Processing", unit="iteration"):
            line = i
            file.write(f"{i}\n")
            print(f"\nResult: {line}")
            file.flush()

            # Ждем одну секунду
            time.sleep(1)
