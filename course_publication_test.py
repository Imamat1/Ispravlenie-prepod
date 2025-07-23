import requests
import sys
import json
import uuid
from datetime import datetime

class CoursePublicationTester:
    def __init__(self, base_url="https://8bc1a919-b952-4667-94e5-4aadb2ce50b3.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.token = None
        self.admin_token = None
        self.created_course_id = None

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

    def admin_login(self, username, password):
        """Login as admin and get token"""
        print(f"\n🔑 Logging in as admin with username: {username}")
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "admin/login",
            200,
            data={"username": username, "password": password}
        )
        
        if success:
            try:
                self.token = response.json().get('access_token')
                print(f"✅ Admin login successful, token obtained")
                return True
            except:
                print("❌ Failed to extract token from response")
                return False
        return False

    def get_admin_courses(self):
        """Get all courses in admin panel"""
        print("\n📚 Getting all courses from admin panel")
        success, response = self.run_test(
            "Get Admin Courses",
            "GET",
            "admin/courses",
            200
        )
        
        if success:
            try:
                courses = response.json()
                print(f"✅ Found {len(courses)} courses in admin panel")
                
                # Find a draft course for testing
                draft_course = None
                for course in courses:
                    if course.get('status') == 'draft':
                        draft_course = course
                        break
                
                if draft_course:
                    print(f"✅ Found a draft course: {draft_course.get('title')} (ID: {draft_course.get('id')})")
                    self.created_course_id = draft_course.get('id')
                    return True, draft_course
                else:
                    print("ℹ️ No draft courses found, creating a new one")
                    return self.create_draft_course()
            except Exception as e:
                print(f"❌ Failed to parse courses: {str(e)}")
                return False, None
        return False, None

    def create_draft_course(self):
        """Create a new draft course for testing"""
        print("\n📝 Creating a new draft course")
        
        course_data = {
            "title": f"Test Course {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "description": "This is a test course created for testing the publication system",
            "level": "level_1",
            "teacher_id": str(uuid.uuid4()),  # Dummy teacher ID
            "teacher_name": "Test Teacher",
            "difficulty": "Легко",
            "estimated_duration_hours": 10,
            "image_url": "https://example.com/image.jpg",
            "status": "draft"  # Explicitly set as draft
        }
        
        success, response = self.run_test(
            "Create Draft Course",
            "POST",
            "admin/courses",
            200,
            data=course_data
        )
        
        if success:
            try:
                course = response.json()
                self.created_course_id = course.get('id')
                print(f"✅ Created new draft course with ID: {self.created_course_id}")
                return True, course
            except Exception as e:
                print(f"❌ Failed to parse created course: {str(e)}")
                return False, None
        return False, None

    def update_course_status(self, course_id, new_status):
        """Update course status (draft -> published)"""
        print(f"\n📝 Updating course {course_id} status to '{new_status}'")
        
        update_data = {
            "status": new_status
        }
        
        success, response = self.run_test(
            f"Update Course Status to {new_status}",
            "PUT",
            f"admin/courses/{course_id}",
            200,
            data=update_data
        )
        
        if success:
            try:
                updated_course = response.json()
                actual_status = updated_course.get('status')
                if actual_status == new_status:
                    print(f"✅ Course status successfully updated to '{actual_status}'")
                    return True, updated_course
                else:
                    print(f"❌ Course status not updated correctly. Expected '{new_status}', got '{actual_status}'")
                    return False, updated_course
            except Exception as e:
                print(f"❌ Failed to parse updated course: {str(e)}")
                return False, None
        return False, None

    def get_public_courses(self):
        """Get public courses (should only show published ones)"""
        print("\n🌐 Getting public courses")
        
        # Use a clean session without admin token
        headers = {'Content-Type': 'application/json'}
        
        success, response = self.run_test(
            "Get Public Courses",
            "GET",
            "courses",
            200,
            headers=headers
        )
        
        if success:
            try:
                courses = response.json()
                print(f"✅ Found {len(courses)} public courses")
                
                # Check if our published course is in the list
                if self.created_course_id:
                    course_found = False
                    for course in courses:
                        if course.get('id') == self.created_course_id:
                            course_found = True
                            print(f"✅ Our published course is visible in public API")
                            break
                    
                    if not course_found:
                        print(f"❌ Our published course is NOT visible in public API")
                        return False, courses
                
                # Verify all courses are published
                all_published = True
                for course in courses:
                    if course.get('status') != 'published':
                        all_published = False
                        print(f"❌ Found a non-published course in public API: {course.get('id')} (status: {course.get('status')})")
                
                if all_published:
                    print("✅ All courses in public API are published")
                
                return all_published, courses
            except Exception as e:
                print(f"❌ Failed to parse public courses: {str(e)}")
                return False, None
        return False, None

    def verify_draft_not_visible(self):
        """Verify that draft courses are not visible in public API"""
        print("\n🔒 Verifying draft courses are not visible in public API")
        
        # First, ensure we have a draft course
        if not self.created_course_id:
            success, course = self.create_draft_course()
            if not success:
                return False
        
        # Update course to draft if it's not already
        success, course = self.update_course_status(self.created_course_id, "draft")
        if not success:
            return False
        
        # Get public courses and verify our draft course is not there
        success, courses = self.get_public_courses()
        
        if success:
            course_found = False
            for course in courses:
                if course.get('id') == self.created_course_id:
                    course_found = True
                    print(f"❌ Draft course is incorrectly visible in public API")
                    break
            
            if not course_found:
                print(f"✅ Draft course is correctly hidden from public API")
                return True
            return False
        return False

    def verify_published_visible(self):
        """Verify that published courses are visible in public API"""
        print("\n🌐 Verifying published courses are visible in public API")
        
        # First, ensure we have a course
        if not self.created_course_id:
            success, course = self.create_draft_course()
            if not success:
                return False
        
        # Update course to published
        success, course = self.update_course_status(self.created_course_id, "published")
        if not success:
            return False
        
        # Get public courses and verify our published course is there
        success, courses = self.get_public_courses()
        
        if success:
            course_found = False
            for course in courses:
                if course.get('id') == self.created_course_id:
                    course_found = True
                    print(f"✅ Published course is correctly visible in public API")
                    break
            
            if not course_found:
                print(f"❌ Published course is incorrectly hidden from public API")
                return False
            return True
        return False

def main():
    tester = CoursePublicationTester()
    
    # Login as admin
    if not tester.admin_login("admin", "admin123"):
        print("❌ Admin login failed, stopping tests")
        return 1
    
    # Get all courses from admin panel
    success, draft_course = tester.get_admin_courses()
    if not success:
        print("❌ Failed to get or create a draft course, stopping tests")
        return 1
    
    # Verify draft courses are not visible in public API
    draft_hidden = tester.verify_draft_not_visible()
    
    # Verify published courses are visible in public API
    published_visible = tester.verify_published_visible()
    
    # Print overall results
    print("\n=== Course Publication System Test Results ===")
    print(f"Admin Courses API: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"Draft Courses Hidden: {'✅ PASSED' if draft_hidden else '❌ FAILED'}")
    print(f"Published Courses Visible: {'✅ PASSED' if published_visible else '❌ FAILED'}")
    
    overall_success = success and draft_hidden and published_visible
    print(f"\n=== Overall Test Result: {'✅ PASSED' if overall_success else '❌ FAILED'} ===")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())