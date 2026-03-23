#!/usr/bin/env python3
import json
import random
from pathlib import Path


def main() -> None:
    values = [random.randint(0, 10) for _ in range(10)]
    output_path = Path(__file__).parent / "random_values.json"

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(values, f, ensure_ascii=False, indent=2)

    print(f"Сохранено в: {output_path}")


if __name__ == "__main__":
    main()