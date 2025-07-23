from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models import *

# Import both clients
try:
    from postgres_client import postgres_client
    POSTGRES_AVAILABLE = True
    print("✅ PostgreSQL client доступен")
except ImportError:
    POSTGRES_AVAILABLE = False
    print("❌ PostgreSQL client недоступен")

try:
    from supabase_client import supabase_client
    SUPABASE_AVAILABLE = True
    print("✅ Supabase client доступен")
except ImportError:
    SUPABASE_AVAILABLE = False
    print("❌ Supabase client недоступен")

import shutil
import aiofiles
import json
import csv
import random
import io
import re
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create the main app
app = FastAPI(title="Уроки Ислама API", version="2.0.0")

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "uroki-islama-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database client selection
USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() == "true"

if USE_POSTGRES and POSTGRES_AVAILABLE:
    db_client = postgres_client
    print("🔗 Используется прямое PostgreSQL подключение")
elif SUPABASE_AVAILABLE:
    db_client = supabase_client
    print("🔗 Используется Supabase API")
else:
    raise Exception("Ни один клиент базы данных не доступен!")

# Utility functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Simple password verification for development
def verify_simple_password(username: str, password: str) -> bool:
    """Temporary simple password check until proper auth is implemented"""
    simple_passwords = {
        "admin": "admin123",
        "miftahulum": "197724"
    }
    return simple_passwords.get(username) == password

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    admin = await db_client.find_one("admin_users", {"username": username})
    if admin is None:
        raise credentials_exception
    return admin

async def require_admin_role(current_admin: dict = Depends(get_current_admin)):
    if current_admin["role"] not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_admin

# File upload utilities
async def save_uploaded_file(upload_file: UploadFile, folder: str = "general") -> str:
    """Save uploaded file and return the URL"""
    file_extension = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    folder_path = UPLOAD_DIR / folder
    folder_path.mkdir(exist_ok=True)
    file_path = folder_path / unique_filename
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await upload_file.read()
        await f.write(content)
    
    return f"/uploads/{folder}/{unique_filename}"

def convert_to_embed_url(url: str) -> str:
    """Convert YouTube URL to embed format"""
    if not url:
        return url
    
    # Handle different YouTube URL formats
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}"
    
    return url

# ====================================================================
# ROOT ENDPOINTS
# ====================================================================

@api_router.get("/")
async def root():
    client_type = "PostgreSQL" if USE_POSTGRES and POSTGRES_AVAILABLE else "Supabase"
    return {"message": f"Hello World with {client_type}"}

# Database Administration Routes
@api_router.get("/admin/database/tables", response_model=List[Dict[str, Any]])
async def get_database_tables(current_admin: dict = Depends(get_current_admin)):
    """Получить список всех таблиц в базе данных"""
    try:
        if USE_POSTGRES and POSTGRES_AVAILABLE:
            # Для PostgreSQL получаем через information_schema
            query = """
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
            """
            result = await db_client.execute_raw_sql(query)
            tables = []
            for row in result:
                table_name = row.get('table_name')
                # Получаем количество записей в каждой таблице
                count_query = f"SELECT COUNT(*) as count FROM {table_name};"
                count_result = await db_client.execute_raw_sql(count_query)
                count = count_result[0]['count'] if count_result else 0
                
                tables.append({
                    "name": table_name,
                    "type": row.get('table_type', 'BASE TABLE'),
                    "record_count": count
                })
            return tables
        else:
            # Для Supabase API получаем список известных таблиц
            known_tables = [
                "courses", "lessons", "tests", "test_questions", "test_attempts",
                "students", "admin_users", "teachers", "team_members",
                "qa_questions", "qa_categories", "applications", "status_checks"
            ]
            tables = []
            for table_name in known_tables:
                try:
                    count = await db_client.count_records(table_name)
                    tables.append({
                        "name": table_name,
                        "type": "BASE TABLE",
                        "record_count": count
                    })
                except Exception as e:
                    # Таблица может не существовать
                    continue
            return tables
    except Exception as e:
        logger.error(f"Error getting database tables: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@api_router.get("/admin/database/table/{table_name}", response_model=Dict[str, Any])
async def get_table_data(
    table_name: str, 
    limit: int = 100, 
    offset: int = 0,
    current_admin: dict = Depends(get_current_admin)
):
    """Получить данные из конкретной таблицы"""
    try:
        # Получаем данные из таблицы
        if USE_POSTGRES and POSTGRES_AVAILABLE:
            query = f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset};"
            records = await db_client.execute_raw_sql(query)
            
            # Получаем общее количество записей
            count_query = f"SELECT COUNT(*) as count FROM {table_name};"
            count_result = await db_client.execute_raw_sql(count_query)
            total_count = count_result[0]['count'] if count_result else 0
            
            # Получаем структуру таблицы
            structure_query = f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' AND table_schema = 'public'
            ORDER BY ordinal_position;
            """
            structure = await db_client.execute_raw_sql(structure_query)
        else:
            # Для Supabase API
            records = await db_client.get_records(table_name, limit=limit)
            # Пропускаем offset записей
            if offset > 0:
                all_records = await db_client.get_records(table_name)
                records = all_records[offset:offset+limit] if offset < len(all_records) else []
            
            total_count = await db_client.count_records(table_name)
            
            # Получаем структуру из первой записи (приблизительно)
            structure = []
            if records:
                for key, value in records[0].items():
                    data_type = type(value).__name__
                    structure.append({
                        "column_name": key,
                        "data_type": data_type,
                        "is_nullable": "YES",
                        "column_default": None
                    })
        
        return {
            "table_name": table_name,
            "records": records,
            "total_count": total_count,
            "current_page": offset // limit + 1 if limit > 0 else 1,
            "per_page": limit,
            "structure": structure
        }
    except Exception as e:
        logger.error(f"Error getting table data for {table_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@api_router.post("/admin/database/query")
async def execute_sql_query(
    query_data: Dict[str, str],
    current_admin: dict = Depends(require_admin_role)
):
    """Выполнить произвольный SQL запрос (только для супер-админов)"""
    try:
        query = query_data.get("query", "").strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Базовая проверка безопасности
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE"]
        query_upper = query.upper()
        
        # Разрешаем только SELECT запросы для обычных админов
        if current_admin.get("role") != UserRole.SUPER_ADMIN:
            if not query_upper.startswith("SELECT"):
                raise HTTPException(
                    status_code=403, 
                    detail="Only SELECT queries are allowed for regular admins"
                )
        
        # Дополнительная проверка для опасных операций
        for keyword in dangerous_keywords:
            if keyword in query_upper and not query_upper.startswith("SELECT"):
                if current_admin.get("role") != UserRole.SUPER_ADMIN:
                    raise HTTPException(
                        status_code=403, 
                        detail=f"'{keyword}' operations require super admin privileges"
                    )
        
        result = await db_client.execute_raw_sql(query)
        
        return {
            "success": True,
            "query": query,
            "result": result,
            "row_count": len(result) if result else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing SQL query: {str(e)}")
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "result": []
        }

@api_router.get("/admin/database/stats")
async def get_database_stats(current_admin: dict = Depends(get_current_admin)):
    """Получить общую статистику базы данных"""
    try:
        stats = {}
        
        # Основные таблицы для статистики
        main_tables = {
            "students": "Студенты",
            "courses": "Курсы", 
            "lessons": "Уроки",
            "tests": "Тесты",
            "test_attempts": "Попытки тестов",
            "admin_users": "Администраторы",
            "team_members": "Команда",
            "qa_questions": "Вопросы Q&A"
        }
        
        for table_name, display_name in main_tables.items():
            try:
                count = await db_client.count_records(table_name)
                stats[table_name] = {
                    "name": display_name,
                    "count": count
                }
            except Exception:
                stats[table_name] = {
                    "name": display_name,
                    "count": 0
                }
        
        # Дополнительная статистика
        try:
            # Активные студенты
            active_students = await db_client.count_records("students", {"is_active": True})
            stats["active_students"] = {
                "name": "Активные студенты",
                "count": active_students
            }
            
            # Опубликованные курсы
            published_courses = await db_client.count_records("courses", {"status": CourseStatus.PUBLISHED})
            stats["published_courses"] = {
                "name": "Опубликованные курсы", 
                "count": published_courses
            }
        except Exception:
            pass
        
        return {
            "database_type": "PostgreSQL via Supabase" if USE_POSTGRES else "Supabase API",
            "connection_status": "connected",
            "stats": stats,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@api_router.post("/admin/database/backup")
async def create_database_backup(current_admin: dict = Depends(require_admin_role)):
    """Создать резервную копию важных данных"""
    try:
        backup_data = {}
        
        # Список таблиц для резервного копирования
        backup_tables = [
            "courses", "lessons", "tests", "test_questions",
            "students", "admin_users", "team_members", "qa_questions"
        ]
        
        for table_name in backup_tables:
            try:
                records = await db_client.get_records(table_name, limit=10000)
                backup_data[table_name] = records
            except Exception as e:
                logger.warning(f"Could not backup table {table_name}: {str(e)}")
        
        # Создаем файл резервной копии
        backup_filename = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = UPLOAD_DIR / backup_filename
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
        
        return {
            "success": True,
            "backup_file": backup_filename,
            "backup_path": str(backup_path),
            "tables_backed_up": list(backup_data.keys()),
            "total_records": sum(len(records) for records in backup_data.values()),
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating database backup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Backup error: {str(e)}")

@api_router.get("/admin/database/connection-info")
async def get_connection_info(current_admin: dict = Depends(get_current_admin)):
    """Получить информацию о подключении к базе данных"""
    try:
        connection_info = {
            "database_type": "PostgreSQL via Supabase" if USE_POSTGRES else "Supabase API",
            "use_postgres": USE_POSTGRES,
            "supabase_url": os.getenv("SUPABASE_URL", "Not set"),
            "has_supabase_key": bool(os.getenv("SUPABASE_ANON_KEY")),
            "has_database_url": bool(os.getenv("DATABASE_URL")),
            "connection_status": "connected",
            "clients_available": {
                "postgres": POSTGRES_AVAILABLE,
                "supabase": SUPABASE_AVAILABLE
            }
        }
        
        # Скрываем чувствительную информацию от обычных админов
        if current_admin.get("role") == UserRole.SUPER_ADMIN:
            connection_info["supabase_key_preview"] = os.getenv("SUPABASE_ANON_KEY", "")[:20] + "..."
            connection_info["database_url_preview"] = os.getenv("DATABASE_URL", "")[:50] + "..."
        
        return connection_info
        
    except Exception as e:
        logger.error(f"Error getting connection info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Connection error: {str(e)}")

@api_router.put("/admin/database/record/{table_name}/{record_id}")
async def update_database_record(
    table_name: str,
    record_id: str,
    update_data: Dict[str, Any],
    current_admin: dict = Depends(require_admin_role)
):
    """Обновить запись в базе данных"""
    try:
        # Определяем поле ID для таблицы
        id_field = "id"  # По умолчанию используем id
        
        # Специальные случаи для некоторых таблиц
        if table_name == "admin_users":
            # Для админов можем искать по email или username
            existing_record = await db_client.get_record(table_name, "id", record_id)
            if not existing_record:
                existing_record = await db_client.get_record(table_name, "email", record_id)
                if existing_record:
                    id_field = "email"
                else:
                    existing_record = await db_client.get_record(table_name, "username", record_id)
                    if existing_record:
                        id_field = "username"
        
        # Обновляем запись
        updated_record = await db_client.update_record(table_name, id_field, record_id, update_data)
        
        if not updated_record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        return {
            "success": True,
            "updated_record": updated_record,
            "table_name": table_name,
            "record_id": record_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating record in {table_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")

@api_router.delete("/admin/database/record/{table_name}/{record_id}")
async def delete_database_record(
    table_name: str,
    record_id: str,
    current_admin: dict = Depends(require_admin_role)
):
    """Удалить запись из базы данных"""
    try:
        # Защита от удаления критически важных записей
        if table_name == "admin_users":
            # Не позволяем удалить последнего админа
            admin_count = await db_client.count_records("admin_users")
            if admin_count <= 1:
                raise HTTPException(
                    status_code=403,
                    detail="Cannot delete the last admin user"
                )
            
            # Не позволяем админу удалить самого себя
            if current_admin.get("id") == record_id or current_admin.get("email") == record_id:
                raise HTTPException(
                    status_code=403,
                    detail="Cannot delete your own admin account"
                )
        
        success = await db_client.delete_record(table_name, "id", record_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Record not found")
        
        return {
            "success": True,
            "message": f"Record {record_id} deleted from {table_name}",
            "table_name": table_name,
            "record_id": record_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting record from {table_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")

@api_router.post("/admin/database/record/{table_name}")
async def create_database_record(
    table_name: str,
    record_data: Dict[str, Any],
    current_admin: dict = Depends(require_admin_role)
):
    """Создать новую запись в базе данных"""
    try:
        # Добавляем обязательные поля если их нет
        if "id" not in record_data:
            record_data["id"] = str(uuid.uuid4())
        
        if "created_at" not in record_data:
            record_data["created_at"] = datetime.utcnow().isoformat()
        
        # Создаем запись
        created_record = await db_client.create_record(table_name, record_data)
        
        return {
            "success": True,
            "created_record": created_record,
            "table_name": table_name
        }
        
    except Exception as e:
        logger.error(f"Error creating record in {table_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Create error: {str(e)}")

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    created_status = await db_client.create_record("status_checks", status_obj.dict())
    return StatusCheck(**created_status)

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db_client.get_records("status_checks", limit=1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# ====================================================================
# AUTHENTICATION ENDPOINTS
# ====================================================================

@api_router.post("/admin/login", response_model=Token)
async def admin_login(admin_data: AdminLogin):
    admin = await db_client.find_one("admin_users", {"username": admin_data.username})
    if not admin or not verify_simple_password(admin_data.username, admin_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    await db_client.update_record(
        "admin_users", "username", admin_data.username,
        {"last_login": datetime.utcnow().isoformat()}
    )
    
    access_token = create_access_token(data={"sub": admin["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/auth/login")
async def unified_login(login_data: dict):
    email = login_data.get("email")
    password = login_data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    # First check if it's an admin by email
    admin = await db_client.find_one("admin_users", {"email": email})
    if admin:
        # Use username from admin record for password verification
        if verify_simple_password(admin["username"], password):
            # Update last login
            await db_client.update_record(
                "admin_users", "email", email,
                {"last_login": datetime.utcnow().isoformat()}
            )
            
            access_token = create_access_token(data={"sub": admin["username"], "type": "admin"})
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_type": "admin",
                "user": {
                    "id": admin["id"],
                    "email": admin["email"],
                    "name": admin["full_name"],
                    "role": admin["role"]
                }
            }
    
    # If not admin, check regular users
    student = await db_client.find_one("students", {"email": email})
    if not student:
        # Create new student record
        student_data = {
            "id": str(uuid.uuid4()),
            "name": email.split("@")[0].title(),
            "email": email,
            "total_score": 0,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "completed_courses": [],
            "current_level": CourseLevel.LEVEL_1
        }
        student = await db_client.create_record("students", student_data)
    else:
        # Update last activity
        await db_client.update_record(
            "students", "email", email,
            {"last_activity": datetime.utcnow().isoformat()}
        )
    
    access_token = create_access_token(data={"sub": email, "type": "user"})
    return {
        "access_token": access_token,
        "token_type": "bearer", 
        "user_type": "user",
        "user": {
            "id": student["id"],
            "email": student["email"],
            "name": student["name"],
            "total_score": student.get("total_score", 0)
        }
    }

@api_router.get("/admin/me", response_model=AdminUser)
async def get_current_admin_info(current_admin: dict = Depends(get_current_admin)):
    return AdminUser(**current_admin)

# ====================================================================
# DASHBOARD ENDPOINTS
# ====================================================================

@api_router.get("/admin/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(current_admin: dict = Depends(get_current_admin)):
    total_students = await db_client.count_records("students")
    total_courses = await db_client.count_records("courses")
    total_lessons = await db_client.count_records("lessons")
    total_tests = await db_client.count_records("tests")
    total_teachers = await db_client.count_records("teachers")
    active_students = await db_client.count_records("students", {"is_active": True})
    pending_applications = await db_client.count_records("applications", {"status": "pending"})
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    completed_tests_today = await db_client.count_records("test_attempts", {
        "completed_at": {"$gte": today.isoformat()}
    })
    
    return DashboardStats(
        total_students=total_students,
        total_courses=total_courses,
        total_lessons=total_lessons,
        total_tests=total_tests,
        total_teachers=total_teachers,
        active_students=active_students,
        pending_applications=pending_applications,
        completed_tests_today=completed_tests_today
    )

# ====================================================================
# COURSE MANAGEMENT ENDPOINTS
# ====================================================================

@api_router.get("/courses", response_model=List[Course])
async def get_public_courses():
    """Public endpoint for published courses"""
    courses = await db_client.get_records(
        "courses", 
        filters={"status": "published"},
        order_by="order"
    )
    return [Course(**course) for course in courses]

@api_router.get("/admin/courses", response_model=List[Course])
async def get_admin_courses(current_admin: dict = Depends(get_current_admin)):
    courses = await db_client.get_records("courses", order_by="order")
    return [Course(**course) for course in courses]

@api_router.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: str):
    course = await db_client.get_record("courses", "id", course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return Course(**course)

@api_router.post("/admin/courses", response_model=Course)
async def create_course(course_data: CourseCreate, current_admin: dict = Depends(get_current_admin)):
    course_dict = course_data.dict()
    course_obj = Course(**course_dict)
    created_course = await db_client.create_record("courses", course_obj.dict())
    return Course(**created_course)

@api_router.put("/admin/courses/{course_id}", response_model=Course)
async def update_course(course_id: str, course_data: CourseUpdate, current_admin: dict = Depends(get_current_admin)):
    course = await db_client.get_record("courses", "id", course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    update_data = {k: v for k, v in course_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_course = await db_client.update_record("courses", "id", course_id, update_data)
    return Course(**updated_course)

@api_router.delete("/admin/courses/{course_id}")
async def delete_course(course_id: str, current_admin: dict = Depends(require_admin_role)):
    course = await db_client.get_record("courses", "id", course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    success = await db_client.delete_record("courses", "id", course_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete course")
    return {"message": "Course deleted successfully"}

# ====================================================================
# LESSON MANAGEMENT ENDPOINTS  
# ====================================================================

@api_router.get("/courses/{course_id}/lessons", response_model=List[Lesson])
async def get_course_lessons(course_id: str):
    lessons = await db_client.get_records(
        "lessons", 
        filters={"course_id": course_id, "is_published": True},
        order_by="order"
    )
    return [Lesson(**lesson) for lesson in lessons]

@api_router.get("/admin/courses/{course_id}/lessons", response_model=List[Lesson])
async def get_admin_course_lessons(course_id: str, current_admin: dict = Depends(get_current_admin)):
    lessons = await db_client.get_records(
        "lessons", 
        filters={"course_id": course_id},
        order_by="order"
    )
    return [Lesson(**lesson) for lesson in lessons]

@api_router.get("/lessons/{lesson_id}", response_model=Lesson)
async def get_lesson(lesson_id: str):
    lesson = await db_client.get_record("lessons", "id", lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return Lesson(**lesson)

@api_router.get("/admin/lessons/{lesson_id}", response_model=Lesson)
async def get_admin_lesson(lesson_id: str, current_admin: dict = Depends(get_current_admin)):
    lesson = await db_client.get_record("lessons", "id", lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return Lesson(**lesson)

@api_router.post("/admin/lessons", response_model=Lesson)
async def create_lesson(lesson_data: LessonCreate, current_admin: dict = Depends(get_current_admin)):
    lesson_dict = lesson_data.dict()
    
    # Convert YouTube URL to embed format
    if lesson_dict.get("video_url"):
        lesson_dict["video_url"] = convert_to_embed_url(lesson_dict["video_url"])
    
    lesson_obj = Lesson(**lesson_dict)
    created_lesson = await db_client.create_record("lessons", lesson_obj.dict())
    return Lesson(**created_lesson)

@api_router.put("/admin/lessons/{lesson_id}", response_model=Lesson)
async def update_lesson(lesson_id: str, lesson_data: LessonUpdate, current_admin: dict = Depends(get_current_admin)):
    lesson = await db_client.get_record("lessons", "id", lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    update_data = {k: v for k, v in lesson_data.dict().items() if v is not None}
    
    # Convert YouTube URL to embed format
    if update_data.get("video_url"):
        update_data["video_url"] = convert_to_embed_url(update_data["video_url"])
    
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_lesson = await db_client.update_record("lessons", "id", lesson_id, update_data)
    return Lesson(**updated_lesson)

@api_router.delete("/admin/lessons/{lesson_id}")
async def delete_lesson(lesson_id: str, current_admin: dict = Depends(require_admin_role)):
    lesson = await db_client.get_record("lessons", "id", lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    success = await db_client.delete_record("lessons", "id", lesson_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete lesson")
    return {"message": "Lesson deleted successfully"}

# ====================================================================
# TEAM MANAGEMENT ENDPOINTS
# ====================================================================

@api_router.get("/team", response_model=List[TeamMember])
async def get_team_members():
    """Get all active team members for public page"""
    members = await db_client.get_records(
        "team_members", 
        filters={"is_active": True},
        order_by="order"
    )
    return [TeamMember(**member) for member in members]

@api_router.get("/admin/team", response_model=List[TeamMember])
async def get_admin_team_members(current_admin: dict = Depends(get_current_admin)):
    """Get all team members for admin"""
    members = await db_client.get_records("team_members", order_by="order")
    return [TeamMember(**member) for member in members]

@api_router.post("/admin/team", response_model=TeamMember)
async def create_team_member(member_data: TeamMemberCreate, current_admin: dict = Depends(get_current_admin)):
    """Create new team member"""
    member_dict = member_data.dict()
    member_obj = TeamMember(**member_dict)
    created_member = await db_client.create_record("team_members", member_obj.dict())
    return TeamMember(**created_member)

@api_router.put("/admin/team/{member_id}", response_model=TeamMember)
async def update_team_member(
    member_id: str, 
    member_data: TeamMemberUpdate, 
    current_admin: dict = Depends(get_current_admin)
):
    """Update team member"""
    member = await db_client.get_record("team_members", "id", member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    update_data = {k: v for k, v in member_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_member = await db_client.update_record("team_members", "id", member_id, update_data)
    return TeamMember(**updated_member)

@api_router.delete("/admin/team/{member_id}")
async def delete_team_member(member_id: str, current_admin: dict = Depends(require_admin_role)):
    """Delete team member"""
    success = await db_client.delete_record("team_members", "id", member_id)
    if not success:
        raise HTTPException(status_code=404, detail="Team member not found")
    return {"message": "Team member deleted successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
        "http://localhost:3000",
        "https://*.replit.dev", 
        "https://*.replit.co",
        "https://*.replit.app",
        "https://*.repl.co",
        "*"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize default data and ensure quality content"""
    client_type = "PostgreSQL" if USE_POSTGRES and POSTGRES_AVAILABLE else "Supabase"
    logger.info(f"Starting application with {client_type} integration...")
    
    # Check if admins exist
    try:
        admin_count = await db_client.count_records("admin_users")
        logger.info(f"Found {admin_count} admin users in database")
        
        # Check existing team members
        team_count = await db_client.count_records("team_members")
        logger.info(f"Found {team_count} team members in database")
        
        # Check courses
        course_count = await db_client.count_records("courses", {"status": "published"})
        logger.info(f"Found {course_count} published courses in database")
        
        # Run autostart to ensure quality data (only for Supabase)
        if not USE_POSTGRES:
            logger.info("Running Supabase autostart to ensure quality data...")
            try:
                import subprocess
                import sys
                result = subprocess.run([
                    sys.executable, 
                    str(ROOT_DIR / "autostart_supabase.py")
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    logger.info("✅ Supabase autostart completed successfully")
                else:
                    logger.warning(f"⚠️ Supabase autostart issues: {result.stderr}")
            except Exception as e:
                logger.warning(f"⚠️ Could not run autostart: {e}")
        
        logger.info(f"Application startup completed with {client_type} integration")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")
    if USE_POSTGRES and POSTGRES_AVAILABLE:
        await postgres_client.close_pool()