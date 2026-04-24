from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import CourseViewSet, ExerciseViewSet, ProgressViewSet, AuthViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'courses', CourseViewSet)
router.register(r'exercises', ExerciseViewSet)
router.register(r'progress', ProgressViewSet, basename='progress')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
