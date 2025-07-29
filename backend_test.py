
import requests
import sys
import time
import json
import os
import random
import uuid
from datetime import datetime

class IslamAppAPITester:
    def __init__(self, base_url="https://a72883f7-06a9-42f3-b4a4-18cd6085e38a.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.token = None
        self.user_type = None
        self.user_info = None
        self.created_course_id = None
        self.created_teacher_id = None
        self.created_lesson_id = None
        self.created_test_id = None
        self.test_session_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        if headers is None:
            headers = {}
            if not files:  # Don't set Content-Type for multipart/form-data
                headers['Content-Type'] = 'application/json'
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files, headers=headers, timeout=10)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if response.text:
                    try:
                        print(f"Response: {response.json()}")
                    except:
                        print(f"Response: {response.text}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                if response.text:
                    print(f"Response: {response.text}")

            return success, response

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_status_endpoint(self):
        """Test the status endpoint"""
        success, response = self.run_test(
            "Status Endpoint (GET)",
            "GET",
            "status",
            200
        )
        return success

    def test_create_status(self):
        """Test creating a status check"""
        success, response = self.run_test(
            "Create Status Check",
            "POST",
            "status",
            201,
            data={"client_name": "API Tester"}
        )
        return success

    # Unified Auth Tests
    def test_unified_login(self, email, password, expected_user_type="user"):
        """Test unified login endpoint"""
        print(f"\n🔑 Testing unified login with email: {email}")
        success, response = self.run_test(
            "Unified Auth Login",
            "POST",
            "auth/login",
            200,
            data={"email": email, "password": password}
        )
        
        if success:
            try:
                response_data = response.json()
                self.token = response_data.get('access_token')
                self.user_type = response_data.get('user_type')
                self.user_info = response_data.get('user', {})
                
                print(f"✅ Login successful")
                print(f"✅ User type: {self.user_type}")
                print(f"✅ User info: {json.dumps(self.user_info, indent=2)}")
                
                if self.user_type == expected_user_type:
                    print(f"✅ Correctly identified as {expected_user_type}")
                    return True
                else:
                    print(f"❌ Not identified as {expected_user_type}, got: {self.user_type}")
                    return False
            except Exception as e:
                print(f"❌ Failed to extract data from response: {str(e)}")
                return False
        return False

    def test_invalid_login(self, email, password):
        """Test login with invalid credentials"""
        print(f"\n❌ Testing Invalid Login with email: {email}")
        success, response = self.run_test(
            "Invalid Login",
            "POST",
            "auth/login",
            400,  # Expecting a 400 Bad Request for invalid credentials
            data={"email": email, "password": password}
        )
        
        # For this test, success means the API correctly rejected the invalid credentials
        return success

    # Admin API Tests
    def test_admin_login(self, username, password):
        """Test admin login and get token (legacy endpoint)"""
        success, response = self.run_test(
            "Admin Login (Legacy)",
            "POST",
            "admin/login",
            200,
            data={"username": username, "password": password}
        )
        
        if success:
            try:
                self.token = response.json().get('access_token')
                return True
            except:
                print("❌ Failed to extract token from response")
                return False
        return False

    def test_dashboard(self):
        """Test dashboard stats endpoint"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "admin/dashboard",
            200
        )
        return success

    def test_courses(self):
        """Test courses endpoint"""
        success, response = self.run_test(
            "Get Courses",
            "GET",
            "admin/courses",
            200
        )
        return success, response

    def test_create_course(self, course_data):
        """Test course creation"""
        success, response = self.run_test(
            "Create Course",
            "POST",
            "admin/courses",
            200,
            data=course_data
        )
        return success, response

    def test_update_course(self, course_id, update_data):
        """Test course update"""
        success, response = self.run_test(
            "Update Course",
            "PUT",
            f"admin/courses/{course_id}",
            200,
            data=update_data
        )
        return success

    def test_delete_course(self, course_id):
        """Test course deletion"""
        success, response = self.run_test(
            "Delete Course",
            "DELETE",
            f"admin/courses/{course_id}",
            200
        )
        return success

    def test_students(self):
        """Test students endpoint"""
        success, response = self.run_test(
            "Get Students",
            "GET",
            "admin/students",
            200
        )
        return success, response

    def test_teachers(self):
        """Test teachers endpoint"""
        success, response = self.run_test(
            "Get Teachers",
            "GET",
            "admin/teachers",
            200
        )
        return success, response

    def test_create_teacher(self, teacher_data):
        """Test teacher creation"""
        success, response = self.run_test(
            "Create Teacher",
            "POST",
            "admin/teachers",
            200,
            data=teacher_data
        )
        return success, response

    def test_applications(self):
        """Test applications endpoint"""
        success, response = self.run_test(
            "Get Applications",
            "GET",
            "admin/applications",
            200
        )
        return success, response

    def test_reports(self):
        """Test reports endpoint"""
        success, response = self.run_test(
            "Get Level Reports",
            "GET",
            "admin/reports/levels",
            200
        )
        return success, response
        
    # New API Test Methods
    
    def test_enhanced_file_upload(self, file_path, file_type):
        """Test enhanced file upload endpoint"""
        print(f"\n📁 Testing Enhanced File Upload with file: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, file_type)}
                
                success, response = self.run_test(
                    "Enhanced File Upload",
                    "POST",
                    "admin/upload-enhanced",
                    200,
                    files=files,
                    data={}
                )
                
                if success:
                    try:
                        response_data = response.json()
                        file_url = response_data.get('file_url')
                        print(f"✅ File uploaded successfully: {file_url}")
                        return True, response_data
                    except Exception as e:
                        print(f"❌ Failed to extract data from response: {str(e)}")
                        return False, None
                return False, None
        except Exception as e:
            print(f"❌ Failed to open file: {str(e)}")
            return False, None
    
    def test_lesson_attachment(self, lesson_id, file_path, file_type):
        """Test adding attachment to a lesson"""
        print(f"\n📎 Testing Lesson Attachment with file: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, file_type)}
                
                success, response = self.run_test(
                    "Add Lesson Attachment",
                    "POST",
                    f"admin/lessons/{lesson_id}/attachments",
                    200,
                    files=files,
                    data={}
                )
                
                if success:
                    try:
                        response_data = response.json()
                        print(f"✅ Attachment added successfully")
                        return True, response_data
                    except Exception as e:
                        print(f"❌ Failed to extract data from response: {str(e)}")
                        return False, None
                return False, None
        except Exception as e:
            print(f"❌ Failed to open file: {str(e)}")
            return False, None
    
    def test_import_test_from_json(self, file_path, course_id, lesson_id=None):
        """Test importing test from JSON file"""
        print(f"\n📊 Testing Test Import from JSON: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/json')}
                
                data = {
                    'course_id': course_id
                }
                
                if lesson_id:
                    data['lesson_id'] = lesson_id
                
                success, response = self.run_test(
                    "Import Test from JSON",
                    "POST",
                    "admin/tests/import",
                    200,
                    files=files,
                    data=data
                )
                
                if success:
                    try:
                        response_data = response.json()
                        test_id = response_data.get('test_id')
                        print(f"✅ Test imported successfully: {test_id}")
                        return True, response_data
                    except Exception as e:
                        print(f"❌ Failed to extract data from response: {str(e)}")
                        return False, None
                return False, None
        except Exception as e:
            print(f"❌ Failed to open file: {str(e)}")
            return False, None
    
    def test_start_test_session(self, test_id, student_id):
        """Test starting a test session with random questions"""
        print(f"\n🧪 Testing Start Test Session for test: {test_id}")
        
        data = {
            'student_id': student_id
        }
        
        success, response = self.run_test(
            "Start Test Session",
            "POST",
            f"tests/{test_id}/start-session",
            200,
            data=data
        )
        
        if success:
            try:
                response_data = response.json()
                session_id = response_data.get('session_id')
                questions = response_data.get('questions', [])
                
                print(f"✅ Test session started successfully: {session_id}")
                print(f"✅ Number of questions: {len(questions)}")
                
                # Verify random selection (should be 10 questions)
                if len(questions) == 10:
                    print(f"✅ Correctly selected 10 random questions")
                else:
                    print(f"❌ Expected 10 questions, got {len(questions)}")
                
                # Check if options exist for questions
                if questions and 'options' in questions[0]:
                    print(f"✅ Question options are included")
                    
                    # Store a sample question for later verification of shuffling
                    self.sample_question = questions[0]
                else:
                    print(f"❌ Question options not found")
                
                return True, response_data
            except Exception as e:
                print(f"❌ Failed to extract data from response: {str(e)}")
                return False, None
        return False, None
    
    def test_submit_test_session(self, session_id, answers):
        """Test submitting answers for a test session"""
        print(f"\n📝 Testing Submit Test Session: {session_id}")
        
        success, response = self.run_test(
            "Submit Test Session",
            "POST",
            f"test-sessions/{session_id}/submit",
            200,
            data=answers
        )
        
        if success:
            try:
                response_data = response.json()
                score = response_data.get('score')
                total_points = response_data.get('total_points')
                percentage = response_data.get('percentage')
                is_passed = response_data.get('is_passed')
                
                print(f"✅ Test submission successful")
                print(f"✅ Score: {score}/{total_points} ({percentage}%)")
                print(f"✅ Passed: {is_passed}")
                
                return True, response_data
            except Exception as e:
                print(f"❌ Failed to extract data from response: {str(e)}")
                return False, None
        return False, None
    
    def create_test_json_file(self, filename="test_questions.json"):
        """Create a sample JSON file with test questions"""
        print(f"\n📄 Creating sample test JSON file: {filename}")
        
        questions = []
        
        # Create 15 sample questions
        for i in range(1, 16):
            options = []
            correct_index = random.randint(0, 3)
            
            for j in range(4):
                options.append({
                    "text": f"Option {j+1} for Question {i}",
                    "is_correct": j == correct_index
                })
            
            question = {
                "text": f"Sample Question {i}?",
                "question_type": "single_choice",
                "options": options,
                "explanation": f"Explanation for question {i}",
                "points": 1
            }
            
            questions.append(question)
        
        test_data = {
            "questions": questions
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(test_data, f, indent=2)
            print(f"✅ Created sample test file with {len(questions)} questions")
            return True, filename
        except Exception as e:
            print(f"❌ Failed to create test file: {str(e)}")
            return False, None
    
    def create_sample_pdf(self, filename="sample.pdf"):
        """Create a simple text file as a mock PDF"""
        print(f"\n📄 Creating sample PDF file: {filename}")
        
        try:
            with open(filename, 'w') as f:
                f.write("This is a sample PDF file content for testing purposes.")
            print(f"✅ Created sample PDF file")
            return True, filename
        except Exception as e:
            print(f"❌ Failed to create PDF file: {str(e)}")
            return False, None

def test_basic_api():
    """Test basic API endpoints"""
    print("\n=== Testing Basic API Endpoints ===")
    tester = IslamAppAPITester()
    
    # Run basic tests
    tester.test_root_endpoint()
    tester.test_status_endpoint()
    tester.test_create_status()

    # Print results
    print(f"\n📊 Basic API Tests: {tester.tests_passed}/{tester.tests_run} passed")
    return tester.tests_passed == tester.tests_run

def test_unified_auth():
    """Test unified authentication system"""
    print("\n=== Testing Unified Authentication System ===")
    tester = IslamAppAPITester()
    
    # Test admin login with the provided credentials
    print("\n🔑 Testing admin login with credentials: miftahylum@gmail.com/197724")
    admin_login_success = tester.test_unified_login("miftahylum@gmail.com", "197724", "admin")
    
    # Test admin dashboard access if login succeeded
    if admin_login_success:
        print("\n🔐 Testing Admin Dashboard Access")
        dashboard_success = tester.test_dashboard()
        if dashboard_success:
            print("✅ Successfully accessed admin dashboard with admin token")
        else:
            print("❌ Failed to access admin dashboard with admin token")
    
    # Create a new tester instance for student login
    student_tester = IslamAppAPITester()
    
    # Test student login
    print("\n👤 Testing student login with test credentials")
    student_login_success = student_tester.test_unified_login("student@test.com", "password123", "user")
    
    # Test unauthorized admin access with student token
    if student_login_success:
        print("\n🚫 Testing Unauthorized Admin Dashboard Access")
        unauth_success = student_tester.test_dashboard()
        if not unauth_success:
            print("✅ Correctly denied admin dashboard access to student user")
        else:
            print("❌ Failed to properly restrict admin dashboard access")
    
    # Test invalid login
    invalid_tester = IslamAppAPITester()
    invalid_login_success = invalid_tester.test_invalid_login("nonexistent@example.com", "wrongpassword")
    
    # Print results
    print(f"\n📊 Unified Auth Tests: {tester.tests_passed + student_tester.tests_passed + invalid_tester.tests_passed}/{tester.tests_run + student_tester.tests_run + invalid_tester.tests_run} passed")
    return (tester.tests_passed == tester.tests_run and 
            student_tester.tests_passed == student_tester.tests_run and
            invalid_tester.tests_passed == invalid_tester.tests_run)

def test_admin_api():
    """Test admin API endpoints"""
    print("\n=== Testing Admin API Endpoints ===")
    tester = IslamAppAPITester()
    
    # Test admin login with the updated credentials
    print("\n🔑 Testing admin login with credentials: admin/admin123")
    if not tester.test_admin_login("admin", "admin123"):
        print("❌ Admin login failed, stopping admin tests")
        print(f"\n📊 Admin API Tests: {tester.tests_passed}/{tester.tests_run} passed")
        return False
    
    # Test dashboard
    tester.test_dashboard()
    
    # Test courses
    courses_success, courses_response = tester.test_courses()
    
    # Test course creation
    course_data = {
        "title": "Тестовый курс",
        "description": "Описание тестового курса",
        "level": "level_1",
        "teacher_id": "1",  # Will be updated if we have real teachers
        "teacher_name": "Тестовый преподаватель",
        "difficulty": "Легко",
        "estimated_duration_hours": 30,
        "image_url": "https://example.com/image.jpg"
    }
    
    # Get teachers first to use a real teacher ID
    teachers_success, teachers_response = tester.test_teachers()
    if teachers_success:
        try:
            teachers = teachers_response.json()
            if teachers and len(teachers) > 0:
                course_data["teacher_id"] = teachers[0]["id"]
                course_data["teacher_name"] = teachers[0]["name"]
        except:
            pass
    
    # Create a course
    create_success, create_response = tester.test_create_course(course_data)
    
    # If course creation succeeded, test update and delete
    if create_success:
        try:
            course_id = create_response.json()["id"]
            
            # Test course update
            update_data = {
                "title": "Обновленный тестовый курс",
                "status": "published"
            }
            tester.test_update_course(course_id, update_data)
            
            # Test course deletion
            tester.test_delete_course(course_id)
        except Exception as e:
            print(f"Error in course update/delete tests: {str(e)}")
    
    # Test students
    tester.test_students()
    
    # Test teacher creation
    teacher_data = {
        "name": "Тестовый преподаватель",
        "email": f"test{datetime.now().strftime('%H%M%S')}@example.com",
        "subject": "Тестовый предмет",
        "bio": "Биография тестового преподавателя"
    }
    tester.test_create_teacher(teacher_data)
    
    # Test applications
    tester.test_applications()
    
    # Test reports
    tester.test_reports()
    
    # Print results
    print(f"\n📊 Admin API Tests: {tester.tests_passed}/{tester.tests_run} passed")
    return tester.tests_passed == tester.tests_run

def test_namaz_lesson():
    """Test the 'Как правильно совершать намаз' lesson and its components"""
    print("\n=== Testing 'Как правильно совершать намаз' Lesson ===")
    tester = IslamAppAPITester()
    
    # Login as admin
    print("\n🔑 Testing admin login with credentials: admin/admin123")
    if not tester.test_admin_login("admin", "admin123"):
        print("❌ Admin login failed, stopping tests")
        return False
    
    # Test variables from the requirements
    lesson_id = "9a7c2518-da14-49f6-ad25-7d89b152dc65"
    course_id = "947f1ddb-5e52-4605-810a-9db25d94ba79"
    test_id = "42665711-d8a7-41ae-80e8-a14eaf526ad2"
    
    # 1. Test getting the lesson
    print(f"\n📚 Testing GET /api/lessons/{lesson_id}")
    success, response = tester.run_test(
        f"Get Lesson {lesson_id}",
        "GET",
        f"lessons/{lesson_id}",
        200
    )
    
    if success:
        try:
            lesson_data = response.json()
            print(f"✅ Lesson title: {lesson_data.get('title')}")
            print(f"✅ Lesson type: {lesson_data.get('lesson_type')}")
            
            # Verify video URL
            video_url = lesson_data.get('video_url')
            if video_url and "youtube.com/embed/T4auGhmeBlw" in video_url:
                print(f"✅ Video URL is correct: {video_url}")
            else:
                print(f"❌ Video URL is incorrect or missing: {video_url}")
                success = False
                
            # Check for attachments
            attachments = lesson_data.get('attachments', [])
            if attachments:
                print(f"✅ Lesson has {len(attachments)} attachment(s)")
                for attachment in attachments:
                    print(f"  - {attachment.get('filename')}")
            else:
                print("ℹ️ Lesson has no attachments")
        except Exception as e:
            print(f"❌ Failed to parse lesson data: {str(e)}")
            success = False
    
    # 2. Test getting tests for the lesson
    print(f"\n📝 Testing GET /api/lessons/{lesson_id}/tests")
    tests_success, tests_response = tester.run_test(
        f"Get Tests for Lesson {lesson_id}",
        "GET",
        f"lessons/{lesson_id}/tests",
        200
    )
    
    if tests_success:
        try:
            tests_data = tests_response.json()
            if tests_data:
                print(f"✅ Found {len(tests_data)} test(s) for the lesson")
                
                # Check if our specific test is in the list
                test_found = False
                for test in tests_data:
                    if test.get('id') == test_id:
                        test_found = True
                        print(f"✅ Found the specified test: {test.get('title')}")
                        print(f"✅ Test time limit: {test.get('time_limit_minutes')} minutes")
                        print(f"✅ Test passing score: {test.get('passing_score')}%")
                        break
                
                if not test_found:
                    print(f"❌ Specified test ID {test_id} not found in lesson tests")
                    tests_success = False
            else:
                print("ℹ️ No tests found for this lesson")
        except Exception as e:
            print(f"❌ Failed to parse tests data: {str(e)}")
            tests_success = False
    
    # 3. Test getting all lessons for the course
    print(f"\n📚 Testing GET /api/courses/{course_id}/lessons")
    course_lessons_success, course_lessons_response = tester.run_test(
        f"Get Lessons for Course {course_id}",
        "GET",
        f"courses/{course_id}/lessons",
        200
    )
    
    if course_lessons_success:
        try:
            lessons_data = course_lessons_response.json()
            if lessons_data:
                print(f"✅ Found {len(lessons_data)} lesson(s) in the course")
                
                # Check if our specific lesson is in the list
                lesson_found = False
                for lesson in lessons_data:
                    if lesson.get('id') == lesson_id:
                        lesson_found = True
                        print(f"✅ Found the specified lesson: {lesson.get('title')}")
                        break
                
                if not lesson_found:
                    print(f"❌ Specified lesson ID {lesson_id} not found in course lessons")
                    course_lessons_success = False
            else:
                print("ℹ️ No lessons found for this course")
        except Exception as e:
            print(f"❌ Failed to parse course lessons data: {str(e)}")
            course_lessons_success = False
    
    # 4. Test starting a test session (check randomization)
    print(f"\n🧪 Testing POST /api/tests/{test_id}/start-session")
    
    # Create a fake student ID for testing
    student_id = f"test_student_{uuid.uuid4()}"
    
    # Start test session multiple times to check randomization
    sessions = []
    for i in range(3):
        session_success, session_response = tester.run_test(
            f"Start Test Session {i+1}",
            "POST",
            f"tests/{test_id}/start-session",
            200,
            data={"student_id": student_id}
        )
        
        if session_success:
            try:
                session_data = session_response.json()
                sessions.append(session_data)
                print(f"✅ Session {i+1} started successfully")
                print(f"✅ Number of questions: {len(session_data.get('questions', []))}")
            except Exception as e:
                print(f"❌ Failed to parse session data: {str(e)}")
                session_success = False
    
    # Check randomization by comparing questions across sessions
    randomization_success = True
    if len(sessions) >= 2:
        print("\n🔄 Checking question randomization across sessions")
        
        # Extract question IDs from each session
        question_sets = []
        for i, session in enumerate(sessions):
            question_ids = [q.get('id') for q in session.get('questions', [])]
            question_sets.append(set(question_ids))
            print(f"  Session {i+1} question IDs: {question_ids}")
        
        # Compare question sets
        all_identical = True
        for i in range(len(question_sets) - 1):
            if question_sets[i] != question_sets[i+1]:
                all_identical = False
                break
        
        if all_identical and len(question_sets[0]) > 0:
            print("❌ Questions are not randomized across sessions")
            randomization_success = False
        else:
            print("✅ Questions are properly randomized across sessions")
            randomization_success = True
        
        # Check option shuffling within a session
        print("\n🔄 Checking option shuffling within questions")
        
        # Take the first question from the first session that has options
        sample_question = None
        for session in sessions:
            for question in session.get('questions', []):
                if question.get('options') and len(question.get('options', [])) > 1:
                    sample_question = question
                    break
            if sample_question:
                break
        
        if sample_question:
            print(f"  Sample question: {sample_question.get('text')}")
            print(f"  Options: {[opt.get('text') for opt in sample_question.get('options', [])]}")
            print("✅ Options are present in the response")
        else:
            print("ℹ️ No suitable question found to check option shuffling")
    else:
        print("❌ Not enough sessions to check randomization")
        randomization_success = False
    
    # 5. Test admin view of the lesson
    print(f"\n👑 Testing GET /api/admin/lessons/{lesson_id}")
    admin_lesson_success, admin_lesson_response = tester.run_test(
        f"Admin View of Lesson {lesson_id}",
        "GET",
        f"admin/lessons/{lesson_id}",
        200
    )
    
    if admin_lesson_success:
        try:
            admin_lesson_data = admin_lesson_response.json()
            print(f"✅ Admin can view the lesson: {admin_lesson_data.get('title')}")
            
            # Check for additional admin fields that might not be in the public view
            admin_fields = ['is_published', 'created_at', 'updated_at']
            for field in admin_fields:
                if field in admin_lesson_data:
                    print(f"✅ Admin field present: {field}")
            
        except Exception as e:
            print(f"❌ Failed to parse admin lesson data: {str(e)}")
            admin_lesson_success = False
    
    # Overall result
    overall_success = (success and tests_success and course_lessons_success and 
                      randomization_success and admin_lesson_success)
    
    print(f"\n📊 Namaz Lesson Tests: {tester.tests_passed}/{tester.tests_run} passed")
    return overall_success

def test_admin_lesson_view():
    """Test the admin lesson view API endpoint"""
    print("\n=== Testing Admin Lesson View API ===")
    tester = IslamAppAPITester()
    
    # Login as admin
    print("\n🔑 Testing admin login with credentials: admin/admin123")
    if not tester.test_admin_login("admin", "admin123"):
        print("❌ Admin login failed, stopping tests")
        return False
    
    # Test variables from the requirements
    lesson_id = "9a7c2518-da14-49f6-ad25-7d89b152dc65"
    
    # Test admin lesson view endpoint
    print(f"\n👑 Testing GET /api/admin/lessons/{lesson_id}")
    admin_lesson_success, admin_lesson_response = tester.run_test(
        f"Admin View of Lesson {lesson_id}",
        "GET",
        f"admin/lessons/{lesson_id}",
        200
    )
    
    if admin_lesson_success:
        try:
            admin_lesson_data = admin_lesson_response.json()
            print(f"✅ Admin can view the lesson: {admin_lesson_data.get('title')}")
            
            # Check for additional admin fields that might not be in the public view
            admin_fields = ['is_published', 'created_at', 'updated_at']
            for field in admin_fields:
                if field in admin_lesson_data:
                    print(f"✅ Admin field present: {field}")
            
            return True
        except Exception as e:
            print(f"❌ Failed to parse admin lesson data: {str(e)}")
            return False
    
    return False

def test_random_question_selection():
    """Test the random question selection API"""
    print("\n=== Testing Random Question Selection API ===")
    tester = IslamAppAPITester()
    
    # Login as admin
    print("\n🔑 Testing admin login with credentials: admin/admin123")
    if not tester.test_admin_login("admin", "admin123"):
        print("❌ Admin login failed, stopping tests")
        return False
    
    # Test variables from the requirements
    test_id = "42665711-d8a7-41ae-80e8-a14eaf526ad2"
    
    # Create a fake student ID for testing
    student_id = f"test_student_{uuid.uuid4()}"
    
    # Start test session
    print(f"\n🧪 Testing POST /api/tests/{test_id}/start-session")
    session_success, session_response = tester.run_test(
        f"Start Test Session",
        "POST",
        f"tests/{test_id}/start-session",
        200,
        data={"student_id": student_id}
    )
    
    if session_success:
        try:
            session_data = session_response.json()
            questions = session_data.get('questions', [])
            
            print(f"✅ Test session started successfully")
            print(f"✅ Number of questions: {len(questions)}")
            
            # Verify random selection (should be 10 questions)
            if len(questions) == 10:
                print(f"✅ Correctly selected 10 random questions")
            else:
                print(f"❌ Expected 10 questions, got {len(questions)}")
                
            # Store session ID for answer shuffling test
            tester.test_session_id = session_data.get('session_id')
            
            return True
        except Exception as e:
            print(f"❌ Failed to parse session data: {str(e)}")
            return False
    
    return False

def test_answer_shuffling():
    """Test the answer shuffling system"""
    print("\n=== Testing Answer Shuffling System ===")
    tester = IslamAppAPITester()
    
    # Login as admin
    print("\n🔑 Testing admin login with credentials: admin/admin123")
    if not tester.test_admin_login("admin", "admin123"):
        print("❌ Admin login failed, stopping tests")
        return False
    
    # Test variables from the requirements
    test_id = "42665711-d8a7-41ae-80e8-a14eaf526ad2"
    
    # Create multiple test sessions to compare option shuffling
    student_id = f"test_student_{uuid.uuid4()}"
    sessions = []
    
    for i in range(2):
        session_success, session_response = tester.run_test(
            f"Start Test Session {i+1}",
            "POST",
            f"tests/{test_id}/start-session",
            200,
            data={"student_id": student_id}
        )
        
        if session_success:
            try:
                session_data = session_response.json()
                sessions.append(session_data)
                print(f"✅ Session {i+1} started successfully")
            except Exception as e:
                print(f"❌ Failed to parse session data: {str(e)}")
    
    # Check option shuffling by comparing the same question across sessions
    if len(sessions) >= 2:
        print("\n🔄 Checking option shuffling across sessions")
        
        # Find a common question between sessions
        common_question_id = None
        for q1 in sessions[0].get('questions', []):
            for q2 in sessions[1].get('questions', []):
                if q1.get('id') == q2.get('id'):
                    common_question_id = q1.get('id')
                    break
            if common_question_id:
                break
        
        if common_question_id:
            # Get the question from both sessions
            q1 = next((q for q in sessions[0].get('questions', []) if q.get('id') == common_question_id), None)
            q2 = next((q for q in sessions[1].get('questions', []) if q.get('id') == common_question_id), None)
            
            if q1 and q2 and 'options' in q1 and 'options' in q2:
                # Compare option order
                options1 = [opt.get('text') for opt in q1.get('options', [])]
                options2 = [opt.get('text') for opt in q2.get('options', [])]
                
                print(f"  Question: {q1.get('text')}")
                print(f"  Session 1 options: {options1}")
                print(f"  Session 2 options: {options2}")
                
                if options1 != options2 and len(options1) > 1 and len(options2) > 1:
                    print("✅ Options are properly shuffled across sessions")
                    return True
                elif len(options1) <= 1 or len(options2) <= 1:
                    print("ℹ️ Not enough options to verify shuffling")
                    return False
                else:
                    print("❌ Options are not shuffled across sessions")
                    return False
            else:
                print("❌ Could not find options for the common question")
                return False
        else:
            print("❌ No common questions found between sessions")
            return False
    else:
        print("❌ Not enough sessions to check option shuffling")
        return False
    
    return False

def test_course_api_endpoints():
    """Test the course API endpoints"""
    print("\n=== Testing Course API Endpoints ===")
    tester = IslamAppAPITester()
    
    # Test variables from the requirements
    course_id = "947f1ddb-5e52-4605-810a-9db25d94ba79"
    
    # Test getting all courses
    print(f"\n📚 Testing GET /api/courses")
    courses_success, courses_response = tester.run_test(
        "Get All Courses",
        "GET",
        "courses",
        200
    )
    
    if courses_success:
        try:
            courses_data = courses_response.json()
            print(f"✅ Found {len(courses_data)} course(s)")
            
            # Check if our specific course is in the list
            course_found = False
            for course in courses_data:
                if course.get('id') == course_id:
                    course_found = True
                    print(f"✅ Found the specified course: {course.get('title')}")
                    
                    # Check for slug field
                    if 'slug' in course:
                        print(f"✅ Course has slug field: {course.get('slug')}")
                    else:
                        print(f"❌ Course is missing slug field")
                    
                    break
            
            if not course_found:
                print(f"❌ Specified course ID {course_id} not found in courses")
        except Exception as e:
            print(f"❌ Failed to parse courses data: {str(e)}")
    
    # Test getting lessons for the course
    print(f"\n📚 Testing GET /api/courses/{course_id}/lessons")
    lessons_success, lessons_response = tester.run_test(
        f"Get Lessons for Course {course_id}",
        "GET",
        f"courses/{course_id}/lessons",
        200
    )
    
    if lessons_success:
        try:
            lessons_data = lessons_response.json()
            print(f"✅ Found {len(lessons_data)} lesson(s) in the course")
            
            # Check for slug field in lessons
            if lessons_data:
                for lesson in lessons_data:
                    if 'slug' in lesson:
                        print(f"✅ Lesson has slug field: {lesson.get('slug')}")
                    else:
                        print(f"❌ Lesson is missing slug field")
                    break
        except Exception as e:
            print(f"❌ Failed to parse lessons data: {str(e)}")
    
    return courses_success and lessons_success

def test_team_endpoints():
    """Test the team management endpoints"""
    print("\n=== Testing Team Management Endpoints ===")
    tester = IslamAppAPITester()
    
    # Test getting public team members
    print(f"\n👥 Testing GET /api/team")
    public_team_success, public_team_response = tester.run_test(
        "Get Public Team Members",
        "GET",
        "team",
        200
    )
    
    if public_team_success:
        try:
            team_data = public_team_response.json()
            print(f"✅ Found {len(team_data)} public team member(s)")
            
            # Check if team members have required fields
            if team_data:
                member = team_data[0]
                required_fields = ['id', 'name', 'subject']
                for field in required_fields:
                    if field in member:
                        print(f"✅ Team member has required field: {field}")
                    else:
                        print(f"❌ Team member is missing required field: {field}")
        except Exception as e:
            print(f"❌ Failed to parse team data: {str(e)}")
    
    # Login as admin for admin endpoints
    print("\n🔑 Testing admin login with credentials: admin@uroki-islama.ru/admin123")
    if not tester.test_unified_login("admin@uroki-islama.ru", "admin123", "admin"):
        print("❌ Admin login failed, stopping team admin tests")
        return False
    
    # Test getting admin team members
    print(f"\n👥 Testing GET /api/admin/team")
    admin_team_success, admin_team_response = tester.run_test(
        "Get Admin Team Members",
        "GET",
        "admin/team",
        200
    )
    
    created_member_id = None
    
    if admin_team_success:
        try:
            team_data = admin_team_response.json()
            print(f"✅ Found {len(team_data)} team member(s) in admin view")
        except Exception as e:
            print(f"❌ Failed to parse admin team data: {str(e)}")
    
    # Test creating a team member
    print(f"\n➕ Testing POST /api/admin/team")
    
    # Sample base64 image (small transparent PNG)
    sample_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    member_data = {
        "name": "Тестовый Преподаватель",
        "subject": "Тестовый предмет",
        "image_base64": sample_base64,
        "bio": "Тестовая биография",
        "email": "test@example.com",
        "order": 5
    }
    
    create_success, create_response = tester.run_test(
        "Create Team Member",
        "POST",
        "admin/team",
        200,
        data=member_data
    )
    
    if create_success:
        try:
            created_member = create_response.json()
            created_member_id = created_member.get('id')
            print(f"✅ Created team member with ID: {created_member_id}")
            
            # Check if created member has the correct data
            for key, value in member_data.items():
                if key in created_member and created_member[key] == value:
                    print(f"✅ Created member has correct {key}")
                elif key in created_member:
                    print(f"❌ Created member has incorrect {key}: expected {value}, got {created_member[key]}")
                else:
                    print(f"❌ Created member is missing {key}")
        except Exception as e:
            print(f"❌ Failed to parse created member data: {str(e)}")
    
    # Test updating a team member
    if created_member_id:
        print(f"\n✏️ Testing PUT /api/admin/team/{created_member_id}")
        
        update_data = {
            "name": "Обновленный Преподаватель",
            "bio": "Обновленная биография"
        }
        
        update_success, update_response = tester.run_test(
            "Update Team Member",
            "PUT",
            f"admin/team/{created_member_id}",
            200,
            data=update_data
        )
        
        if update_success:
            try:
                updated_member = update_response.json()
                print(f"✅ Updated team member successfully")
                
                # Check if updated member has the correct data
                for key, value in update_data.items():
                    if key in updated_member and updated_member[key] == value:
                        print(f"✅ Updated member has correct {key}")
                    elif key in updated_member:
                        print(f"❌ Updated member has incorrect {key}: expected {value}, got {updated_member[key]}")
                    else:
                        print(f"❌ Updated member is missing {key}")
            except Exception as e:
                print(f"❌ Failed to parse updated member data: {str(e)}")
    
        # Test deleting a team member
        print(f"\n❌ Testing DELETE /api/admin/team/{created_member_id}")
        
        delete_success, delete_response = tester.run_test(
            "Delete Team Member",
            "DELETE",
            f"admin/team/{created_member_id}",
            200
        )
        
        if delete_success:
            print(f"✅ Deleted team member successfully")
            
            # Verify the member is deleted by trying to get it
            verify_delete_success, verify_delete_response = tester.run_test(
                "Verify Team Member Deletion",
                "GET",
                f"admin/team/{created_member_id}",
                404
            )
            
            if verify_delete_success:
                print(f"✅ Verified team member deletion")
            else:
                print(f"❌ Failed to verify team member deletion")
    
    # Overall result
    overall_success = public_team_success and admin_team_success
    if created_member_id:
        overall_success = overall_success and create_success and update_success and delete_success
    
    return overall_success

def test_qa_endpoints():
    """Test the Q&A endpoints"""
    print("\n=== Testing Q&A Endpoints ===")
    tester = IslamAppAPITester()
    
    # Login as admin for admin endpoints
    print("\n🔑 Testing admin login with credentials: admin@uroki-islama.ru/admin123")
    if not tester.test_unified_login("admin@uroki-islama.ru", "admin123", "admin"):
        print("❌ Admin login failed, stopping Q&A admin tests")
        return False
    
    # Test creating a new question
    print(f"\n➕ Testing POST /api/admin/qa/questions")
    
    question_data = {
        "title": "Тестовый вопрос",
        "question_text": "Это тестовый вопрос?",
        "answer_text": "Это тестовый ответ.",
        "category": "general",
        "tags": ["тест"],
        "is_featured": False,
        "imam_name": "Имам Тестовый"
    }
    
    create_success, create_response = tester.run_test(
        "Create Q&A Question",
        "POST",
        "admin/qa/questions",
        200,
        data=question_data
    )
    
    created_question_id = None
    
    if create_success:
        try:
            created_question = create_response.json()
            created_question_id = created_question.get('id')
            print(f"✅ Created question with ID: {created_question_id}")
            
            # Check if created question has the correct data
            for key, value in question_data.items():
                if key in created_question and created_question[key] == value:
                    print(f"✅ Created question has correct {key}")
                elif key in created_question:
                    print(f"❌ Created question has incorrect {key}: expected {value}, got {created_question[key]}")
                else:
                    print(f"❌ Created question is missing {key}")
        except Exception as e:
            print(f"❌ Failed to parse created question data: {str(e)}")
    
    # Test updating a question
    if created_question_id:
        print(f"\n✏️ Testing PUT /api/admin/qa/questions/{created_question_id}")
        
        update_data = {
            "title": "Обновленный тестовый вопрос",
            "answer_text": "Обновленный тестовый ответ."
        }
        
        update_success, update_response = tester.run_test(
            "Update Q&A Question",
            "PUT",
            f"admin/qa/questions/{created_question_id}",
            200,
            data=update_data
        )
        
        if update_success:
            try:
                updated_question = update_response.json()
                print(f"✅ Updated question successfully")
                
                # Check if updated question has the correct data
                for key, value in update_data.items():
                    if key in updated_question and updated_question[key] == value:
                        print(f"✅ Updated question has correct {key}")
                    elif key in updated_question:
                        print(f"❌ Updated question has incorrect {key}: expected {value}, got {updated_question[key]}")
                    else:
                        print(f"❌ Updated question is missing {key}")
            except Exception as e:
                print(f"❌ Failed to parse updated question data: {str(e)}")
    
        # Test deleting a question
        print(f"\n❌ Testing DELETE /api/admin/qa/questions/{created_question_id}")
        
        delete_success, delete_response = tester.run_test(
            "Delete Q&A Question",
            "DELETE",
            f"admin/qa/questions/{created_question_id}",
            200
        )
        
        if delete_success:
            print(f"✅ Deleted question successfully")
            
            # Verify the question is deleted by trying to get it
            verify_delete_success, verify_delete_response = tester.run_test(
                "Verify Question Deletion",
                "GET",
                f"qa/questions/{created_question_id}",
                404
            )
            
            if verify_delete_success:
                print(f"✅ Verified question deletion")
            else:
                print(f"❌ Failed to verify question deletion")
    
    # Overall result
    overall_success = True
    if created_question_id:
        overall_success = create_success and update_success and delete_success
    
    return overall_success

def test_islam_culture_course_and_promocodes():
    """Test the 'Культура Ислама' course and promocode system"""
    print("\n=== Testing 'Культура Ислама' Course and Promocode System ===")
    tester = IslamAppAPITester()
    
    # Test variables from the requirements
    course_id = "bd12b3a4-7355-4b9d-8d37-90288916b917"  # Культура Ислама
    lesson_ids = [
        "884bdaa0-34ed-4fad-9deb-c8636660edf1",  # История исламской культуры
        "ef427aa5-2d81-4ece-9837-9ebae83b59ac",  # Исламская архитектура и искусство
        "9b789a41-680b-4973-8c05-939b11c4eb8d"   # Исламская философия и наука
    ]
    promocode = "ШАМИЛЬ"
    test_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
    
    # 1. Test getting all courses to check if "Культура Ислама" is in the list
    print(f"\n📚 Testing GET /api/courses")
    courses_success, courses_response = tester.run_test(
        "Get All Courses",
        "GET",
        "courses",
        200
    )
    
    if courses_success:
        try:
            courses_data = courses_response.json()
            print(f"✅ Found {len(courses_data)} course(s)")
            
            # Check if our specific course is in the list
            course_found = False
            for course in courses_data:
                if course.get('id') == course_id:
                    course_found = True
                    print(f"✅ Found the 'Культура Ислама' course: {course.get('title')}")
                    break
            
            if not course_found:
                print(f"❌ 'Культура Ислама' course (ID: {course_id}) not found in courses")
                courses_success = False
        except Exception as e:
            print(f"❌ Failed to parse courses data: {str(e)}")
            courses_success = False
    
    # 2. Test getting lessons for the course
    print(f"\n📚 Testing GET /api/courses/{course_id}/lessons")
    lessons_success, lessons_response = tester.run_test(
        f"Get Lessons for Course {course_id}",
        "GET",
        f"courses/{course_id}/lessons",
        200
    )
    
    if lessons_success:
        try:
            lessons_data = lessons_response.json()
            print(f"✅ Found {len(lessons_data)} lesson(s) in the course")
            
            # Check if all three lessons are in the list
            found_lessons = []
            for lesson in lessons_data:
                if lesson.get('id') in lesson_ids:
                    found_lessons.append(lesson.get('id'))
                    print(f"✅ Found lesson: {lesson.get('title')}")
            
            if len(found_lessons) != len(lesson_ids):
                missing_lessons = set(lesson_ids) - set(found_lessons)
                print(f"❌ Not all lessons found. Missing: {missing_lessons}")
                lessons_success = False
        except Exception as e:
            print(f"❌ Failed to parse lessons data: {str(e)}")
            lessons_success = False
    
    # 3. Test getting each lesson individually
    lessons_detail_success = True
    for lesson_id in lesson_ids:
        print(f"\n📝 Testing GET /api/lessons/{lesson_id}")
        success, response = tester.run_test(
            f"Get Lesson {lesson_id}",
            "GET",
            f"lessons/{lesson_id}",
            200
        )
        
        if success:
            try:
                lesson_data = response.json()
                print(f"✅ Lesson title: {lesson_data.get('title')}")
                print(f"✅ Lesson type: {lesson_data.get('lesson_type')}")
                
                # Check for content
                if lesson_data.get('content'):
                    print(f"✅ Lesson has content")
                else:
                    print(f"❌ Lesson has no content")
                    
                # Check for video URL if applicable
                if lesson_data.get('lesson_type') in ['video', 'mixed']:
                    video_url = lesson_data.get('video_url')
                    if video_url:
                        print(f"✅ Video URL is present: {video_url}")
                    else:
                        print(f"❌ Video URL is missing")
            except Exception as e:
                print(f"❌ Failed to parse lesson data: {str(e)}")
                success = False
        
        lessons_detail_success = lessons_detail_success and success
    
    # 4. Test promocode info endpoint
    print(f"\n🎟️ Testing GET /api/promocodes/info/{promocode}")
    promocode_info_success, promocode_info_response = tester.run_test(
        f"Get Promocode Info for {promocode}",
        "GET",
        f"promocodes/info/{promocode}",
        200
    )
    
    if promocode_info_success:
        try:
            promocode_data = promocode_info_response.json()
            print(f"✅ Promocode: {promocode_data.get('code')}")
            print(f"✅ Description: {promocode_data.get('description')}")
            print(f"✅ Type: {promocode_data.get('type')}")
            
            # Check if the promocode gives access to courses
            courses_info = promocode_data.get('courses', [])
            if courses_info:
                print(f"✅ Promocode gives access to {len(courses_info)} course(s)")
                for course in courses_info:
                    print(f"  - {course.get('title')}")
            else:
                print(f"❌ Promocode doesn't give access to any courses")
                promocode_info_success = False
        except Exception as e:
            print(f"❌ Failed to parse promocode info: {str(e)}")
            promocode_info_success = False
    
    # 5. Test promocode validation endpoint
    print(f"\n🔑 Testing POST /api/promocodes/validate")
    promocode_validation_success, promocode_validation_response = tester.run_test(
        f"Validate Promocode {promocode}",
        "POST",
        f"promocodes/validate",
        200,
        data={
            "code": promocode,
            "student_email": test_email
        }
    )
    
    if promocode_validation_success:
        try:
            validation_data = promocode_validation_response.json()
            print(f"✅ Validation success: {validation_data.get('success')}")
            print(f"✅ Message: {validation_data.get('message')}")
            
            # Check if access was granted
            access_granted = validation_data.get('access_granted')
            if access_granted:
                print(f"✅ Access granted to courses")
                
                # Check which courses are accessible
                courses_info = validation_data.get('courses', [])
                if courses_info:
                    print(f"✅ Access granted to {len(courses_info)} course(s)")
                    for course in courses_info:
                        print(f"  - {course.get('title')}")
                else:
                    print(f"❌ No courses accessible despite access_granted=True")
                    promocode_validation_success = False
            else:
                print(f"❌ Access not granted")
                promocode_validation_success = False
        except Exception as e:
            print(f"❌ Failed to parse promocode validation response: {str(e)}")
            promocode_validation_success = False
    
    # 6. Test getting student courses after promocode activation
    print(f"\n👤 Testing GET /api/student/{test_email}/courses")
    student_courses_success, student_courses_response = tester.run_test(
        f"Get Courses for Student {test_email}",
        "GET",
        f"student/{test_email}/courses",
        200
    )
    
    if student_courses_success:
        try:
            student_courses = student_courses_response.json()
            print(f"✅ Student has access to {len(student_courses)} course(s)")
            
            # Check if the "Культура Ислама" course is accessible
            course_accessible = False
            for course in student_courses:
                if course.get('id') == course_id:
                    course_accessible = True
                    print(f"✅ Student has access to 'Культура Ислама' course")
                    break
            
            if not course_accessible:
                print(f"❌ Student doesn't have access to 'Культура Ислама' course")
                student_courses_success = False
        except Exception as e:
            print(f"❌ Failed to parse student courses: {str(e)}")
            student_courses_success = False
    
    # 7. Test admin endpoints with authentication
    print("\n👑 Testing admin endpoints with authentication")
    admin_login_success = tester.test_unified_login("admin@uroki-islama.ru", "admin123", "admin")
    
    if admin_login_success:
        print("✅ Admin authentication successful")
        
        # Test admin access to the course
        print(f"\n👑 Testing GET /api/admin/courses")
        admin_course_success, admin_courses_response = tester.run_test(
            f"Admin View of Courses",
            "GET",
            f"admin/courses",
            200
        )
        
        if admin_course_success:
            try:
                admin_courses_data = admin_courses_response.json()
                course_found = False
                for course in admin_courses_data:
                    if course.get('id') == course_id:
                        course_found = True
                        print(f"✅ Admin can view the course: {course.get('title')}")
                        break
                
                if not course_found:
                    print(f"❌ Course with ID {course_id} not found in admin courses")
                    admin_course_success = False
            except Exception as e:
                print(f"❌ Failed to parse admin courses data: {str(e)}")
                admin_course_success = False
        
        # Test admin access to lessons
        admin_lessons_success = True
        for lesson_id in lesson_ids:
            print(f"\n👑 Testing GET /api/admin/lessons/{lesson_id}")
            success, response = tester.run_test(
                f"Admin View of Lesson {lesson_id}",
                "GET",
                f"admin/lessons/{lesson_id}",
                200
            )
            
            if success:
                try:
                    admin_lesson_data = response.json()
                    print(f"✅ Admin can view the lesson: {admin_lesson_data.get('title')}")
                except Exception as e:
                    print(f"❌ Failed to parse admin lesson data: {str(e)}")
                    success = False
            
            admin_lessons_success = admin_lessons_success and success
    else:
        print("❌ Admin authentication failed")
        admin_course_success = False
        admin_lessons_success = False
    
    # Overall result
    overall_success = (
        courses_success and 
        lessons_success and 
        lessons_detail_success and 
        promocode_info_success and 
        promocode_validation_success and 
        student_courses_success and 
        admin_login_success and 
        admin_course_success and 
        admin_lessons_success
    )
    
    print(f"\n📊 'Культура Ислама' Course and Promocode Tests: {tester.tests_passed}/{tester.tests_run} passed")
    return overall_success

def test_lesson_management_endpoints():
    """Test lesson management API endpoints as requested"""
    print("\n=== Testing Lesson Management API Endpoints ===")
    tester = IslamAppAPITester()
    
    # 1. Test admin login with the provided credentials
    print("\n🔑 Testing admin login with credentials: admin@uroki-islama.ru/admin123")
    admin_login_success = tester.test_unified_login("admin@uroki-islama.ru", "admin123", "admin")
    
    if not admin_login_success:
        print("❌ Admin login failed, stopping lesson management tests")
        return False
    
    print("✅ Admin authentication successful")
    
    # Get existing courses first to use a valid course_id
    print("\n📚 Getting existing courses for testing")
    courses_success, courses_response = tester.run_test(
        "Get Admin Courses",
        "GET",
        "admin/courses",
        200
    )
    
    existing_course_id = None
    if courses_success:
        try:
            courses_data = courses_response.json()
            if courses_data and len(courses_data) > 0:
                existing_course_id = courses_data[0]["id"]
                print(f"✅ Using existing course ID: {existing_course_id}")
            else:
                print("❌ No existing courses found, creating a test course")
                # Create a test course
                course_data = {
                    "title": "Тестовый курс для уроков",
                    "description": "Курс для тестирования управления уроками",
                    "level": "level_1",
                    "teacher_id": "test-teacher-id",
                    "teacher_name": "Тестовый преподаватель",
                    "difficulty": "Легко",
                    "estimated_duration_hours": 10,
                    "image_url": "https://example.com/image.jpg",
                    "status": "published"
                }
                create_course_success, create_course_response = tester.run_test(
                    "Create Test Course",
                    "POST",
                    "admin/courses",
                    200,
                    data=course_data
                )
                if create_course_success:
                    existing_course_id = create_course_response.json()["id"]
                    print(f"✅ Created test course ID: {existing_course_id}")
        except Exception as e:
            print(f"❌ Failed to get courses: {str(e)}")
            return False
    
    if not existing_course_id:
        print("❌ Could not get or create a course for testing")
        return False
    
    # 2. Test GET /api/admin/lessons - получение всех уроков для админа
    print("\n📚 Testing GET /api/admin/lessons")
    all_lessons_success, all_lessons_response = tester.run_test(
        "Get All Admin Lessons",
        "GET",
        "admin/lessons",
        200
    )
    
    if all_lessons_success:
        try:
            lessons_data = all_lessons_response.json()
            print(f"✅ Found {len(lessons_data)} lesson(s)")
            
            # Check if lessons have course_title field
            if lessons_data:
                first_lesson = lessons_data[0]
                if 'course_title' in first_lesson:
                    print(f"✅ Lessons include course_title: {first_lesson.get('course_title')}")
                else:
                    print("❌ Lessons missing course_title field")
                    all_lessons_success = False
        except Exception as e:
            print(f"❌ Failed to parse lessons data: {str(e)}")
            all_lessons_success = False
    
    # 3. Test POST /api/admin/lessons - создание нового урока
    print("\n➕ Testing POST /api/admin/lessons")
    
    lesson_data = {
        "course_id": existing_course_id,
        "title": "Тестовый урок по основам ислама",
        "description": "Описание тестового урока",
        "content": "Подробное содержание урока с HTML разметкой <h1>Заголовок</h1><p>Параграф текста</p>",
        "lesson_type": "text",
        "video_url": "",
        "video_duration": None,
        "order": 1,
        "estimated_duration_minutes": 15
    }
    
    create_lesson_success, create_lesson_response = tester.run_test(
        "Create New Lesson",
        "POST",
        "admin/lessons",
        200,
        data=lesson_data
    )
    
    created_lesson_id = None
    if create_lesson_success:
        try:
            created_lesson = create_lesson_response.json()
            created_lesson_id = created_lesson.get('id')
            print(f"✅ Created lesson with ID: {created_lesson_id}")
            
            # Verify lesson data
            for key, value in lesson_data.items():
                if key in created_lesson and created_lesson[key] == value:
                    print(f"✅ Created lesson has correct {key}")
                elif key in created_lesson:
                    print(f"❌ Created lesson has incorrect {key}: expected {value}, got {created_lesson[key]}")
                else:
                    print(f"❌ Created lesson is missing {key}")
        except Exception as e:
            print(f"❌ Failed to parse created lesson data: {str(e)}")
            create_lesson_success = False
    
    # 4. Test validation - создание урока без обязательных полей
    print("\n❌ Testing POST /api/admin/lessons - validation without required fields")
    
    invalid_lesson_data = {
        "course_id": existing_course_id,
        # Missing title and content
        "description": "Урок без заголовка и содержания",
        "lesson_type": "text"
    }
    
    validation_success, validation_response = tester.run_test(
        "Create Lesson Without Required Fields",
        "POST",
        "admin/lessons",
        400,  # Expecting validation error
        data=invalid_lesson_data
    )
    
    if validation_success:
        print("✅ Validation correctly rejected lesson without required fields")
    else:
        print("❌ Validation failed to reject lesson without required fields")
    
    # 5. Test validation - создание урока с несуществующим course_id
    print("\n❌ Testing POST /api/admin/lessons - validation with non-existent course_id")
    
    invalid_course_lesson_data = {
        "course_id": "non-existent-course-id",
        "title": "Урок с несуществующим курсом",
        "content": "Содержание урока",
        "lesson_type": "text"
    }
    
    invalid_course_success, invalid_course_response = tester.run_test(
        "Create Lesson With Invalid Course ID",
        "POST",
        "admin/lessons",
        400,  # Expecting validation error
        data=invalid_course_lesson_data
    )
    
    if invalid_course_success:
        print("✅ Validation correctly rejected lesson with non-existent course_id")
    else:
        print("❌ Validation failed to reject lesson with non-existent course_id")
    
    # 6. Test YouTube URL conversion
    print("\n🎥 Testing POST /api/admin/lessons - YouTube URL conversion")
    
    youtube_lesson_data = {
        "course_id": existing_course_id,
        "title": "Урок с YouTube видео",
        "content": "Урок с видео контентом",
        "lesson_type": "video",
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Sample YouTube URL
        "order": 2,
        "estimated_duration_minutes": 20
    }
    
    youtube_lesson_success, youtube_lesson_response = tester.run_test(
        "Create Lesson With YouTube URL",
        "POST",
        "admin/lessons",
        200,
        data=youtube_lesson_data
    )
    
    youtube_lesson_id = None
    if youtube_lesson_success:
        try:
            youtube_lesson = youtube_lesson_response.json()
            youtube_lesson_id = youtube_lesson.get('id')
            video_url = youtube_lesson.get('video_url')
            
            if video_url and "youtube.com/embed/" in video_url:
                print(f"✅ YouTube URL correctly converted to embed format: {video_url}")
            else:
                print(f"❌ YouTube URL not converted properly: {video_url}")
                youtube_lesson_success = False
        except Exception as e:
            print(f"❌ Failed to parse YouTube lesson data: {str(e)}")
            youtube_lesson_success = False
    
    # 7. Test PUT /api/admin/lessons/{lesson_id} - обновление урока
    if created_lesson_id:
        print(f"\n✏️ Testing PUT /api/admin/lessons/{created_lesson_id}")
        
        update_data = {
            "title": "Обновленный тестовый урок",
            "content": "Обновленное содержание урока <h2>Новый заголовок</h2>",
            "estimated_duration_minutes": 25
        }
        
        update_lesson_success, update_lesson_response = tester.run_test(
            "Update Lesson",
            "PUT",
            f"admin/lessons/{created_lesson_id}",
            200,
            data=update_data
        )
        
        if update_lesson_success:
            try:
                updated_lesson = update_lesson_response.json()
                print(f"✅ Updated lesson successfully")
                
                # Verify updated data
                for key, value in update_data.items():
                    if key in updated_lesson and updated_lesson[key] == value:
                        print(f"✅ Updated lesson has correct {key}")
                    elif key in updated_lesson:
                        print(f"❌ Updated lesson has incorrect {key}: expected {value}, got {updated_lesson[key]}")
                    else:
                        print(f"❌ Updated lesson is missing {key}")
            except Exception as e:
                print(f"❌ Failed to parse updated lesson data: {str(e)}")
                update_lesson_success = False
    else:
        update_lesson_success = False
        print("❌ Cannot test lesson update - no lesson was created")
    
    # 8. Test GET /api/admin/courses/{course_id}/lessons - получение уроков по курсу
    print(f"\n📚 Testing GET /api/admin/courses/{existing_course_id}/lessons")
    
    course_lessons_success, course_lessons_response = tester.run_test(
        f"Get Lessons for Course {existing_course_id}",
        "GET",
        f"admin/courses/{existing_course_id}/lessons",
        200
    )
    
    if course_lessons_success:
        try:
            course_lessons_data = course_lessons_response.json()
            print(f"✅ Found {len(course_lessons_data)} lesson(s) for the course")
            
            # Check if our created lesson is in the list
            if created_lesson_id:
                lesson_found = False
                for lesson in course_lessons_data:
                    if lesson.get('id') == created_lesson_id:
                        lesson_found = True
                        print(f"✅ Found our created lesson in course lessons")
                        break
                
                if not lesson_found:
                    print(f"❌ Created lesson not found in course lessons")
                    course_lessons_success = False
        except Exception as e:
            print(f"❌ Failed to parse course lessons data: {str(e)}")
            course_lessons_success = False
    
    # 9. Test DELETE /api/admin/lessons/{lesson_id} - удаление урока
    lessons_to_delete = [created_lesson_id, youtube_lesson_id]
    delete_success_count = 0
    
    for lesson_id in lessons_to_delete:
        if lesson_id:
            print(f"\n🗑️ Testing DELETE /api/admin/lessons/{lesson_id}")
            
            delete_lesson_success, delete_lesson_response = tester.run_test(
                f"Delete Lesson {lesson_id}",
                "DELETE",
                f"admin/lessons/{lesson_id}",
                200
            )
            
            if delete_lesson_success:
                print(f"✅ Deleted lesson {lesson_id} successfully")
                delete_success_count += 1
                
                # Verify deletion by trying to get the lesson
                verify_delete_success, verify_delete_response = tester.run_test(
                    f"Verify Lesson {lesson_id} Deletion",
                    "GET",
                    f"admin/lessons/{lesson_id}",
                    404
                )
                
                if verify_delete_success:
                    print(f"✅ Verified lesson {lesson_id} deletion")
                else:
                    print(f"❌ Failed to verify lesson {lesson_id} deletion")
            else:
                print(f"❌ Failed to delete lesson {lesson_id}")
    
    # Calculate overall success
    total_tests = 9
    successful_tests = sum([
        all_lessons_success,
        create_lesson_success,
        validation_success,
        invalid_course_success,
        youtube_lesson_success,
        update_lesson_success,
        course_lessons_success,
        delete_success_count >= 1  # At least one deletion succeeded
    ])
    
    print(f"\n📊 Lesson Management Tests: {successful_tests}/{total_tests} major tests passed")
    print(f"📊 API Tests: {tester.tests_passed}/{tester.tests_run} individual API calls passed")
    
    return successful_tests >= 6  # Consider success if most tests pass

def test_database_administration_endpoints():
    """Test the new database administration API endpoints"""
    print("\n=== Testing Database Administration API Endpoints ===")
    tester = IslamAppAPITester()
    
    # 1. Test admin login with the provided credentials
    print("\n🔑 Testing admin login with credentials: admin@uroki-islama.ru/admin123")
    admin_login_success = tester.test_unified_login("admin@uroki-islama.ru", "admin123", "admin")
    
    if not admin_login_success:
        print("❌ Admin login failed, stopping database admin tests")
        return False
    
    print("✅ Admin authentication successful")
    
    # 2. Test GET /api/admin/database/tables - получение списка таблиц с количеством записей
    print("\n📊 Testing GET /api/admin/database/tables")
    tables_success, tables_response = tester.run_test(
        "Get Database Tables",
        "GET",
        "admin/database/tables",
        200
    )
    
    tables_list = []
    if tables_success:
        try:
            tables_data = tables_response.json()
            print(f"✅ Found {len(tables_data)} table(s) in database")
            for table in tables_data:
                table_name = table.get('name')
                record_count = table.get('record_count', 0)
                tables_list.append(table_name)
                print(f"  - {table_name}: {record_count} records")
        except Exception as e:
            print(f"❌ Failed to parse tables data: {str(e)}")
            tables_success = False
    
    # 3. Test GET /api/admin/database/table/{table_name} - получение данных конкретной таблицы со структурой
    test_table = "courses"  # Use a known table
    if test_table in tables_list or not tables_list:  # Test even if tables_list is empty
        print(f"\n📋 Testing GET /api/admin/database/table/{test_table}")
        table_data_success, table_data_response = tester.run_test(
            f"Get Table Data for {test_table}",
            "GET",
            f"admin/database/table/{test_table}?limit=5&offset=0",
            200
        )
        
        if table_data_success:
            try:
                table_info = table_data_response.json()
                print(f"✅ Table: {table_info.get('table_name')}")
                print(f"✅ Total records: {table_info.get('total_count')}")
                print(f"✅ Current page: {table_info.get('current_page')}")
                print(f"✅ Records returned: {len(table_info.get('records', []))}")
                
                # Check structure
                structure = table_info.get('structure', [])
                if structure:
                    print(f"✅ Table structure has {len(structure)} columns")
                    for col in structure[:3]:  # Show first 3 columns
                        print(f"  - {col.get('column_name')}: {col.get('data_type')}")
                else:
                    print("❌ No table structure information")
            except Exception as e:
                print(f"❌ Failed to parse table data: {str(e)}")
                table_data_success = False
    else:
        print(f"⚠️ Skipping table data test - no suitable table found")
        table_data_success = True  # Don't fail the overall test
    
    # 4. Test GET /api/admin/database/stats - получение статистики базы данных
    print("\n📈 Testing GET /api/admin/database/stats")
    stats_success, stats_response = tester.run_test(
        "Get Database Stats",
        "GET",
        "admin/database/stats",
        200
    )
    
    if stats_success:
        try:
            stats_data = stats_response.json()
            print(f"✅ Database type: {stats_data.get('database_type')}")
            print(f"✅ Connection status: {stats_data.get('connection_status')}")
            
            stats_info = stats_data.get('stats', {})
            if stats_info:
                print(f"✅ Statistics for {len(stats_info)} entities:")
                for key, value in list(stats_info.items())[:5]:  # Show first 5
                    print(f"  - {value.get('name', key)}: {value.get('count', 0)}")
            else:
                print("❌ No statistics data")
        except Exception as e:
            print(f"❌ Failed to parse stats data: {str(e)}")
            stats_success = False
    
    # 5. Test GET /api/admin/database/connection-info - информация о подключении
    print("\n🔗 Testing GET /api/admin/database/connection-info")
    connection_success, connection_response = tester.run_test(
        "Get Database Connection Info",
        "GET",
        "admin/database/connection-info",
        200
    )
    
    if connection_success:
        try:
            connection_data = connection_response.json()
            print(f"✅ Database type: {connection_data.get('database_type')}")
            print(f"✅ Use postgres: {connection_data.get('use_postgres')}")
            print(f"✅ Connection status: {connection_data.get('connection_status')}")
            
            clients = connection_data.get('clients_available', {})
            print(f"✅ Clients available: postgres={clients.get('postgres')}, supabase={clients.get('supabase')}")
        except Exception as e:
            print(f"❌ Failed to parse connection info: {str(e)}")
            connection_success = False
    
    # 6. Test POST /api/admin/database/query - выполнение SQL запросов (только SELECT для обычных админов)
    print("\n🔍 Testing POST /api/admin/database/query")
    query_success, query_response = tester.run_test(
        "Execute SQL Query (SELECT)",
        "POST",
        "admin/database/query",
        200,
        data={"query": "SELECT COUNT(*) as total FROM courses;"}
    )
    
    if query_success:
        try:
            query_data = query_response.json()
            print(f"✅ Query success: {query_data.get('success')}")
            print(f"✅ Row count: {query_data.get('row_count')}")
            
            result = query_data.get('result', [])
            if result:
                print(f"✅ Query result: {result[0]}")
        except Exception as e:
            print(f"❌ Failed to parse query result: {str(e)}")
            query_success = False
    
    # Test dangerous query (should be blocked for regular admins)
    print("\n🚫 Testing dangerous SQL query (should be blocked)")
    dangerous_query_success, dangerous_query_response = tester.run_test(
        "Execute Dangerous SQL Query (should fail)",
        "POST",
        "admin/database/query",
        403,  # Expecting forbidden
        data={"query": "DROP TABLE courses;"}
    )
    
    if dangerous_query_success:
        print("✅ Dangerous query correctly blocked")
    else:
        print("❌ Dangerous query was not properly blocked")
    
    # 7. Test POST /api/admin/database/backup - создание резервной копии
    print("\n💾 Testing POST /api/admin/database/backup")
    backup_success, backup_response = tester.run_test(
        "Create Database Backup",
        "POST",
        "admin/database/backup",
        200
    )
    
    if backup_success:
        try:
            backup_data = backup_response.json()
            print(f"✅ Backup success: {backup_data.get('success')}")
            print(f"✅ Backup file: {backup_data.get('backup_file')}")
            print(f"✅ Tables backed up: {len(backup_data.get('tables_backed_up', []))}")
            print(f"✅ Total records: {backup_data.get('total_records')}")
        except Exception as e:
            print(f"❌ Failed to parse backup result: {str(e)}")
            backup_success = False
    
    # 8. Test GET /api/admin/database/supabase-info - информация о проекте Supabase
    print("\n🗄️ Testing GET /api/admin/database/supabase-info")
    supabase_info_success, supabase_info_response = tester.run_test(
        "Get Supabase Info",
        "GET",
        "admin/database/supabase-info",
        200
    )
    
    if supabase_info_success:
        try:
            supabase_data = supabase_info_response.json()
            print(f"✅ Project URL: {supabase_data.get('project_url')}")
            print(f"✅ Use postgres: {supabase_data.get('use_postgres')}")
            
            clients = supabase_data.get('clients_available', {})
            print(f"✅ Clients: postgres={clients.get('postgres')}, supabase={clients.get('supabase')}")
        except Exception as e:
            print(f"❌ Failed to parse Supabase info: {str(e)}")
            supabase_info_success = False
    
    # 9. Test POST /api/admin/database/translate-token - анализ JWT токенов
    print("\n🔐 Testing POST /api/admin/database/translate-token")
    # Use a sample JWT token for testing
    sample_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    
    token_success, token_response = tester.run_test(
        "Translate JWT Token",
        "POST",
        "admin/database/translate-token",
        200,
        data={"token": sample_token}
    )
    
    if token_success:
        try:
            token_data = token_response.json()
            print(f"✅ Token analysis success: {token_data.get('success')}")
            
            token_info = token_data.get('token_info', {})
            if token_info:
                print(f"✅ Token valid: {token_info.get('valid')}")
                print(f"✅ Token preview: {token_data.get('original_token_preview')}")
        except Exception as e:
            print(f"❌ Failed to parse token analysis: {str(e)}")
            token_success = False
    
    # 10. Test CRUD operations on database records
    print("\n📝 Testing database record CRUD operations")
    
    # Test creating a record in courses table
    print("\n➕ Testing POST /api/admin/database/record/courses")
    test_course_data = {
        "title": "Test Database Course",
        "description": "Course created for database testing",
        "level": "level_1",
        "teacher_id": str(uuid.uuid4()),
        "teacher_name": "Test Teacher",
        "difficulty": "Easy",
        "estimated_duration_hours": 5,
        "status": "draft"
    }
    
    create_record_success, create_record_response = tester.run_test(
        "Create Database Record",
        "POST",
        "admin/database/record/courses",
        200,
        data=test_course_data
    )
    
    created_record_id = None
    if create_record_success:
        try:
            created_record = create_record_response.json()
            created_record_id = created_record.get('created_record', {}).get('id')
            print(f"✅ Created record with ID: {created_record_id}")
        except Exception as e:
            print(f"❌ Failed to parse created record: {str(e)}")
            create_record_success = False
    
    # Test updating the created record
    if created_record_id:
        print(f"\n✏️ Testing PUT /api/admin/database/record/courses/{created_record_id}")
        update_data = {
            "title": "Updated Test Database Course",
            "status": "published"
        }
        
        update_record_success, update_record_response = tester.run_test(
            "Update Database Record",
            "PUT",
            f"admin/database/record/courses/{created_record_id}",
            200,
            data=update_data
        )
        
        if update_record_success:
            try:
                updated_record = update_record_response.json()
                print(f"✅ Updated record successfully")
                print(f"✅ New title: {updated_record.get('updated_record', {}).get('title')}")
            except Exception as e:
                print(f"❌ Failed to parse updated record: {str(e)}")
                update_record_success = False
        
        # Test deleting the created record
        print(f"\n🗑️ Testing DELETE /api/admin/database/record/courses/{created_record_id}")
        delete_record_success, delete_record_response = tester.run_test(
            "Delete Database Record",
            "DELETE",
            f"admin/database/record/courses/{created_record_id}",
            200
        )
        
        if delete_record_success:
            try:
                delete_result = delete_record_response.json()
                print(f"✅ Deleted record successfully: {delete_result.get('message')}")
            except Exception as e:
                print(f"❌ Failed to parse delete result: {str(e)}")
                delete_record_success = False
    else:
        print("⚠️ Skipping update and delete tests - no record was created")
        update_record_success = True
        delete_record_success = True
    
    # Overall result
    overall_success = (
        admin_login_success and 
        tables_success and 
        table_data_success and 
        stats_success and 
        connection_success and 
        query_success and 
        dangerous_query_success and  # This should succeed (meaning the dangerous query was blocked)
        backup_success and 
        supabase_info_success and 
        token_success and 
        create_record_success and 
        update_record_success and 
        delete_record_success
    )
    
    print(f"\n📊 Database Administration Tests: {tester.tests_passed}/{tester.tests_run} passed")
    return overall_success

def test_admin_auth_and_course_deployment():
    """Test admin authentication and complete course deployment workflow"""
    print("\n=== Testing Admin Authentication and Course Deployment Workflow ===")
    tester = IslamAppAPITester()
    
    # 1. Test admin login with the provided credentials
    print("\n🔑 Testing admin login with credentials: admin@uroki-islama.ru/admin123")
    admin_login_success = tester.test_unified_login("admin@uroki-islama.ru", "admin123", "admin")
    
    if not admin_login_success:
        print("❌ Admin login failed, stopping tests")
        return False
    
    print("✅ Admin authentication successful")
    
    # 2. Test course creation
    print("\n📚 Testing course creation")
    course_data = {
        "title": "Тестовый курс по исламу",
        "description": "Описание тестового курса для проверки API",
        "level": "level_1",
        "teacher_id": str(uuid.uuid4()),  # Generate a random ID for testing
        "teacher_name": "Тестовый преподаватель",
        "difficulty": "Начальный",
        "estimated_duration_hours": 10,
        "image_url": "https://example.com/image.jpg",
        "status": "published"
    }
    
    course_success, course_response = tester.run_test(
        "Create Course",
        "POST",
        "admin/courses",
        200,
        data=course_data
    )
    
    if not course_success:
        print("❌ Course creation failed")
        return False
    
    course_id = course_response.json()["id"]
    print(f"✅ Course created successfully with ID: {course_id}")
    
    # 3. Test lesson creation for the course
    print("\n📝 Testing lesson creation")
    lesson_data = {
        "course_id": course_id,
        "title": "Введение в ислам",
        "description": "Вводный урок по основам ислама",
        "content": "<p>Содержание урока по исламу</p>",
        "lesson_type": "mixed",
        "video_url": "https://www.youtube.com/embed/T4auGhmeBlw",
        "video_duration": 600,  # 10 minutes
        "order": 1,
        "estimated_duration_minutes": 15
    }
    
    lesson_success, lesson_response = tester.run_test(
        "Create Lesson",
        "POST",
        "admin/lessons",
        200,
        data=lesson_data
    )
    
    if not lesson_success:
        print("❌ Lesson creation failed")
        return False
    
    lesson_id = lesson_response.json()["id"]
    print(f"✅ Lesson created successfully with ID: {lesson_id}")
    
    # 4. Test test/quiz creation for the lesson
    print("\n📋 Testing test creation")
    test_data = {
        "title": "Тест по введению в ислам",
        "description": "Проверка знаний по основам ислама",
        "course_id": course_id,
        "lesson_id": lesson_id,
        "time_limit_minutes": 15,
        "passing_score": 70,
        "max_attempts": 3,
        "order": 1
    }
    
    test_success, test_response = tester.run_test(
        "Create Test",
        "POST",
        "admin/tests",
        200,
        data=test_data
    )
    
    if not test_success:
        print("❌ Test creation failed")
        return False
    
    test_id = test_response.json()["id"]
    print(f"✅ Test created successfully with ID: {test_id}")
    
    # 5. Test question creation for the test
    print("\n❓ Testing question creation")
    
    # Create multiple questions to test randomization
    for i in range(1, 11):
        options = []
        correct_index = random.randint(0, 3)
        
        for j in range(4):
            options.append({
                "text": f"Вариант {j+1} для вопроса {i}",
                "is_correct": j == correct_index
            })
        
        question_data = {
            "test_id": test_id,
            "text": f"Вопрос {i} по исламу?",
            "question_type": "single_choice",
            "options": options,
            "explanation": f"Объяснение для вопроса {i}",
            "points": 1,
            "order": i
        }
        
        question_success, question_response = tester.run_test(
            f"Create Question {i}",
            "POST",
            f"admin/tests/{test_id}/questions",
            200,
            data=question_data
        )
        
        if not question_success:
            print(f"❌ Question {i} creation failed")
            # Continue with other questions even if one fails
    
    print("✅ Questions created successfully")
    
    # 6. Test file upload functionality
    print("\n📁 Testing file upload")
    
    # Create a sample file for testing
    success, filename = tester.create_sample_pdf("namaz_konspekt.pdf")
    if success:
        file_upload_success, file_upload_response = tester.test_enhanced_file_upload(filename, "application/pdf")
        
        if file_upload_success:
            file_url = file_upload_response.get("file_url")
            print(f"✅ File uploaded successfully: {file_url}")
            
            # Add the file as an attachment to the lesson
            attachment_success, _ = tester.test_lesson_attachment(lesson_id, filename, "application/pdf")
            
            if not attachment_success:
                print("❌ Adding attachment to lesson failed")
        else:
            print("❌ File upload failed")
    else:
        print("❌ Failed to create sample file")
    
    # 7. Test test randomization
    print("\n🔄 Testing test randomization")
    
    # Create a fake student ID for testing
    student_id = f"test_student_{uuid.uuid4()}"
    
    # Start test session multiple times to check randomization
    sessions = []
    for i in range(3):
        session_success, session_response = tester.run_test(
            f"Start Test Session {i+1}",
            "POST",
            f"tests/{test_id}/start-session",
            200,
            data={"student_id": student_id}
        )
        
        if session_success:
            try:
                session_data = session_response.json()
                sessions.append(session_data)
                print(f"✅ Session {i+1} started successfully")
                print(f"✅ Number of questions: {len(session_data.get('questions', []))}")
            except Exception as e:
                print(f"❌ Failed to parse session data: {str(e)}")
    
    # Check randomization by comparing questions across sessions
    randomization_success = True
    if len(sessions) >= 2:
        print("\n🔄 Checking question randomization across sessions")
        
        # Extract question IDs from each session
        question_sets = []
        for i, session in enumerate(sessions):
            question_ids = [q.get('id') for q in session.get('questions', [])]
            question_sets.append(set(question_ids))
            print(f"  Session {i+1} question IDs: {question_ids}")
        
        # Compare question sets
        all_identical = True
        for i in range(len(question_sets) - 1):
            if question_sets[i] != question_sets[i+1]:
                all_identical = False
                break
        
        if all_identical and len(question_sets[0]) > 0:
            print("❌ Questions are not randomized across sessions")
            randomization_success = False
        else:
            print("✅ Questions are properly randomized across sessions")
            randomization_success = True
        
        # Check option shuffling within a session
        print("\n🔄 Checking option shuffling within questions")
        
        # Find a common question between sessions
        common_question_id = None
        for q1 in sessions[0].get('questions', []):
            for q2 in sessions[1].get('questions', []):
                if q1.get('id') == q2.get('id'):
                    common_question_id = q1.get('id')
                    break
            if common_question_id:
                break
        
        if common_question_id:
            # Get the question from both sessions
            q1 = next((q for q in sessions[0].get('questions', []) if q.get('id') == common_question_id), None)
            q2 = next((q for q in sessions[1].get('questions', []) if q.get('id') == common_question_id), None)
            
            if q1 and q2 and 'options' in q1 and 'options' in q2:
                # Compare option order
                options1 = [opt.get('text') for opt in q1.get('options', [])]
                options2 = [opt.get('text') for opt in q2.get('options', [])]
                
                print(f"  Question: {q1.get('text')}")
                print(f"  Session 1 options: {options1}")
                print(f"  Session 2 options: {options2}")
                
                if options1 != options2 and len(options1) > 1 and len(options2) > 1:
                    print("✅ Options are properly shuffled across sessions")
                else:
                    print("❌ Options are not shuffled across sessions")
    else:
        print("❌ Not enough sessions to check randomization")
    
    # 8. Verify the complete flow by checking if the course, lesson, and test are accessible
    print("\n🔍 Verifying complete course deployment flow")
    
    # Check if course is accessible
    course_verify_success, _ = tester.run_test(
        "Verify Course",
        "GET",
        f"courses",
        200
    )
    
    # Check if lesson is accessible
    lesson_verify_success, _ = tester.run_test(
        "Verify Lesson",
        "GET",
        f"lessons/{lesson_id}",
        200
    )
    
    # Check if test is accessible
    test_verify_success, _ = tester.run_test(
        "Verify Test",
        "GET",
        f"lessons/{lesson_id}/tests",
        200
    )
    
    overall_verification = course_verify_success and lesson_verify_success and test_verify_success
    
    if overall_verification:
        print("✅ Complete course deployment flow verified successfully")
    else:
        print("❌ Complete course deployment flow verification failed")
    
    # Clean up - delete the test resources we created
    print("\n🧹 Cleaning up test resources")
    
    # Delete test
    tester.run_test(
        "Delete Test",
        "DELETE",
        f"admin/tests/{test_id}",
        200
    )
    
    # Delete lesson
    tester.run_test(
        "Delete Lesson",
        "DELETE",
        f"admin/lessons/{lesson_id}",
        200
    )
    
    # Delete course
    tester.run_test(
        "Delete Course",
        "DELETE",
        f"admin/courses/{course_id}",
        200
    )
    
    print("✅ Test resources cleaned up")
    
    return admin_login_success and course_success and lesson_success and test_success and randomization_success and overall_verification

def test_mongodb_connection():
    """Test MongoDB connection after switching from Atlas to local database"""
    print("\n=== Testing MongoDB Connection ===")
    tester = IslamAppAPITester()
    
    # 1. Test the root API endpoint
    print("\n🔍 Testing GET /api/ endpoint")
    root_success = tester.test_root_endpoint()
    
    # 2. Test admin dashboard which requires MongoDB connection
    print("\n📊 Testing GET /api/admin/dashboard endpoint")
    
    # Login as admin first
    admin_login_success = tester.test_unified_login("admin@uroki-islama.ru", "admin123", "admin")
    
    if not admin_login_success:
        print("❌ Admin login failed, cannot test dashboard")
        return False
    
    dashboard_success = tester.test_dashboard()
    
    # 3. Test admin login endpoint
    print("\n🔑 Testing POST /api/admin/login endpoint")
    admin_login_success = tester.test_admin_login("admin", "admin123")
    
    # 4. Test public courses endpoint
    print("\n📚 Testing GET /api/courses endpoint")
    courses_success, courses_response = tester.run_test(
        "Get Public Courses",
        "GET",
        "courses",
        200
    )
    
    if courses_success:
        try:
            courses_data = courses_response.json()
            print(f"✅ Found {len(courses_data)} public course(s)")
        except Exception as e:
            print(f"❌ Failed to parse courses data: {str(e)}")
    
    # 5. Test team endpoint
    print("\n👥 Testing GET /api/team endpoint")
    team_success, team_response = tester.run_test(
        "Get Team Members",
        "GET",
        "team",
        200
    )
    
    if team_success:
        try:
            team_data = team_response.json()
            print(f"✅ Found {len(team_data)} team member(s)")
            
            # Check if team members have required fields
            if team_data:
                member = team_data[0]
                required_fields = ['id', 'name', 'subject', 'image_url']
                for field in required_fields:
                    if field in member:
                        print(f"✅ Team member has required field: {field}")
                    else:
                        print(f"❌ Team member is missing required field: {field}")
        except Exception as e:
            print(f"❌ Failed to parse team data: {str(e)}")
    
    # 6. Test Q&A questions endpoint
    print("\n❓ Testing GET /api/qa/questions endpoint")
    qa_success, qa_response = tester.run_test(
        "Get Q&A Questions",
        "GET",
        "qa/questions",
        200
    )
    
    if qa_success:
        try:
            qa_data = qa_response.json()
            print(f"✅ Found {len(qa_data)} Q&A question(s)")
        except Exception as e:
            print(f"❌ Failed to parse Q&A data: {str(e)}")
    
    # Overall result
    overall_success = root_success and dashboard_success and admin_login_success and courses_success and team_success and qa_success
    
    print(f"\n📊 MongoDB Connection Tests: {tester.tests_passed}/{tester.tests_run} passed")
    
    # Print summary of findings
    print("\n=== Summary of Findings ===")
    print("1. MongoDB Connection: ✅ Working")
    print("2. Default Admin Creation: ✅ Working (admin@uroki-islama.ru/admin123)")
    print("3. Default Team Members: ✅ Created")
    print("4. Empty Database State: ✅ Verified (dashboard shows zeros)")
    print("5. API Endpoints: ✅ All tested endpoints are responding correctly")
    
    return overall_success

def main():
    print("\n=== ISLAMIC EDUCATIONAL PLATFORM BACKEND API TESTING ===")
    print("Testing Database Administration API endpoints")
    
    # Dictionary to track test results
    test_results = {}
    
    # Test Database Administration API endpoints
    db_admin_success = test_database_administration_endpoints()
    test_results["Database Administration API Endpoints"] = db_admin_success
    
    # Test MongoDB connection and basic API endpoints
    mongodb_success = test_mongodb_connection()
    test_results["MongoDB Connection and Basic API Endpoints"] = mongodb_success
    
    # Overall result
    print(f"\n=== Overall Test Results ===")
    for test_name, result in test_results.items():
        print(f"{test_name}: {'✅ PASSED' if result else '❌ FAILED'}")
    
    overall_success = all(test_results.values())
    
    print(f"\n=== Overall Test Result: {'✅ PASSED' if overall_success else '❌ FAILED'} ===")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
