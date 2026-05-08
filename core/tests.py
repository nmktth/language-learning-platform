from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from core.models import Achievement, Course, Enrollment, Exercise, Language, UserAchievement
from core.patterns.behavioral import AchievementDefinitionAdapter, AchievementObserver, LegacyExternalSystem, ProgressEvent, Subject
from core.services.course_builder import CourseCreationModule, CourseSpec, ExerciseModifierSpec, LessonSpec


class CourseCreationModuleTests(TestCase):
    def setUp(self):
        self.ru = Language.objects.create(name='Русский', code='ru')
        self.en = Language.objects.create(name='English', code='en')

    def test_course_builder_creates_rich_exercise_set(self):
        course = CourseCreationModule().create_course(
            CourseSpec(
                title='Английский: Основы',
                description='Тестовый курс',
                target_language_code='en',
                source_language_code='ru',
                lessons=[
                    LessonSpec(
                        title='Урок 1',
                        vocabulary=[
                            {'source': 'Дом', 'target': 'House'},
                            {'source': 'Вода', 'target': 'Water'},
                        ],
                        modifiers=ExerciseModifierSpec(
                            timed_seconds=30,
                            hint_text='Подумайте о бытовой лексике.',
                            shuffle_options=True,
                            add_audio_support=True,
                            voice_locale='en-US',
                        ),
                    )
                ],
            )
        )

        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(course.lessons.count(), 1)
        self.assertEqual(course.lessons.first().exercises.count(), 7)
        listening = Exercise.objects.filter(type=Exercise.TYPE_LISTENING).first()
        matching = Exercise.objects.filter(type=Exercise.TYPE_MATCHING_PAIRS).first()
        self.assertIsNotNone(listening)
        self.assertIsNotNone(matching)
        self.assertEqual(listening.data['time_limit'], 30)
        self.assertTrue(listening.data['has_audio_support'])
        self.assertIn('hint', matching.data)


class AchievementObserverTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='secret')
        self.profile = self.user.profile
        AchievementDefinitionAdapter(LegacyExternalSystem()).sync()

    def test_observer_unlocks_achievement_via_adapter_synced_definitions(self):
        self.profile.total_xp = 15
        self.profile.save(update_fields=['total_xp'])

        subject = Subject()
        subject.attach(AchievementObserver(AchievementDefinitionAdapter(LegacyExternalSystem())))
        notifications = subject.notify(
            ProgressEvent(user=self.user, profile=self.profile, is_correct=True, lesson_id=1)
        )

        unlocked = [item for notification in notifications for item in notification.unlocked]
        self.assertTrue(unlocked)
        self.assertTrue(UserAchievement.objects.filter(user=self.user).exists())
        self.assertGreaterEqual(Achievement.objects.count(), 3)


class SubmitAnswerApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='student', password='password123')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        ru = Language.objects.create(name='Русский', code='ru')
        en = Language.objects.create(name='English', code='en')
        course = Course.objects.create(title='English', description='Desc', language=en, source_language=ru)
        lesson = course.lessons.create(title='Lesson 1', order=1)
        self.exercise = lesson.exercises.create(
            type=Exercise.TYPE_MATCHING_PAIRS,
            data={
                'question': 'Соедините пары',
                'pairs': [
                    {'left': 'Дом', 'right': 'House'},
                    {'left': 'Вода', 'right': 'Water'},
                ],
                'correct_answer': [
                    {'left': 'Дом', 'right': 'House'},
                    {'left': 'Вода', 'right': 'Water'},
                ],
            },
        )
        self.course = course

    def test_submit_matching_answer_returns_achievements_payload(self):
        response = self.client.post(
            f'/api/exercises/{self.exercise.id}/submit_answer/',
            {
                'answer': [
                    {'left': 'Дом', 'right': 'House'},
                    {'left': 'Вода', 'right': 'Water'},
                ]
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_correct'])
        self.assertIn('unlocked_achievements', response.data)
        self.assertGreaterEqual(response.data['xp'], 15)

    def test_enrollment_state_actions_change_status(self):
        enroll_response = self.client.post('/api/enrollments/enroll/', {'course_id': self.course.id}, format='json')
        self.assertEqual(enroll_response.status_code, 201)
        enrollment_id = enroll_response.data['id']
        self.assertEqual(enroll_response.data['status'], 'active')

        pause_response = self.client.post(f'/api/enrollments/{enrollment_id}/pause/')
        self.assertEqual(pause_response.status_code, 200)
        self.assertEqual(pause_response.data['status'], 'paused')

        resume_response = self.client.post(f'/api/enrollments/{enrollment_id}/resume/')
        self.assertEqual(resume_response.status_code, 200)
        self.assertEqual(resume_response.data['status'], 'active')

        complete_response = self.client.post(f'/api/enrollments/{enrollment_id}/complete/')
        self.assertEqual(complete_response.status_code, 200)
        self.assertEqual(complete_response.data['status'], 'completed')
        self.assertEqual(Enrollment.objects.get(pk=enrollment_id).status, 'completed')
