import requests
import sys
import json
import uuid
import random
from datetime import datetime

class QAAPITester:
    def __init__(self, base_url="https://a72883f7-06a9-42f3-b4a4-18cd6085e38a.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.token = None
        self.admin_token = None
        self.created_question_id = None

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
                        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
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

    def admin_login(self, username="admin", password="admin123"):
        """Login as admin to get token"""
        print(f"\n🔑 Logging in as admin: {username}")
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "admin/login",
            200,
            data={"username": username, "password": password}
        )
        
        if success:
            try:
                self.admin_token = response.json().get('access_token')
                self.token = self.admin_token  # Set as default token
                print(f"✅ Admin login successful")
                return True
            except Exception as e:
                print(f"❌ Failed to extract token: {str(e)}")
                return False
        return False

    def test_get_qa_questions(self):
        """Test GET /api/qa/questions endpoint"""
        success, response = self.run_test(
            "Get Q&A Questions",
            "GET",
            "qa/questions",
            200
        )
        
        if success:
            try:
                questions = response.json()
                print(f"✅ Retrieved {len(questions)} questions")
                return True, questions
            except Exception as e:
                print(f"❌ Failed to parse response: {str(e)}")
                return False, None
        return False, None

    def test_get_qa_question_by_id(self, question_id):
        """Test GET /api/qa/questions/{question_id} endpoint"""
        success, response = self.run_test(
            f"Get Q&A Question by ID: {question_id}",
            "GET",
            f"qa/questions/{question_id}",
            200
        )
        
        if success:
            try:
                question = response.json()
                print(f"✅ Retrieved question: {question.get('title')}")
                
                # Check if views_count increased
                print(f"✅ Views count: {question.get('views_count')}")
                return True, question
            except Exception as e:
                print(f"❌ Failed to parse response: {str(e)}")
                return False, None
        return False, None

    def test_get_qa_question_by_slug(self, slug):
        """Test GET /api/qa/questions/slug/{slug} endpoint"""
        success, response = self.run_test(
            f"Get Q&A Question by Slug: {slug}",
            "GET",
            f"qa/questions/slug/{slug}",
            200
        )
        
        if success:
            try:
                question = response.json()
                print(f"✅ Retrieved question by slug: {question.get('title')}")
                
                # Check if views_count increased
                print(f"✅ Views count: {question.get('views_count')}")
                return True, question
            except Exception as e:
                print(f"❌ Failed to parse response: {str(e)}")
                return False, None
        return False, None

    def test_get_qa_categories(self):
        """Test GET /api/qa/categories endpoint"""
        success, response = self.run_test(
            "Get Q&A Categories",
            "GET",
            "qa/categories",
            200
        )
        
        if success:
            try:
                categories = response.json()
                print(f"✅ Retrieved {len(categories)} categories")
                for category in categories:
                    print(f"  - {category.get('name')} ({category.get('id')}): {category.get('count')} questions")
                return True, categories
            except Exception as e:
                print(f"❌ Failed to parse response: {str(e)}")
                return False, None
        return False, None

    def test_get_featured_questions(self):
        """Test GET /api/qa/featured endpoint"""
        success, response = self.run_test(
            "Get Featured Q&A Questions",
            "GET",
            "qa/featured",
            200
        )
        
        if success:
            try:
                questions = response.json()
                print(f"✅ Retrieved {len(questions)} featured questions")
                for question in questions:
                    print(f"  - {question.get('title')}")
                return True, questions
            except Exception as e:
                print(f"❌ Failed to parse response: {str(e)}")
                return False, None
        return False, None

    def test_get_popular_questions(self):
        """Test GET /api/qa/popular endpoint"""
        success, response = self.run_test(
            "Get Popular Q&A Questions",
            "GET",
            "qa/popular",
            200
        )
        
        if success:
            try:
                questions = response.json()
                print(f"✅ Retrieved {len(questions)} popular questions")
                for question in questions[:3]:  # Show top 3
                    print(f"  - {question.get('title')} (Views: {question.get('views_count')})")
                return True, questions
            except Exception as e:
                print(f"❌ Failed to parse response: {str(e)}")
                return False, None
        return False, None

    def test_get_recent_questions(self):
        """Test GET /api/qa/recent endpoint"""
        success, response = self.run_test(
            "Get Recent Q&A Questions",
            "GET",
            "qa/recent",
            200
        )
        
        if success:
            try:
                questions = response.json()
                print(f"✅ Retrieved {len(questions)} recent questions")
                for question in questions[:3]:  # Show top 3
                    print(f"  - {question.get('title')}")
                return True, questions
            except Exception as e:
                print(f"❌ Failed to parse response: {str(e)}")
                return False, None
        return False, None

    def test_get_qa_stats(self):
        """Test GET /api/qa/stats endpoint"""
        success, response = self.run_test(
            "Get Q&A Stats",
            "GET",
            "qa/stats",
            200
        )
        
        if success:
            try:
                stats = response.json()
                print(f"✅ Total questions: {stats.get('total_questions')}")
                print(f"✅ Featured questions: {stats.get('featured_count')}")
                print(f"✅ Total views: {stats.get('total_views')}")
                
                # Print categories
                print("✅ Questions by category:")
                for category, count in stats.get('questions_by_category', {}).items():
                    print(f"  - {category}: {count}")
                
                # Print most viewed questions
                print("✅ Most viewed questions:")
                for question in stats.get('most_viewed_questions', [])[:3]:
                    print(f"  - {question.get('title')} (Views: {question.get('views')})")
                
                return True, stats
            except Exception as e:
                print(f"❌ Failed to parse response: {str(e)}")
                return False, None
        return False, None

    def test_search_questions(self, search_term):
        """Test GET /api/qa/questions?search={search_term} endpoint"""
        success, response = self.run_test(
            f"Search Q&A Questions for: {search_term}",
            "GET",
            f"qa/questions?search={search_term}",
            200
        )
        
        if success:
            try:
                questions = response.json()
                print(f"✅ Found {len(questions)} questions matching '{search_term}'")
                for question in questions[:3]:  # Show top 3
                    print(f"  - {question.get('title')}")
                return True, questions
            except Exception as e:
                print(f"❌ Failed to parse response: {str(e)}")
                return False, None
        return False, None

    def test_filter_questions_by_category(self, category):
        """Test GET /api/qa/questions?category={category} endpoint"""
        success, response = self.run_test(
            f"Filter Q&A Questions by Category: {category}",
            "GET",
            f"qa/questions?category={category}",
            200
        )
        
        if success:
            try:
                questions = response.json()
                print(f"✅ Found {len(questions)} questions in category '{category}'")
                for question in questions[:3]:  # Show top 3
                    print(f"  - {question.get('title')}")
                return True, questions
            except Exception as e:
                print(f"❌ Failed to parse response: {str(e)}")
                return False, None
        return False, None

    def test_create_question(self, question_data):
        """Test POST /api/admin/qa/questions endpoint"""
        # Save current token
        current_token = self.token
        
        # Use admin token
        self.token = self.admin_token
        
        success, response = self.run_test(
            "Create Q&A Question",
            "POST",
            "admin/qa/questions",
            200,
            data=question_data
        )
        
        # Restore token
        self.token = current_token
        
        if success:
            try:
                question = response.json()
                self.created_question_id = question.get('id')
                print(f"✅ Created question: {question.get('title')}")
                print(f"✅ Question ID: {self.created_question_id}")
                print(f"✅ Slug: {question.get('slug')}")
                return True, question
            except Exception as e:
                print(f"❌ Failed to parse response: {str(e)}")
                return False, None
        return False, None

    def test_update_question(self, question_id, update_data):
        """Test PUT /api/admin/qa/questions/{question_id} endpoint"""
        # Save current token
        current_token = self.token
        
        # Use admin token
        self.token = self.admin_token
        
        success, response = self.run_test(
            f"Update Q&A Question: {question_id}",
            "PUT",
            f"admin/qa/questions/{question_id}",
            200,
            data=update_data
        )
        
        # Restore token
        self.token = current_token
        
        if success:
            try:
                question = response.json()
                print(f"✅ Updated question: {question.get('title')}")
                return True, question
            except Exception as e:
                print(f"❌ Failed to parse response: {str(e)}")
                return False, None
        return False, None

    def test_delete_question(self, question_id):
        """Test DELETE /api/admin/qa/questions/{question_id} endpoint"""
        # Save current token
        current_token = self.token
        
        # Use admin token
        self.token = self.admin_token
        
        success, response = self.run_test(
            f"Delete Q&A Question: {question_id}",
            "DELETE",
            f"admin/qa/questions/{question_id}",
            200
        )
        
        # Restore token
        self.token = current_token
        
        if success:
            try:
                result = response.json()
                print(f"✅ Deleted question: {result.get('message')}")
                return True, result
            except Exception as e:
                print(f"❌ Failed to parse response: {str(e)}")
                return False, None
        return False, None

    def test_get_admin_questions(self):
        """Test GET /api/admin/qa/questions endpoint"""
        # Save current token
        current_token = self.token
        
        # Use admin token
        self.token = self.admin_token
        
        success, response = self.run_test(
            "Get Admin Q&A Questions",
            "GET",
            "admin/qa/questions",
            200
        )
        
        # Restore token
        self.token = current_token
        
        if success:
            try:
                questions = response.json()
                print(f"✅ Retrieved {len(questions)} questions for admin")
                return True, questions
            except Exception as e:
                print(f"❌ Failed to parse response: {str(e)}")
                return False, None
        return False, None

def main():
    print("\n=== Testing Q&A API Endpoints ===")
    tester = QAAPITester()
    
    # Test public endpoints
    print("\n--- Testing Public Q&A Endpoints ---")
    
    # 1. Get all questions
    questions_success, questions = tester.test_get_qa_questions()
    
    # Store a question ID and slug for later tests
    question_id = None
    question_slug = None
    if questions_success and questions:
        question_id = questions[0].get('id')
        question_slug = questions[0].get('slug')
    
    # 2. Get question by ID
    if question_id:
        tester.test_get_qa_question_by_id(question_id)
    else:
        print("❌ No question ID available for testing")
    
    # 3. Get question by slug
    if question_slug:
        tester.test_get_qa_question_by_slug(question_slug)
    else:
        print("❌ No question slug available for testing")
    
    # 4. Get categories
    categories_success, categories = tester.test_get_qa_categories()
    
    # Store a category for filter test
    category = None
    if categories_success and categories:
        category = categories[0].get('id')
    
    # 5. Get featured questions
    tester.test_get_featured_questions()
    
    # 6. Get popular questions
    tester.test_get_popular_questions()
    
    # 7. Get recent questions
    tester.test_get_recent_questions()
    
    # 8. Get stats
    tester.test_get_qa_stats()
    
    # 9. Search questions
    tester.test_search_questions("намаз")
    
    # 10. Filter by category
    if category:
        tester.test_filter_questions_by_category(category)
    else:
        print("❌ No category available for testing")
    
    # Test admin endpoints
    print("\n--- Testing Admin Q&A Endpoints ---")
    
    # Login as admin
    if tester.admin_login():
        # 1. Get admin questions
        tester.test_get_admin_questions()
        
        # 2. Create a new question
        new_question = {
            "title": "Как правильно совершать намаз?",
            "question_text": "Я недавно принял ислам и хочу узнать, как правильно совершать намаз. Какие шаги нужно выполнить?",
            "answer_text": "Намаз состоит из следующих шагов: 1. Совершить омовение (вуду). 2. Встать лицом к Кибле. 3. Сделать намерение (ният). 4. Произнести такбир (Аллаху Акбар). 5. Прочитать суру Аль-Фатиха и еще одну суру. 6. Совершить поясной поклон (руку). 7. Выпрямиться. 8. Совершить земной поклон (саджда). 9. Сесть. 10. Совершить второй земной поклон. 11. Завершить намаз приветствием (салям).",
            "category": "ibadah",
            "tags": ["намаз", "молитва", "ислам"],
            "is_featured": True,
            "imam_name": "Имам Абдуллах",
            "references": ["Сахих аль-Бухари", "Сахих Муслим"]
        }
        
        create_success, created_question = tester.test_create_question(new_question)
        
        # 3. Update the created question
        if create_success and tester.created_question_id:
            update_data = {
                "answer_text": "Намаз состоит из следующих шагов: 1. Совершить омовение (вуду). 2. Встать лицом к Кибле. 3. Сделать намерение (ният). 4. Произнести такбир (Аллаху Акбар). 5. Прочитать суру Аль-Фатиха и еще одну суру. 6. Совершить поясной поклон (руку). 7. Выпрямиться. 8. Совершить земной поклон (саджда). 9. Сесть. 10. Совершить второй земной поклон. 11. Завершить намаз приветствием (салям). Важно выполнять намаз пять раз в день в установленное время.",
                "tags": ["намаз", "молитва", "ислам", "вуду", "кибла"]
            }
            
            update_success, updated_question = tester.test_update_question(tester.created_question_id, update_data)
            
            # 4. Delete the created question
            if update_success:
                tester.test_delete_question(tester.created_question_id)
    
    # Print results
    print(f"\n=== Q&A API Test Results ===")
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Success rate: {tester.tests_passed/tester.tests_run*100:.2f}%")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())