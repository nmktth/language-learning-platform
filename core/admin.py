from django.contrib import admin
from .models import Language, Course, Lesson, Exercise, Enrollment, ProgressLog, SpacedRepetition

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'source_language')
    list_filter = ('language', 'source_language')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'type')
    list_filter = ('type', 'lesson__course')

@admin.register(ProgressLog)
class ProgressLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'exercise', 'is_correct', 'timestamp')
    list_filter = ('is_correct', 'user')

@admin.register(SpacedRepetition)
class SpacedRepetitionAdmin(admin.ModelAdmin):
    list_display = ('user', 'exercise', 'interval', 'next_review_date')
    list_filter = ('user',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'started_at')
