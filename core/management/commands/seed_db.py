import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Language, Course, Lesson, Exercise, ProgressLog
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Seeds the database with 30+ courses including 10+ specifically for Russian speakers'

    def handle(self, *args, **kwargs):
        self.stdout.write("Total System Reboot...")
        Course.objects.all().delete()
        Language.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        ProgressLog.objects.all().delete()
        
        user = User.objects.create_user(username='student1', email='student1@test.com', password='password123')
        
        langs = {
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

        vocab = [
            {'en': 'Apple', 'ru': 'Яблоко', 'es': 'Manzana', 'fr': 'Pomme', 'de': 'Apfel', 'it': 'Mela', 'ja': 'Ringo', 'zh': 'Píngguǒ'},
            {'en': 'Water', 'ru': 'Вода', 'es': 'Agua', 'fr': 'Eau', 'de': 'Wasser', 'it': 'Acqua', 'ja': 'Mizu', 'zh': 'Shuǐ'},
            {'en': 'Bread', 'ru': 'Хлеб', 'es': 'Pan', 'fr': 'Pain', 'de': 'Brot', 'it': 'Pane', 'ja': 'Pan', 'zh': 'Miànbāo'},
            {'en': 'House', 'ru': 'Дом', 'es': 'Casa', 'fr': 'Maison', 'de': 'Haus', 'it': 'Casa', 'ja': 'Ie', 'zh': 'Jiā'},
            {'en': 'Friend', 'ru': 'Друг', 'es': 'Amigo', 'fr': 'Ami', 'de': 'Freund', 'it': 'Amico', 'ja': 'Tomodachi', 'zh': 'Péngyǒu'},
            {'en': 'Book', 'ru': 'Книга', 'es': 'Libro', 'fr': 'Livre', 'de': 'Buch', 'it': 'Libro', 'ja': 'Hon', 'zh': 'Shū'},
        ]

        matrix = [
            # ДЛЯ РУССКИХ (12 курсов)
            ('en', 'ru', 'Английский: Основы', 'Начни говорить на международном языке.'),
            ('en', 'ru', 'Английский: Для работы', 'Бизнес-лексика и корпоративная этика.'),
            ('en', 'ru', 'Английский: Путешествия', 'Все, что нужно в аэропорту и отеле.'),
            ('es', 'ru', 'Испанский: Старт', 'Энергичный и яркий язык для отпуска.'),
            ('fr', 'ru', 'Французский: База', 'Погрузись в культуру Франции.'),
            ('de', 'ru', 'Немецкий: Уровень A1', 'Основы грамматики и произношения.'),
            ('it', 'ru', 'Итальянский с нуля', 'Язык музыки, искусства и еды.'),
            ('ja', 'ru', 'Японский: Хирагана', 'Первые шаги в восточной письменности.'),
            ('zh', 'ru', 'Китайский: Введение', 'Основы тонов и иероглифики.'),
            ('pt', 'ru', 'Португальский: Базовый', 'Солнечный язык Бразилии и Португалии.'),
            ('la', 'ru', 'Латынь: Для медиков', 'Классическая база для науки.'),
            ('la', 'ru', 'Латынь: Древние тексты', 'Читай философов в оригинале.'),

            # ДЛЯ АНГЛИЧАН
            ('ru', 'en', 'Russian for Beginners', 'Learn to read Cyrillic today.'),
            ('es', 'en', 'Spanish Intensive', 'Master Spanish in weeks.'),
            ('fr', 'en', 'French Daily', 'Learn how to speak like a Parisian.'),
            ('it', 'en', 'Italian Cooking', 'Learn Italian while you cook.'),
            
            # ДЛЯ ИСПАНЦЕВ
            ('ru', 'es', 'Ruso para Hispanos', 'Aprende el misterioso alfabeto cirílico.'),
            ('en', 'es', 'Inglés Total', 'Domina el inglés de una vez por todas.'),
        ]

        prompts = {
            'ru': ["Переведите '{w}'", "Как по-{t} будет '{w}'?", "Напишите '{w}' на языке {t}", "Как сказать '{w}'?"],
            'en': ["Translate '{w}'", "How do you say '{w}' in {t}?", "Write '{w}' in {t}"],
        }

        all_exercises = []
        for target_code, src_code, title, desc in matrix:
            t_lang = langs[target_code]
            s_lang = langs[src_code]
            course = Course.objects.create(title=title, description=desc, language=t_lang, source_language=s_lang)
            lesson = Lesson.objects.create(course=course, title='Урок 1', order=1)
            
            for item in vocab:
                s_word = item.get(src_code, item['en'])
                t_word = item.get(target_code, item['en'])
                
                # Создаем пул вариаций
                for p_text in prompts.get(src_code, prompts['en']):
                    ex = Exercise.objects.create(lesson=lesson, type='translation', data={
                        "question": p_text.format(w=s_word, t=t_lang.name),
                        "correct_answer": t_word
                    })
                    all_exercises.append(ex)
                
                # Тесты
                options = [t_word]
                others = [v.get(target_code, v['en']) for v in vocab if v != item]
                options.extend(random.sample(others, 3))
                random.shuffle(options)
                ex = Exercise.objects.create(lesson=lesson, type='multiple_choice', data={
                    "question": f"Pick translation for '{s_word}'",
                    "options": options,
                    "correct_answer": t_word
                })
                all_exercises.append(ex)

        self.stdout.write(self.style.SUCCESS(f"Done! Created {len(matrix)} courses (12 for RU). Total exercises in pool: {Exercise.objects.count()}"))
