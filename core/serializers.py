from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Achievement, Course, Enrollment, Exercise, Language, Lesson, UserAchievement


class UserSessionSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'is_staff', 'is_superuser', 'role']

    def get_role(self, obj):
        return 'admin' if obj.is_staff else 'student'


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name', 'code']


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['code', 'title', 'description', 'icon', 'medal_tier', 'condition_type', 'threshold', 'xp_reward']


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ['id', 'awarded_at', 'progress_snapshot', 'achievement']


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    source_language_code = serializers.CharField(source='source_language.code', read_only=True)
    target_language_code = serializers.CharField(source='language.code', read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_title', 'status', 'started_at']
