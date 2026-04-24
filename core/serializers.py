from rest_framework import serializers
from .models import Course, Lesson, Exercise, ProgressLog

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

    class Meta:
        model = Course
        fields = '__all__'
