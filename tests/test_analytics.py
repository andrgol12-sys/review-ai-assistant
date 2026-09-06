import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from analytics import calculate_statistics
from assistant import ReviewAssistant


TEST_REVIEWS = [
    "Холодильник отличный, доставили быстро, всё понравилось.",
    "Стиральная машина приехала с мятой коробкой, но сам товар работает.",
    "Курьер опоздал на пять часов и даже не извинился.",
    "Телевизор перестал включаться через неделю после покупки.",
    "Спасибо менеджеру, всё подробно объяснил и помог выбрать товар.",
    "Чайник начал искрить и появился запах гари.",
]


EXPECTED_STATISTICS = {
    "total_reviews": 6,
    "sentiment": {
        "positive": 2,
        "mixed": 1,
        "negative": 3,
    },
    "topics": {
        "delivery": 2,
        "service": 2,
        "quality": 2,
        "packaging": 1,
    },
    "high_criticality": 1,
    "escalation_required": 2,
}


def compare_dict_part(
    actual: dict,
    expected: dict,
    section_name: str,
) -> list[str]:
    problems = []

    for key, expected_value in expected.items():
        actual_value = actual.get(key, 0)

        if actual_value != expected_value:
            problems.append(
                f"{section_name}: {key} "
                f"ожидалось {expected_value}, получено {actual_value}"
            )

    return problems


def main():
    assistant = ReviewAssistant()

    print("=" * 70)
    print("              TESTING GROUP ANALYTICS")
    print("=" * 70)
    print()

    classified_reviews = []

    for index, review in enumerate(TEST_REVIEWS, start=1):
        print(
            f"Классификация отзыва "
            f"{index}/{len(TEST_REVIEWS)}..."
        )

        classification = assistant.classify_review(review)

        classification["review_number"] = index
        classification["review_text"] = review

        classified_reviews.append(classification)

    print()
    print("Проверка отдельных классификаций...")
    print()

    problems = []

    # Отзыв №3 — обычная задержка доставки.
    review_3 = classified_reviews[2]

    if review_3.get("criticality") != "medium":
        problems.append(
            "Отзыв №3: criticality должен быть medium"
        )

    if review_3.get("escalation_required") is not False:
        problems.append(
            "Отзыв №3: escalation_required должен быть False"
        )

    # Отзыв №4 — обычная неисправность.
    review_4 = classified_reviews[3]

    if review_4.get("criticality") != "medium":
        problems.append(
            "Отзыв №4: criticality должен быть medium"
        )

    if review_4.get("escalation_required") is not True:
        problems.append(
            "Отзыв №4: escalation_required должен быть True"
        )

    # Отзыв №6 — потенциально опасная неисправность.
    review_6 = classified_reviews[5]

    if review_6.get("criticality") != "high":
        problems.append(
            "Отзыв №6: criticality должен быть high"
        )

    if review_6.get("escalation_required") is not True:
        problems.append(
            "Отзыв №6: escalation_required должен быть True"
        )

    statistics = calculate_statistics(classified_reviews)

    print("Проверка статистики...")
    print()

    if (
        statistics.get("total_reviews")
        != EXPECTED_STATISTICS["total_reviews"]
    ):
        problems.append(
            "Общее количество отзывов: "
            f"ожидалось {EXPECTED_STATISTICS['total_reviews']}, "
            f"получено {statistics.get('total_reviews')}"
        )

    problems.extend(
        compare_dict_part(
            actual=statistics.get("sentiment", {}),
            expected=EXPECTED_STATISTICS["sentiment"],
            section_name="Тональность",
        )
    )

    problems.extend(
        compare_dict_part(
            actual=statistics.get("topics", {}),
            expected=EXPECTED_STATISTICS["topics"],
            section_name="Темы",
        )
    )

    if (
        statistics.get("high_criticality")
        != EXPECTED_STATISTICS["high_criticality"]
    ):
        problems.append(
            "Количество high-criticality: "
            f"ожидалось {EXPECTED_STATISTICS['high_criticality']}, "
            f"получено {statistics.get('high_criticality')}"
        )

    if (
        statistics.get("escalation_required")
        != EXPECTED_STATISTICS["escalation_required"]
    ):
        problems.append(
            "Количество эскалаций: "
            f"ожидалось {EXPECTED_STATISTICS['escalation_required']}, "
            f"получено {statistics.get('escalation_required')}"
        )

    print("=" * 70)

    if problems:
        print("FAIL")
        print()

        for problem in problems:
            print(f"- {problem}")

        print()
        print("Фактическая статистика:")
        print(statistics)

    else:
        print("PASS")
        print()
        print("Групповая классификация и статистика корректны.")
        print()
        print(f"Всего отзывов: {statistics['total_reviews']}")
        print(
            f"High-criticality: "
            f"{statistics['high_criticality']}"
        )
        print(
            f"Эскалаций: "
            f"{statistics['escalation_required']}"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()