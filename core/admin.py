from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .models import Achievement, Course, Exercise, Language, Lesson, UserAchievement, UserProfile


admin.site.site_header = 'Lingo Admin'
admin.site.site_title = 'Lingo Admin'
admin.site.index_title = 'Панель администратора курсов и заданий'


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0
    fields = ('total_xp', 'streak', 'last_activity')


class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'is_staff', 'is_active', 'has_token', 'profile_ready')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    def has_token(self, obj):
        return Token.objects.filter(user=obj).exists()

    has_token.boolean = True
    has_token.short_description = 'Токен'

    def profile_ready(self, obj):
        return UserProfile.objects.filter(user=obj).exists()

    profile_ready.boolean = True
    profile_ready.short_description = 'Профиль'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 1
    fields = ('type', 'data')
    show_change_link = True


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'order')
    show_change_link = True


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_xp', 'streak', 'last_activity')
    search_fields = ('user__username',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'source_language', 'lesson_count', 'exercise_count')
    search_fields = ('title', 'description')
    list_filter = ('language', 'source_language')
    inlines = [LessonInline]

    def lesson_count(self, obj):
        return obj.lessons.count()

    lesson_count.short_description = 'Уроков'

    def exercise_count(self, obj):
        return Exercise.objects.filter(lesson__course=obj).count()

    exercise_count.short_description = 'Заданий'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'exercise_count')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    inlines = [ExerciseInline]

    def exercise_count(self, obj):
        return obj.exercises.count()

    exercise_count.short_description = 'Заданий'


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'course_title', 'type')
    list_filter = ('type', 'lesson__course')
    search_fields = ('lesson__title', 'lesson__course__title')
    autocomplete_fields = ('lesson',)

    def course_title(self, obj):
        return obj.lesson.course.title

    course_title.short_description = 'Курс'


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'condition_type', 'threshold', 'xp_reward', 'medal_tier')
    list_filter = ('condition_type', 'medal_tier')
    search_fields = ('title', 'code', 'description')


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'awarded_at')
    list_filter = ('achievement',)
    search_fields = ('user__username', 'achievement__title')
