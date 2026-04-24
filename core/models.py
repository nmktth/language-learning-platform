from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Language(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    def __str__(self): return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_xp = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    last_activity = models.DateField(null=True, blank=True)
    def __str__(self): return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created: UserProfile.objects.get_or_create(user=instance)

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='target_courses')
    source_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='source_courses', null=True)
    def __str__(self): return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = models.IntegerField()
    class Meta: ordering = ['order']
    def __str__(self): return f"{self.course.title} - {self.title}"

class Exercise(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='exercises', on_delete=models.CASCADE)
    type = models.CharField(max_length=20)
    data = models.JSONField()

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
    class Meta: unique_together = ('user', 'exercise')
