import csv
import time

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL
from knowledge_base import KnowledgeBase
from prompts_ab import build_system_prompt_a, build_system_prompt_b


# --------------------------------------------------
# Настройки A/B-теста
# --------------------------------------------------

COMPANY_NAME = "HomeTech"
COMPANY_DESCRIPTION = "Интернет-магазин бытовой техники и электроники."
RESPONSE_LANGUAGE = "русский"
TEMPERATURE = 0.2

DATASET_FILE = "dataset_ab.csv"
RESULTS_FILE = "ab_results.csv"


# --------------------------------------------------
# OpenAI и база знаний
# --------------------------------------------------

client = OpenAI(api_key=OPENAI_API_KEY)
knowledge_base = KnowledgeBase()


# --------------------------------------------------
# Версии системного промпта
# --------------------------------------------------

prompt_a = build_system_prompt_a(
    company_name=COMPANY_NAME,
    company_description=COMPANY_DESCRIPTION,
    response_language=RESPONSE_LANGUAGE,
)

prompt_b = build_system_prompt_b(
    company_name=COMPANY_NAME,
    company_description=COMPANY_DESCRIPTION,
    response_language=RESPONSE_LANGUAGE,
)


# --------------------------------------------------
# Анализ одного отзыва
# --------------------------------------------------

def analyze_with_prompt(review: str, system_prompt: str) -> str:
    relevant_context = knowledge_base.search(review)
    company_rules = knowledge_base.get_company_rules()

    user_prompt = f"""
Проанализируй следующий клиентский отзыв.

ОТЗЫВ:
{review}

ОБЩИЕ ПРАВИЛА HOMETECH:
{company_rules}

РЕЛЕВАНТНЫЕ ЗАПИСИ БАЗЫ ЗНАНИЙ:
{relevant_context}

Выполни анализ строго по правилам системного промпта.
"""

    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=system_prompt,
        input=user_prompt,
        temperature=TEMPERATURE,
    )

    return response.output_text


# --------------------------------------------------
# Чтение датасета
# --------------------------------------------------

def load_dataset() -> list[dict]:
    with open(
        DATASET_FILE,
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return list(
            csv.DictReader(
                file,
                delimiter=";",
            )
        )


# --------------------------------------------------
# Сохранение результатов
# --------------------------------------------------

def save_results(results: list[dict]) -> None:
    with open(
        RESULTS_FILE,
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
                "answer_a",
                "answer_b",
            ],
            delimiter=";",
            quoting=csv.QUOTE_ALL,
        )

        writer.writeheader()
        writer.writerows(results)


# --------------------------------------------------
# Полный A/B-тест
# --------------------------------------------------

def run_ab_test() -> None:
    dataset = load_dataset()
    results = []

    print(f"Загружено отзывов: {len(dataset)}")
    print(f"Модель: {OPENAI_MODEL}")
    print(f"Temperature: {TEMPERATURE}")
    print()

    for index, row in enumerate(dataset, start=1):
        review = row["review"]

        print(
            f"[{index}/{len(dataset)}] "
            f"ID {row['id']} — {row['category']}"
        )

        # Чередуем порядок A/B.
        if index % 2 == 1:
            print("  Запрос A...")
            answer_a = analyze_with_prompt(review, prompt_a)

            print("  Запрос B...")
            answer_b = analyze_with_prompt(review, prompt_b)

        else:
            print("  Запрос B...")
            answer_b = analyze_with_prompt(review, prompt_b)

            print("  Запрос A...")
            answer_a = analyze_with_prompt(review, prompt_a)

        results.append(
            {
                "id": row["id"],
                "category": row["category"],
                "review": review,
                "answer_a": answer_a,
                "answer_b": answer_b,
            }
        )

        # Сохраняем после каждого отзыва.
        save_results(results)

        print("  Сохранено.")
        print()

        # Небольшая пауза между парами запросов.
        time.sleep(0.5)

    print("=" * 50)
    print("A/B-тест завершён.")
    print(f"Обработано отзывов: {len(results)}")
    print(f"Выполнено API-запросов: {len(results) * 2}")
    print(f"Результаты сохранены: {RESULTS_FILE}")


if __name__ == "__main__":
    run_ab_test()