from __future__ import annotations

from dataclasses import dataclass, field

from core.models import Course, Exercise, Language, Lesson
from core.patterns.abstract_factory import (
    AudioSupportDecorator,
    BaseExercise,
    HintExerciseDecorator,
    ShuffleOptionsDecorator,
    TimedExerciseDecorator,
    VocabularyEntry,
    VocabularyExerciseFactory,
)


@dataclass
class ExerciseModifierSpec:
    timed_seconds: int | None = None
    hint_text: str | None = None
    shuffle_options: bool = False
    add_audio_support: bool = False
    voice_locale: str = 'en-US'


@dataclass
class LessonSpec:
    title: str
    vocabulary: list[dict]
    include_matching_pairs: bool = True
    modifiers: ExerciseModifierSpec = field(default_factory=ExerciseModifierSpec)


@dataclass
class CourseSpec:
    title: str
    description: str
    target_language_code: str
    source_language_code: str
    lessons: list[LessonSpec]


class CourseCreationModule:
    def create_course(self, spec: CourseSpec) -> Course:
        target_language = Language.objects.get(code=spec.target_language_code)
        source_language = Language.objects.get(code=spec.source_language_code)
        course = Course.objects.create(
            title=spec.title,
            description=spec.description,
            language=target_language,
            source_language=source_language,
        )

        factory = VocabularyExerciseFactory(
            source_language_name=source_language.name,
            target_language_name=target_language.name,
        )

        for order, lesson_spec in enumerate(spec.lessons, start=1):
            lesson = Lesson.objects.create(course=course, title=lesson_spec.title, order=order)
            entries = self._build_entries(lesson_spec.vocabulary)

            for entry in entries:
                self._create_exercise(lesson, factory.create_translation(entry), lesson_spec.modifiers)
                self._create_exercise(lesson, factory.create_multiple_choice(entry), lesson_spec.modifiers)
                self._create_exercise(lesson, factory.create_listening(entry), lesson_spec.modifiers)

            if lesson_spec.include_matching_pairs and len(entries) >= 2:
                matching_blueprint = factory.create_matching_pairs(entries[: min(4, len(entries))])
                self._create_exercise(lesson, matching_blueprint, lesson_spec.modifiers)

        return course

    def _build_entries(self, vocabulary: list[dict]) -> list[VocabularyEntry]:
        entries: list[VocabularyEntry] = []
        for item in vocabulary:
            distractors = [
                candidate['target']
                for candidate in vocabulary
                if candidate['target'] != item['target']
            ][:3]
            entries.append(
                VocabularyEntry(
                    source_word=item['source'],
                    target_word=item['target'],
                    distractors=distractors,
                )
            )
        return entries

    def _create_exercise(self, lesson: Lesson, blueprint, modifiers: ExerciseModifierSpec) -> Exercise:
        component = BaseExercise(blueprint)

        if modifiers.hint_text:
            component = HintExerciseDecorator(component, modifiers.hint_text)
        if modifiers.timed_seconds:
            component = TimedExerciseDecorator(component, modifiers.timed_seconds)
        if modifiers.shuffle_options:
            component = ShuffleOptionsDecorator(component)
        if modifiers.add_audio_support:
            component = AudioSupportDecorator(component, modifiers.voice_locale)

        exercise_blueprint = component.build()
        return Exercise.objects.create(
            lesson=lesson,
            type=exercise_blueprint.exercise_type,
            data=exercise_blueprint.payload,
        )
