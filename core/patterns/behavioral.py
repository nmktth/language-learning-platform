from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from django.contrib.auth.models import User
from django.db.models import Count

from core.models import Achievement, ProgressLog, UserAchievement, UserProfile


@dataclass
class AchievementProgress:
    unlocked: list[UserAchievement] = field(default_factory=list)


@dataclass
class ProgressEvent:
    user: User
    profile: UserProfile
    is_correct: bool
    lesson_id: int


class Observer(ABC):
    @abstractmethod
    def update(self, event: ProgressEvent) -> AchievementProgress:
        raise NotImplementedError


class Subject:
    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def notify(self, event: ProgressEvent) -> list[AchievementProgress]:
        return [observer.update(event) for observer in self._observers]


class AchievementObserver(Observer):
    def __init__(self, adapter):
        self.adapter = adapter

    def update(self, event: ProgressEvent) -> AchievementProgress:
        self.adapter.sync()
        unlocked: list[UserAchievement] = []

        for achievement in Achievement.objects.all():
            if UserAchievement.objects.filter(user=event.user, achievement=achievement).exists():
                continue

            current_value = self._resolve_metric(event, achievement.condition_type)
            if current_value < achievement.threshold:
                continue

            user_achievement = UserAchievement.objects.create(
                user=event.user,
                achievement=achievement,
                progress_snapshot={
                    'metric': achievement.condition_type,
                    'value': current_value,
                    'threshold': achievement.threshold,
                },
            )
            unlocked.append(user_achievement)

            if achievement.xp_reward:
                event.profile.total_xp += achievement.xp_reward
                event.profile.save(update_fields=['total_xp'])

        return AchievementProgress(unlocked=unlocked)

    def _resolve_metric(self, event: ProgressEvent, condition_type: str) -> int:
        if condition_type == Achievement.CONDITION_XP:
            return event.profile.total_xp
        if condition_type == Achievement.CONDITION_STREAK:
            return event.profile.streak
        if condition_type == Achievement.CONDITION_CORRECT:
            return ProgressLog.objects.filter(user=event.user, is_correct=True).count()
        if condition_type == Achievement.CONDITION_COMPLETED:
            return (
                ProgressLog.objects.filter(user=event.user, is_correct=True)
                .values('exercise__lesson_id')
                .annotate(total=Count('exercise__lesson_id'))
                .count()
            )
        return 0


class Command(ABC):
    @abstractmethod
    def execute(self):
        raise NotImplementedError


class SubmitAnswerCommand(Command):
    def __init__(self, workflow, data):
        self.workflow = workflow
        self.data = data

    def execute(self):
        return self.workflow.execute_workflow(self.data)


class Invoker:
    def __init__(self):
        self._history = []

    def store_and_execute(self, command: Command):
        self._history.append(command)
        return command.execute()


class LegacyExternalSystem:
    def get_raw_achievements(self):
        return [
            {
                'slug': 'first-steps',
                'name': 'Первые шаги',
                'details': 'Дайте 1 правильный ответ.',
                'tier': 'bronze',
                'metric': 'correct_answers',
                'goal': 1,
                'bonus_xp': 5,
            },
            {
                'slug': 'focus-10',
                'name': 'Фокус на 10 XP',
                'details': 'Наберите 10 XP.',
                'tier': 'silver',
                'metric': 'xp',
                'goal': 10,
                'bonus_xp': 10,
            },
            {
                'slug': 'streak-3',
                'name': 'Серия 3 дня',
                'details': 'Сохраняйте серию 3 дня.',
                'tier': 'gold',
                'metric': 'streak',
                'goal': 3,
                'bonus_xp': 20,
            },
        ]


class AchievementDefinitionAdapter:
    def __init__(self, legacy_system: LegacyExternalSystem):
        self.legacy_system = legacy_system

    def sync(self):
        for payload in self.legacy_system.get_raw_achievements():
            Achievement.objects.update_or_create(
                code=payload['slug'],
                defaults={
                    'title': payload['name'],
                    'description': payload['details'],
                    'icon': payload['tier'],
                    'medal_tier': payload['tier'],
                    'condition_type': payload['metric'],
                    'threshold': payload['goal'],
                    'xp_reward': payload['bonus_xp'],
                },
            )
