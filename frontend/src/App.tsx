import React, { useEffect, useState } from 'react';
import './App.css';

const translations: Record<string, any> = {
  en: { choose: 'Select Training', start: 'Begin', streak: 'Streak', xp: 'XP', back: '← Profile', check: 'Check', continue: 'Next', excellent: 'Excellent!', meaning: 'Meaning', correct: 'Solution', out_of_hearts: 'Out of Hearts!', game_over: 'Try again!', victory: 'Lesson Complete!', login: 'Log In', register: 'Sign Up', username: 'Username', password: 'Password', dashboard: 'My Stats', activity: 'Activity (30d)', logout: 'Exit', translate: 'Translate', select: 'Choose Correct', flag: '🇺🇸' },
  ru: { choose: 'Выберите курс', start: 'Начать', streak: 'Серия', xp: 'Опыт', back: '← В профиль', check: 'Проверить', continue: 'Дальше', excellent: 'Отлично!', meaning: 'Значение', correct: 'Правильно', out_of_hearts: 'Нет жизней!', game_over: 'Не сдавайся!', victory: 'Урок пройден!', login: 'Войти', register: 'Создать аккаунт', username: 'Логин', password: 'Пароль', dashboard: 'Личный кабинет', activity: 'Активность', logout: 'Выйти', translate: 'Переведи это', select: 'Выбери ответ', flag: '🇷🇺' },
  es: { choose: 'Elige un curso', start: 'Empezar', streak: 'Racha', xp: 'XP', back: '← Volver', check: 'Comprobar', continue: 'Siguiente', excellent: '¡Excelente!', meaning: 'Significado', correct: 'Solución', out_of_hearts: '¡Sin vidas!', game_over: '¡Inténtalo!', victory: '¡Completado!', login: 'Entrar', register: 'Registro', username: 'Usuario', password: 'Clave', dashboard: 'Perfil', logout: 'Salir', translate: 'Traduce', select: 'Selecciona', flag: '🇪🇸' },
  fr: { choose: 'Choisir un cours', start: 'Démarrer', streak: 'Série', xp: 'XP', back: '← Retour', check: 'Vérifier', continue: 'Continuer', excellent: 'Excellent !', meaning: 'Sens', correct: 'Solution', out_of_hearts: 'Plus de vies !', game_over: 'Réessayez !', victory: 'Terminé !', login: 'Connexion', register: 'Inscription', username: 'Pseudo', password: 'Mot de passe', dashboard: 'Profil', logout: 'Sortir', translate: 'Traduisez', select: 'Choisissez', flag: '🇫🇷' },
  de: { choose: 'Kurs wählen', start: 'Start', streak: 'Serie', xp: 'XP', back: '← Zurück', check: 'Prüfen', continue: 'Weiter', excellent: 'Exzellent!', meaning: 'Bedeutung', correct: 'Lösung', out_of_hearts: 'Keine Leben!', game_over: 'Nochmal!', victory: 'Fertig!', login: 'Login', register: 'Anmelden', username: 'Nutzername', password: 'Passwort', dashboard: 'Profil', logout: 'Logout', translate: 'Übersetzen', select: 'Wählen', flag: '🇩🇪' },
  it: { choose: 'Scegli un corso', start: 'Inizia', streak: 'Serie', xp: 'XP', back: '← Indietro', check: 'Controlla', continue: 'Continua', excellent: 'Eccellente!', meaning: 'Significato', correct: 'Soluzione', out_of_hearts: 'Senza vite!', game_over: 'Riprova!', victory: 'Finito!', login: 'Login', register: 'Registrati', username: 'Username', password: 'Password', dashboard: 'Profilo', logout: 'Esci', translate: 'Traduci', select: 'Scegli', flag: '🇮🇹' },
  ja: { choose: 'コースを選択', start: '開始', streak: '連続', xp: 'XP', back: '← 戻る', check: '確認', continue: '次へ', excellent: '素晴らしい!', meaning: '意味', correct: '正解', out_of_hearts: 'ハート切れ!', game_over: 'また明日!', victory: '完了!', login: 'ログイン', register: '登録', username: 'ユーザー', password: 'パスワード', dashboard: 'プロフィール', logout: '終了', translate: '翻訳', select: '選択', flag: '🇯🇵' },
  zh: { choose: '选择课程', start: '开始', streak: '连胜', xp: '经验', back: '← 返回', check: '检查', continue: '继续', excellent: '太棒了!', meaning: '意思', correct: '正确答案', out_of_hearts: '体力耗尽!', game_over: '再试一次!', victory: '完成!', login: '登录', register: '注册', username: '用户名', password: '密码', dashboard: '个人资料', logout: '退出', translate: '翻译', select: '选择', flag: '🇨🇳' }
};

interface Exercise { id: number; type: 'multiple_choice' | 'translation'; data: { question: string; correct_answer: string; options?: string[] }; }
interface Course { id: number; title: string; description: string; source_language_code: string; lessons: { id: number; exercises: Exercise[] }[]; }

const App: React.FC = () => {
  const [view, setView] = useState<'auth' | 'dashboard' | 'courses' | 'learning' | 'game_over' | 'victory'>('auth');
  const [theme, setTheme] = useState<'light' | 'dark'>(localStorage.getItem('theme') as any || 'light');
  const [uiLang, setUiLang] = useState<string>(localStorage.getItem('uiLang') || 'ru');
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  
  const [courses, setCourses] = useState<Course[]>([]);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [userStats, setUserStats] = useState({ streak: 0, xp: 0, activity_graph: {} });

  const [hearts, setHearts] = useState(5);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [answer, setAnswer] = useState('');
  const [checkState, setCheckState] = useState<'idle' | 'correct' | 'incorrect'>('idle');

  const t = (key: string) => translations[uiLang]?.[key] || translations['en'][key] || key;

  useEffect(() => { document.documentElement.setAttribute('data-theme', theme); localStorage.setItem('theme', theme); }, [theme]);
  useEffect(() => { localStorage.setItem('uiLang', uiLang); if (token) loadData(); }, [token, uiLang]);

  const loadData = async () => {
    try {
      const cr = await fetch('http://127.0.0.1:8000/api/courses/');
      const data = await cr.json(); setCourses(Array.isArray(data) ? data : []);
      if (token) {
        const stats = await fetch('http://127.0.0.1:8000/api/progress/', { headers: { 'Authorization': `Token ${token}` } });
        const sd = await stats.json(); if (sd.status === 'ok') setUserStats(sd);
        if (view === 'auth') setView('dashboard');
      }
    } catch (e) {}
  };

  const handleLogin = async (reg: boolean) => {
    const url = reg ? 'http://127.0.0.1:8000/api/auth/register/' : 'http://127.0.0.1:8000/api/auth/login/';
    const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, password }) });
    const data = await res.json();
    if (data.token) { localStorage.setItem('token', data.token); setToken(data.token); } else alert("Check inputs.");
  };

  const logout = () => { localStorage.removeItem('token'); setToken(null); setView('auth'); setUserStats({streak:0, xp:0, activity_graph:{}}); setUsername(''); setPassword(''); };

  const start = (c: Course) => {
    const lesson = c.lessons[0];
    if (lesson?.exercises.length > 0) {
      setExercises([...lesson.exercises].sort(() => Math.random() - 0.5).slice(0, 7));
      setCurrentIndex(0); setHearts(5); setView('learning'); setCheckState('idle'); setAnswer('');
    }
  };

  const handleCheck = async () => {
    const ex = exercises[currentIndex];
    const isCorrect = answer.trim().toLowerCase() === ex.data.correct_answer.toLowerCase();
    const res = await fetch(`http://127.0.0.1:8000/api/exercises/${ex.id}/submit_answer/`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Token ${token}` }, body: JSON.stringify({ answer })
    });
    const data = await res.json();
    if (isCorrect) { setCheckState('correct'); setUserStats(p => ({...p, xp: data.xp, streak: data.streak})); }
    else { setCheckState('incorrect'); setHearts(p => p - 1); }
  };

  const LangSelect = () => (
    <select className="control-item" value={uiLang} onChange={e => setUiLang(e.target.value)}>
      {Object.keys(translations).map(code => (<option key={code} value={code}>{translations[code].flag}</option>))}
    </select>
  );

  const ThemeBtn = () => (
    <button className="control-item" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
      {theme === 'light' ? '🌙' : '☀️'}
    </button>
  );

  if (view === 'auth' && !token) {
    return (
      <div className="app-container">
        <div className="auth-wrapper">
            <div className="auth-card">
                <h1 className="logo-text" style={{fontSize:'4rem', marginBottom: 30}}>Lingo</h1>
                <input className="auth-input" type="text" placeholder={t('username')} value={username} onChange={e => setUsername(e.target.value)} />
                <input className="auth-input" type="password" placeholder={t('password')} value={password} onChange={e => setPassword(e.target.value)} />
                <button className="btn-primary" style={{width:'100%', marginBottom: 15}} onClick={() => handleLogin(false)}>{t('login')}</button>
                <button className="btn-secondary" style={{width:'100%'}} onClick={() => handleLogin(true)}>{t('register')}</button>
                <div style={{marginTop:30, display:'flex', gap:10, justifyContent:'center'}}><ThemeBtn /><LangSelect /></div>
            </div>
        </div>
      </div>
    );
  }

  const filtered = courses.filter(c => c.source_language_code === uiLang);

  return (
    <div className="app-container">
      {view !== 'learning' && (
        <header className="main-header">
            <h1 className="logo-text" onClick={() => setView('dashboard')}>Lingo</h1>
            <div className="header-stats">
            <div onClick={() => setView('dashboard')} style={{cursor:'pointer'}}>🔥 {userStats.streak}</div>
            <div onClick={() => setView('dashboard')} style={{cursor:'pointer'}}>⚡ {userStats.xp}</div>
            <ThemeBtn /><LangSelect />
            <button className="control-item btn-danger-icon" onClick={logout}>✕</button>
            </div>
        </header>
      )}

      <main className="center-content">
        {view === 'dashboard' && (
          <div>
            <div className="stat-box">🔥 {userStats.streak} {t('streak')}</div>
            <div className="stat-box">⚡ {userStats.xp} {t('xp')}</div>
            <button className="btn-primary" style={{padding: 25, fontSize:'1.5rem'}} onClick={() => setView('courses')}>{t('choose')} →</button>
            <div className="activity-graph" style={{marginTop:40}}>
                {Array.from({length: 30}).map((_, i) => {
                    const d = new Date(); d.setDate(d.getDate() - (29 - i));
                    const ds = d.toISOString().split('T')[0];
                    const c = (userStats.activity_graph as any)[ds] || 0;
                    return <div key={ds} className="activity-day" data-level={c === 0 ? 0 : c < 5 ? 1 : 3} />;
                })}
            </div>
          </div>
        )}

        {view === 'courses' && (
          <div>
            <button className="btn-secondary" style={{marginBottom: 20}} onClick={() => setView('dashboard')}>{t('back')}</button>
            <div className="grid-2">
              {filtered.map(c => (
                <div key={c.id} className="card" onClick={() => start(c)}>
                  <h2>{c.title}</h2><p>{c.description}</p>
                  <button className="btn-primary" style={{marginTop:'auto'}}>{t('start')}</button>
                </div>
              ))}
            </div>
          </div>
        )}

        {view === 'learning' && (
          <div className="exercise-container">
            <header className="learning-header">
                <div style={{fontSize:'2.5rem', cursor:'pointer', fontWeight:900, color:'#ccc'}} onClick={() => { loadData(); setView('dashboard'); }}>✕</div>
                <div className="progress-bar-container"><div className="progress-fill" style={{width: `${(currentIndex / exercises.length)*100}%`}}></div></div>
                <div style={{fontSize:'1.8rem', fontWeight:900, color:'var(--danger)'}}>❤️ {hearts}</div>
            </header>
            <p style={{color:'var(--text-light)', fontWeight:900, textTransform:'uppercase'}}>{exercises[currentIndex].type === 'translation' ? t('translate') : t('select')}</p>
            <h1 className="question-title">{exercises[currentIndex].data.question}</h1>
            {exercises[currentIndex].type === 'multiple_choice' ? (
              <div className="options-list">
                {exercises[currentIndex].data.options?.map(opt => (
                  <button key={opt} className={`option-btn ${answer === opt ? 'selected' : ''}`} onClick={() => setAnswer(opt)}>{opt}</button>
                ))}
              </div>
            ) : <input className="input-field" type="text" value={answer} onChange={e => setAnswer(e.target.value)} autoFocus placeholder="..." />}
            <footer className={`bottom-bar ${checkState}`}>
                <div className="bar-inner">
                    <div className="feedback-msg">
                        {checkState === 'correct' ? t('excellent') : checkState === 'incorrect' ? t('correct') : ''}
                        {checkState !== 'idle' && <span>{exercises[currentIndex].data.correct_answer}</span>}
                    </div>
                    <button className="btn-primary" style={{minWidth: 150}} onClick={() => {
                        if (checkState === 'idle') handleCheck();
                        else if (hearts <= 0) setView('game_over');
                        else if (currentIndex + 1 < exercises.length) { setCurrentIndex(p => p + 1); setCheckState('idle'); setAnswer(''); }
                        else { loadData(); setView('victory'); }
                    }} disabled={checkState === 'idle' && !answer}>{checkState === 'idle' ? t('check') : t('continue')}</button>
                </div>
            </footer>
          </div>
        )}

        {(view === 'victory' || view === 'game_over') && (
          <div style={{textAlign:'center'}}>
            <h1 style={{fontSize:'5rem', color: view === 'game_over' ? 'var(--danger)' : 'var(--gold)'}}>{view === 'game_over' ? t('out_of_hearts') : t('victory')}</h1>
            <button className="btn-primary" style={{marginTop: 40, maxWidth: 400}} onClick={() => { loadData(); setView('dashboard'); }}>{t('dashboard')}</button>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
