from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from random import shuffle


@dataclass
class ExerciseBlueprint:
    exercise_type: str
    payload: dict


@dataclass
class VocabularyEntry:
    source_word: str
    target_word: str
    distractors: list[str] = field(default_factory=list)


class AbstractExerciseFactory(ABC):
    @abstractmethod
    def create_multiple_choice(self, entry: VocabularyEntry) -> ExerciseBlueprint:
        raise NotImplementedError

    @abstractmethod
    def create_translation(self, entry: VocabularyEntry) -> ExerciseBlueprint:
        raise NotImplementedError

    @abstractmethod
    def create_matching_pairs(self, entries: list[VocabularyEntry]) -> ExerciseBlueprint:
        raise NotImplementedError

    @abstractmethod
    def create_listening(self, entry: VocabularyEntry) -> ExerciseBlueprint:
        raise NotImplementedError


class VocabularyExerciseFactory(AbstractExerciseFactory):
    def __init__(self, source_language_name: str, target_language_name: str):
        self.source_language_name = source_language_name
        self.target_language_name = target_language_name

    def create_multiple_choice(self, entry: VocabularyEntry) -> ExerciseBlueprint:
        options = [entry.target_word, *entry.distractors]
        shuffle(options)
        return ExerciseBlueprint(
            exercise_type='multiple_choice',
            payload={
                'question': f"Выберите перевод слова '{entry.source_word}'",
                'options': options,
                'correct_answer': entry.target_word,
            },
        )

    def create_translation(self, entry: VocabularyEntry) -> ExerciseBlueprint:
        return ExerciseBlueprint(
            exercise_type='translation',
            payload={
                'question': f"Переведите '{entry.source_word}' на {self.target_language_name}",
                'correct_answer': entry.target_word,
            },
        )

    def create_matching_pairs(self, entries: list[VocabularyEntry]) -> ExerciseBlueprint:
        return ExerciseBlueprint(
            exercise_type='matching_pairs',
            payload={
                'question': f"Соедините слова на {self.source_language_name} и {self.target_language_name}",
                'pairs': [
                    {
                        'left': pair.source_word,
                        'right': pair.target_word,
                    }
                    for pair in entries
                ],
                'correct_answer': [
                    {
                        'left': pair.source_word,
                        'right': pair.target_word,
                    }
                    for pair in entries
                ],
            },
        )

    def create_listening(self, entry: VocabularyEntry) -> ExerciseBlueprint:
        return ExerciseBlueprint(
            exercise_type='listening',
            payload={
                'question': f"Прослушайте слово и введите перевод на {self.source_language_name}",
                'audio_text': entry.target_word,
                'correct_answer': entry.source_word,
                'transcript': entry.target_word,
            },
        )


class ExerciseComponent(ABC):
    @abstractmethod
    def build(self) -> ExerciseBlueprint:
        raise NotImplementedError


class BaseExercise(ExerciseComponent):
    def __init__(self, blueprint: ExerciseBlueprint):
        self.blueprint = blueprint

    def build(self) -> ExerciseBlueprint:
        return ExerciseBlueprint(
            exercise_type=self.blueprint.exercise_type,
            payload=deepcopy(self.blueprint.payload),
        )


class ExerciseDecorator(ExerciseComponent):
    def __init__(self, component: ExerciseComponent):
        self.component = component

    def build(self) -> ExerciseBlueprint:
        return self.component.build()


class TimedExerciseDecorator(ExerciseDecorator):
    def __init__(self, component: ExerciseComponent, seconds: int):
        super().__init__(component)
        self.seconds = seconds

    def build(self) -> ExerciseBlueprint:
        blueprint = super().build()
        blueprint.payload['time_limit'] = self.seconds
        return blueprint


class HintExerciseDecorator(ExerciseDecorator):
    def __init__(self, component: ExerciseComponent, hint_text: str):
        super().__init__(component)
        self.hint_text = hint_text

    def build(self) -> ExerciseBlueprint:
        blueprint = super().build()
        blueprint.payload['hint'] = self.hint_text
        return blueprint


class ShuffleOptionsDecorator(ExerciseDecorator):
    def build(self) -> ExerciseBlueprint:
        blueprint = super().build()
        options = blueprint.payload.get('options')
        if isinstance(options, list):
            shuffle(options)
        return blueprint


class AudioSupportDecorator(ExerciseDecorator):
    def __init__(self, component: ExerciseComponent, voice_locale: str):
        super().__init__(component)
        self.voice_locale = voice_locale

    def build(self) -> ExerciseBlueprint:
        blueprint = super().build()
        blueprint.payload['voice_locale'] = self.voice_locale
        blueprint.payload['has_audio_support'] = True
        return blueprint
