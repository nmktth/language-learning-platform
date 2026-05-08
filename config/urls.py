from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.views import AuthViewSet, CourseViewSet, EnrollmentViewSet, ExerciseViewSet, LanguageViewSet, LessonViewSet, ProgressViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'languages', LanguageViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'enrollments', EnrollmentViewSet, basename='enrollments')
router.register(r'exercises', ExerciseViewSet)
router.register(r'progress', ProgressViewSet, basename='progress')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
