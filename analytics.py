from collections import Counter


def collect_reviews() -> list[str]:
    reviews = []

    print()
    print("Введите отзывы по одному.")
    print("Для завершения оставьте строку пустой и нажмите Enter.")
    print()

    while True:
        review = input(f"Отзыв #{len(reviews) + 1}: ").strip()

        if not review:
            break

        reviews.append(review)

    return reviews


def calculate_statistics(classified_reviews: list[dict]) -> dict:
    sentiment_counter = Counter()
    topic_counter = Counter()

    high_criticality = 0
    escalation_required = 0

    for review in classified_reviews:
        sentiment = review.get("sentiment")

        if sentiment:
            sentiment_counter[sentiment] += 1

        topics = review.get("topics", [])

        for topic in topics:
            topic_counter[topic] += 1

        if review.get("criticality") == "high":
            high_criticality += 1

        if review.get("escalation_required") is True:
            escalation_required += 1

    total_reviews = len(classified_reviews)

    sentiment_percentages = {}

    for sentiment, count in sentiment_counter.items():
        percentage = (
            round(count / total_reviews * 100, 1)
            if total_reviews
            else 0
        )

        sentiment_percentages[sentiment] = {
            "count": count,
            "percentage": percentage,
        }

    statistics = {
        "total_reviews": total_reviews,
        "sentiment": dict(sentiment_counter),
        "sentiment_percentages": sentiment_percentages,
        "topics": dict(topic_counter),
        "high_criticality": high_criticality,
        "escalation_required": escalation_required,
    }

    return statistics