import csv
import random


SOURCE_FILE = "ab_results.csv"
BLIND_FILE = "blind_evaluation.csv"
KEY_FILE = "blind_key.csv"

# Фиксируем seed, чтобы перемешивание было воспроизводимым.
random.seed(42)


with open(
    SOURCE_FILE,
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:
    rows = list(
        csv.DictReader(
            file,
            delimiter=";",
        )
    )


blind_rows = []
key_rows = []


for row in rows:
    if random.choice([True, False]):
        response_1 = row["answer_a"]
        response_2 = row["answer_b"]

        version_1 = "A"
        version_2 = "B"

    else:
        response_1 = row["answer_b"]
        response_2 = row["answer_a"]

        version_1 = "B"
        version_2 = "A"

    blind_rows.append(
        {
            "id": row["id"],
            "category": row["category"],
            "review": row["review"],
            "response_1": response_1,
            "response_2": response_2,
        }
    )

    key_rows.append(
        {
            "id": row["id"],
            "response_1_version": version_1,
            "response_2_version": version_2,
        }
    )


with open(
    BLIND_FILE,
    "w",
    encoding="utf-8-sig",
    newline="",
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "id",
            "category",
            "review",
            "response_1",
            "response_2",
        ],
        delimiter=";",
        quoting=csv.QUOTE_ALL,
    )

    writer.writeheader()
    writer.writerows(blind_rows)


with open(
    KEY_FILE,
    "w",
    encoding="utf-8-sig",
    newline="",
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "id",
            "response_1_version",
            "response_2_version",
        ],
        delimiter=";",
        quoting=csv.QUOTE_ALL,
    )

    writer.writeheader()
    writer.writerows(key_rows)


print("Слепой набор подготовлен.")
print(f"Строк: {len(blind_rows)}")
print(f"Файл для оценки: {BLIND_FILE}")
print(f"Секретный ключ: {KEY_FILE}")
print()
print("ВАЖНО: blind_key.csv не открывать до завершения оценки.")