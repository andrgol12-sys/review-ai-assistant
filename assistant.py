import json

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL
from knowledge_base import KnowledgeBase
from prompts import build_system_prompt


class ReviewAssistant:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.knowledge_base = KnowledgeBase()

        self.system_prompt = build_system_prompt(
            company_name="HomeTech",
            company_description="Интернет-магазин бытовой техники и электроники.",
            response_language="русский",
        )

    def analyze_review(self, review: str) -> str:
        relevant_context = self.knowledge_base.search(review)
        company_rules = self.knowledge_base.get_company_rules()

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

        response = self.client.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=user_prompt,
            temperature=0.2,
        )

        return response.output_text

    def classify_review(self, review: str) -> dict:
        """
        Выполняет структурированную классификацию отзыва.

        Результат используется Python-кодом
        для построения групповой аналитики.
        """

        relevant_context = self.knowledge_base.search(review)
        company_rules = self.knowledge_base.get_company_rules()

        classification_prompt = f"""
Проанализируй отзыв и верни ТОЛЬКО корректный JSON.

ОТЗЫВ:
{review}

ОБЩИЕ ПРАВИЛА HOMETECH:
{company_rules}

РЕЛЕВАНТНЫЕ ЗАПИСИ БАЗЫ ЗНАНИЙ:
{relevant_context}

Верни объект строго такой структуры:

{{
  "sentiment": "positive | neutral | negative | mixed",
  "type": "gratitude | complaint | suggestion | question | mixed",
  "topics": ["topic1", "topic2"],
  "criticality": "low | medium | high",
  "escalation_required": true,
  "main_issue": "краткое описание сути обращения"
}}

Допустимые темы:
- product
- quality
- delivery
- packaging
- service
- price
- website
- return_exchange
- warranty
- assortment
- compensation
- privacy
- legal
- other

ВАЖНО:

- не добавляй тему, которой нет в отзыве;
- не придумывай компенсацию;
- не придумывай гарантию;
- не придумывай возврат;
- не придумывай требования клиента;
- учитывай все явно выраженные темы;
- если причина проблемы неизвестна, используй other;
- если присутствуют персональные данные,
  добавь тему privacy;
- верни только JSON;
- не используй Markdown;
- не добавляй пояснения до или после JSON.
"""

        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "Ты выполняешь структурированную классификацию "
                "клиентского отзыва для дальнейшей обработки Python-кодом. "
                "Верни только валидный JSON без Markdown и пояснений."
            ),
            input=classification_prompt,
            temperature=0,
        )

        raw_text = response.output_text.strip()

        # Иногда модель всё равно возвращает:
        #
        # ```json
        # {...}
        # ```
        #
        # Удаляем Markdown-обёртку.
        if raw_text.startswith("```"):
            raw_text = raw_text.removeprefix("```json")
            raw_text = raw_text.removeprefix("```")
            raw_text = raw_text.removesuffix("```")
            raw_text = raw_text.strip()

        try:
            classification = json.loads(raw_text)

        except json.JSONDecodeError as error:
            raise ValueError(
                "Модель вернула некорректный JSON.\n"
                f"Ответ модели:\n{raw_text}"
            ) from error

        # Применяем единые бизнес-правила HomeTech.
        classification = self._apply_business_rules(
            review=review,
            classification=classification,
        )

        return classification

    def _apply_business_rules(
        self,
        review: str,
        classification: dict,
    ) -> dict:
        """
        Приводит критичность и эскалацию
        к единым бизнес-правилам HomeTech.

        LLM определяет смысл отзыва,
        а Python гарантирует соблюдение
        ключевых правил эскалации.
        """

        text = review.lower()

        topics = classification.get("topics", [])

        if not isinstance(topics, list):
            topics = []

        topics = [str(topic).lower() for topic in topics]

        criticality = classification.get(
            "criticality",
            "low",
        )

        escalation = bool(
            classification.get(
                "escalation_required",
                False,
            )
        )

        # --------------------------------------------------
        # 1. Потенциально опасная неисправность
        # --------------------------------------------------

        dangerous_phrases = [
            "искрит",
            "задымился",
            "дымит",
            "запах гари",
            "пахнет горелым",
            "перегревается",
            "горит",
        ]

        if any(
            phrase in text
            for phrase in dangerous_phrases
        ):
            criticality = "high"
            escalation = True

        # --------------------------------------------------
        # 2. Обычная неисправность товара
        # --------------------------------------------------

        defect_phrases = [
            "не работает",
            "перестал работать",
            "перестал включаться",
            "не включается",
            "сломался",
            "сломалась",
            "неисправен",
            "неисправна",
            "брак",
        ]

        elif_defect = any(
            phrase in text
            for phrase in defect_phrases
        )

        if (
            elif_defect
            and not any(
                phrase in text
                for phrase in dangerous_phrases
            )
        ):
            criticality = "medium"
            escalation = True

        # --------------------------------------------------
        # 3. Требование компенсации
        # --------------------------------------------------

        if "compensation" in topics:
            criticality = "high"
            escalation = True

        # --------------------------------------------------
        # 4. Возврат или обмен
        # --------------------------------------------------

        if "return_exchange" in topics:
            if criticality != "high":
                criticality = "medium"

            escalation = True

        # --------------------------------------------------
        # 5. Гарантийный вопрос
        # --------------------------------------------------

        if "warranty" in topics:
            if criticality != "high":
                criticality = "medium"

            escalation = True

        # --------------------------------------------------
        # 6. Юридические угрозы / контролирующие органы
        # --------------------------------------------------

        if "legal" in topics:
            criticality = "high"
            escalation = True

        # --------------------------------------------------
        # 7. Заказ вообще не доставлен
        # --------------------------------------------------

        not_delivered_phrases = [
            "не доставили",
            "не привезли",
            "заказ не приехал",
            "товар не приехал",
        ]

        if any(
            phrase in text
            for phrase in not_delivered_phrases
        ):
            criticality = "high"
            escalation = True

        # --------------------------------------------------
        # 8. Доставлен неправильный товар
        # --------------------------------------------------

        wrong_item_phrases = [
            "не тот товар",
            "другая модель",
            "привезли другой",
            "перепутали товар",
        ]

        if any(
            phrase in text
            for phrase in wrong_item_phrases
        ):
            criticality = "high"
            escalation = True

        # --------------------------------------------------
        # 9. Повторная нерешённая жалоба
        # --------------------------------------------------

        repeat_phrases = [
            "уже обращался",
            "уже обращалась",
            "повторно пишу",
            "снова проблема",
            "до сих пор не решили",
            "никто не решил",
        ]

        if any(
            phrase in text
            for phrase in repeat_phrases
        ):
            criticality = "high"
            escalation = True

        # --------------------------------------------------
        # 10. Обычная задержка доставки
        #
        # Если нет более серьёзного основания,
        # обычное опоздание не требует эскалации.
        # --------------------------------------------------

        delay_phrases = [
            "опоздал",
            "опоздала",
            "задержали доставку",
            "доставка задержалась",
            "доставили позже",
        ]

        ordinary_delay = any(
            phrase in text
            for phrase in delay_phrases
        )

        serious_topics = {
            "compensation",
            "return_exchange",
            "warranty",
            "legal",
        }

        has_serious_topic = any(
            topic in serious_topics
            for topic in topics
        )

        has_danger = any(
            phrase in text
            for phrase in dangerous_phrases
        )

        has_defect = any(
            phrase in text
            for phrase in defect_phrases
        )

        has_not_delivered = any(
            phrase in text
            for phrase in not_delivered_phrases
        )

        has_repeat = any(
            phrase in text
            for phrase in repeat_phrases
        )

        if (
            ordinary_delay
            and not has_serious_topic
            and not has_danger
            and not has_defect
            and not has_not_delivered
            and not has_repeat
        ):
            criticality = "medium"
            escalation = False

        classification["criticality"] = criticality
        classification["escalation_required"] = escalation

        return classification

    def generate_analytics_summary(
        self,
        statistics: dict,
        classified_reviews: list[dict],
    ) -> str:
        """
        Формирует текстовую аналитическую сводку
        на основе уже рассчитанной Python-статистики.
        """

        analytics_examples = (
            self.knowledge_base.get_analytics_examples()
        )

        user_prompt = f"""
Сформируй краткую аналитическую сводку по отзывам HomeTech.

СТАТИСТИКА, РАССЧИТАННАЯ PYTHON:
{json.dumps(statistics, ensure_ascii=False, indent=2)}

КЛАССИФИЦИРОВАННЫЕ ОТЗЫВЫ:
{json.dumps(classified_reviews, ensure_ascii=False, indent=2)}

ПРИМЕРЫ СТРУКТУРЫ АНАЛИТИКИ:
{analytics_examples}

ВАЖНЫЕ ПРАВИЛА:

1. Не пересчитывай статистику самостоятельно.

2. Используй количественные значения только из блока
   «СТАТИСТИКА, РАССЧИТАННАЯ PYTHON».

3. Не придумывай:
   - темы;
   - требования;
   - компенсации;
   - причины проблем;
   - характеристики товаров.

4. Не называй отзыв критическим,
   если его criticality != "high".

5. Не утверждай причины выявленных проблем,
   если они прямо не содержатся во входных данных.

6. Все выводы относятся только
   к предоставленной выборке.

7. Не добавляй факты или требования,
   которых нет в классифицированных отзывах.

Структура ответа:

1. Объём выборки
2. Распределение по тональности
3. Основные темы
4. Повторяющиеся проблемы
5. Положительные тенденции
6. Критические случаи
7. Рекомендации
"""

        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "Ты формируешь аналитическую сводку "
                "по уже рассчитанным структурированным данным. "
                "Не изменяй количественные показатели "
                "и не придумывай отсутствующие факты."
            ),
            input=user_prompt,
            temperature=0.2,
        )

        return response.output_text