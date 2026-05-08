from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Language(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_xp = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    last_activity = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='target_courses')
    source_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='source_courses', null=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Exercise(models.Model):
    TYPE_MULTIPLE_CHOICE = 'multiple_choice'
    TYPE_TRANSLATION = 'translation'
    TYPE_MATCHING_PAIRS = 'matching_pairs'
    TYPE_LISTENING = 'listening'

    TYPE_CHOICES = [
        (TYPE_MULTIPLE_CHOICE, 'Multiple choice'),
        (TYPE_TRANSLATION, 'Translation'),
        (TYPE_MATCHING_PAIRS, 'Matching pairs'),
        (TYPE_LISTENING, 'Listening'),
    ]

    lesson = models.ForeignKey(Lesson, related_name='exercises', on_delete=models.CASCADE)
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    data = models.JSONField()

    def __str__(self):
        return f"{self.lesson.title}: {self.type}"


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active')


class ProgressLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)


class SpacedRepetition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    easiness_factor = models.FloatField(default=2.5)
    interval = models.IntegerField(default=0)
    repetitions = models.IntegerField(default=0)
    next_review_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'exercise')


class Achievement(models.Model):
    CONDITION_XP = 'xp'
    CONDITION_STREAK = 'streak'
    CONDITION_CORRECT = 'correct_answers'
    CONDITION_COMPLETED = 'completed_lessons'

    CONDITION_CHOICES = [
        (CONDITION_XP, 'XP reached'),
        (CONDITION_STREAK, 'Streak reached'),
        (CONDITION_CORRECT, 'Correct answers count'),
        (CONDITION_COMPLETED, 'Completed lessons count'),
    ]

    code = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=120)
    description = models.TextField()
    icon = models.CharField(max_length=32, default='bronze')
    medal_tier = models.CharField(max_length=32, default='bronze')
    condition_type = models.CharField(max_length=32, choices=CONDITION_CHOICES)
    threshold = models.PositiveIntegerField(default=1)
    xp_reward = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='users')
    awarded_at = models.DateTimeField(auto_now_add=True)
    progress_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('user', 'achievement')
        ordering = ['-awarded_at']

    def __str__(self):
        return f"{self.user.username} -> {self.achievement.code}"
