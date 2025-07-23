import React, { useState } from 'react';
import { useAuth } from './components';
import { CompleteAdminProvider, useCompleteAdmin, EnhancedCourseManagement, EnhancedTeacherManagement } from './CompleteAdminPanel';
import { LessonManagement, TestManagement } from './AdminLessonsTests';
import { StudentManagement, ApplicationManagement, ReportsComponent } from './AdminComponents';
import MaterialUploadPanel from './MaterialUploadPanel';
import { QAManagement } from './QAManagement';
import { TeamManagement } from './TeamManagement';
import DatabaseAdmin from './DatabaseAdmin';

// Login Component for Admin Panel
const AdminLoginComponent = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (response.ok && data.user_type === 'admin') {
        localStorage.setItem('userToken', data.access_token);
        localStorage.setItem('userData', JSON.stringify({ ...data.user, user_type: data.user_type }));
        window.location.reload();
      } else if (response.ok && data.user_type !== 'admin') {
        setError('У вас нет прав администратора');
      } else {
        setError(data.detail || 'Ошибка входа');
      }
    } catch (error) {
      setError('Ошибка подключения к серверу');
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Админ панель</h1>
          <p className="text-gray-600">Система управления "Уроки Ислама"</p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email администратора
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              placeholder="admin@example.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Пароль
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              placeholder="Введите пароль"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-teal-600 text-white py-3 px-4 rounded-lg hover:bg-teal-700 transition-colors font-medium disabled:opacity-50"
          >
            {loading ? 'Вход...' : 'Войти в панель'}
          </button>
        </form>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg text-sm">
          <div className="font-medium text-blue-900 mb-1">💡 Данные для входа:</div>
          <div className="text-blue-700">Email: miftahylum@gmail.com</div>
          <div className="text-blue-700">Пароль: 197724</div>
        </div>
      </div>
    </div>
  );
};

// Dashboard Component
const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { token } = useCompleteAdmin();

  React.useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
    setLoading(false);
  };

  if (loading) {
    return <div className="flex justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
    </div>;
  }

  const statCards = [
    { title: 'Всего студентов', value: stats?.total_students || 0, icon: '👥', color: 'bg-blue-500' },
    { title: 'Активные студенты', value: stats?.active_students || 0, icon: '✅', color: 'bg-green-500' },
    { title: 'Курсы', value: stats?.total_courses || 0, icon: '📚', color: 'bg-purple-500' },
    { title: 'Уроки', value: stats?.total_lessons || 0, icon: '📖', color: 'bg-indigo-500' },
    { title: 'Тесты', value: stats?.total_tests || 0, icon: '📝', color: 'bg-yellow-500' },
    { title: 'Преподаватели', value: stats?.total_teachers || 0, icon: '👨‍🏫', color: 'bg-orange-500' },
    { title: 'Новые заявки', value: stats?.pending_applications || 0, icon: '📋', color: 'bg-red-500' },
    { title: 'Тесты сегодня', value: stats?.completed_tests_today || 0, icon: '📊', color: 'bg-teal-500' },
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Панель управления</h1>
        <p className="text-gray-600">Добро пожаловать в систему управления "Уроки Ислама"</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((card, index) => (
          <div key={index} className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center">
              <div className={`${card.color} rounded-lg p-3 mr-4`}>
                <span className="text-white text-2xl">{card.icon}</span>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">{card.title}</p>
                <p className="text-2xl font-bold text-gray-900">{card.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Быстрые действия</h3>
          <div className="space-y-3">
            <button className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
              <div className="flex items-center">
                <span className="text-2xl mr-3">📚</span>
                <div>
                  <div className="font-medium">Добавить новый курс</div>
                  <div className="text-sm text-gray-500">Создать курс с уроками и тестами</div>
                </div>
              </div>
            </button>
            <button className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
              <div className="flex items-center">
                <span className="text-2xl mr-3">👨‍🏫</span>
                <div>
                  <div className="font-medium">Добавить преподавателя</div>
                  <div className="text-sm text-gray-500">Зарегистрировать нового преподавателя</div>
                </div>
              </div>
            </button>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Последняя активность</h3>
          <div className="space-y-3">
            <div className="flex items-center text-sm">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
              <span>Новый студент зарегистрировался</span>
              <span className="text-gray-500 ml-auto">2 мин назад</span>
            </div>
            <div className="flex items-center text-sm">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
              <span>Тест по курсу "Основы веры" пройден</span>
              <span className="text-gray-500 ml-auto">5 мин назад</span>
            </div>
            <div className="flex items-center text-sm">
              <span className="w-2 h-2 bg-yellow-500 rounded-full mr-3"></span>
              <span>Новая заявка на курс</span>
              <span className="text-gray-500 ml-auto">10 мин назад</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main Admin Layout
const AdminLayout = ({ children, currentPage, setCurrentPage }) => {
  const { adminUser, isAuthenticated } = useCompleteAdmin();

  // Show login if not authenticated
  if (!isAuthenticated) {
    return <AdminLoginComponent />;
  }

  const menuItems = [
    { id: 'dashboard', name: 'Главная', icon: '📊' },
    { id: 'upload', name: 'Загрузка материалов', icon: '⬆️' },
    { id: 'courses', name: 'Курсы', icon: '📚' },
    { id: 'lessons', name: 'Уроки', icon: '📖' },
    { id: 'tests', name: 'Тесты', icon: '📝' },
    { id: 'qa', name: 'Вопросы и Ответы', icon: '❓' },
    { id: 'team', name: 'Наша команда', icon: '👥' },
    { id: 'students', name: 'Ученики', icon: '🎓' },
    { id: 'teachers', name: 'Преподаватели', icon: '👨‍🏫' },
    { id: 'applications', name: 'Заявки', icon: '📋' },
    { id: 'reports', name: 'Отчеты', icon: '📈' },
  ];

  const handleLogout = () => {
    localStorage.removeItem('userToken');
    localStorage.removeItem('userData');
    window.location.reload();
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-xl border-r border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-800">Админ панель</h1>
          <p className="text-sm text-gray-600 mt-1">{adminUser?.name || adminUser?.email}</p>
        </div>
        
        <nav className="mt-6">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full text-left px-6 py-3 text-sm font-medium flex items-center space-x-3 transition-colors ${
                currentPage === item.id
                  ? 'bg-teal-50 text-teal-700 border-r-2 border-teal-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.name}</span>
            </button>
          ))}
        </nav>

        <div className="absolute bottom-6 left-6 right-6">
          <button
            onClick={handleLogout}
            className="w-full px-4 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-lg flex items-center space-x-3 transition-colors"
          >
            <span className="text-lg">🚪</span>
            <span>Выйти</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          {children}
        </div>
      </div>
    </div>
  );
};

// Main Admin Panel Component
const MainAdminPanel = () => {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <AdminDashboard />;
      case 'upload':
        return <MaterialUploadPanel />;
      case 'courses':
        return <EnhancedCourseManagement />;
      case 'lessons':
        return <LessonManagement />;
      case 'tests':
        return <TestManagement />;
      case 'qa':
        return <QAManagement />;
      case 'team':
        return <TeamManagement />;
      case 'students':
        return <StudentManagement />;
      case 'teachers':
        return <EnhancedTeacherManagement />;
      case 'applications':
        return <ApplicationManagement />;
      case 'reports':
        return <ReportsComponent />;
      default:
        return <AdminDashboard />;
    }
  };

  return (
    <CompleteAdminProvider>
      <AdminLayout currentPage={currentPage} setCurrentPage={setCurrentPage}>
        {renderPage()}
      </AdminLayout>
    </CompleteAdminProvider>
  );
};

export default MainAdminPanel;