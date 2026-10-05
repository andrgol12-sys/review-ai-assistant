import csv


# --------------------------------------------------
# Файлы
# --------------------------------------------------

EVALUATION_FILE = (
    "PEd04_AB_Test_Review_AI_Assistant - Blind Evaluation.csv"
)

KEY_FILE = "blind_key.csv"


# --------------------------------------------------
# Параметры эксперимента
# --------------------------------------------------

# Минимальное улучшение Completeness,
# которое мы заранее считаем значимым.
MDE = 5.0

# Максимально допустимый процент галлюцинаций
# для версии B.
GUARD_LIMIT = 5.0


# --------------------------------------------------
# Чтение CSV
# --------------------------------------------------

def load_csv(filename, delimiter=","):
    with open(
        filename,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        return list(
            csv.DictReader(
                file,
                delimiter=delimiter,
            )
        )


# Google Sheets сохраняет CSV с запятой.
evaluations = load_csv(
    EVALUATION_FILE,
    delimiter=",",
)

# Наш blind_key.csv был создан с точкой с запятой.
keys = load_csv(
    KEY_FILE,
    delimiter=";",
)


# --------------------------------------------------
# Проверка файлов
# --------------------------------------------------

if len(evaluations) != len(keys):
    raise ValueError(
        f"Количество строк не совпадает: "
        f"оценки={len(evaluations)}, "
        f"ключ={len(keys)}"
    )


key_by_id = {
    row["id"]: row
    for row in keys
}


# --------------------------------------------------
# Подготовка результатов A и B
# --------------------------------------------------

results = {
    "A": {
        "completeness": [],
        "hallucination": [],
    },
    "B": {
        "completeness": [],
        "hallucination": [],
    },
}


# --------------------------------------------------
# Раскрытие слепого теста
# --------------------------------------------------

for row in evaluations:
    row_id = row["id"]

    if row_id not in key_by_id:
        raise ValueError(
            f"ID {row_id} отсутствует в blind_key.csv"
        )

    key = key_by_id[row_id]

    response_1_version = key["response_1_version"]
    response_2_version = key["response_2_version"]

    completeness_1 = int(row["Completeness 1"])
    completeness_2 = int(row["Completeness 2"])

    hallucination_1 = int(row["Hallucination 1"])
    hallucination_2 = int(row["Hallucination 2"])

    # Оценка Response 1 возвращается к настоящей версии A или B.
    results[response_1_version]["completeness"].append(
        completeness_1
    )

    results[response_1_version]["hallucination"].append(
        hallucination_1
    )

    # Оценка Response 2 возвращается к настоящей версии A или B.
    results[response_2_version]["completeness"].append(
        completeness_2
    )

    results[response_2_version]["hallucination"].append(
        hallucination_2
    )


# --------------------------------------------------
# Расчёт метрик
# --------------------------------------------------

total = len(evaluations)

a_complete = sum(
    results["A"]["completeness"]
)

b_complete = sum(
    results["B"]["completeness"]
)

a_hallucinations = sum(
    results["A"]["hallucination"]
)

b_hallucinations = sum(
    results["B"]["hallucination"]
)


a_completeness_rate = (
    a_complete / total * 100
)

b_completeness_rate = (
    b_complete / total * 100
)

a_hallucination_rate = (
    a_hallucinations / total * 100
)

b_hallucination_rate = (
    b_hallucinations / total * 100
)


# --------------------------------------------------
# Проверка гипотезы
# --------------------------------------------------

completeness_difference = (
    b_completeness_rate
    - a_completeness_rate
)

mde_passed = (
    completeness_difference >= MDE
)

guard_passed = (
    b_hallucination_rate <= GUARD_LIMIT
)

hypothesis_confirmed = (
    mde_passed
    and guard_passed
)


# --------------------------------------------------
# Вывод результатов
# --------------------------------------------------

print()
print("=" * 55)
print("ИТОГИ A/B-ТЕСТА")
print("=" * 55)

print()

print("PROMPT A")

print(
    f"Completeness: "
    f"{a_complete}/{total} = "
    f"{a_completeness_rate:.1f}%"
)

print(
    f"Hallucination: "
    f"{a_hallucinations}/{total} = "
    f"{a_hallucination_rate:.1f}%"
)


print()

print("PROMPT B")

print(
    f"Completeness: "
    f"{b_complete}/{total} = "
    f"{b_completeness_rate:.1f}%"
)

print(
    f"Hallucination: "
    f"{b_hallucinations}/{total} = "
    f"{b_hallucination_rate:.1f}%"
)


print()

print("-" * 55)

print(
    f"Разница Completeness B - A: "
    f"{completeness_difference:+.1f} п.п."
)

print(
    f"MDE: +{MDE:.1f} п.п."
)

print(
    "MDE пройден:",
    "ДА"
    if mde_passed
    else "НЕТ",
)


print()

print(
    f"Guard для B: "
    f"Hallucination <= {GUARD_LIMIT:.1f}%"
)

print(
    "Guard пройден:",
    "ДА"
    if guard_passed
    else "НЕТ",
)


print()

print("-" * 55)

print(
    "Итог гипотезы:",
    "ПОДТВЕРЖДЕНА"
    if hypothesis_confirmed
    else "НЕ ПОДТВЕРЖДЕНА",
)

print("=" * 55)