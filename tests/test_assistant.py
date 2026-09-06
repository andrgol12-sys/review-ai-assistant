import sys
from pathlib import Path


# Добавляем корневую папку проекта в sys.path,
# чтобы тест мог импортировать assistant.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from assistant import ReviewAssistant


TEST_CASES = [
    {
        "name": "Опасная неисправность",
        "review": "Чайник начал искрить и появился запах гари.",
        "must_contain": [
            "Тональность: negative",
            "Тип обращения: complaint",
            "Темы: quality",
            "Критичность: high",
            "Эскалация: yes",
        ],
        "must_not_contain": [
            "мы передадим",
            "мы проверим",
            "мы свяжемся",
        ],
    },
    {
        "name": "Смешанный отзыв",
        "review": (
            "Холодильник отличный, работает хорошо, "
            "но курьер опоздал на четыре часа и даже не извинился."
        ),
        "must_contain": [
            "Тональность: mixed",
            "Тип обращения: mixed",
            "product",
            "delivery",
            "service",
            "Критичность: medium",
            "Эскалация: no",
        ],
        "must_not_contain": [
            "мы передадим",
            "мы проверим",
            "мы свяжемся",
        ],
    },
    {
        "name": "Требование компенсации",
        "review": (
            "Курьер опоздал на пять часов. Я потерял весь день. "
            "Требую скидку 30 процентов и компенсацию "
            "за потраченное время."
        ),
        "must_contain": [
            "Тональность: negative",
            "Тип обращения: complaint",
            "delivery",
            "compensation",
            "Критичность: high",
            "Эскалация: yes",
        ],
        "must_not_contain": [
            "скидка будет предоставлена",
            "мы предоставим скидку",
            "компенсация будет выплачена",
            "мы выплатим компенсацию",
            "мы передадим",
        ],
    },
    {
        "name": "Неясная жалоба",
        "review": (
            "Ужасный магазин. Больше никогда у вас ничего не куплю. "
            "Полное разочарование."
        ),
        "must_contain": [
            "Тональность: negative",
            "Тип обращения: complaint",
            "Темы: other",
            "Эскалация: no",
        ],
        "must_not_contain": [
            "задержка доставки",
            "бракованный товар",
            "неисправный товар",
        ],
    },
    {
        "name": "Персональные данные",
        "review": (
            "Меня зовут Иван Петров, мой телефон +7 999 123-45-67. "
            "Заказ так и не доставили. Никто мне не отвечает."
        ),
        "must_contain": [
            "Тональность: negative",
            "Тип обращения: complaint",
            "delivery",
            "service",
            "privacy",
            "Критичность: high",
            "Эскалация: yes",
        ],
        "must_not_contain": [
            "+7 999 123-45-67",
            "мы передадим",
            "мы свяжемся",
        ],
    },
]


def check_test(
    result: str,
    test_case: dict,
) -> tuple[bool, list[str]]:
    problems = []

    result_lower = result.lower()

    for expected in test_case["must_contain"]:
        if expected.lower() not in result_lower:
            problems.append(
                f"Не найдено ожидаемое значение: {expected}"
            )

    for forbidden in test_case["must_not_contain"]:
        if forbidden.lower() in result_lower:
            problems.append(
                f"Найдена запрещённая формулировка: {forbidden}"
            )

    return len(problems) == 0, problems


def main():
    assistant = ReviewAssistant()

    passed = 0

    print("=" * 70)
    print("               TESTING REVIEW AI ASSISTANT")
    print("=" * 70)

    for index, test_case in enumerate(TEST_CASES, start=1):
        print()
        print(f"TEST {index:02d} — {test_case['name']}")
        print("-" * 70)

        try:
            result = assistant.analyze_review(
                test_case["review"]
            )

            success, problems = check_test(
                result,
                test_case,
            )

            if success:
                print("PASS")
                passed += 1

            else:
                print("FAIL")

                for problem in problems:
                    print(f"  - {problem}")

                print()
                print("Ответ ассистента:")
                print(result)

        except Exception as error:
            print("ERROR")
            print(f"  {error}")

    print()
    print("=" * 70)
    print(
        f"Результат: {passed}/{len(TEST_CASES)} "
        f"тестов пройдено"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()