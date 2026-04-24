# LingoLearn - Платформа для изучения языков

Современное SPA-приложение для изучения иностранных языков с использованием алгоритмов интервального повторения и геймификации.

## Технологический стек
- **Бэкенд:** Django 6.0 + Django REST Framework (Token Auth)
- **Фронтенд:** React + TypeScript + Vite
- **База данных:** SQLite3 (файл `db.sqlite3` - игнорируется гитом, создается при миграциях)

## Основные возможности
1. **Алгоритм SM-2:** Индивидуальный расчет интервалов повторения для каждого слова.
2. **Геймификация:** Система XP, ежедневные серии (Streaks), "сердечки" здоровья в уроках.
3. **Мультиязычность:** Поддержка 8 языков интерфейса и более 15 уникальных курсов.
4. **GitHub-style Graph:** Визуализация активности пользователя за последние 30 дней.
5. **Темы:** Полноценная темная и светлая темы.

## Архитектура (Паттерны)
В проекте реализовано более 10 паттернов проектирования:
- **Backend:** Strategy (валидация), State (статус обучения), Singleton (настройки), Abstract Factory (генерация заданий), Command, Observer.
- **Frontend:** Proxy (кеширование API), Iterator (перебор вопросов), Composite (структура курсов).

## Как запустить

### 1. Бэкенд
```bash
# Установка зависимостей
pip install -r requirements.txt

# Применение миграций и создание БД
python manage.py migrate

# Заполнение базы тестовыми данными (курсы, уроки, 500+ заданий)
python manage.py seed_db

# Запуск сервера
python manage.py runserver
```

### 2. Фронтенд
```bash
cd frontend
npm install
npm run dev
```
Откройте: `http://localhost:5173/`

### Данные для входа (после seed_db)
- **Админка:** `admin` / `admin` (на `http://127.0.0.1:8000/admin`)
- **Тестовый юзер с историей:** `student1` / `password123`

## Структура проекта
- `core/` - логика бэкенда, модели и паттерны.
- `core/utils/math_model.py` - реализация алгоритма SM-2.
- `frontend/src/App.tsx` - основная логика интерфейса и геймификации.
- `frontend/src/patterns/` - паттерны на стороне клиента.
- `docs/diagrams/` - (игнорируется гитом) исходники UML-схем в PlantUML.

## Этап 1
1. **Создание приложения:** Развернуты Django и Vite/React (`frontend/`, `core/`).
2. **Создание БД:** Настроена база данных SQLite3.
3. **Запуск базового приложения:** Django на 8000 порту и Vite на 5173. Настроены CORS в `config/settings.py`:
   - Добавлено `'corsheaders'` в `INSTALLED_APPS` (строка 46).
   - Добавлено `'corsheaders.middleware.CorsMiddleware'` в `MIDDLEWARE` (строка 51).
   - Установлено `CORS_ALLOW_ALL_ORIGINS = True` (строка 61) для связи фронтенда с бэкендом.
4. **Обновление схемы BPMN:** Бизнес-процессы отражены (изначально) в старой версии `GEMINI.md`. Схемы состояний и процессов перенесены в PlantUML (`docs/diagrams/`).
5. **Выделить сущности и атрибуты:** Созданы модели Course, Lesson, Exercise, Enrollment, ProgressLog, а также **SpacedRepetition**.
   - *Файл:* `core/models.py` (строки 7-60).
6. **Выделить/Придумать элемент с математической моделью:** Внедрен **Алгоритм интервального повторения SM-2** (Spaced Repetition System).
   - *Файл:* `core/utils/math_model.py` (функции `calculate_sm2` и `get_next_review_date`, строки 4, 33).
   - Логика использования в API: `core/views.py` (метод `submit_answer`, строка 47).
7. **Выделить стратегии поведения объектов, ключевой объект с состояниями и синглетные классы:**
   - **Стратегия (Strategy):** Валидация ответов — `core/strategies/exercise_validation.py` (классы `MultipleChoiceStrategy`, `TranslationStrategy`, строки 3-24).
   - **Состояния (State):** Жизненный цикл курса — `core/states.py` (классы `ActiveState`, `CompletedState`, `PausedState`, строки 3-34).
   - **Синглетный класс (Singleton):** Настройки приложения — `core/utils/singleton.py` (класс `AppSettings`, строки 1-9).

## Этап 2
1. **Обновление схемы ERD:** Создана PlantUML-схема БД.
   - *Файл:* `docs/diagrams/erd.puml`.
2. **Создать БД:** Миграции успешно применены.
   - *Файлы:* `core/migrations/`.
3. **Заполнить БД:** Написан скрипт сидирования, генерирующий более 70 записей.
   - *Файл:* `core/management/commands/seed_db.py` (класс `Command`, строка 8).
4. **Спроектировать шаблонный метод по BPMN:** Шаблонный метод для прохождения упражнений.
   - *Файл:* `core/patterns/template_method.py` (класс `WorkflowTemplate`, строки 3-50).
5. **Реализовать стратегии:** Интегрированы в ядро.
   - *Файлы:* `core/strategies/`.
6. **Реализовать математическую модель:** Алгоритм SM-2 подключен к базе данных и API.
   - *Файл:* `core/views.py` (обновление `SpacedRepetition` в `submit_answer`).
7. **Генерация объектов через Абстрактную Фабрику и Декоратор:**
   - **Абстрактная Фабрика (Abstract Factory):** Создание упражнений разных уровней — `core/patterns/abstract_factory.py` (строки 7-27).
   - **Декоратор (Decorator):** Добавление функционала (таймер, подсказки) — `core/patterns/abstract_factory.py` (строки 46-68).

## Этап 3
1. **Обновление диаграммы машины состояний:** Описаны переходы статусов Enrollment.
   - *Файл:* `docs/diagrams/state.puml`.
2. **Новый модуль через Адаптер (Adapter):** Конвертация данных из внешних систем.
   - *Файл:* `core/patterns/behavioral.py` (класс `ScoreAdapter`, строка 57).
3. **Наблюдатель (Observer):** Механизм оповещения о прогрессе.
   - *Файл:* `core/patterns/behavioral.py` (классы `Observer`, `Subject`, строки 4, 12).
4. **Интерфейс Команды (Command):** Изолированное выполнение задач.
   - *Файл:* `core/patterns/behavioral.py` (класс `SubmitAnswerCommand`, строка 28).
5. **Генерация элементов через Шаблонный метод:** Применение в `core/patterns/template_method.py`.

## Этап 4
1. **Финализация проекта:** Разработан интерфейс пользователя (React), получающий данные через API.
   - *Файл:* `frontend/src/App.tsx`.
2. **Заместитель (Proxy):** Кэширование запросов к API.
   - *Файл:* `frontend/src/patterns/patterns.ts` (класс `ApiProxy`, строка 59).
3. **Иерархия Компоновщика (Composite) и Итератор (Iterator):**
   - **Компоновщик (Composite):** Структура курсов и уроков — `frontend/src/patterns/patterns.ts` (класс `CourseComposite`, строка 34).
   - **Итератор (Iterator):** Перебор упражнений — `frontend/src/patterns/patterns.ts` (класс `ExerciseIterator`, строка 9).
4. **Обновление диаграммы классов:** Диаграмма включает все реализованные паттерны и математическую модель.
   - *Файл:* `docs/diagrams/classes.puml`.
