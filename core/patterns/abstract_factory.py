from abc import ABC, abstractmethod
import json

# ==========================================
# ABSTRACT FACTORY PATTERN
# ==========================================
class AbstractExerciseFactory(ABC):
    @abstractmethod
    def create_multiple_choice(self):
        pass

    @abstractmethod
    def create_translation(self):
        pass

class BeginnerExerciseFactory(AbstractExerciseFactory):
    def create_multiple_choice(self):
        return {"type": "multiple_choice", "data": {"question": "What is 2+2?", "options": ["3", "4"], "correct_answer": "4"}}

    def create_translation(self):
        return {"type": "translation", "data": {"question": "Translate 'Dog'", "correct_answer": "Perro"}}

class AdvancedExerciseFactory(AbstractExerciseFactory):
    def create_multiple_choice(self):
        return {"type": "multiple_choice", "data": {"question": "Quantum superposition implies...", "options": ["A", "B", "C"], "correct_answer": "C"}}

    def create_translation(self):
        return {"type": "translation", "data": {"question": "Translate 'Serendipity'", "correct_answer": "Serendipia"}}


# ==========================================
# DECORATOR PATTERN
# ==========================================
class ExerciseComponent(ABC):
    @abstractmethod
    def get_data(self) -> dict:
        pass

class BaseExercise(ExerciseComponent):
    def __init__(self, exercise_data: dict):
        self._data = exercise_data

    def get_data(self) -> dict:
        return self._data

class ExerciseDecorator(ExerciseComponent):
    def __init__(self, component: ExerciseComponent):
        self._component = component

    def get_data(self) -> dict:
        return self._component.get_data()

class TimedExerciseDecorator(ExerciseDecorator):
    def __init__(self, component: ExerciseComponent, time_limit_sec: int):
        super().__init__(component)
        self.time_limit = time_limit_sec

    def get_data(self) -> dict:
        data = super().get_data()
        data["time_limit"] = self.time_limit
        return data

class HintExerciseDecorator(ExerciseDecorator):
    def __init__(self, component: ExerciseComponent, hint_text: str):
        super().__init__(component)
        self.hint_text = hint_text

    def get_data(self) -> dict:
        data = super().get_data()
        data["hint"] = self.hint_text
        return data
