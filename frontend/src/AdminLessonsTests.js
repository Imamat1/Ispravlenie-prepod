import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useCompleteAdmin } from './CompleteAdminPanel';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Lesson Management Component
export const LessonManagement = () => {
  const [lessons, setLessons] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingLesson, setEditingLesson] = useState(null);
  const [selectedCourse, setSelectedCourse] = useState('');
  const { token } = useCompleteAdmin();

  useEffect(() => {
    fetchLessons();
    fetchCourses();
  }, []);

  const fetchLessons = async () => {
    try {
      // Get all lessons across all courses
      const coursesResponse = await axios.get(`${API}/admin/courses`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const allLessons = [];
      for (const course of coursesResponse.data) {
        try {
          const lessonsResponse = await axios.get(`${API}/admin/courses/${course.id}/lessons`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          const courseLessons = lessonsResponse.data.map(lesson => ({
            ...lesson,
            course_title: course.title
          }));
          allLessons.push(...courseLessons);
        } catch (error) {
          console.log(`No lessons found for course ${course.title}`);
        }
      }
      
      setLessons(allLessons);
    } catch (error) {
      console.error('Failed to fetch lessons:', error);
    }
    setLoading(false);
  };

  const fetchCourses = async () => {
    try {
      const response = await axios.get(`${API}/admin/courses`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCourses(response.data);
    } catch (error) {
      console.error('Failed to fetch courses:', error);
    }
  };

  const handleCreateLesson = () => {
    setEditingLesson(null);
    setShowModal(true);
  };

  const handleEditLesson = (lesson) => {
    setEditingLesson(lesson);
    setShowModal(true);
  };

  const handleDeleteLesson = async (lessonId) => {
    if (window.confirm('Вы уверены, что хотите удалить этот урок?')) {
      try {
        await axios.delete(`${API}/admin/lessons/${lessonId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        fetchLessons();
      } catch (error) {
        console.error('Failed to delete lesson:', error);
      }
    }
  };

  const filteredLessons = selectedCourse ? 
    lessons.filter(lesson => lesson.course_id === selectedCourse) : 
    lessons;

  if (loading) {
    return <div className="flex justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
    </div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Управление уроками</h1>
        <button
          onClick={handleCreateLesson}
          className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 flex items-center space-x-2"
        >
          <span>➕</span>
          <span>Добавить урок</span>
        </button>
      </div>

      {/* Course Filter */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Фильтр по курсу:</span>
          <select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
          >
            <option value="">Все курсы</option>
            {courses.map((course) => (
              <option key={course.id} value={course.id}>
                {course.title} ({course.level})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Lessons Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Урок
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Курс
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Тип
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Порядок
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
            {filteredLessons.map((lesson) => (
              <tr key={lesson.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{lesson.title}</div>
                    <div className="text-sm text-gray-500">{lesson.description}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {lesson.course_title}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    lesson.lesson_type === 'video' ? 'bg-blue-100 text-blue-800' :
                    lesson.lesson_type === 'text' ? 'bg-green-100 text-green-800' :
                    'bg-purple-100 text-purple-800'
                  }`}>
                    {lesson.lesson_type === 'video' ? 'Видео' :
                     lesson.lesson_type === 'text' ? 'Текст' : 'Смешанный'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {lesson.order}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    lesson.is_published ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {lesson.is_published ? 'Опубликован' : 'Черновик'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => handleEditLesson(lesson)}
                    className="text-teal-600 hover:text-teal-900 mr-3"
                  >
                    Редактировать
                  </button>
                  <button
                    onClick={() => handleDeleteLesson(lesson.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {filteredLessons.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">Уроки не найдены</p>
          </div>
        )}
      </div>

      {showModal && (
        <LessonModal
          lesson={editingLesson}
          courses={courses}
          onClose={() => setShowModal(false)}
          onSave={() => {
            setShowModal(false);
            fetchLessons();
          }}
        />
      )}
    </div>
  );
};

// Lesson Modal Component
const LessonModal = ({ lesson, courses, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    course_id: lesson?.course_id || '',
    title: lesson?.title || '',
    description: lesson?.description || '',
    content: lesson?.content || '',
    lesson_type: lesson?.lesson_type || 'text',
    video_url: lesson?.video_url || '',
    video_duration: lesson?.video_duration || '',
    order: lesson?.order || 1,
    estimated_duration_minutes: lesson?.estimated_duration_minutes || 15
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showTestForm, setShowTestForm] = useState(false);
  const [testFormData, setTestFormData] = useState({
    title: '',
    description: '',
    time_limit_minutes: 15,
    passing_score: 70,
    max_attempts: 3,
    questions: []
  });
  const [newQuestion, setNewQuestion] = useState({
    question_text: '',
    question_type: 'single_choice',
    options: [
      { text: '', is_correct: false },
      { text: '', is_correct: false }
    ],
    explanation: '',
    points: 1
  });
  const { token } = useCompleteAdmin();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Client-side validation
      if (!formData.title.trim()) {
        setError('Название урока обязательно для заполнения');
        setLoading(false);
        return;
      }
      
      if (!formData.course_id) {
        setError('Выберите курс для урока');
        setLoading(false);
        return;
      }
      
      if (!formData.content.trim()) {
        setError('Содержание урока обязательно для заполнения');
        setLoading(false);
        return;
      }

      if (lesson) {
        await axios.put(`${API}/admin/lessons/${lesson.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post(`${API}/admin/lessons`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      onSave();
    } catch (error) {
      console.error('Failed to save lesson:', error);
      
      let errorMessage = 'Ошибка сохранения урока';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.status === 400) {
        errorMessage = 'Неверные данные. Проверьте правильность заполнения полей.';
      } else if (error.response?.status === 401) {
        errorMessage = 'Нет прав доступа. Пожалуйста, войдите в систему заново.';
      } else if (error.response?.status === 404) {
        errorMessage = 'Курс не найден. Выберите существующий курс.';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
    }
    setLoading(false);
  };

  const addQuestionOption = () => {
    setNewQuestion({
      ...newQuestion,
      options: [...newQuestion.options, { text: '', is_correct: false }]
    });
  };

  const removeQuestionOption = (index) => {
    const options = newQuestion.options.filter((_, i) => i !== index);
    setNewQuestion({ ...newQuestion, options });
  };

  const updateQuestionOption = (index, field, value) => {
    const options = [...newQuestion.options];
    options[index] = { ...options[index], [field]: value };
    setNewQuestion({ ...newQuestion, options });
  };

  const addQuestionToTest = () => {
    if (!newQuestion.question_text.trim()) {
      alert('Введите текст вопроса');
      return;
    }
    
    const validOptions = newQuestion.options.filter(opt => opt.text.trim());
    if (validOptions.length < 2) {
      alert('Добавьте минимум 2 варианта ответа');
      return;
    }
    
    if (!validOptions.some(opt => opt.is_correct)) {
      alert('Отметьте минимум один правильный ответ');
      return;
    }

    setTestFormData({
      ...testFormData,
      questions: [...testFormData.questions, { ...newQuestion, options: validOptions }]
    });

    // Reset question form
    setNewQuestion({
      question_text: '',
      question_type: 'single_choice',
      options: [
        { text: '', is_correct: false },
        { text: '', is_correct: false }
      ],
      explanation: '',
      points: 1
    });
  };

  const removeQuestionFromTest = (index) => {
    const questions = testFormData.questions.filter((_, i) => i !== index);
    setTestFormData({ ...testFormData, questions });
  };

  const createTestForLesson = async () => {
    if (!testFormData.title.trim()) {
      alert('Введите название теста');
      return;
    }
    
    if (testFormData.questions.length === 0) {
      alert('Добавьте минимум один вопрос');
      return;
    }

    try {
      const testData = {
        ...testFormData,
        course_id: formData.course_id,
        lesson_id: lesson?.id || null // Will be updated after lesson creation
      };

      await axios.post(`${API}/admin/tests`, testData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      alert('Тест успешно создан!');
      setShowTestForm(false);
      setTestFormData({
        title: '',
        description: '',
        time_limit_minutes: 15,
        passing_score: 70,
        max_attempts: 3,
        questions: []
      });
    } catch (error) {
      console.error('Failed to create test:', error);
      alert('Ошибка создания теста');
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {lesson ? 'Редактировать урок' : 'Добавить урок'}
          </h3>
          
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded-md">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Курс</label>
                <select
                  value={formData.course_id}
                  onChange={(e) => setFormData({...formData, course_id: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  required
                >
                  <option value="">Выберите курс</option>
                  {courses.map((course) => (
                    <option key={course.id} value={course.id}>
                      {course.title} ({course.level})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Тип урока</label>
                <select
                  value={formData.lesson_type}
                  onChange={(e) => setFormData({...formData, lesson_type: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="text">Текстовый</option>
                  <option value="video">Видео</option>
                  <option value="mixed">Смешанный</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Название урока</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Описание</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                rows="2"
              />
            </div>

            {(formData.lesson_type === 'video' || formData.lesson_type === 'mixed') && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">URL видео</label>
                  <input
                    type="url"
                    value={formData.video_url}
                    onChange={(e) => setFormData({...formData, video_url: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                    placeholder="https://www.youtube.com/embed/..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Длительность видео (сек)</label>
                  <input
                    type="number"
                    value={formData.video_duration}
                    onChange={(e) => setFormData({...formData, video_duration: parseInt(e.target.value) || ''})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700">Содержание урока</label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({...formData, content: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                rows="8"
                placeholder="Введите HTML содержание урока..."
                required
              />
              <p className="text-xs text-gray-500 mt-1">Поддерживается HTML разметка</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Порядок</label>
                <input
                  type="number"
                  value={formData.order}
                  onChange={(e) => setFormData({...formData, order: parseInt(e.target.value)})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  min="1"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Время изучения (мин)</label>
                <input
                  type="number"
                  value={formData.estimated_duration_minutes}
                  onChange={(e) => setFormData({...formData, estimated_duration_minutes: parseInt(e.target.value)})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  min="1"
                  required
                />
              </div>
            </div>

            {/* Test Creation Section */}
            <div className="border-t pt-6 mt-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-medium text-gray-900">Тест к уроку</h4>
                <button
                  type="button"
                  onClick={() => setShowTestForm(!showTestForm)}
                  className="px-4 py-2 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                >
                  {showTestForm ? 'Скрыть форму теста' : 'Добавить тест'}
                </button>
              </div>

              {showTestForm && (
                <div className="bg-gray-50 rounded-lg p-4 space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Название теста</label>
                      <input
                        type="text"
                        value={testFormData.title}
                        onChange={(e) => setTestFormData({...testFormData, title: e.target.value})}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                        placeholder="Например: Тест по уроку о намазе"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Время (мин)</label>
                      <input
                        type="number"
                        value={testFormData.time_limit_minutes}
                        onChange={(e) => setTestFormData({...testFormData, time_limit_minutes: parseInt(e.target.value)})}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                        min="1"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Описание теста</label>
                    <textarea
                      value={testFormData.description}
                      onChange={(e) => setTestFormData({...testFormData, description: e.target.value})}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                      rows="2"
                      placeholder="Краткое описание теста"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Проходной балл (%)</label>
                      <input
                        type="number"
                        value={testFormData.passing_score}
                        onChange={(e) => setTestFormData({...testFormData, passing_score: parseInt(e.target.value)})}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                        min="1"
                        max="100"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Макс. попыток</label>
                      <input
                        type="number"
                        value={testFormData.max_attempts}
                        onChange={(e) => setTestFormData({...testFormData, max_attempts: parseInt(e.target.value)})}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                        min="1"
                      />
                    </div>
                  </div>

                  {/* Question Creation Form */}
                  <div className="border-t pt-4">
                    <h5 className="font-medium text-gray-900 mb-3">Добавить вопрос</h5>
                    
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Текст вопроса</label>
                        <input
                          type="text"
                          value={newQuestion.question_text}
                          onChange={(e) => setNewQuestion({...newQuestion, question_text: e.target.value})}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                          placeholder="Введите текст вопроса"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">Варианты ответов</label>
                        <div className="space-y-2 mt-2">
                          {newQuestion.options.map((option, index) => (
                            <div key={index} className="flex items-center space-x-2">
                              <input
                                type="checkbox"
                                checked={option.is_correct}
                                onChange={(e) => updateQuestionOption(index, 'is_correct', e.target.checked)}
                                className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded"
                              />
                              <input
                                type="text"
                                value={option.text}
                                onChange={(e) => updateQuestionOption(index, 'text', e.target.value)}
                                className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                                placeholder={`Вариант ${index + 1}`}
                              />
                              {newQuestion.options.length > 2 && (
                                <button
                                  type="button"
                                  onClick={() => removeQuestionOption(index)}
                                  className="text-red-600 hover:text-red-800"
                                >
                                  ✕
                                </button>
                              )}
                            </div>
                          ))}
                        </div>
                        
                        <div className="flex space-x-2 mt-2">
                          <button
                            type="button"
                            onClick={addQuestionOption}
                            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                          >
                            + Добавить вариант
                          </button>
                          <button
                            type="button"
                            onClick={addQuestionToTest}
                            className="px-3 py-1 text-sm bg-teal-100 text-teal-700 rounded hover:bg-teal-200"
                          >
                            Добавить вопрос
                          </button>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">Объяснение (необязательно)</label>
                        <input
                          type="text"
                          value={newQuestion.explanation}
                          onChange={(e) => setNewQuestion({...newQuestion, explanation: e.target.value})}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                          placeholder="Объяснение правильного ответа"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Questions List */}
                  {testFormData.questions.length > 0 && (
                    <div className="border-t pt-4">
                      <h5 className="font-medium text-gray-900 mb-3">Вопросы теста ({testFormData.questions.length})</h5>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        {testFormData.questions.map((question, index) => (
                          <div key={index} className="flex items-center justify-between bg-white p-3 rounded border">
                            <div className="flex-1">
                              <p className="text-sm font-medium">{index + 1}. {question.question_text}</p>
                              <p className="text-xs text-gray-500">{question.options.length} вариантов ответа</p>
                            </div>
                            <button
                              type="button"
                              onClick={() => removeQuestionFromTest(index)}
                              className="text-red-600 hover:text-red-800 text-sm"
                            >
                              Удалить
                            </button>
                          </div>
                        ))}
                      </div>
                      
                      <button
                        type="button"
                        onClick={createTestForLesson}
                        className="mt-3 w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                      >
                        Создать тест ({testFormData.questions.length} вопросов)
                      </button>
                    </div>
                  )}
                </div>
              )}
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

// Test Management Component
export const TestManagement = () => {
  const [tests, setTests] = useState([]);
  const [courses, setCourses] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTest, setEditingTest] = useState(null);
  const [selectedCourse, setSelectedCourse] = useState('');
  const { token } = useCompleteAdmin();

  useEffect(() => {
    fetchTests();
    fetchCourses();
  }, []);

  const fetchTests = async () => {
    try {
      const response = await axios.get(`${API}/admin/tests`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTests(response.data);
    } catch (error) {
      console.error('Failed to fetch tests:', error);
    }
    setLoading(false);
  };

  const fetchCourses = async () => {
    try {
      const response = await axios.get(`${API}/admin/courses`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCourses(response.data);
    } catch (error) {
      console.error('Failed to fetch courses:', error);
    }
  };

  const handleCreateTest = () => {
    setEditingTest(null);
    setShowModal(true);
  };

  const handleEditTest = (test) => {
    setEditingTest(test);
    setShowModal(true);
  };

  const handleDeleteTest = async (testId) => {
    if (window.confirm('Вы уверены, что хотите удалить этот тест?')) {
      try {
        await axios.delete(`${API}/admin/tests/${testId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        fetchTests();
      } catch (error) {
        console.error('Failed to delete test:', error);
      }
    }
  };

  const filteredTests = selectedCourse ? 
    tests.filter(test => test.course_id === selectedCourse) : 
    tests;

  if (loading) {
    return <div className="flex justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
    </div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Управление тестами</h1>
        <button
          onClick={handleCreateTest}
          className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 flex items-center space-x-2"
        >
          <span>➕</span>
          <span>Добавить тест</span>
        </button>
      </div>

      {/* Course Filter */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Фильтр по курсу:</span>
          <select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
          >
            <option value="">Все курсы</option>
            {courses.map((course) => (
              <option key={course.id} value={course.id}>
                {course.title} ({course.level})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Tests Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Тест
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Курс/Урок
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Вопросы
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Настройки
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
            {filteredTests.map((test) => (
              <tr key={test.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{test.title}</div>
                    <div className="text-sm text-gray-500">{test.description}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div>
                    <div>{courses.find(c => c.id === test.course_id)?.title || 'Курс не найден'}</div>
                    {test.lesson_id && (
                      <div className="text-xs text-gray-500">Урок: {test.lesson_id}</div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {test.questions.length} вопросов
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div>{test.time_limit_minutes} мин</div>
                  <div>Проходной: {test.passing_score}%</div>
                  <div>Попыток: {test.max_attempts}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    test.is_published ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {test.is_published ? 'Опубликован' : 'Черновик'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => handleEditTest(test)}
                    className="text-teal-600 hover:text-teal-900 mr-3"
                  >
                    Редактировать
                  </button>
                  <button
                    onClick={() => handleDeleteTest(test.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {filteredTests.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">Тесты не найдены</p>
          </div>
        )}
      </div>

      {showModal && (
        <TestModal
          test={editingTest}
          courses={courses}
          onClose={() => setShowModal(false)}
          onSave={() => {
            setShowModal(false);
            fetchTests();
          }}
        />
      )}
    </div>
  );
};

// Test Modal Component  
const TestModal = ({ test, courses, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    title: test?.title || '',
    description: test?.description || '',
    course_id: test?.course_id || '',
    lesson_id: test?.lesson_id || '',
    time_limit_minutes: test?.time_limit_minutes || 15,
    passing_score: test?.passing_score || 70,
    max_attempts: test?.max_attempts || 3,
    order: test?.order || 1
  });
  const [questions, setQuestions] = useState(test?.questions || []);
  const [loading, setLoading] = useState(false);
  const { token } = useCompleteAdmin();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      let testData = { ...formData };
      
      if (test) {
        await axios.put(`${API}/admin/tests/${test.id}`, testData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        // Update questions separately
        // For simplicity, we'll replace all questions
        const updatedTest = { ...test, ...testData, questions };
        await axios.put(`${API}/admin/tests/${test.id}`, updatedTest, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        const response = await axios.post(`${API}/admin/tests`, testData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        // Add questions to the new test
        if (questions.length > 0) {
          const testWithQuestions = { ...response.data, questions };
          await axios.put(`${API}/admin/tests/${response.data.id}`, testWithQuestions, {
            headers: { Authorization: `Bearer ${token}` }
          });
        }
      }
      onSave();
    } catch (error) {
      console.error('Failed to save test:', error);
    }
    setLoading(false);
  };

  const addQuestion = () => {
    const newQuestion = {
      id: Date.now().toString(),
      text: '',
      question_type: 'single_choice',
      options: [
        { id: Date.now() + '-1', text: '', is_correct: false },
        { id: Date.now() + '-2', text: '', is_correct: false }
      ],
      explanation: '',
      points: 1,
      order: questions.length + 1
    };
    setQuestions([...questions, newQuestion]);
  };

  const updateQuestion = (index, field, value) => {
    const updated = [...questions];
    updated[index] = { ...updated[index], [field]: value };
    setQuestions(updated);
  };

  const removeQuestion = (index) => {
    setQuestions(questions.filter((_, i) => i !== index));
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white mb-10">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {test ? 'Редактировать тест' : 'Добавить тест'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Название теста</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Курс</label>
                <select
                  value={formData.course_id}
                  onChange={(e) => setFormData({...formData, course_id: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  required
                >
                  <option value="">Выберите курс</option>
                  {courses.map((course) => (
                    <option key={course.id} value={course.id}>
                      {course.title} ({course.level})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Описание</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                rows="2"
              />
            </div>

            {/* Test Settings */}
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Время (мин)</label>
                <input
                  type="number"
                  value={formData.time_limit_minutes}
                  onChange={(e) => setFormData({...formData, time_limit_minutes: parseInt(e.target.value)})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  min="1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Проходной балл (%)</label>
                <input
                  type="number"
                  value={formData.passing_score}
                  onChange={(e) => setFormData({...formData, passing_score: parseInt(e.target.value)})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  min="1"
                  max="100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Попыток</label>
                <input
                  type="number"
                  value={formData.max_attempts}
                  onChange={(e) => setFormData({...formData, max_attempts: parseInt(e.target.value)})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  min="1"
                />
              </div>
            </div>

            {/* Questions */}
            <div>
              <div className="flex justify-between items-center mb-4">
                <h4 className="text-md font-medium text-gray-900">Вопросы теста</h4>
                <button
                  type="button"
                  onClick={addQuestion}
                  className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                >
                  + Добавить вопрос
                </button>
              </div>

              {questions.length === 0 ? (
                <div className="text-center py-8 bg-gray-50 rounded-lg">
                  <p className="text-gray-500">Добавьте вопросы к тесту</p>
                </div>
              ) : (
                <div className="space-y-4 max-h-60 overflow-y-auto">
                  {questions.map((question, index) => (
                    <div key={question.id} className="border border-gray-200 rounded p-4">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-medium text-sm">Вопрос {index + 1}</span>
                        <button
                          type="button"
                          onClick={() => removeQuestion(index)}
                          className="text-red-600 hover:text-red-800 text-sm"
                        >
                          Удалить
                        </button>
                      </div>
                      
                      <input
                        type="text"
                        value={question.text}
                        onChange={(e) => updateQuestion(index, 'text', e.target.value)}
                        placeholder="Текст вопроса"
                        className="w-full px-3 py-2 border border-gray-300 rounded mb-2 text-sm"
                      />
                      
                      <div className="grid grid-cols-2 gap-2">
                        {question.options.map((option, optIndex) => (
                          <div key={option.id} className="flex items-center space-x-2">
                            <input
                              type="radio"
                              name={`correct-${question.id}`}
                              checked={option.is_correct}
                              onChange={() => {
                                const updatedOptions = question.options.map((opt, i) => ({
                                  ...opt,
                                  is_correct: i === optIndex
                                }));
                                updateQuestion(index, 'options', updatedOptions);
                              }}
                              className="text-teal-600"
                            />
                            <input
                              type="text"
                              value={option.text}
                              onChange={(e) => {
                                const updatedOptions = [...question.options];
                                updatedOptions[optIndex].text = e.target.value;
                                updateQuestion(index, 'options', updatedOptions);
                              }}
                              placeholder={`Вариант ${optIndex + 1}`}
                              className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t">
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

export default LessonManagement;