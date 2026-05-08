from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Course, Enrollment, Exercise, Language, Lesson, ProgressLog, UserAchievement, UserProfile
from .patterns.behavioral import Invoker, SubmitAnswerCommand
from .patterns.template_method import ExerciseSubmissionWorkflow, SubmissionContext
from .permissions import IsStaffOrReadOnly
from .serializers import (
    CourseSerializer,
    EnrollmentSerializer,
    ExerciseSerializer,
    LanguageSerializer,
    LessonSerializer,
    UserAchievementSerializer,
    UserSessionSerializer,
)
from .states import EnrollmentContext
from .strategies.exercise_validation import (
    ListeningStrategy,
    MatchingPairsStrategy,
    MultipleChoiceStrategy,
    TranslationStrategy,
)


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        username = (request.data.get('username') or '').strip()
        password = request.data.get('password') or ''
        password_confirm = request.data.get('password_confirm') or ''

        if len(username) < 3:
            return Response({'error': 'Username must be at least 3 characters.'}, status=400)
        if len(password) < 8:
            return Response({'error': 'Password must be at least 8 characters.'}, status=400)
        if password != password_confirm:
            return Response({'error': 'Passwords do not match.'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username is already taken.'}, status=400)

        user = User.objects.create_user(username=username, password=password)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSessionSerializer(user).data}, status=201)

    @action(detail=False, methods=['post'])
    def login(self, request):
        user = authenticate(
            username=request.data.get('username'),
            password=request.data.get('password'),
        )
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': UserSessionSerializer(user).data})
        return Response({'error': 'Invalid username or password.'}, status=401)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response({'user': UserSessionSerializer(request.user).data})


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all().order_by('name')
    serializer_class = LanguageSerializer
    permission_classes = [IsStaffOrReadOnly]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.prefetch_related('lessons__exercises').all()
    serializer_class = CourseSerializer
    permission_classes = [IsStaffOrReadOnly]


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.prefetch_related('exercises').all()
    serializer_class = LessonSerializer
    permission_classes = [IsStaffOrReadOnly]


class EnrollmentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Enrollment.objects.filter(user=request.user).select_related('course')
        return Response(EnrollmentSerializer(queryset, many=True).data)

    @action(detail=False, methods=['post'])
    def enroll(self, request):
        course = get_object_or_404(Course, pk=request.data.get('course_id'))
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'status': 'active'},
        )
        if not created and enrollment.status == 'completed':
            enrollment.status = 'active'
            enrollment.save(update_fields=['status'])
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        enrollment = get_object_or_404(Enrollment, pk=pk, user=request.user)
        EnrollmentContext(enrollment).pause()
        return Response(EnrollmentSerializer(enrollment).data)

    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        enrollment = get_object_or_404(Enrollment, pk=pk, user=request.user)
        EnrollmentContext(enrollment).resume()
        return Response(EnrollmentSerializer(enrollment).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        enrollment = get_object_or_404(Enrollment, pk=pk, user=request.user)
        EnrollmentContext(enrollment).complete()
        return Response(EnrollmentSerializer(enrollment).data)


class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsStaffOrReadOnly]

    def _resolve_strategy(self, exercise_type: str):
        strategy_map = {
            Exercise.TYPE_MULTIPLE_CHOICE: MultipleChoiceStrategy(),
            Exercise.TYPE_TRANSLATION: TranslationStrategy(),
            Exercise.TYPE_MATCHING_PAIRS: MatchingPairsStrategy(),
            Exercise.TYPE_LISTENING: ListeningStrategy(),
        }
        return strategy_map.get(exercise_type, TranslationStrategy())

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit_answer(self, request, pk=None):
        exercise = self.get_object()
        workflow = ExerciseSubmissionWorkflow()
        payload = SubmissionContext(
            user=request.user,
            exercise=exercise,
            answer=request.data.get('answer', ''),
            strategy=self._resolve_strategy(exercise.type),
        )
        result = Invoker().store_and_execute(SubmitAnswerCommand(workflow, payload))

        return Response(
            {
                'is_correct': result['is_correct'],
                'xp': result['xp'],
                'streak': result['streak'],
                'unlocked_achievements': UserAchievementSerializer(result['unlocked_achievements'], many=True).data,
            }
        )


class ProgressViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        activity = (
            ProgressLog.objects.filter(user=request.user)
            .annotate(date=TruncDate('timestamp'))
            .values('date')
            .annotate(count=Count('id'))
        )
        activity_map = {item['date'].strftime('%Y-%m-%d'): item['count'] for item in activity}
        achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement')
        enrollments = Enrollment.objects.filter(user=request.user).select_related('course')

        return Response(
            {
                'status': 'ok',
                'streak': profile.streak,
                'xp': profile.total_xp,
                'activity_graph': activity_map,
                'achievements': UserAchievementSerializer(achievements, many=True).data,
                'enrollments': EnrollmentSerializer(enrollments, many=True).data,
                'user': UserSessionSerializer(request.user).data,
            }
        )
