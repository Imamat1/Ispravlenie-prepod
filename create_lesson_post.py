#!/usr/bin/env python3
import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://8bc1a919-b952-4667-94e5-4aadb2ce50b3.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def get_admin_token():
    """Get admin authentication token"""
    login_url = f"{BASE_URL}/admin/login"
    login_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to login: {response.text}")

def convert_youtube_to_embed(url):
    """Convert YouTube URL to embed format"""
    if not url:
        return ''
    
    # If it's already an embed URL, return as is
    if 'youtube.com/embed/' in url:
        return url
    
    # Extract video ID from various YouTube URL formats
    import re
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/\n\s]+/\S+/|(?:v|e(?:mbed)?)/|\S*?[?&]v=)|youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"
    
    return url

def create_lesson():
    """Create lesson about post (fasting)"""
    token = get_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Course ID for "Пост" course
    course_id = "02d1ddee-a2cb-4720-b962-41dc54c7a997"
    
    # YouTube video URL
    youtube_url = "https://youtu.be/mIQeYegFeYU?si=4I7dxUwajAKr2o7k"
    embed_url = convert_youtube_to_embed(youtube_url)
    
    # Lesson content based on provided material
    lesson_content = """
    <div class="lesson-content">
        <h2>Конспект по главе "Китабус-сиям" (Глава про пост)</h2>
        
        <h3>1. Введение в пост</h3>
        <p>Глава посвящена вопросам поста: кто обязан соблюдать, что необходимо, от чего воздерживаться и т.д.</p>
        
        <h3>2. Условия обязательности поста (4 основных условия)</h3>
        <p>Для того чтобы человек был обязан соблюдать пост, должны быть выполнены следующие условия:</p>
        
        <h4>• Ислам</h4>
        <p>— человек должен быть мусульманином. Немусульманин пост не предписывается, сначала нужно принять ислам.</p>
        
        <h4>• Совершеннолетие (зрелость)</h4>
        <p>— достижение возраста половой зрелости (мужчина или женщина) до наступления календаря.</p>
        
        <h4>• Разумность</h4>
        <p>— человек должен быть в здравом уме, пост не обязателен для душевнобольных.</p>
        
        <h4>• Физическая способность</h4>
        <p>— человек должен быть здоров и физически способен соблюдать пост.</p>
        
        <h3>Дополнительно для женщин:</h3>
        
        <h4>• Отсутствие состояния хайда (менструации) или нифаса (послеродового кровотечения)</h4>
        <p>В эти периоды женщинам пост не обязателен, но пропущенные дни нужно возместить позже.</p>
    </div>
    """
    
    # Lesson data
    lesson_data = {
        "course_id": course_id,
        "title": "Китабус-сиям (Глава про пост)",
        "description": "Изучение основных положений о посте в исламе: условия обязательности, правила соблюдения и особенности для разных категорий людей",
        "content": lesson_content,
        "lesson_type": "mixed",  # Contains both video and text
        "video_url": embed_url,
        "video_duration": "344",  # Duration from the form
        "order": 1,
        "estimated_duration_minutes": 60,
        "is_published": True
    }
    
    # Create lesson
    create_url = f"{BASE_URL}/admin/lessons"
    response = requests.post(create_url, headers=headers, json=lesson_data)
    
    if response.status_code == 200:
        lesson = response.json()
        print(f"✅ Урок успешно создан!")
        print(f"ID урока: {lesson['id']}")
        print(f"Название: {lesson['title']}")
        print(f"Курс ID: {lesson['course_id']}")
        print(f"Видео URL: {lesson['video_url']}")
        return lesson
    else:
        print(f"❌ Ошибка создания урока: {response.text}")
        return None

def create_test_for_lesson(lesson_id):
    """Create test with 30 questions for the lesson"""
    token = get_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Sample test questions about fasting
    questions = [
        {
            "question_text": "Сколько основных условий обязательности поста?",
            "question_type": "single_choice",
            "options": [
                {"text": "3", "is_correct": False},
                {"text": "4", "is_correct": True},
                {"text": "5", "is_correct": False},
                {"text": "6", "is_correct": False}
            ],
            "explanation": "Есть 4 основных условия: ислам, совершеннолетие, разумность, физическая способность",
            "points": 1
        },
        {
            "question_text": "Что является первым условием обязательности поста?",
            "question_type": "single_choice",
            "options": [
                {"text": "Ислам", "is_correct": True},
                {"text": "Совершеннолетие", "is_correct": False},
                {"text": "Разумность", "is_correct": False},
                {"text": "Здоровье", "is_correct": False}
            ],
            "explanation": "Человек должен быть мусульманином",
            "points": 1
        },
        {
            "question_text": "Обязан ли соблюдать пост душевнобольной?",
            "question_type": "single_choice",
            "options": [
                {"text": "Да, обязан", "is_correct": False},
                {"text": "Нет, не обязан", "is_correct": True},
                {"text": "Только в определенные дни", "is_correct": False},
                {"text": "По желанию", "is_correct": False}
            ],
            "explanation": "Разумность - одно из условий обязательности поста",
            "points": 1
        },
        {
            "question_text": "Должна ли женщина поститься во время менструации?",
            "question_type": "single_choice",
            "options": [
                {"text": "Да, должна", "is_correct": False},
                {"text": "Нет, но должна возместить позже", "is_correct": True},
                {"text": "Нет, и возмещать не нужно", "is_correct": False},
                {"text": "По желанию", "is_correct": False}
            ],
            "explanation": "В период хайда пост не обязателен, но пропущенные дни нужно возместить",
            "points": 1
        },
        {
            "question_text": "Что означает 'хайд'?",
            "question_type": "single_choice",
            "options": [
                {"text": "Болезнь", "is_correct": False},
                {"text": "Менструация", "is_correct": True},
                {"text": "Беременность", "is_correct": False},
                {"text": "Путешествие", "is_correct": False}
            ],
            "explanation": "Хайд - это менструация",
            "points": 1
        },
        {
            "question_text": "Что означает 'нифас'?",
            "question_type": "single_choice",
            "options": [
                {"text": "Менструация", "is_correct": False},
                {"text": "Послеродовое кровотечение", "is_correct": True},
                {"text": "Болезнь", "is_correct": False},
                {"text": "Путешествие", "is_correct": False}
            ],
            "explanation": "Нифас - это послеродовое кровотечение",
            "points": 1
        },
        {
            "question_text": "Обязан ли поститься немусульманин?",
            "question_type": "single_choice",
            "options": [
                {"text": "Да, обязан", "is_correct": False},
                {"text": "Нет, сначала нужно принять ислам", "is_correct": True},
                {"text": "Только в Рамадан", "is_correct": False},
                {"text": "По желанию", "is_correct": False}
            ],
            "explanation": "Ислам - первое условие обязательности поста",
            "points": 1
        },
        {
            "question_text": "С какого возраста становится обязательным пост?",
            "question_type": "single_choice",
            "options": [
                {"text": "С 7 лет", "is_correct": False},
                {"text": "С 15 лет", "is_correct": False},
                {"text": "С достижения половой зрелости", "is_correct": True},
                {"text": "С 18 лет", "is_correct": False}
            ],
            "explanation": "Совершеннолетие определяется достижением половой зрелости",
            "points": 1
        },
        {
            "question_text": "Можно ли больному человеку не поститься?",
            "question_type": "single_choice",
            "options": [
                {"text": "Нет, должен поститься", "is_correct": False},
                {"text": "Да, если пост может навредить здоровью", "is_correct": True},
                {"text": "Только при высокой температуре", "is_correct": False},
                {"text": "Только по разрешению врача", "is_correct": False}
            ],
            "explanation": "Физическая способность - условие обязательности поста",
            "points": 1
        },
        {
            "question_text": "Что означает 'совершеннолетие' в исламе?",
            "question_type": "single_choice",
            "options": [
                {"text": "18 лет", "is_correct": False},
                {"text": "Достижение половой зрелости", "is_correct": True},
                {"text": "21 год", "is_correct": False},
                {"text": "16 лет", "is_correct": False}
            ],
            "explanation": "В исламе совершеннолетие определяется достижением половой зрелости",
            "points": 1
        },
        # Additional 20 questions to make 30 total
        {
            "question_text": "Как называется глава о посте?",
            "question_type": "single_choice",
            "options": [
                {"text": "Китабус-салят", "is_correct": False},
                {"text": "Китабус-сиям", "is_correct": True},
                {"text": "Китабус-закят", "is_correct": False},
                {"text": "Китабус-хадж", "is_correct": False}
            ],
            "explanation": "Китабус-сиям - глава о посте",
            "points": 1
        },
        {
            "question_text": "Сколько условий должно выполняться для женщин дополнительно?",
            "question_type": "single_choice",
            "options": [
                {"text": "0", "is_correct": False},
                {"text": "1", "is_correct": True},
                {"text": "2", "is_correct": False},
                {"text": "3", "is_correct": False}
            ],
            "explanation": "Дополнительно для женщин - отсутствие хайда или нифаса",
            "points": 1
        },
        {
            "question_text": "Должен ли ребенок соблюдать пост?",
            "question_type": "single_choice",
            "options": [
                {"text": "Да, обязательно", "is_correct": False},
                {"text": "Нет, до совершеннолетия", "is_correct": True},
                {"text": "Только половину дня", "is_correct": False},
                {"text": "По желанию родителей", "is_correct": False}
            ],
            "explanation": "Совершеннолетие - условие обязательности поста",
            "points": 1
        },
        {
            "question_text": "Что нужно сделать женщине после окончания менструации?",
            "question_type": "single_choice",
            "options": [
                {"text": "Ничего не делать", "is_correct": False},
                {"text": "Возместить пропущенные дни поста", "is_correct": True},
                {"text": "Заплатить фидью", "is_correct": False},
                {"text": "Поститься двойное количество дней", "is_correct": False}
            ],
            "explanation": "Пропущенные дни поста нужно возместить",
            "points": 1
        },
        {
            "question_text": "Является ли здоровье условием поста?",
            "question_type": "single_choice",
            "options": [
                {"text": "Нет", "is_correct": False},
                {"text": "Да, физическая способность", "is_correct": True},
                {"text": "Только для пожилых", "is_correct": False},
                {"text": "Только при хронических болезнях", "is_correct": False}
            ],
            "explanation": "Физическая способность - одно из основных условий",
            "points": 1
        },
        {
            "question_text": "Обязательно ли соблюдать пост путешественнику?",
            "question_type": "single_choice",
            "options": [
                {"text": "Да, всегда", "is_correct": False},
                {"text": "Нет, может не поститься и возместить позже", "is_correct": True},
                {"text": "Только в дальних поездках", "is_correct": False},
                {"text": "По желанию", "is_correct": False}
            ],
            "explanation": "Путешественник может не поститься, но должен возместить",
            "points": 1
        },
        {
            "question_text": "Что означает слово 'сиям'?",
            "question_type": "single_choice",
            "options": [
                {"text": "Молитва", "is_correct": False},
                {"text": "Пост", "is_correct": True},
                {"text": "Закят", "is_correct": False},
                {"text": "Паломничество", "is_correct": False}
            ],
            "explanation": "Сиям означает пост",
            "points": 1
        },
        {
            "question_text": "В каком месяце обязательно соблюдать пост?",
            "question_type": "single_choice",
            "options": [
                {"text": "Шаваль", "is_correct": False},
                {"text": "Рамадан", "is_correct": True},
                {"text": "Мухаррам", "is_correct": False},
                {"text": "Раджаб", "is_correct": False}
            ],
            "explanation": "Обязательный пост соблюдается в месяц Рамадан",
            "points": 1
        },
        {
            "question_text": "Может ли беременная женщина не поститься?",
            "question_type": "single_choice",
            "options": [
                {"text": "Нет, должна поститься", "is_correct": False},
                {"text": "Да, если есть опасность для здоровья", "is_correct": True},
                {"text": "Только в последние месяцы", "is_correct": False},
                {"text": "По желанию", "is_correct": False}
            ],
            "explanation": "Если пост может навредить здоровью матери или ребенка",
            "points": 1
        },
        {
            "question_text": "Что такое 'фидья'?",
            "question_type": "single_choice",
            "options": [
                {"text": "Дополнительная молитва", "is_correct": False},
                {"text": "Компенсация за пропущенный пост", "is_correct": True},
                {"text": "Вид закята", "is_correct": False},
                {"text": "Дополнительный пост", "is_correct": False}
            ],
            "explanation": "Фидья - компенсация для тех, кто не может поститься",
            "points": 1
        },
        {
            "question_text": "Обязан ли пожилой человек поститься?",
            "question_type": "single_choice",
            "options": [
                {"text": "Да, всегда", "is_correct": False},
                {"text": "Нет, если не способен физически", "is_correct": True},
                {"text": "Только половину дня", "is_correct": False},
                {"text": "Только по желанию", "is_correct": False}
            ],
            "explanation": "Если нет физической способности, пост не обязателен",
            "points": 1
        },
        {
            "question_text": "Когда женщина должна возместить пост?",
            "question_type": "single_choice",
            "options": [
                {"text": "Сразу после окончания менструации", "is_correct": False},
                {"text": "До следующего Рамадана", "is_correct": True},
                {"text": "В течение месяца", "is_correct": False},
                {"text": "Когда захочет", "is_correct": False}
            ],
            "explanation": "Возмещение должно быть до следующего Рамадана",
            "points": 1
        },
        {
            "question_text": "Что нужно для соблюдения поста кроме условий?",
            "question_type": "single_choice",
            "options": [
                {"text": "Только условия", "is_correct": False},
                {"text": "Намерение (ния)", "is_correct": True},
                {"text": "Разрешение имама", "is_correct": False},
                {"text": "Специальная одежда", "is_correct": False}
            ],
            "explanation": "Намерение (ния) обязательно для поста",
            "points": 1
        },
        {
            "question_text": "Можно ли принимать лекарства во время поста?",
            "question_type": "single_choice",
            "options": [
                {"text": "Нет, никогда", "is_correct": False},
                {"text": "Да, если необходимо для здоровья", "is_correct": True},
                {"text": "Только в форме инъекций", "is_correct": False},
                {"text": "Только витамины", "is_correct": False}
            ],
            "explanation": "При необходимости лечения можно принимать лекарства",
            "points": 1
        },
        {
            "question_text": "Что происходит с постом при болезни?",
            "question_type": "single_choice",
            "options": [
                {"text": "Должен продолжать поститься", "is_correct": False},
                {"text": "Может прервать и возместить позже", "is_correct": True},
                {"text": "Пост становится недействительным", "is_correct": False},
                {"text": "Должен заплатить фидью", "is_correct": False}
            ],
            "explanation": "Больной может прервать пост и возместить после выздоровления",
            "points": 1
        },
        {
            "question_text": "Кто освобождается от возмещения поста?",
            "question_type": "single_choice",
            "options": [
                {"text": "Никто", "is_correct": False},
                {"text": "Те, кто не может поститься постоянно", "is_correct": True},
                {"text": "Все больные", "is_correct": False},
                {"text": "Все пожилые", "is_correct": False}
            ],
            "explanation": "При постоянной неспособности поститься платят фидью",
            "points": 1
        },
        {
            "question_text": "Когда начинается время поста?",
            "question_type": "single_choice",
            "options": [
                {"text": "С восходом солнца", "is_correct": False},
                {"text": "С рассветом (фаджр)", "is_correct": True},
                {"text": "В полночь", "is_correct": False},
                {"text": "После утренней молитвы", "is_correct": False}
            ],
            "explanation": "Пост начинается с наступлением времени фаджра",
            "points": 1
        },
        {
            "question_text": "Когда заканчивается время поста?",
            "question_type": "single_choice",
            "options": [
                {"text": "На закате (магриб)", "is_correct": True},
                {"text": "После вечерней молитвы", "is_correct": False},
                {"text": "В полночь", "is_correct": False},
                {"text": "Когда станет темно", "is_correct": False}
            ],
            "explanation": "Пост заканчивается с наступлением времени магриба",
            "points": 1
        },
        {
            "question_text": "Что нарушает пост?",
            "question_type": "single_choice",
            "options": [
                {"text": "Только еда и питье", "is_correct": False},
                {"text": "Еда, питье и интимная близость", "is_correct": True},
                {"text": "Только еда", "is_correct": False},
                {"text": "Разговор", "is_correct": False}
            ],
            "explanation": "Основные нарушители поста: еда, питье и интимная близость",
            "points": 1
        },
        {
            "question_text": "Нарушает ли пост случайный прием пищи?",
            "question_type": "single_choice",
            "options": [
                {"text": "Да, всегда", "is_correct": False},
                {"text": "Нет, если по забывчивости", "is_correct": True},
                {"text": "Только если съел много", "is_correct": False},
                {"text": "Зависит от времени дня", "is_correct": False}
            ],
            "explanation": "Случайный прием пищи по забывчивости не нарушает пост",
            "points": 1
        }
    ]
    
    # Test data
    test_data = {
        "course_id": "02d1ddee-a2cb-4720-b962-41dc54c7a997",
        "lesson_id": lesson_id,
        "title": "Тест по главе 'Китабус-сиям' (Пост)",
        "description": "Проверочный тест по основам поста в исламе. Из 30 вопросов случайным образом выбираются 10.",
        "time_limit_minutes": 15,
        "passing_score": 70,
        "max_attempts": 3,
        "order": 1,
        "questions": questions,
        "is_published": True
    }
    
    # Create test
    create_url = f"{BASE_URL}/admin/tests"
    response = requests.post(create_url, headers=headers, json=test_data)
    
    if response.status_code == 200:
        test = response.json()
        print(f"✅ Тест успешно создан!")
        print(f"ID теста: {test['id']}")
        print(f"Название: {test['title']}")
        print(f"Количество вопросов: {len(test['questions'])}")
        print(f"Время: {test['time_limit_minutes']} минут")
        print(f"Проходной балл: {test['passing_score']}%")
        return test
    else:
        print(f"❌ Ошибка создания теста: {response.text}")
        return None

def main():
    print("🚀 Создание урока 'Китабус-сиям' в курсе 'Пост'...")
    
    # Create lesson
    lesson = create_lesson()
    if not lesson:
        return
    
    print("\n📝 Создание теста для урока...")
    
    # Create test for the lesson
    test = create_test_for_lesson(lesson['id'])
    if not test:
        return
    
    print("\n✅ Урок и тест успешно созданы!")
    print("\n📋 Сводка:")
    print(f"Урок: {lesson['title']}")
    print(f"ID урока: {lesson['id']}")
    print(f"Тип урока: {lesson['lesson_type']}")
    print(f"Видео: {lesson['video_url']}")
    print(f"Тест: {test['title']}")
    print(f"ID теста: {test['id']}")
    print(f"Вопросов в банке: {len(test['questions'])}")
    print(f"Показывается случайно: 10 вопросов")

if __name__ == "__main__":
    main()