import React, { useState, useEffect } from 'react';
import { useCompleteAdmin } from './AdminComponents';

const DatabaseAdmin = () => {
  const { adminData, token } = useCompleteAdmin();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // States for different views
  const [dbStats, setDbStats] = useState(null);
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [tableData, setTableData] = useState(null);
  const [connectionInfo, setConnectionInfo] = useState(null);
  const [sqlQuery, setSqlQuery] = useState('');
  const [sqlResult, setSqlResult] = useState(null);
  const [supabaseInfo, setSupabaseInfo] = useState(null);
  const [tokenToTranslate, setTokenToTranslate] = useState('');
  const [tokenResult, setTokenResult] = useState(null);
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Helper function for API calls
  const apiCall = async (endpoint, options = {}) => {
    try {
      const response = await fetch(`${backendUrl}/api${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API Error on ${endpoint}:`, error);
      throw error;
    }
  };

  // Load database overview
  const loadDatabaseOverview = async () => {
    setLoading(true);
    try {
      const [statsData, tablesData, connectionData, supabaseData] = await Promise.all([
        apiCall('/admin/database/stats'),
        apiCall('/admin/database/tables'),
        apiCall('/admin/database/connection-info'),
        apiCall('/admin/database/supabase-info')
      ]);
      
      setDbStats(statsData);
      setTables(tablesData);
      setConnectionInfo(connectionData);
      setSupabaseInfo(supabaseData);
      setError('');
    } catch (error) {
      setError(`Ошибка загрузки данных: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Load table data
  const loadTableData = async (tableName, limit = 100, offset = 0) => {
    setLoading(true);
    try {
      const data = await apiCall(`/admin/database/table/${tableName}?limit=${limit}&offset=${offset}`);
      setTableData(data);
      setSelectedTable(tableName);
      setError('');
    } catch (error) {
      setError(`Ошибка загрузки таблицы ${tableName}: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Execute SQL query
  const executeSqlQuery = async () => {
    if (!sqlQuery.trim()) {
      setError('Введите SQL запрос');
      return;
    }

    setLoading(true);
    try {
      const result = await apiCall('/admin/database/query', {
        method: 'POST',
        body: JSON.stringify({ query: sqlQuery })
      });
      
      setSqlResult(result);
      setError('');
    } catch (error) {
      setError(`Ошибка выполнения запроса: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Create database backup
  const createBackup = async () => {
    setLoading(true);
    try {
      const result = await apiCall('/admin/database/backup', { method: 'POST' });
      alert(`Резервная копия создана: ${result.backup_file}\nТаблиц: ${result.tables_backed_up.length}\nЗаписей: ${result.total_records}`);
      setError('');
    } catch (error) {
      setError(`Ошибка создания резервной копии: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Translate token
  const translateToken = async () => {
    if (!tokenToTranslate.trim()) {
      setError('Введите токен для анализа');
      return;
    }

    setLoading(true);
    try {
      const result = await apiCall('/admin/database/translate-token', {
        method: 'POST',
        body: JSON.stringify({ token: tokenToTranslate })
      });
      
      setTokenResult(result);
      setError('');
    } catch (error) {
      setError(`Ошибка анализа токена: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'overview') {
      loadDatabaseOverview();
    }
  }, [activeTab]);

  // Render connection info
  const renderConnectionInfo = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Информация о подключении</h3>
      {connectionInfo && (
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="font-medium">Тип базы данных:</span>
            <span className="text-green-600">{connectionInfo.database_type}</span>
          </div>
          <div className="flex justify-between">
            <span className="font-medium">Статус подключения:</span>
            <span className="text-green-600 capitalize">{connectionInfo.connection_status}</span>
          </div>
          <div className="flex justify-between">
            <span className="font-medium">Supabase URL:</span>
            <span className="text-sm text-gray-600">{connectionInfo.supabase_url}</span>
          </div>
          <div className="flex justify-between">
            <span className="font-medium">Использование PostgreSQL:</span>
            <span className={connectionInfo.use_postgres ? "text-blue-600" : "text-gray-600"}>
              {connectionInfo.use_postgres ? "Да" : "Нет"}
            </span>
          </div>
          {adminData?.role === 'super_admin' && connectionInfo.supabase_key_preview && (
            <div className="flex justify-between">
              <span className="font-medium">Ключ Supabase:</span>
              <span className="text-xs text-gray-500 font-mono">{connectionInfo.supabase_key_preview}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );

  // Render Supabase info
  const renderSupabaseInfo = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Информация о проекте Supabase</h3>
      {supabaseInfo && (
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="font-medium">URL проекта:</span>
            <span className="text-sm text-blue-600 break-all">{supabaseInfo.project_url}</span>
          </div>
          
          {adminData?.role === 'super_admin' && (
            <>
              {supabaseInfo.project_id && (
                <div className="flex justify-between">
                  <span className="font-medium">ID проекта:</span>
                  <span className="text-sm font-mono text-gray-600">{supabaseInfo.project_id}</span>
                </div>
              )}
              
              {supabaseInfo.dashboard_url && (
                <div className="flex justify-between">
                  <span className="font-medium">Ссылка на дашборд:</span>
                  <a 
                    href={supabaseInfo.dashboard_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-sm underline"
                  >
                    Открыть дашборд Supabase
                  </a>
                </div>
              )}
              
              {supabaseInfo.key_preview && (
                <div className="flex justify-between">
                  <span className="font-medium">Anon Key:</span>
                  <span className="text-xs text-gray-500 font-mono">{supabaseInfo.key_preview}</span>
                </div>
              )}
            </>
          )}
          
          <div className="flex justify-between">
            <span className="font-medium">Режим подключения:</span>
            <span className={supabaseInfo.use_postgres ? "text-blue-600" : "text-green-600"}>
              {supabaseInfo.use_postgres ? "PostgreSQL прямое" : "Supabase API"}
            </span>
          </div>
          
          <div className="border-t pt-3">
            <span className="font-medium block mb-2">Доступные клиенты:</span>
            <div className="flex gap-4">
              <span className={`px-2 py-1 rounded text-sm ${supabaseInfo.clients_available.supabase ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                Supabase: {supabaseInfo.clients_available.supabase ? 'Доступен' : 'Недоступен'}
              </span>
              <span className={`px-2 py-1 rounded text-sm ${supabaseInfo.clients_available.postgres ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                PostgreSQL: {supabaseInfo.clients_available.postgres ? 'Доступен' : 'Недоступен'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  // Render database statistics
  const renderDatabaseStats = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Статистика базы данных</h3>
        <button
          onClick={createBackup}
          disabled={loading}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
        >
          Создать резервную копию
        </button>
      </div>
      
      {dbStats && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {Object.entries(dbStats.stats).map(([key, data]) => (
            <div key={key} className="bg-gray-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{data.count}</div>
              <div className="text-sm text-gray-600">{data.name}</div>
            </div>
          ))}
        </div>
      )}
      
      {dbStats && (
        <div className="mt-4 text-sm text-gray-500">
          Последнее обновление: {new Date(dbStats.last_updated).toLocaleString('ru-RU')}
        </div>
      )}
    </div>
  );

  // Render tables list
  const renderTablesList = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Таблицы базы данных</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full table-auto">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-4 py-2 text-left">Название таблицы</th>
              <th className="px-4 py-2 text-left">Тип</th>
              <th className="px-4 py-2 text-left">Записей</th>
              <th className="px-4 py-2 text-left">Действия</th>
            </tr>
          </thead>
          <tbody>
            {tables.map((table) => (
              <tr key={table.name} className="border-t hover:bg-gray-50">
                <td className="px-4 py-2 font-medium">{table.name}</td>
                <td className="px-4 py-2 text-gray-600">{table.type}</td>
                <td className="px-4 py-2 text-blue-600">{table.record_count}</td>
                <td className="px-4 py-2">
                  <button
                    onClick={() => {
                      setActiveTab('table-data');
                      loadTableData(table.name);
                    }}
                    className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                  >
                    Просмотр
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  // Render table data
  const renderTableData = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">
          Данные таблицы: {selectedTable}
        </h3>
        <button
          onClick={() => setActiveTab('overview')}
          className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        >
          Назад к обзору
        </button>
      </div>
      
      {tableData && (
        <>
          <div className="mb-4 text-sm text-gray-600">
            Всего записей: {tableData.total_count} | 
            Страница: {tableData.current_page} | 
            На странице: {tableData.per_page}
          </div>
          
          {/* Table structure */}
          <div className="mb-6">
            <h4 className="font-semibold mb-2">Структура таблицы:</h4>
            <div className="bg-gray-50 p-3 rounded text-sm">
              {tableData.structure.map((col, index) => (
                <div key={index} className="mb-1">
                  <span className="font-mono font-medium">{col.column_name}</span>
                  <span className="text-gray-600 ml-2">({col.data_type})</span>
                  {col.is_nullable === 'NO' && <span className="text-red-500 ml-1">NOT NULL</span>}
                </div>
              ))}
            </div>
          </div>
          
          {/* Table data */}
          <div className="overflow-x-auto">
            <table className="min-w-full table-auto text-sm">
              <thead>
                <tr className="bg-gray-50">
                  {tableData.structure.map((col) => (
                    <th key={col.column_name} className="px-3 py-2 text-left font-medium">
                      {col.column_name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tableData.records.map((record, index) => (
                  <tr key={index} className="border-t hover:bg-gray-50">
                    {tableData.structure.map((col) => (
                      <td key={col.column_name} className="px-3 py-2 max-w-xs truncate">
                        {typeof record[col.column_name] === 'object' 
                          ? JSON.stringify(record[col.column_name])
                          : String(record[col.column_name] || '')
                        }
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );

  // Render SQL console
  const renderSqlConsole = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">SQL Консоль</h3>
      
      <div className="mb-4">
        <textarea
          value={sqlQuery}
          onChange={(e) => setSqlQuery(e.target.value)}
          placeholder="Введите SQL запрос..."
          className="w-full h-32 p-3 border rounded-lg font-mono text-sm"
        />
      </div>
      
      <div className="flex gap-2 mb-4">
        <button
          onClick={executeSqlQuery}
          disabled={loading || !sqlQuery.trim()}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
        >
          Выполнить запрос
        </button>
        <button
          onClick={() => {
            setSqlQuery('');
            setSqlResult(null);
          }}
          className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        >
          Очистить
        </button>
      </div>
      
      {adminData?.role !== 'super_admin' && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-sm">
          ⚠️ Обычные администраторы могут выполнять только SELECT запросы
        </div>
      )}
      
      {sqlResult && (
        <div className="border rounded-lg p-4">
          <h4 className="font-semibold mb-2">
            Результат {sqlResult.success ? '✅' : '❌'}
            {sqlResult.row_count && ` (${sqlResult.row_count} строк)`}
          </h4>
          
          {sqlResult.success ? (
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto text-sm">
                <tbody>
                  {sqlResult.result.map((row, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : ''}>
                      {Object.entries(row).map(([key, value]) => (
                        <td key={key} className="px-3 py-2 border-r">
                          <div className="font-medium text-xs text-gray-500">{key}:</div>
                          <div className="max-w-xs truncate">
                            {typeof value === 'object' ? JSON.stringify(value) : String(value || '')}
                          </div>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-red-600 bg-red-50 p-3 rounded">
              <strong>Ошибка:</strong> {sqlResult.error}
            </div>
          )}
        </div>
      )}
    </div>
  );

  if (!adminData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-gray-500">Требуется авторизация администратора</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Администрирование базы данных</h1>
        <p className="text-gray-600">Управление базой данных Supabase</p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          {error}
        </div>
      )}

      {/* Navigation tabs */}
      <div className="mb-6 border-b">
        <nav className="flex space-x-8">
          {[
            { id: 'overview', label: 'Обзор', icon: '📊' },
            { id: 'table-data', label: 'Данные таблиц', icon: '📋' },
            { id: 'sql-console', label: 'SQL Консоль', icon: '💻' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      )}

      {/* Tab content */}
      {!loading && (
        <div className="space-y-6">
          {activeTab === 'overview' && (
            <>
              {renderConnectionInfo()}
              {renderDatabaseStats()}
              {renderTablesList()}
            </>
          )}
          
          {activeTab === 'table-data' && renderTableData()}
          {activeTab === 'sql-console' && renderSqlConsole()}
        </div>
      )}
    </div>
  );
};

export default DatabaseAdmin;