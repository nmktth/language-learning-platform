from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import timedelta

from django.utils import timezone

from core.models import ProgressLog, SpacedRepetition, UserProfile
from core.patterns.behavioral import AchievementDefinitionAdapter, AchievementObserver, LegacyExternalSystem, ProgressEvent, Subject
from core.utils.math_model import calculate_sm2, get_next_review_date


@dataclass
class SubmissionContext:
    user: object
    exercise: object
    answer: object
    strategy: object
    profile: UserProfile | None = None
    is_correct: bool = False
    unlocked_achievements: list = field(default_factory=list)


class WorkflowTemplate(ABC):
    def execute_workflow(self, data):
        self.step_start(data)
        if self.step_validate(data):
            self.step_process(data)
            self.step_log_progress(data)
        self.step_end(data)
        return self.get_result(data)

    def step_start(self, data):
        return None

    @abstractmethod
    def step_validate(self, data) -> bool:
        raise NotImplementedError

    @abstractmethod
    def step_process(self, data):
        raise NotImplementedError

    @abstractmethod
    def step_log_progress(self, data):
        raise NotImplementedError

    def step_end(self, data):
        return None

    @abstractmethod
    def get_result(self, data):
        raise NotImplementedError


class ExerciseSubmissionWorkflow(WorkflowTemplate):
    def step_validate(self, data: SubmissionContext) -> bool:
        return data.answer is not None and data.strategy is not None

    def step_process(self, data: SubmissionContext):
        data.is_correct = data.strategy.validate(
            data.answer,
            data.exercise.data.get('correct_answer', ''),
        )

    def step_log_progress(self, data: SubmissionContext):
        ProgressLog.objects.create(user=data.user, exercise=data.exercise, is_correct=data.is_correct)

        profile, _ = UserProfile.objects.get_or_create(user=data.user)
        if data.is_correct:
            profile.total_xp += 15
            today = timezone.now().date()
            if profile.last_activity != today:
                if profile.last_activity == today - timedelta(days=1):
                    profile.streak += 1
                elif profile.last_activity is None or profile.last_activity < today - timedelta(days=1):
                    profile.streak = 1
                profile.last_activity = today
            profile.save()

        spaced_repetition, _ = SpacedRepetition.objects.get_or_create(user=data.user, exercise=data.exercise)
        new_ef, new_interval, new_repetitions = calculate_sm2(
            5 if data.is_correct else 0,
            spaced_repetition.repetitions,
            spaced_repetition.easiness_factor,
            spaced_repetition.interval,
        )
        spaced_repetition.easiness_factor = new_ef
        spaced_repetition.interval = new_interval
        spaced_repetition.repetitions = new_repetitions
        spaced_repetition.next_review_date = get_next_review_date(new_interval)
        spaced_repetition.save()

        achievement_subject = Subject()
        achievement_subject.attach(
            AchievementObserver(
                AchievementDefinitionAdapter(LegacyExternalSystem())
            )
        )
        notifications = achievement_subject.notify(
            ProgressEvent(
                user=data.user,
                profile=profile,
                is_correct=data.is_correct,
                lesson_id=data.exercise.lesson_id,
            )
        )
        data.profile = profile
        data.unlocked_achievements = [item for notification in notifications for item in notification.unlocked]

    def get_result(self, data: SubmissionContext):
        return {
            'is_correct': data.is_correct,
            'xp': data.profile.total_xp if data.profile else 0,
            'streak': data.profile.streak if data.profile else 0,
            'unlocked_achievements': data.unlocked_achievements,
        }
