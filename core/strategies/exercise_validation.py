from abc import ABC, abstractmethod

class ValidationStrategy(ABC):
    @abstractmethod
    def validate(self, user_answer, correct_answer):
        pass

class MultipleChoiceStrategy(ValidationStrategy):
    def validate(self, user_answer, correct_answer):
        return str(user_answer).strip().lower() == str(correct_answer).strip().lower()

class TranslationStrategy(ValidationStrategy):
    def validate(self, user_answer, correct_answer):
        # Could be more complex (fuzzy matching)
        return str(user_answer).strip().lower() == str(correct_answer).strip().lower()

class ValidationContext:
    def __init__(self, strategy: ValidationStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ValidationStrategy):
        self._strategy = strategy

    def validate_answer(self, user_answer, correct_answer):
        return self._strategy.validate(user_answer, correct_answer)
