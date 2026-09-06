import pandas as pd

from config import KNOWLEDGE_BASE_PATH


class KnowledgeBase:
    def __init__(self):
        self.df = pd.read_csv(KNOWLEDGE_BASE_PATH)

    def get_company_rules(self) -> str:
        rules = self.df[self.df["record_type"] == "company_rule"]

        blocks = []

        for _, row in rules.iterrows():
            blocks.append(
                "\n".join(
                    [
                        f"Тема: {self._safe(row.get('topic'))}",
                        f"Правило: {self._safe(row.get('subtopic'))}",
                        f"Описание: {self._safe(row.get('recommended_action'))}",
                        f"Ограничения: {self._safe(row.get('rules'))}",
                        f"Примечание: {self._safe(row.get('notes'))}",
                    ]
                )
            )

        return "\n\n".join(blocks)

    def search(self, text: str, limit: int = 6) -> str:
        text_lower = text.lower()

        situations = self.df[
            self.df["record_type"] == "situation"
        ].copy()

        situations["score"] = situations.apply(
            lambda row: self._calculate_score(row, text_lower),
            axis=1,
        )

        relevant = situations.sort_values(
            by="score",
            ascending=False,
        )

        relevant = relevant[relevant["score"] > 0].head(limit)

        blocks = []

        for _, row in relevant.iterrows():
            blocks.append(
                "\n".join(
                    [
                        f"Тип ситуации: {self._safe(row.get('situation_type'))}",
                        f"Тональность: {self._safe(row.get('sentiment'))}",
                        f"Тема: {self._safe(row.get('topic'))}",
                        f"Подтема: {self._safe(row.get('subtopic'))}",
                        f"Характерные фразы: {self._safe(row.get('trigger_phrases'))}",
                        f"Шаблон ответа: {self._safe(row.get('response_template'))}",
                        f"Действие: {self._safe(row.get('recommended_action'))}",
                        f"Эскалация: {self._safe(row.get('escalation_required'))}",
                        f"Критичность: {self._safe(row.get('criticality'))}",
                        f"Правила: {self._safe(row.get('rules'))}",
                        f"Примечания: {self._safe(row.get('notes'))}",
                    ]
                )
            )

        if not blocks:
            return "Релевантные записи не найдены."

        return "\n\n".join(blocks)

    def get_analytics_examples(self) -> str:
        examples = self.df[
            self.df["record_type"] == "analytics_example"
        ]

        blocks = []

        for _, row in examples.iterrows():
            text = self._safe(row.get("recommended_action"))

            if text:
                blocks.append(text)

        return "\n".join(blocks)

    def _calculate_score(self, row, text: str) -> int:
        score = 0

        searchable_fields = [
            "trigger_phrases",
            "topic",
            "subtopic",
            "situation_type",
            "notes",
        ]

        for field in searchable_fields:
            value = self._safe(row.get(field)).lower()

            if not value:
                continue

            terms = [
                term.strip()
                for term in value.replace(",", ";").split(";")
                if term.strip()
            ]

            for term in terms:
                if term in text:
                    score += 2

                for word in term.split():
                    if len(word) >= 4 and word in text:
                        score += 1

        return score

    @staticmethod
    def _safe(value) -> str:
        if pd.isna(value):
            return ""

        return str(value).strip()