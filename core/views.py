from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.db.models import Count
from django.db.models.functions import TruncDate
from .models import Course, Exercise, ProgressLog, Enrollment, SpacedRepetition, UserProfile
from .serializers import CourseSerializer, ExerciseSerializer
from .strategies.exercise_validation import ValidationContext, MultipleChoiceStrategy, TranslationStrategy
from .utils.math_model import calculate_sm2, get_next_review_date
from datetime import timedelta, date
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    @action(detail=False, methods=['post'])
    def register(self, request):
        u, p = request.data.get('username'), request.data.get('password')
        if not u or not p: return Response({'error': 'Required fields missing'}, 400)
        if User.objects.filter(username=u).exists(): return Response({'error': 'Taken'}, 400)
        user = User.objects.create_user(username=u, password=p)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.username})

    @action(detail=False, methods=['post'])
    def login(self, request):
        user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'username': user.username})
        return Response({'error': 'Invalid'}, 401)

class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Course.objects.prefetch_related('lessons__exercises').all()
    serializer_class = CourseSerializer

class ExerciseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        exercise = self.get_object()
        is_correct = ValidationContext(
            MultipleChoiceStrategy() if exercise.type == 'multiple_choice' else TranslationStrategy()
        ).validate_answer(request.data.get('answer', ''), exercise.data.get('correct_answer', ''))
        
        ProgressLog.objects.create(user=request.user, exercise=exercise, is_correct=is_correct)

        # ЖЕЛЕЗНОЕ ОБНОВЛЕНИЕ XP И СТРИКА
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if is_correct:
            profile.total_xp += 15
            
            today = timezone.now().date()
            if profile.last_activity != today:
                if profile.last_activity == today - timedelta(days=1):
                    profile.streak += 1
                elif profile.last_activity is None or profile.last_activity < today - timedelta(days=1):
                    profile.streak = 1
                profile.last_activity = today
            profile.save()

        # SM-2
        sr, _ = SpacedRepetition.objects.get_or_create(user=request.user, exercise=exercise)
        new_ef, new_iv, new_reps = calculate_sm2(5 if is_correct else 0, sr.repetitions, sr.easiness_factor, sr.interval)
        sr.easiness_factor, sr.interval, sr.repetitions = new_ef, new_iv, new_reps
        sr.next_review_date = get_next_review_date(new_iv)
        sr.save()
        
        return Response({'is_correct': is_correct, 'xp': profile.total_xp, 'streak': profile.streak})

class ProgressViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def list(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        
        # GitHub Graph Data
        activity = ProgressLog.objects.filter(user=request.user).annotate(
            date=TruncDate('timestamp')).values('date').annotate(count=Count('id'))
        activity_map = {item['date'].strftime('%Y-%m-%d'): item['count'] for item in activity}

        return Response({
            'status': 'ok',
            'streak': profile.streak,
            'xp': profile.total_xp,
            'activity_graph': activity_map
        })
