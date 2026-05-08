from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import Achievement, Course, Language, ProgressLog, UserAchievement
from core.patterns.behavioral import AchievementDefinitionAdapter, LegacyExternalSystem
from core.services.course_builder import CourseCreationModule, CourseSpec, ExerciseModifierSpec, LessonSpec


class Command(BaseCommand):
    help = 'Seeds the database with courses, lessons, multiple exercise types, and achievements.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Total System Reboot...')
        UserAchievement.objects.all().delete()
        Achievement.objects.all().delete()
        Course.objects.all().delete()
        Language.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        ProgressLog.objects.all().delete()

        User.objects.create_user(username='student1', email='student1@test.com', password='password123')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(username='admin', email='admin@test.com', password='admin12345')

        languages = {
            'ru': Language.objects.create(name='Русский', code='ru'),
            'en': Language.objects.create(name='English', code='en'),
            'es': Language.objects.create(name='Español', code='es'),
            'fr': Language.objects.create(name='Français', code='fr'),
            'de': Language.objects.create(name='Deutsch', code='de'),
            'it': Language.objects.create(name='Italiano', code='it'),
            'ja': Language.objects.create(name='日本語', code='ja'),
            'zh': Language.objects.create(name='中文 (Chinese)', code='zh'),
            'pt': Language.objects.create(name='Português', code='pt'),
            'la': Language.objects.create(name='Latina', code='la'),
        }

        AchievementDefinitionAdapter(LegacyExternalSystem()).sync()

        vocabulary_map = {
            'ru_to_en': [
                {'source': 'Яблоко', 'target': 'Apple'},
                {'source': 'Вода', 'target': 'Water'},
                {'source': 'Дом', 'target': 'House'},
                {'source': 'Друг', 'target': 'Friend'},
            ],
            'ru_to_es': [
                {'source': 'Яблоко', 'target': 'Manzana'},
                {'source': 'Вода', 'target': 'Agua'},
                {'source': 'Книга', 'target': 'Libro'},
                {'source': 'Дом', 'target': 'Casa'},
            ],
            'ru_to_fr': [
                {'source': 'Вода', 'target': 'Eau'},
                {'source': 'Хлеб', 'target': 'Pain'},
                {'source': 'Друг', 'target': 'Ami'},
                {'source': 'Книга', 'target': 'Livre'},
            ],
            'ru_to_de': [
                {'source': 'Дом', 'target': 'Haus'},
                {'source': 'Хлеб', 'target': 'Brot'},
                {'source': 'Книга', 'target': 'Buch'},
                {'source': 'Друг', 'target': 'Freund'},
            ],
            'ru_to_it': [
                {'source': 'Яблоко', 'target': 'Mela'},
                {'source': 'Вода', 'target': 'Acqua'},
                {'source': 'Дом', 'target': 'Casa'},
                {'source': 'Друг', 'target': 'Amico'},
            ],
            'ru_to_ja': [
                {'source': 'Яблоко', 'target': 'Ringo'},
                {'source': 'Вода', 'target': 'Mizu'},
                {'source': 'Дом', 'target': 'Ie'},
                {'source': 'Друг', 'target': 'Tomodachi'},
            ],
            'ru_to_zh': [
                {'source': 'Яблоко', 'target': 'Píngguǒ'},
                {'source': 'Вода', 'target': 'Shuǐ'},
                {'source': 'Дом', 'target': 'Jiā'},
                {'source': 'Друг', 'target': 'Péngyǒu'},
            ],
            'ru_to_pt': [
                {'source': 'Яблоко', 'target': 'Maçã'},
                {'source': 'Вода', 'target': 'Água'},
                {'source': 'Дом', 'target': 'Casa'},
                {'source': 'Друг', 'target': 'Amigo'},
            ],
            'ru_to_la': [
                {'source': 'Вода', 'target': 'Aqua'},
                {'source': 'Дом', 'target': 'Domus'},
                {'source': 'Друг', 'target': 'Amicus'},
                {'source': 'Книга', 'target': 'Liber'},
            ],
            'en_to_ru': [
                {'source': 'Apple', 'target': 'Яблоко'},
                {'source': 'Water', 'target': 'Вода'},
                {'source': 'Friend', 'target': 'Друг'},
                {'source': 'Book', 'target': 'Книга'},
            ],
            'en_to_es': [
                {'source': 'Apple', 'target': 'Manzana'},
                {'source': 'Water', 'target': 'Agua'},
                {'source': 'House', 'target': 'Casa'},
                {'source': 'Book', 'target': 'Libro'},
            ],
        }

        course_specs = [
            CourseSpec(
                title='Английский: Основы',
                description='Начни говорить на международном языке.',
                target_language_code='en',
                source_language_code='ru',
                lessons=[
                    LessonSpec(
                        title='Урок 1: Базовые слова',
                        vocabulary=vocabulary_map['ru_to_en'],
                        modifiers=ExerciseModifierSpec(
                            timed_seconds=45,
                            hint_text='Подумайте о базовой лексике.',
                            shuffle_options=True,
                            add_audio_support=True,
                            voice_locale='en-US',
                        ),
                    )
                ],
            ),
            CourseSpec(
                title='Испанский: Старт',
                description='Энергичный и яркий язык для отпуска.',
                target_language_code='es',
                source_language_code='ru',
                lessons=[
                    LessonSpec(
                        title='Урок 1: В путешествии',
                        vocabulary=vocabulary_map['ru_to_es'],
                        modifiers=ExerciseModifierSpec(hint_text='Вспомните слова из поездки.', shuffle_options=True),
                    )
                ],
            ),
            CourseSpec(
                title='Французский: База',
                description='Погрузись в культуру Франции.',
                target_language_code='fr',
                source_language_code='ru',
                lessons=[LessonSpec(title='Урок 1: Everyday French', vocabulary=vocabulary_map['ru_to_fr'])],
            ),
            CourseSpec(
                title='Немецкий: Уровень A1',
                description='Основы грамматики и произношения.',
                target_language_code='de',
                source_language_code='ru',
                lessons=[LessonSpec(title='Урок 1: Erste Worte', vocabulary=vocabulary_map['ru_to_de'])],
            ),
            CourseSpec(
                title='Итальянский с нуля',
                description='Язык музыки, искусства и еды.',
                target_language_code='it',
                source_language_code='ru',
                lessons=[LessonSpec(title='Урок 1: Parole semplici', vocabulary=vocabulary_map['ru_to_it'])],
            ),
            CourseSpec(
                title='Японский: Хирагана',
                description='Первые шаги в восточной письменности.',
                target_language_code='ja',
                source_language_code='ru',
                lessons=[LessonSpec(title='Урок 1: First words', vocabulary=vocabulary_map['ru_to_ja'])],
            ),
            CourseSpec(
                title='Китайский: Введение',
                description='Основы тонов и иероглифики.',
                target_language_code='zh',
                source_language_code='ru',
                lessons=[LessonSpec(title='Урок 1: Basic tones', vocabulary=vocabulary_map['ru_to_zh'])],
            ),
            CourseSpec(
                title='Португальский: Базовый',
                description='Солнечный язык Бразилии и Португалии.',
                target_language_code='pt',
                source_language_code='ru',
                lessons=[LessonSpec(title='Урок 1: Primeiras palavras', vocabulary=vocabulary_map['ru_to_pt'])],
            ),
            CourseSpec(
                title='Латынь: Для медиков',
                description='Классическая база для науки.',
                target_language_code='la',
                source_language_code='ru',
                lessons=[LessonSpec(title='Урок 1: Terminus basicus', vocabulary=vocabulary_map['ru_to_la'])],
            ),
            CourseSpec(
                title='Russian for Beginners',
                description='Learn to read Cyrillic today.',
                target_language_code='ru',
                source_language_code='en',
                lessons=[
                    LessonSpec(
                        title='Lesson 1: Core vocabulary',
                        vocabulary=vocabulary_map['en_to_ru'],
                        modifiers=ExerciseModifierSpec(timed_seconds=30, add_audio_support=True, voice_locale='ru-RU'),
                    )
                ],
            ),
            CourseSpec(
                title='Spanish Intensive',
                description='Master Spanish in weeks.',
                target_language_code='es',
                source_language_code='en',
                lessons=[LessonSpec(title='Lesson 1: Fast start', vocabulary=vocabulary_map['en_to_es'])],
            ),
        ]

        creator = CourseCreationModule()
        for spec in course_specs:
            creator.create_course(spec)

        self.stdout.write(
            self.style.SUCCESS(
                (
                    f"Done! Created {Course.objects.count()} courses with {languages.__len__()} languages "
                    f"and {Achievement.objects.count()} achievements. "
                    "Admin login: admin / admin12345"
                )
            )
        )
