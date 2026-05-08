from abc import ABC, abstractmethod


class ValidationStrategy(ABC):
    @abstractmethod
    def validate(self, user_answer, correct_answer):
        raise NotImplementedError


class MultipleChoiceStrategy(ValidationStrategy):
    def validate(self, user_answer, correct_answer):
        return str(user_answer).strip().lower() == str(correct_answer).strip().lower()


class TranslationStrategy(ValidationStrategy):
    def validate(self, user_answer, correct_answer):
        return str(user_answer).strip().lower() == str(correct_answer).strip().lower()


class MatchingPairsStrategy(ValidationStrategy):
    def validate(self, user_answer, correct_answer):
        normalized_user = sorted(user_answer, key=lambda item: item['left']) if isinstance(user_answer, list) else []
        normalized_correct = sorted(correct_answer, key=lambda item: item['left']) if isinstance(correct_answer, list) else []
        return normalized_user == normalized_correct


class ListeningStrategy(ValidationStrategy):
    def validate(self, user_answer, correct_answer):
        return str(user_answer).strip().lower() == str(correct_answer).strip().lower()


class ValidationContext:
    def __init__(self, strategy: ValidationStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ValidationStrategy):
        self._strategy = strategy

    def validate_answer(self, user_answer, correct_answer):
        return self._strategy.validate(user_answer, correct_answer)
