from analytics import collect_reviews, calculate_statistics
from assistant import ReviewAssistant


def print_header():
    print("=" * 60)
    print("              REVIEW AI ASSISTANT")
    print("                    HOMETECH")
    print("=" * 60)


def print_menu():
    print()
    print("Выберите режим:")
    print()
    print("1. Обработать один отзыв")
    print("2. Проанализировать несколько отзывов")
    print("3. Выход")
    print()


def main():
    print_header()

    print()
    print("Инициализация ассистента...")

    assistant = ReviewAssistant()

    print("Ассистент готов к работе.")

    while True:
        print_menu()

        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            print()
            review = input("Введите отзыв клиента:\n> ").strip()

            if not review:
                print("Отзыв не может быть пустым.")
                continue

            print()
            print("Анализирую отзыв...")
            print()

            try:
                result = assistant.analyze_review(review)

                print("=" * 60)
                print("РЕЗУЛЬТАТ")
                print("=" * 60)
                print()
                print(result)

            except Exception as error:
                print()
                print(f"Ошибка при обращении к OpenAI API: {error}")

        elif choice == "2":
            reviews = collect_reviews()

            if not reviews:
                print("Отзывы не были введены.")
                continue

            print()
            print(f"Анализирую {len(reviews)} отзывов...")
            print()

            try:
                classified_reviews = []

                for index, review in enumerate(reviews, start=1):
                    print(
                        f"Классификация отзыва "
                        f"{index}/{len(reviews)}..."
                    )

                    classification = assistant.classify_review(review)

                    classification["review_number"] = index
                    classification["review_text"] = review

                    classified_reviews.append(classification)


                statistics = calculate_statistics(
                    classified_reviews
                )

                print()
                print("Формирую аналитическую сводку...")

                result = assistant.generate_analytics_summary(
                    statistics=statistics,
                    classified_reviews=classified_reviews,
                )

                print()
                print("=" * 60)
                print("АНАЛИТИЧЕСКАЯ СВОДКА")
                print("=" * 60)
                print()
                print(result)

            except Exception as error:
                print()
                print(
                    f"Ошибка при анализе отзывов: {error}"
                )

        elif choice == "3":
            print()
            print("Работа завершена.")
            break

        else:
            print("Введите 1, 2 или 3.")


if __name__ == "__main__":
    main()