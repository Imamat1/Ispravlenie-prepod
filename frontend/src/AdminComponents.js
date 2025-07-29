import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useCompleteAdmin } from './CompleteAdminPanel';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Student Management Component
export const StudentManagement = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterActive, setFilterActive] = useState('all');
  const { token } = useCompleteAdmin();

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    try {
      const response = await axios.get(`${API}/admin/students`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStudents(response.data);
    } catch (error) {
      console.error('Failed to fetch students:', error);
    }
    setLoading(false);
  };

  const handleToggleActive = async (studentId, isActive) => {
    try {
      await axios.put(`${API}/admin/students/${studentId}`, 
        { is_active: !isActive },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchStudents();
    } catch (error) {
      console.error('Failed to update student:', error);
    }
  };

  const filteredStudents = students.filter(student => {
    const matchesSearch = student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         student.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterActive === 'all' || 
                         (filterActive === 'active' && student.is_active) ||
                         (filterActive === 'inactive' && !student.is_active);
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return <div className="flex justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
    </div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Управление учениками</h1>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div className="flex-1 max-w-md">
            <input
              type="text"
              placeholder="Поиск по имени или email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
            />
          </div>
          <div className="flex space-x-4">
            <select
              value={filterActive}
              onChange={(e) => setFilterActive(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
            >
              <option value="all">Все студенты</option>
              <option value="active">Активные</option>
              <option value="inactive">Заблокированные</option>
            </select>
          </div>
        </div>
      </div>

      {/* Students Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Студент
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Баллы
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Последняя активность
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Статус
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredStudents.map((student) => (
              <tr key={student.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-10 h-10 rounded-full bg-teal-100 flex items-center justify-center">
                      <span className="text-teal-600 font-medium">
                        {student.name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">{student.name}</div>
                      <div className="text-sm text-gray-500">{student.email}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900 font-medium">{student.total_score || 0}</div>
                  <div className="text-sm text-gray-500">
                    {student.completed_courses?.length || 0} курсов завершено
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {student.last_activity ? 
                    new Date(student.last_activity).toLocaleDateString('ru-RU') : 
                    'Нет данных'
                  }
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    student.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {student.is_active ? 'Активен' : 'Заблокирован'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => handleToggleActive(student.id, student.is_active)}
                    className={`mr-3 ${
                      student.is_active ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'
                    }`}
                  >
                    {student.is_active ? 'Заблокировать' : 'Разблокировать'}
                  </button>
                  <button className="text-teal-600 hover:text-teal-900">
                    Подробно
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {filteredStudents.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">Студенты не найдены</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Teacher Management Component
export const TeacherManagement = () => {
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTeacher, setEditingTeacher] = useState(null);
  const { token } = useCompleteAdmin();

  useEffect(() => {
    fetchTeachers();
  }, []);

  const fetchTeachers = async () => {
    try {
      const response = await axios.get(`${API}/admin/teachers`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTeachers(response.data);
    } catch (error) {
      console.error('Failed to fetch teachers:', error);
    }
    setLoading(false);
  };

  const handleCreateTeacher = () => {
    setEditingTeacher(null);
    setShowModal(true);
  };

  const handleEditTeacher = (teacher) => {
    setEditingTeacher(teacher);
    setShowModal(true);
  };

  const handleDeleteTeacher = async (teacherId) => {
    if (window.confirm('Вы уверены, что хотите удалить этого преподавателя?')) {
      try {
        await axios.delete(`${API}/admin/teachers/${teacherId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        fetchTeachers();
      } catch (error) {
        console.error('Failed to delete teacher:', error);
      }
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
    </div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Управление преподавателями</h1>
        <button
          onClick={handleCreateTeacher}
          className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 flex items-center space-x-2"
        >
          <span>➕</span>
          <span>Добавить преподавателя</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {teachers.map((teacher) => (
          <div key={teacher.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-4 mb-4">
              {teacher.image_url ? (
                <img
                  src={teacher.image_url}
                  alt={teacher.name}
                  className="w-16 h-16 rounded-full object-cover"
                />
              ) : (
                <div className="w-16 h-16 rounded-full bg-teal-100 flex items-center justify-center">
                  <span className="text-teal-600 text-xl font-bold">
                    {teacher.name.charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">{teacher.name}</h3>
                <p className="text-teal-600 font-medium">{teacher.subject}</p>
              </div>
            </div>
            
            {teacher.bio && (
              <p className="text-gray-600 text-sm mb-4">{teacher.bio}</p>
            )}
            
            <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
              <span>Email: {teacher.email}</span>
              <span className={`px-2 py-1 rounded-full text-xs ${
                teacher.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {teacher.is_active ? 'Активен' : 'Неактивен'}
              </span>
            </div>
            
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => handleEditTeacher(teacher)}
                className="px-3 py-1 text-sm text-teal-600 hover:text-teal-900"
              >
                Редактировать
              </button>
              <button
                onClick={() => handleDeleteTeacher(teacher.id)}
                className="px-3 py-1 text-sm text-red-600 hover:text-red-900"
              >
                Удалить
              </button>
            </div>
          </div>
        ))}
      </div>

      {teachers.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">Преподаватели не найдены</p>
        </div>
      )}

      {showModal && (
        <TeacherModal
          teacher={editingTeacher}
          onClose={() => setShowModal(false)}
          onSave={() => {
            setShowModal(false);
            fetchTeachers();
          }}
        />
      )}
    </div>
  );
};

// Teacher Modal Component
const TeacherModal = ({ teacher, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: teacher?.name || '',
    email: teacher?.email || '',
    subject: teacher?.subject || '',
    bio: teacher?.bio || '',
    image_url: teacher?.image_url || ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { token } = useCompleteAdmin();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (teacher) {
        await axios.put(`${API}/admin/teachers/${teacher.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post(`${API}/admin/teachers`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      onSave();
    } catch (error) {
      console.error('Failed to save teacher:', error);
      
      let errorMessage = 'Ошибка сохранения преподавателя';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.status === 400) {
        errorMessage = 'Неверные данные. Проверьте правильность заполнения полей.';
      } else if (error.response?.status === 401) {
        errorMessage = 'Нет прав доступа. Пожалуйста, войдите в систему заново.';
      } else if (error.response?.status === 409) {
        errorMessage = 'Преподаватель с таким email уже существует.';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {teacher ? 'Редактировать преподавателя' : 'Добавить преподавателя'}
          </h3>
          
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded-md">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Имя</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Предмет</label>
              <input
                type="text"
                value={formData.subject}
                onChange={(e) => setFormData({...formData, subject: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Биография</label>
              <textarea
                value={formData.bio}
                onChange={(e) => setFormData({...formData, bio: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                rows="3"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">URL фото</label>
              <input
                type="url"
                value={formData.image_url}
                onChange={(e) => setFormData({...formData, image_url: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
              >
                Отмена
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-white bg-teal-600 hover:bg-teal-700 rounded-md disabled:opacity-50"
              >
                {loading ? 'Сохранение...' : 'Сохранить'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Application Management Component
export const ApplicationManagement = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');
  const { token } = useCompleteAdmin();

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      const response = await axios.get(`${API}/admin/applications`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setApplications(response.data);
    } catch (error) {
      console.error('Failed to fetch applications:', error);
    }
    setLoading(false);
  };

  const handleUpdateApplication = async (applicationId, status, comment = '') => {
    try {
      await axios.put(`${API}/admin/applications/${applicationId}`, 
        { status, admin_comment: comment },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchApplications();
    } catch (error) {
      console.error('Failed to update application:', error);
    }
  };

  const filteredApplications = applications.filter(app => {
    return filterStatus === 'all' || app.status === filterStatus;
  });

  if (loading) {
    return <div className="flex justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
    </div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Управление заявками</h1>
      </div>

      {/* Filter */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Фильтр по статусу:</span>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
          >
            <option value="all">Все заявки</option>
            <option value="pending">Ожидающие</option>
            <option value="approved">Одобренные</option>
            <option value="rejected">Отклоненные</option>
          </select>
        </div>
      </div>

      {/* Applications List */}
      <div className="space-y-4">
        {filteredApplications.map((application) => (
          <div key={application.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  {application.student_name}
                </h3>
                <p className="text-gray-600">{application.student_email}</p>
                <p className="text-sm text-gray-500 mt-1">
                  Курс: <span className="font-medium">{application.course_title}</span>
                </p>
                <p className="text-sm text-gray-500">
                  Дата подачи: {new Date(application.created_at).toLocaleDateString('ru-RU')}
                </p>
              </div>
              
              <div className="text-right">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  application.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  application.status === 'approved' ? 'bg-green-100 text-green-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {application.status === 'pending' ? 'Ожидает' :
                   application.status === 'approved' ? 'Одобрено' : 'Отклонено'}
                </span>
              </div>
            </div>

            {application.message && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Сообщение:</h4>
                <p className="text-gray-600 bg-gray-50 p-3 rounded">{application.message}</p>
              </div>
            )}

            {application.admin_comment && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Комментарий администратора:</h4>
                <p className="text-gray-600 bg-blue-50 p-3 rounded">{application.admin_comment}</p>
              </div>
            )}

            {application.status === 'pending' && (
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    const comment = prompt('Комментарий (необязательно):');
                    handleUpdateApplication(application.id, 'approved', comment || '');
                  }}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Одобрить
                </button>
                <button
                  onClick={() => {
                    const comment = prompt('Причина отклонения:');
                    if (comment) {
                      handleUpdateApplication(application.id, 'rejected', comment);
                    }
                  }}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                >
                  Отклонить
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredApplications.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">Заявки не найдены</p>
        </div>
      )}
    </div>
  );
};

// Reports Component
export const ReportsComponent = () => {
  const [courseStats, setCourseStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const { token } = useCompleteAdmin();

  useEffect(() => {
    fetchCourseStats();
  }, []);

  const fetchCourseStats = async () => {
    try {
      const response = await axios.get(`${API}/admin/reports/courses`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCourseStats(response.data);
    } catch (error) {
      console.error('Failed to fetch course stats:', error);
    }
    setLoading(false);
  };

  if (loading) {
    return <div className="flex justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
    </div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Отчеты и аналитика</h1>
        <button className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700">
          Экспорт в Excel
        </button>
      </div>

      {/* Course Statistics */}
      <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Статистика по курсам</h2>
        </div>
        
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Курс
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Записано студентов
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Завершенные тесты
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Средний балл
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                % завершения
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {courseStats.map((stat) => (
              <tr key={stat.course_id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{stat.course_title}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {stat.enrolled_students}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {stat.completed_tests}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {stat.average_score.toFixed(1)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div
                        className="bg-teal-600 h-2 rounded-full"
                        style={{ width: `${Math.min(stat.completion_rate, 100)}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-900">{stat.completion_rate.toFixed(1)}%</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Самый популярный курс</h3>
          <div className="text-center py-4">
            <p className="text-2xl font-bold text-teal-600">
              {courseStats.length > 0 ? 
                courseStats.reduce((a, b) => a.enrolled_students > b.enrolled_students ? a : b).course_title :
                'Нет данных'
              }
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Высокий % завершения</h3>
          <div className="text-center py-4">
            <p className="text-2xl font-bold text-green-600">
              {courseStats.length > 0 ? 
                courseStats.reduce((a, b) => a.completion_rate > b.completion_rate ? a : b).course_title :
                'Нет данных'
              }
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Средний балл</h3>
          <div className="text-center py-4">
            <p className="text-2xl font-bold text-blue-600">
              {courseStats.length > 0 ? 
                (courseStats.reduce((sum, stat) => sum + stat.average_score, 0) / courseStats.length).toFixed(1) :
                '0.0'
              }
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};