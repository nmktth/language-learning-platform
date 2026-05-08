import React, { useEffect, useMemo, useState } from 'react';
import './App.css';
import { ApiProxy, CourseComposite, ExerciseIterator, LessonElement, RealApiService } from './patterns/patterns';

type ExerciseType = 'multiple_choice' | 'translation' | 'matching_pairs' | 'listening';
type AppView = 'auth' | 'dashboard' | 'courses' | 'learning' | 'game_over' | 'victory' | 'admin_dashboard' | 'admin_courses' | 'admin_lessons' | 'admin_exercises';
type AuthMode = 'login' | 'register';
type AdminSection = 'admin_dashboard' | 'admin_courses' | 'admin_lessons' | 'admin_exercises';

type MatchingPair = { left: string; right: string };
type UserSession = { id: number; username: string; is_staff: boolean; is_superuser: boolean; role: 'admin' | 'student' };
type Language = { id: number; name: string; code: string };
type Enrollment = { id: number; course: number; course_title: string; status: string; started_at: string };

type Exercise = {
  id: number;
  lesson: number;
  type: ExerciseType;
  data: {
    question: string;
    correct_answer: string | MatchingPair[];
    options?: string[];
    pairs?: MatchingPair[];
    hint?: string;
    time_limit?: number;
    audio_text?: string;
    transcript?: string;
    has_audio_support?: boolean;
    voice_locale?: string;
  };
};

type Lesson = { id: number; course: number; title: string; order: number; exercises: Exercise[] };
type Course = {
  id: number;
  title: string;
  description: string;
  language: number;
  source_language: number;
  source_language_code: string;
  target_language_code: string;
  lessons: Lesson[];
};

type Achievement = {
  id: number;
  awarded_at: string;
  progress_snapshot: Record<string, unknown>;
  achievement: {
    code: string;
    title: string;
    description: string;
    icon: string;
    medal_tier: 'bronze' | 'silver' | 'gold' | string;
    threshold: number;
    condition_type: string;
    xp_reward: number;
  };
};

type Stats = {
  streak: number;
  xp: number;
  activity_graph: Record<string, number>;
  achievements: Achievement[];
  enrollments: Enrollment[];
  user?: UserSession;
};

type CourseDraft = {
  title: string;
  description: string;
  language: string;
  source_language: string;
};

type LessonDraft = {
  course: string;
  title: string;
  order: string;
};

type ExerciseDraft = {
  lesson: string;
  type: ExerciseType;
  question: string;
  correctAnswer: string;
  options: string;
  pairs: string;
  hint: string;
  timeLimit: string;
  audioText: string;
  voiceLocale: string;
};

const translations: Record<string, Record<string, string>> = {
  en: {
    appName: 'Lingo',
    login: 'Log In',
    register: 'Create Account',
    username: 'Username',
    password: 'Password',
    confirm_password: 'Confirm password',
    choose: 'Choose course',
    dashboard: 'Dashboard',
    courses: 'Courses',
    admin_panel: 'Admin Panel',
    admin_dashboard: 'Admin overview',
    admin_courses: 'Manage courses',
    admin_lessons: 'Manage lessons',
    admin_exercises: 'Manage exercises',
    studentspace: 'Student space',
    adminspace: 'Administrator space',
    streak: 'Streak',
    xp: 'XP',
    activity: 'Activity (30d)',
    achievements: 'Achievements',
    no_achievements: 'Complete exercises to unlock medals.',
    start: 'Start',
    back: 'Back',
    logout: 'Logout',
    lesson_progress: 'Progress',
    timer: 'Timer',
    check: 'Check',
    continue: 'Continue',
    excellent: 'Excellent!',
    correct: 'Correct answer',
    time_up: 'Time is up',
    out_of_hearts: 'Out of hearts',
    victory: 'Lesson complete',
    translate: 'Translate',
    select: 'Choose correct answer',
    matching: 'Match the pairs',
    listening: 'Listening',
    play_audio: 'Play audio',
    answer_field: 'Type your answer',
    select_right: 'Choose translation',
    hint: 'Hint',
    module: 'Course module',
    task_types: 'Task types',
    lesson_plan: 'Exercises',
    timed: 'Timed',
    no_timed: 'Free pace',
    translation_short: 'Translate',
    choice_short: 'Choice',
    matching_short: 'Pairs',
    listening_short: 'Audio',
    unlocked: 'Unlocked',
    welcome: 'Welcome back',
    register_title: 'Create a proper account',
    login_title: 'Log in to continue',
    auth_subtitle: 'Learn languages, manage courses, and show every pattern clearly.',
    nav_learning: 'Learning',
    nav_admin: 'Admin',
    enrolled: 'Enrolled',
    active: 'Active',
    paused: 'Paused',
    completed: 'Completed',
    no_courses: 'No courses yet.',
    no_lessons: 'No lessons yet.',
    no_exercises: 'No exercises yet.',
    create_course: 'Create course',
    create_lesson: 'Create lesson',
    create_exercise: 'Create exercise',
    delete: 'Delete',
    title: 'Title',
    description: 'Description',
    target_language: 'Target language',
    source_language: 'Source language',
    lesson: 'Lesson',
    order: 'Order',
    question: 'Question',
    exercise_type: 'Exercise type',
    correct_answer: 'Correct answer',
    options: 'Options separated by comma',
    pairs: 'Pairs left:right, one per line',
    time_limit: 'Time limit in seconds',
    audio_text: 'Audio text',
    voice_locale: 'Voice locale',
    create: 'Create',
    admin_help: 'Admins can add, edit through admin, and delete content directly in the app.',
    registration_success: 'Account created. You are logged in.',
    form_error_prefix: 'Please fix:',
    total_courses: 'Courses',
    total_lessons: 'Lessons',
    total_exercises: 'Exercises',
    total_achievements: 'Achievements',
    course_structure: 'Structure',
    manage_content: 'Content management',
    username_placeholder: 'For example: student1',
    password_placeholder: 'At least 8 characters',
    confirm_password_placeholder: 'Repeat password',
    login_hint: 'Enter your username and password to continue learning.',
    register_hint: 'Username must be 3+ characters, password 8+ characters, and confirmation must match.',
    login_failed: 'Login failed.',
    registration_failed: 'Registration failed.',
    username_too_short: 'Username must be at least 3 characters long.',
    password_too_short: 'Password must be at least 8 characters long.',
    passwords_do_not_match: 'Passwords do not match.',
    course_created: 'Course created.',
    lesson_created: 'Lesson created.',
    exercise_created: 'Exercise created.',
    delete_done: 'Deletion completed.',
    type_translation: 'Translation',
    type_multiple_choice: 'Multiple choice',
    type_matching_pairs: 'Matching pairs',
    type_listening: 'Listening',
    pattern_observer: 'Observer',
    pattern_adapter: 'Adapter',
    pattern_factory: 'Factory',
    pattern_decorator: 'Decorator',
    flag: '🇺🇸',
  },
  ru: {
    appName: 'Lingo',
    login: 'Войти',
    register: 'Создать аккаунт',
    username: 'Логин',
    password: 'Пароль',
    confirm_password: 'Повторите пароль',
    choose: 'Выбрать курс',
    dashboard: 'Личный кабинет',
    courses: 'Курсы',
    admin_panel: 'Панель администратора',
    admin_dashboard: 'Обзор админа',
    admin_courses: 'Управление курсами',
    admin_lessons: 'Управление уроками',
    admin_exercises: 'Управление заданиями',
    studentspace: 'Пространство ученика',
    adminspace: 'Пространство администратора',
    streak: 'Серия',
    xp: 'Опыт',
    activity: 'Активность (30д)',
    achievements: 'Ачивки',
    no_achievements: 'Решайте задания, чтобы открыть медали.',
    start: 'Начать',
    back: 'Назад',
    logout: 'Выйти',
    lesson_progress: 'Прогресс',
    timer: 'Таймер',
    check: 'Проверить',
    continue: 'Дальше',
    excellent: 'Отлично!',
    correct: 'Правильный ответ',
    time_up: 'Время вышло',
    out_of_hearts: 'Нет жизней',
    victory: 'Урок пройден',
    translate: 'Переведи',
    select: 'Выбери правильный ответ',
    matching: 'Соедини пары',
    listening: 'Аудирование',
    play_audio: 'Проиграть аудио',
    answer_field: 'Введите ответ',
    select_right: 'Выберите перевод',
    hint: 'Подсказка',
    module: 'Модуль курса',
    task_types: 'Типы заданий',
    lesson_plan: 'Задания',
    timed: 'На время',
    no_timed: 'Без таймера',
    translation_short: 'Перевод',
    choice_short: 'Выбор',
    matching_short: 'Пары',
    listening_short: 'Аудио',
    unlocked: 'Открыто',
    welcome: 'С возвращением',
    register_title: 'Нормальная регистрация',
    login_title: 'Войдите, чтобы продолжить',
    auth_subtitle: 'Учитесь, управляйте курсами и показывайте паттерны наглядно.',
    nav_learning: 'Обучение',
    nav_admin: 'Админ',
    enrolled: 'Записан',
    active: 'Активный',
    paused: 'На паузе',
    completed: 'Завершен',
    no_courses: 'Курсов пока нет.',
    no_lessons: 'Уроков пока нет.',
    no_exercises: 'Заданий пока нет.',
    create_course: 'Создать курс',
    create_lesson: 'Создать урок',
    create_exercise: 'Создать задание',
    delete: 'Удалить',
    title: 'Название',
    description: 'Описание',
    target_language: 'Целевой язык',
    source_language: 'Исходный язык',
    lesson: 'Урок',
    order: 'Порядок',
    question: 'Вопрос',
    exercise_type: 'Тип задания',
    correct_answer: 'Правильный ответ',
    options: 'Варианты через запятую',
    pairs: 'Пары left:right, по одной на строку',
    time_limit: 'Лимит времени в секундах',
    audio_text: 'Текст для аудио',
    voice_locale: 'Локаль голоса',
    create: 'Создать',
    admin_help: 'Админ может добавлять, удалять и в целом управлять контентом прямо из приложения.',
    registration_success: 'Аккаунт создан, вход выполнен.',
    form_error_prefix: 'Нужно исправить:',
    total_courses: 'Курсы',
    total_lessons: 'Уроки',
    total_exercises: 'Задания',
    total_achievements: 'Ачивки',
    course_structure: 'Структура',
    manage_content: 'Управление контентом',
    username_placeholder: 'Например: student1',
    password_placeholder: 'Минимум 8 символов',
    confirm_password_placeholder: 'Повторите пароль',
    login_hint: 'Введите логин и пароль, чтобы продолжить обучение.',
    register_hint: 'Логин от 3 символов, пароль от 8 символов и одинаковое подтверждение.',
    login_failed: 'Не удалось войти.',
    registration_failed: 'Не удалось зарегистрироваться.',
    username_too_short: 'Логин должен быть не короче 3 символов.',
    password_too_short: 'Пароль должен быть не короче 8 символов.',
    passwords_do_not_match: 'Пароли не совпадают.',
    course_created: 'Курс создан.',
    lesson_created: 'Урок создан.',
    exercise_created: 'Задание создано.',
    delete_done: 'Удаление выполнено.',
    type_translation: 'Перевод',
    type_multiple_choice: 'Выбор ответа',
    type_matching_pairs: 'Соединение пар',
    type_listening: 'Аудирование',
    pattern_observer: 'Наблюдатель',
    pattern_adapter: 'Адаптер',
    pattern_factory: 'Фабрика',
    pattern_decorator: 'Декоратор',
    flag: '🇷🇺',
  },
  es: { login: 'Entrar', register: 'Registro', username: 'Usuario', password: 'Clave', confirm_password: 'Confirmar clave', dashboard: 'Perfil', courses: 'Cursos', choose: 'Elegir curso', logout: 'Salir', streak: 'Racha', xp: 'XP', achievements: 'Logros', no_achievements: 'Completa ejercicios para desbloquear medallas.', start: 'Empezar', back: 'Volver', timer: 'Tiempo', check: 'Comprobar', continue: 'Siguiente', excellent: 'Excelente', correct: 'Respuesta', time_up: 'Se acabó el tiempo', out_of_hearts: 'Sin vidas', victory: 'Lección completada', translate: 'Traduce', select: 'Selecciona', matching: 'Une pares', listening: 'Escucha', play_audio: 'Audio', answer_field: 'Escribe la respuesta', select_right: 'Elige traducción', hint: 'Pista', translation_short: 'Traducción', choice_short: 'Opciones', matching_short: 'Pares', listening_short: 'Audio', unlocked: 'Desbloqueado', no_courses: 'No hay cursos.', flag: '🇪🇸' },
  fr: { login: 'Connexion', register: 'Inscription', username: 'Pseudo', password: 'Mot de passe', confirm_password: 'Confirmez le mot de passe', dashboard: 'Profil', courses: 'Cours', choose: 'Choisir un cours', logout: 'Sortir', streak: 'Série', xp: 'XP', achievements: 'Succès', no_achievements: 'Terminez des exercices pour débloquer des médailles.', start: 'Démarrer', back: 'Retour', timer: 'Minuteur', check: 'Vérifier', continue: 'Continuer', excellent: 'Excellent', correct: 'Réponse', time_up: 'Temps écoulé', out_of_hearts: 'Plus de vies', victory: 'Leçon terminée', translate: 'Traduire', select: 'Choisir', matching: 'Associez', listening: 'Écoute', play_audio: 'Audio', answer_field: 'Entrez la réponse', select_right: 'Choisissez', hint: 'Indice', translation_short: 'Traduction', choice_short: 'Choix', matching_short: 'Paires', listening_short: 'Audio', unlocked: 'Débloqué', no_courses: 'Aucun cours.', flag: '🇫🇷' },
  de: { login: 'Login', register: 'Registrieren', username: 'Benutzer', password: 'Passwort', confirm_password: 'Passwort bestätigen', dashboard: 'Profil', courses: 'Kurse', choose: 'Kurs wählen', logout: 'Logout', streak: 'Serie', xp: 'XP', achievements: 'Erfolge', no_achievements: 'Löse Übungen, um Medaillen freizuschalten.', start: 'Start', back: 'Zurück', timer: 'Timer', check: 'Prüfen', continue: 'Weiter', excellent: 'Super', correct: 'Antwort', time_up: 'Zeit ist um', out_of_hearts: 'Keine Herzen', victory: 'Lektion fertig', translate: 'Übersetze', select: 'Wähle', matching: 'Paare', listening: 'Hören', play_audio: 'Audio', answer_field: 'Antwort eingeben', select_right: 'Übersetzung wählen', hint: 'Hinweis', translation_short: 'Übersetzen', choice_short: 'Auswahl', matching_short: 'Paare', listening_short: 'Audio', unlocked: 'Freigeschaltet', no_courses: 'Keine Kurse.', flag: '🇩🇪' },
};

const medalPalette: Record<string, { primary: string; accent: string; ribbon: string }> = {
  bronze: { primary: '#b66a35', accent: '#f6c49d', ribbon: '#2f5a8f' },
  silver: { primary: '#9ba7b8', accent: '#eef3f8', ribbon: '#3c7ddd' },
  gold: { primary: '#d8a314', accent: '#ffe89a', ribbon: '#1f8a5b' },
};

const initialCourseDraft: CourseDraft = { title: '', description: '', language: '', source_language: '' };
const initialLessonDraft: LessonDraft = { course: '', title: '', order: '1' };
const initialExerciseDraft: ExerciseDraft = {
  lesson: '', type: 'translation', question: '', correctAnswer: '', options: '', pairs: '', hint: '', timeLimit: '', audioText: '', voiceLocale: 'en-US',
};

function MedalIcon({ tier }: { tier: string }) {
  const palette = medalPalette[tier] ?? medalPalette.bronze;
  return (
    <svg viewBox="0 0 80 80" className="medal-svg" aria-hidden="true">
      <path d="M24 6h12l6 20-10 8L24 6Z" fill={palette.ribbon} />
      <path d="M44 6h12L48 34l-10-8L44 6Z" fill={palette.ribbon} opacity="0.9" />
      <circle cx="40" cy="48" r="22" fill={palette.primary} />
      <circle cx="40" cy="48" r="15" fill={palette.accent} opacity="0.9" />
      <path d="M40 35l3.6 7.5 8.2 1.2-5.9 5.8 1.4 8.1-7.3-3.8-7.3 3.8 1.4-8.1-5.9-5.8 8.2-1.2L40 35Z" fill={palette.primary} />
    </svg>
  );
}

function AchievementCard({ item, label }: { item: Achievement; label: string }) {
  return (
    <div className="achievement-card">
      <div className="achievement-medal"><MedalIcon tier={item.achievement.medal_tier} /></div>
      <div>
        <div className="achievement-tier">{label}</div>
        <h3>{item.achievement.title}</h3>
        <p>{item.achievement.description}</p>
      </div>
    </div>
  );
}

const getExerciseBadge = (type: ExerciseType, t: (key: string) => string) => {
  if (type === 'translation') return t('translation_short');
  if (type === 'multiple_choice') return t('choice_short');
  if (type === 'matching_pairs') return t('matching_short');
  return t('listening_short');
};

const getExerciseTypeLabel = (type: ExerciseType, t: (key: string) => string) => {
  if (type === 'translation') return t('type_translation');
  if (type === 'multiple_choice') return t('type_multiple_choice');
  if (type === 'matching_pairs') return t('type_matching_pairs');
  return t('type_listening');
};

const App: React.FC = () => {
  const [view, setView] = useState<AppView>('auth');
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [theme, setTheme] = useState<'light' | 'dark'>((localStorage.getItem('theme') as 'light' | 'dark') || 'light');
  const [uiLang, setUiLang] = useState<string>(localStorage.getItem('uiLang') || 'ru');
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [currentUser, setCurrentUser] = useState<UserSession | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [authError, setAuthError] = useState('');
  const [authMessage, setAuthMessage] = useState('');
  const [userStats, setUserStats] = useState<Stats>({ streak: 0, xp: 0, activity_graph: {}, achievements: [], enrollments: [] });
  const [recentUnlocks, setRecentUnlocks] = useState<Achievement[]>([]);
  const [hearts, setHearts] = useState(5);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [textAnswer, setTextAnswer] = useState('');
  const [selectedOption, setSelectedOption] = useState('');
  const [matchingAnswers, setMatchingAnswers] = useState<Record<string, string>>({});
  const [checkState, setCheckState] = useState<'idle' | 'correct' | 'incorrect'>('idle');
  const [timeLeft, setTimeLeft] = useState<number | null>(null);
  const [timedOut, setTimedOut] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [courseDraft, setCourseDraft] = useState<CourseDraft>(initialCourseDraft);
  const [lessonDraft, setLessonDraft] = useState<LessonDraft>(initialLessonDraft);
  const [exerciseDraft, setExerciseDraft] = useState<ExerciseDraft>(initialExerciseDraft);
  const [adminMessage, setAdminMessage] = useState('');
  const apiProxy = useMemo(() => new ApiProxy(new RealApiService()), []);
  const t = (key: string) => translations[uiLang]?.[key] || translations.en[key] || key;

  const currentExercise = exercises[currentIndex];
  const filteredCourses = courses.filter((course) => course.source_language_code === uiLang);
  const flatLessons = useMemo(() => courses.flatMap((course) => course.lessons), [courses]);
  const flatExercises = useMemo(() => flatLessons.flatMap((lesson) => lesson.exercises), [flatLessons]);
  const taskTypes = currentExercise ? [...new Set(exercises.map((exercise) => exercise.type))] : [];

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    localStorage.setItem('uiLang', uiLang);
  }, [uiLang]);

  useEffect(() => {
    if (!token) {
      setView('auth');
      setCurrentUser(null);
      return;
    }
    void bootstrap();
  }, [token, uiLang]);

  useEffect(() => {
    if (!currentExercise?.data.time_limit || checkState !== 'idle') {
      setTimeLeft(currentExercise?.data.time_limit ?? null);
      return;
    }

    setTimeLeft(currentExercise.data.time_limit);
    const interval = window.setInterval(() => {
      setTimeLeft((previous) => {
        if (previous === null) return null;
        if (previous <= 1) {
          window.clearInterval(interval);
          return 0;
        }
        return previous - 1;
      });
    }, 1000);

    return () => window.clearInterval(interval);
  }, [currentExercise?.id, currentExercise?.data.time_limit, checkState]);

  useEffect(() => {
    if (timeLeft === 0 && checkState === 'idle' && !submitting) {
      setTimedOut(true);
      void handleCheck('');
    }
  }, [timeLeft, checkState, submitting]);

  const authHeaders = () => ({
    'Content-Type': 'application/json',
    Authorization: `Token ${token}`,
  });

  const bootstrap = async () => {
    try {
      const [coursesData, languagesData, meResponse, progressResponse] = await Promise.all([
        apiProxy.fetchData('http://127.0.0.1:8000/api/courses/'),
        apiProxy.fetchData('http://127.0.0.1:8000/api/languages/'),
        fetch('http://127.0.0.1:8000/api/auth/me/', { headers: { Authorization: `Token ${token}` } }),
        fetch('http://127.0.0.1:8000/api/progress/', { headers: { Authorization: `Token ${token}` } }),
      ]);

      const meData = await meResponse.json();
      const progressData = await progressResponse.json();
      const user = meData.user as UserSession;

      setCurrentUser(user);
      setCourses(Array.isArray(coursesData) ? coursesData : []);
      setLanguages(Array.isArray(languagesData) ? languagesData : []);
      if (progressData.status === 'ok') {
        setUserStats({
          streak: progressData.streak,
          xp: progressData.xp,
          activity_graph: progressData.activity_graph || {},
          achievements: progressData.achievements || [],
          enrollments: progressData.enrollments || [],
          user: progressData.user,
        });
      }

      if (user.is_staff) {
        setView((previous) => (previous === 'learning' ? previous : 'admin_dashboard'));
      } else if (view === 'auth') {
        setView('dashboard');
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleLogin = async () => {
    setAuthError('');
    setAuthMessage('');
    const response = await fetch('http://127.0.0.1:8000/api/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await response.json();
    if (data.token) {
      localStorage.setItem('token', data.token);
      setToken(data.token);
      setCurrentUser(data.user);
      setView(data.user?.is_staff ? 'admin_dashboard' : 'dashboard');
    } else {
      setAuthError(data.error || t('login_failed'));
    }
  };

  const handleRegister = async () => {
    setAuthError('');
    setAuthMessage('');

    if (username.trim().length < 3) {
      setAuthError(t('username_too_short'));
      return;
    }
    if (password.length < 8) {
      setAuthError(t('password_too_short'));
      return;
    }
    if (password !== passwordConfirm) {
      setAuthError(t('passwords_do_not_match'));
      return;
    }

    const response = await fetch('http://127.0.0.1:8000/api/auth/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, password_confirm: passwordConfirm }),
    });
    const data = await response.json();
    if (data.token) {
      localStorage.setItem('token', data.token);
      setToken(data.token);
      setCurrentUser(data.user);
      setAuthMessage(t('registration_success'));
      setView('dashboard');
    } else {
      setAuthError(data.error || t('registration_failed'));
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setCurrentUser(null);
    setView('auth');
    setUserStats({ streak: 0, xp: 0, activity_graph: {}, achievements: [], enrollments: [] });
    setRecentUnlocks([]);
    setUsername('');
    setPassword('');
    setPasswordConfirm('');
    setAuthError('');
    setAuthMessage('');
  };

  const start = async (course: Course) => {
    const existingEnrollment = userStats.enrollments.find((item) => item.course === course.id);
    if (!existingEnrollment && token) {
      await fetch('http://127.0.0.1:8000/api/enrollments/enroll/', {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ course_id: course.id }),
      });
      await bootstrap();
    }

    const lesson = course.lessons[0];
    if (lesson?.exercises.length) {
      const iterator = new ExerciseIterator([...lesson.exercises].sort(() => Math.random() - 0.5));
      const preparedExercises: Exercise[] = [];
      while (iterator.hasNext() && preparedExercises.length < 7) {
        const nextExercise = iterator.next();
        if (nextExercise) preparedExercises.push(nextExercise as Exercise);
      }
      setExercises(preparedExercises);
      setCurrentIndex(0);
      setHearts(5);
      setTextAnswer('');
      setSelectedOption('');
      setMatchingAnswers({});
      setTimedOut(false);
      setSubmitting(false);
      setCheckState('idle');
      setView('learning');
    }
  };

  const matchingOptions = useMemo(() => {
    if (!currentExercise?.data.pairs) return [];
    return [...currentExercise.data.pairs.map((pair) => pair.right)].sort(() => Math.random() - 0.5);
  }, [currentExercise?.id]);

  const getAnswerPayload = (): string | MatchingPair[] => {
    if (!currentExercise) return '';
    if (currentExercise.type === 'multiple_choice') return selectedOption;
    if (currentExercise.type === 'matching_pairs') return Object.entries(matchingAnswers).map(([left, right]) => ({ left, right }));
    return textAnswer;
  };

  const canSubmit = () => {
    if (!currentExercise || submitting || timedOut) return false;
    if (currentExercise.type === 'multiple_choice') return Boolean(selectedOption);
    if (currentExercise.type === 'matching_pairs') return (currentExercise.data.pairs || []).every((pair) => matchingAnswers[pair.left]);
    return Boolean(textAnswer.trim());
  };

  const playAudio = () => {
    if (!currentExercise?.data.audio_text || !('speechSynthesis' in window)) return;
    const utterance = new SpeechSynthesisUtterance(currentExercise.data.audio_text);
    utterance.lang = currentExercise.data.voice_locale || 'en-US';
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  };

  const handleCheck = async (overrideAnswer?: string | MatchingPair[]) => {
    if (!currentExercise || submitting || !token) return;
    setSubmitting(true);
    const response = await fetch(`http://127.0.0.1:8000/api/exercises/${currentExercise.id}/submit_answer/`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ answer: overrideAnswer ?? getAnswerPayload() }),
    });
    const data = await response.json();
    if (data.is_correct) {
      setCheckState('correct');
      setUserStats((prev) => ({ ...prev, xp: data.xp, streak: data.streak }));
    } else {
      setCheckState('incorrect');
      setHearts((prev) => prev - 1);
    }
    if (Array.isArray(data.unlocked_achievements) && data.unlocked_achievements.length) {
      setRecentUnlocks(data.unlocked_achievements);
      setUserStats((prev) => ({ ...prev, achievements: [...data.unlocked_achievements, ...prev.achievements], xp: data.xp, streak: data.streak }));
    }
    setSubmitting(false);
  };

  const resetAnswerState = () => {
    setTextAnswer('');
    setSelectedOption('');
    setMatchingAnswers({});
    setCheckState('idle');
    setTimedOut(false);
    setSubmitting(false);
  };

  const submitCourse = async () => {
    if (!token) return;
    const response = await fetch('http://127.0.0.1:8000/api/courses/', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({
        title: courseDraft.title,
        description: courseDraft.description,
        language: Number(courseDraft.language),
        source_language: Number(courseDraft.source_language),
      }),
    });
    if (response.ok) {
      setCourseDraft(initialCourseDraft);
      setAdminMessage(t('course_created'));
      await bootstrap();
    }
  };

  const submitLesson = async () => {
    if (!token) return;
    const response = await fetch('http://127.0.0.1:8000/api/lessons/', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ course: Number(lessonDraft.course), title: lessonDraft.title, order: Number(lessonDraft.order) }),
    });
    if (response.ok) {
      setLessonDraft(initialLessonDraft);
      setAdminMessage(t('lesson_created'));
      await bootstrap();
    }
  };

  const buildExercisePayload = () => {
    const baseData: Record<string, unknown> = {
      question: exerciseDraft.question,
      correct_answer: exerciseDraft.type === 'matching_pairs'
        ? exerciseDraft.pairs.split('\n').filter(Boolean).map((line) => {
            const [left, right] = line.split(':');
            return { left: (left || '').trim(), right: (right || '').trim() };
          })
        : exerciseDraft.correctAnswer,
    };

    if (exerciseDraft.hint.trim()) baseData.hint = exerciseDraft.hint.trim();
    if (exerciseDraft.timeLimit.trim()) baseData.time_limit = Number(exerciseDraft.timeLimit);

    if (exerciseDraft.type === 'multiple_choice') {
      baseData.options = exerciseDraft.options.split(',').map((item) => item.trim()).filter(Boolean);
    }
    if (exerciseDraft.type === 'matching_pairs') {
      baseData.pairs = exerciseDraft.pairs.split('\n').filter(Boolean).map((line) => {
        const [left, right] = line.split(':');
        return { left: (left || '').trim(), right: (right || '').trim() };
      });
    }
    if (exerciseDraft.type === 'listening') {
      baseData.audio_text = exerciseDraft.audioText || exerciseDraft.correctAnswer;
      baseData.voice_locale = exerciseDraft.voiceLocale || 'en-US';
      baseData.has_audio_support = true;
    }

    return { lesson: Number(exerciseDraft.lesson), type: exerciseDraft.type, data: baseData };
  };

  const submitExercise = async () => {
    if (!token) return;
    const response = await fetch('http://127.0.0.1:8000/api/exercises/', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(buildExercisePayload()),
    });
    if (response.ok) {
      setExerciseDraft(initialExerciseDraft);
      setAdminMessage(t('exercise_created'));
      await bootstrap();
    }
  };

  const deleteEntity = async (kind: 'courses' | 'lessons' | 'exercises', id: number) => {
    if (!token) return;
    const response = await fetch(`http://127.0.0.1:8000/api/${kind}/${id}/`, { method: 'DELETE', headers: { Authorization: `Token ${token}` } });
    if (response.ok || response.status === 204) {
      setAdminMessage(t('delete_done'));
      await bootstrap();
    }
  };

  const LangSelect = () => (
    <select className="control-item" value={uiLang} onChange={(e) => setUiLang(e.target.value)}>
      {Object.keys(translations).map((code) => <option key={code} value={code}>{translations[code].flag}</option>)}
    </select>
  );

  const ThemeBtn = () => <button className="control-item" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>{theme === 'light' ? '🌙' : '☀️'}</button>;

  const renderStudentDashboard = () => (
    <div className="dashboard-layout">
      <section>
        <div className="stat-box">🔥 {userStats.streak} {t('streak')}</div>
        <div className="stat-box">⚡ {userStats.xp} {t('xp')}</div>
        <button className="btn-primary hero-button" onClick={() => setView('courses')}>{t('choose')} →</button>
        <h3 className="section-title">{t('activity')}</h3>
        <div className="activity-graph">
          {Array.from({ length: 30 }).map((_, index) => {
            const day = new Date();
            day.setDate(day.getDate() - (29 - index));
            const key = day.toISOString().split('T')[0];
            const count = userStats.activity_graph[key] || 0;
            return <div key={key} className="activity-day" data-level={count === 0 ? 0 : count < 5 ? 1 : 3} />;
          })}
        </div>
      </section>
      <section className="achievement-panel">
        <h2 className="section-title">{t('achievements')}</h2>
        {userStats.achievements.length > 0 ? (
          <div className="achievement-list">
            {userStats.achievements.map((item) => <AchievementCard key={item.id} item={item} label={t('unlocked')} />)}
          </div>
        ) : <div className="empty-achievements">{t('no_achievements')}</div>}
      </section>
    </div>
  );

  const renderCourses = () => (
    <div>
      <button className="btn-secondary" onClick={() => setView('dashboard')}>{t('back')}</button>
      <div className="grid-2">
        {filteredCourses.length === 0 && <div className="empty-achievements">{t('no_courses')}</div>}
        {filteredCourses.map((course) => {
          const lessonExercises = course.lessons[0]?.exercises || [];
          const uniqueTypes = [...new Set(lessonExercises.map((exercise) => exercise.type))];
          const hasTimedExercises = lessonExercises.some((exercise) => Boolean(exercise.data.time_limit));
          const courseTree = new CourseComposite(course.title);
          course.lessons.forEach((lesson) => courseTree.add(new LessonElement(lesson.title)));
          const isEnrolled = userStats.enrollments.some((item) => item.course === course.id);

          return (
            <div key={course.id} className="card card-course" onClick={() => start(course)}>
              <div className="card-topline">{t('module')}</div>
              <h2>{course.title}</h2>
              <p>{course.description}</p>
              <div className="course-meta-box">
                <div className="course-meta-title">{t('task_types')}</div>
                <div className="exercise-badges">
                  {uniqueTypes.map((type) => <span key={type} className="exercise-badge">{getExerciseBadge(type, t)}</span>)}
                </div>
              </div>
              <div className="course-footer-row">
                <span className="course-pill">{hasTimedExercises ? t('timed') : t('no_timed')}</span>
                <span className="course-pill">{lessonExercises.length} {t('lesson_plan')}</span>
                {isEnrolled && <span className="course-pill">{t('enrolled')}</span>}
              </div>
              <div className="course-structure-preview">{courseTree.display()}</div>
              <button className="btn-primary card-action">{t('start')}</button>
            </div>
          );
        })}
      </div>
    </div>
  );

  const renderLearning = () => currentExercise && (
    <div className="exercise-container">
      <header className="learning-header">
        <div className="close-learning" onClick={() => { void bootstrap(); setView('dashboard'); }}>✕</div>
        <div className="progress-bar-container"><div className="progress-fill" style={{ width: `${((currentIndex + 1) / exercises.length) * 100}%` }} /></div>
        <div className="hearts-counter">❤️ {hearts}</div>
      </header>
      <section className="lesson-info-card">
        <div><div className="card-topline">{t('lesson_progress')}</div><div className="lesson-progress-text">{currentIndex + 1} / {exercises.length}</div></div>
        <div className={`timer-card ${timeLeft !== null && timeLeft <= 10 ? 'danger' : ''}`}><span>{t('timer')}</span><strong>{timeLeft !== null ? `${timeLeft}s` : '∞'}</strong></div>
      </section>
      <section className="task-overview">
        <div className="task-type-block">
          <p className="exercise-type-label">{currentExercise.type === 'translation' && t('translate')}{currentExercise.type === 'multiple_choice' && t('select')}{currentExercise.type === 'matching_pairs' && t('matching')}{currentExercise.type === 'listening' && t('listening')}</p>
          <h1 className="question-title">{currentExercise.data.question}</h1>
        </div>
        <div className="exercise-badges learning-badges">{taskTypes.map((type) => <span key={type} className={`exercise-badge ${currentExercise.type === type ? 'active' : ''}`}>{getExerciseBadge(type, t)}</span>)}</div>
      </section>
      {currentExercise.data.hint && <div className="hint-box">{t('hint')}: {currentExercise.data.hint}</div>}
      {currentExercise.data.time_limit && <div className="modifier-chip">⏱ {currentExercise.data.time_limit}s</div>}
      {currentExercise.type === 'multiple_choice' && <div className="options-list">{currentExercise.data.options?.map((option) => <button key={option} className={`option-btn ${selectedOption === option ? 'selected' : ''}`} onClick={() => setSelectedOption(option)} disabled={checkState !== 'idle'}>{option}</button>)}</div>}
      {(currentExercise.type === 'translation' || currentExercise.type === 'listening') && <div className="answer-panel">{currentExercise.type === 'listening' && <button className="btn-secondary audio-button" onClick={playAudio}>{t('play_audio')}</button>}<input className="input-field" type="text" value={textAnswer} onChange={(e) => setTextAnswer(e.target.value)} placeholder={t('answer_field')} disabled={checkState !== 'idle'} /></div>}
      {currentExercise.type === 'matching_pairs' && <div className="matching-board">{currentExercise.data.pairs?.map((pair) => <div key={pair.left} className="matching-row"><div className="matching-left">{pair.left}</div><select className="matching-select" value={matchingAnswers[pair.left] || ''} onChange={(e) => setMatchingAnswers((prev) => ({ ...prev, [pair.left]: e.target.value }))} disabled={checkState !== 'idle'}><option value="">{t('select_right')}</option>{matchingOptions.map((option) => <option key={`${pair.left}-${option}`} value={option}>{option}</option>)}</select></div>)}</div>}
      <footer className={`bottom-bar ${checkState}`}>
        <div className="bar-inner">
          <div className="feedback-msg">{timedOut && checkState === 'incorrect' ? t('time_up') : checkState === 'correct' ? t('excellent') : checkState === 'incorrect' ? t('correct') : ''}{checkState !== 'idle' && <span>{Array.isArray(currentExercise.data.correct_answer) ? currentExercise.data.correct_answer.map((pair) => `${pair.left} - ${pair.right}`).join(', ') : currentExercise.data.correct_answer}</span>}</div>
          <button className="btn-primary action-button" onClick={() => {
            if (checkState === 'idle') void handleCheck();
            else if (hearts <= 0) setView('game_over');
            else if (currentIndex + 1 < exercises.length) { setCurrentIndex((prev) => prev + 1); resetAnswerState(); }
            else { void bootstrap(); setView('victory'); resetAnswerState(); }
          }} disabled={(checkState === 'idle' && !canSubmit()) || submitting}>{checkState === 'idle' ? t('check') : t('continue')}</button>
        </div>
      </footer>
    </div>
  );

  const renderAdminDashboard = () => (
    <div>
      <section className="admin-hero">
        <div>
          <div className="card-topline">{t('admin_panel')}</div>
          <h1>{t('manage_content')}</h1>
          <p>{t('admin_help')}</p>
        </div>
      </section>
      <div className="admin-stats-grid">
        <div className="stat-box">{courses.length}<span>{t('total_courses')}</span></div>
        <div className="stat-box">{flatLessons.length}<span>{t('total_lessons')}</span></div>
        <div className="stat-box">{flatExercises.length}<span>{t('total_exercises')}</span></div>
        <div className="stat-box">{userStats.achievements.length}<span>{t('total_achievements')}</span></div>
      </div>
    </div>
  );

  const renderAdminCourses = () => (
    <div className="admin-grid">
      <section className="admin-form-card">
        <h2>{t('create_course')}</h2>
        <input className="auth-input" placeholder={t('title')} value={courseDraft.title} onChange={(e) => setCourseDraft((prev) => ({ ...prev, title: e.target.value }))} />
        <textarea className="admin-textarea" placeholder={t('description')} value={courseDraft.description} onChange={(e) => setCourseDraft((prev) => ({ ...prev, description: e.target.value }))} />
        <select className="auth-input" value={courseDraft.source_language} onChange={(e) => setCourseDraft((prev) => ({ ...prev, source_language: e.target.value }))}><option value="">{t('source_language')}</option>{languages.map((language) => <option key={language.id} value={language.id}>{language.name}</option>)}</select>
        <select className="auth-input" value={courseDraft.language} onChange={(e) => setCourseDraft((prev) => ({ ...prev, language: e.target.value }))}><option value="">{t('target_language')}</option>{languages.map((language) => <option key={language.id} value={language.id}>{language.name}</option>)}</select>
        <button className="btn-primary full-width" onClick={() => void submitCourse()}>{t('create')}</button>
      </section>
      <section className="admin-list-card">
        <h2>{t('admin_courses')}</h2>
        {courses.map((course) => <div key={course.id} className="admin-list-item"><div><strong>{course.title}</strong><p>{course.description}</p></div><button className="btn-secondary btn-danger-soft" onClick={() => void deleteEntity('courses', course.id)}>{t('delete')}</button></div>)}
      </section>
    </div>
  );

  const renderAdminLessons = () => (
    <div className="admin-grid">
      <section className="admin-form-card">
        <h2>{t('create_lesson')}</h2>
        <select className="auth-input" value={lessonDraft.course} onChange={(e) => setLessonDraft((prev) => ({ ...prev, course: e.target.value }))}><option value="">{t('courses')}</option>{courses.map((course) => <option key={course.id} value={course.id}>{course.title}</option>)}</select>
        <input className="auth-input" placeholder={t('title')} value={lessonDraft.title} onChange={(e) => setLessonDraft((prev) => ({ ...prev, title: e.target.value }))} />
        <input className="auth-input" placeholder={t('order')} value={lessonDraft.order} onChange={(e) => setLessonDraft((prev) => ({ ...prev, order: e.target.value }))} />
        <button className="btn-primary full-width" onClick={() => void submitLesson()}>{t('create')}</button>
      </section>
      <section className="admin-list-card">
        <h2>{t('admin_lessons')}</h2>
        {flatLessons.map((lesson) => <div key={lesson.id} className="admin-list-item"><div><strong>{lesson.title}</strong><p>{courses.find((course) => course.id === lesson.course)?.title} · #{lesson.order}</p></div><button className="btn-secondary btn-danger-soft" onClick={() => void deleteEntity('lessons', lesson.id)}>{t('delete')}</button></div>)}
      </section>
    </div>
  );

  const renderAdminExercises = () => (
    <div className="admin-grid">
      <section className="admin-form-card">
        <h2>{t('create_exercise')}</h2>
        <select className="auth-input" value={exerciseDraft.lesson} onChange={(e) => setExerciseDraft((prev) => ({ ...prev, lesson: e.target.value }))}><option value="">{t('lesson')}</option>{flatLessons.map((lesson) => <option key={lesson.id} value={lesson.id}>{lesson.title}</option>)}</select>
        <select className="auth-input" value={exerciseDraft.type} onChange={(e) => setExerciseDraft((prev) => ({ ...prev, type: e.target.value as ExerciseType }))}><option value="translation">{t('type_translation')}</option><option value="multiple_choice">{t('type_multiple_choice')}</option><option value="matching_pairs">{t('type_matching_pairs')}</option><option value="listening">{t('type_listening')}</option></select>
        <textarea className="admin-textarea" placeholder={t('question')} value={exerciseDraft.question} onChange={(e) => setExerciseDraft((prev) => ({ ...prev, question: e.target.value }))} />
        <input className="auth-input" placeholder={t('correct_answer')} value={exerciseDraft.correctAnswer} onChange={(e) => setExerciseDraft((prev) => ({ ...prev, correctAnswer: e.target.value }))} />
        {exerciseDraft.type === 'multiple_choice' && <input className="auth-input" placeholder={t('options')} value={exerciseDraft.options} onChange={(e) => setExerciseDraft((prev) => ({ ...prev, options: e.target.value }))} />}
        {exerciseDraft.type === 'matching_pairs' && <textarea className="admin-textarea" placeholder={t('pairs')} value={exerciseDraft.pairs} onChange={(e) => setExerciseDraft((prev) => ({ ...prev, pairs: e.target.value }))} />}
        <input className="auth-input" placeholder={t('hint')} value={exerciseDraft.hint} onChange={(e) => setExerciseDraft((prev) => ({ ...prev, hint: e.target.value }))} />
        <input className="auth-input" placeholder={t('time_limit')} value={exerciseDraft.timeLimit} onChange={(e) => setExerciseDraft((prev) => ({ ...prev, timeLimit: e.target.value }))} />
        {exerciseDraft.type === 'listening' && <><input className="auth-input" placeholder={t('audio_text')} value={exerciseDraft.audioText} onChange={(e) => setExerciseDraft((prev) => ({ ...prev, audioText: e.target.value }))} /><input className="auth-input" placeholder={t('voice_locale')} value={exerciseDraft.voiceLocale} onChange={(e) => setExerciseDraft((prev) => ({ ...prev, voiceLocale: e.target.value }))} /></>}
        <button className="btn-primary full-width" onClick={() => void submitExercise()}>{t('create')}</button>
      </section>
      <section className="admin-list-card">
        <h2>{t('admin_exercises')}</h2>
        {flatExercises.map((exercise) => <div key={exercise.id} className="admin-list-item"><div><strong>{getExerciseTypeLabel(exercise.type, t)}</strong><p>{exercise.data.question}</p></div><button className="btn-secondary btn-danger-soft" onClick={() => void deleteEntity('exercises', exercise.id)}>{t('delete')}</button></div>)}
      </section>
    </div>
  );

  const renderAuth = () => (
    <div className="auth-shell">
      <div className="auth-showcase">
        <div className="card-topline">{authMode === 'login' ? t('welcome') : t('register_title')}</div>
        <h1>{authMode === 'login' ? t('login_title') : t('register_title')}</h1>
        <p>{t('auth_subtitle')}</p>
        <div className="showcase-pills"><span className="course-pill">{t('pattern_observer')}</span><span className="course-pill">{t('pattern_adapter')}</span><span className="course-pill">{t('pattern_factory')}</span><span className="course-pill">{t('pattern_decorator')}</span></div>
      </div>
      <div className="auth-card auth-card-wide">
        <div className="auth-topbar">
          <div className="auth-brand">
            <div className="auth-brand-mark">L</div>
            <div>
              <h1 className="logo-text auth-logo">{t('appName')}</h1>
              <div className="micro-label">{authMode === 'login' ? t('studentspace') : t('register')}</div>
            </div>
          </div>
          <div className="auth-floating-controls"><ThemeBtn /><LangSelect /></div>
        </div>
        <div className="auth-toggle"><button className={`toggle-btn ${authMode === 'login' ? 'active' : ''}`} onClick={() => setAuthMode('login')}>{t('login')}</button><button className={`toggle-btn ${authMode === 'register' ? 'active' : ''}`} onClick={() => setAuthMode('register')}>{t('register')}</button></div>
        <div className="auth-field-group">
          <label className="auth-label">{t('username')}</label>
          <input className="auth-input" type="text" placeholder={t('username_placeholder')} value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>
        <div className="auth-field-group">
          <label className="auth-label">{t('password')}</label>
          <input className="auth-input" type="password" placeholder={t('password_placeholder')} value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        {authMode === 'register' && (
          <div className="auth-field-group">
            <label className="auth-label">{t('confirm_password')}</label>
            <input className="auth-input" type="password" placeholder={t('confirm_password_placeholder')} value={passwordConfirm} onChange={(e) => setPasswordConfirm(e.target.value)} />
          </div>
        )}
        {authError && <div className="form-message error">{t('form_error_prefix')} {authError}</div>}
        {authMessage && <div className="form-message success">{authMessage}</div>}
        <button className="btn-primary full-width" onClick={() => void (authMode === 'login' ? handleLogin() : handleRegister())}>{authMode === 'login' ? t('login') : t('register')}</button>
        <div className="auth-helper-note">
          {authMode === 'register' ? t('register_hint') : t('login_hint')}
        </div>
      </div>
    </div>
  );

  const renderAdminShell = () => {
    const sections: { id: AdminSection; label: string }[] = [
      { id: 'admin_dashboard', label: t('admin_dashboard') },
      { id: 'admin_courses', label: t('admin_courses') },
      { id: 'admin_lessons', label: t('admin_lessons') },
      { id: 'admin_exercises', label: t('admin_exercises') },
    ];

    return (
      <div className="admin-layout">
        <aside className="admin-sidebar">
          <h2>{t('adminspace')}</h2>
          <p>{currentUser?.username}</p>
          {sections.map((section) => <button key={section.id} className={`admin-nav-btn ${view === section.id ? 'active' : ''}`} onClick={() => setView(section.id)}>{section.label}</button>)}
          <div className="sidebar-controls"><ThemeBtn /><LangSelect /></div>
          <button className="btn-secondary full-width" onClick={logout}>{t('logout')}</button>
        </aside>
        <section className="admin-content">
          {adminMessage && <div className="unlock-banner">{adminMessage}</div>}
          {view === 'admin_dashboard' && renderAdminDashboard()}
          {view === 'admin_courses' && renderAdminCourses()}
          {view === 'admin_lessons' && renderAdminLessons()}
          {view === 'admin_exercises' && renderAdminExercises()}
        </section>
      </div>
    );
  };

  if (view === 'auth' || !token) return <div className="app-container">{renderAuth()}</div>;
  if (currentUser?.is_staff) return <div className="app-container admin-app">{renderAdminShell()}</div>;

  return (
    <div className="app-container">
      {view !== 'learning' && (
        <header className="main-header">
          <div>
            <h1 className="logo-text" onClick={() => setView('dashboard')}>{t('appName')}</h1>
            <div className="micro-label">{t('studentspace')}</div>
          </div>
          <div className="header-nav-group">
            <button className={`nav-pill ${view === 'dashboard' ? 'active' : ''}`} onClick={() => setView('dashboard')}>{t('dashboard')}</button>
            <button className={`nav-pill ${view === 'courses' ? 'active' : ''}`} onClick={() => setView('courses')}>{t('courses')}</button>
          </div>
          <div className="header-stats">
            <div className="header-stat">🔥 {userStats.streak}</div>
            <div className="header-stat">⚡ {userStats.xp}</div>
            <ThemeBtn />
            <LangSelect />
            <button className="control-item btn-danger-icon" onClick={logout}>✕</button>
          </div>
        </header>
      )}

      <main className="center-content">
        {recentUnlocks.length > 0 && view !== 'learning' && <section className="unlock-banner"><span>{t('unlocked')}:</span>{recentUnlocks.map((item) => item.achievement.title).join(', ')}</section>}
        {view === 'dashboard' && renderStudentDashboard()}
        {view === 'courses' && renderCourses()}
        {view === 'learning' && renderLearning()}
        {(view === 'victory' || view === 'game_over') && <div className="end-screen"><h1 className={`end-title ${view}`}>{view === 'game_over' ? t('out_of_hearts') : t('victory')}</h1><button className="btn-primary hero-button" onClick={() => { void bootstrap(); setView('dashboard'); }}>{t('dashboard')}</button></div>}
      </main>
    </div>
  );
};

export default App;
