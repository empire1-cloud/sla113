#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Hybrid AI Stack Integration
Tests all endpoints and routing logic for GPT-5.2, Claude Sonnet 4.5, and Gemini 3 Flash
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

class HybridAITester:
    def __init__(self, base_url="https://hybrid-ai-playbook.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test_name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None) -> tuple:
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            response_json = {}
            
            try:
                response_json = response.json()
            except:
                response_json = {"raw_response": response.text}

            details = f"Status: {response.status_code}"
            if not success:
                details += f" (expected {expected_status})"

            self.log_test(name, success, details, response_json)
            return success, response_json

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_health_endpoint(self):
        """Test health check endpoint"""
        print("\n🔍 Testing Health Endpoint...")
        success, response = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        
        if success:
            # Validate health response structure
            expected_fields = ["status", "pipeline", "models", "stages"]
            missing_fields = [f for f in expected_fields if f not in response]
            
            if missing_fields:
                self.log_test(
                    "Health Response Structure",
                    False,
                    f"Missing fields: {missing_fields}"
                )
            else:
                # Check model availability
                models = response.get("models", {})
                expected_models = ["gpt-5.2", "claude-sonnet-4.5", "gemini-3-flash"]
                
                all_available = all(
                    models.get(model) == "available" 
                    for model in expected_models
                )
                
                self.log_test(
                    "Model Availability Check",
                    all_available,
                    f"Models status: {models}"
                )

    def test_routing_decisions(self):
        """Test routing logic for different task types"""
        print("\n🔍 Testing Routing Logic...")
        
        test_cases = [
            {
                "goal": "Write a Python function to sort a list",
                "expected_model": "gpt-5.2",
                "task_type": "code"
            },
            {
                "goal": "Analyze the market trends for AI startups",
                "expected_model": "claude-sonnet-4.5", 
                "task_type": "analysis"
            },
            {
                "goal": "Create a business strategy for scaling our SaaS product",
                "expected_model": "claude-sonnet-4.5",
                "task_type": "strategy"
            },
            {
                "goal": "What is machine learning?",
                "expected_model": "gemini-3-flash",
                "task_type": "quick"
            },
            {
                "goal": "Debug this API endpoint issue",
                "expected_model": "gpt-5.2",
                "task_type": "code"
            }
        ]
        
        for case in test_cases:
            success, response = self.run_test(
                f"Route {case['task_type']} task",
                "POST",
                "route",
                200,
                data={"goal": case["goal"]}
            )
            
            if success:
                actual_model = response.get("model")
                routing_correct = actual_model == case["expected_model"]
                
                self.log_test(
                    f"Routing Logic - {case['task_type']} → {case['expected_model']}",
                    routing_correct,
                    f"Expected: {case['expected_model']}, Got: {actual_model}"
                )

    def test_force_model_routing(self):
        """Test force model override functionality"""
        print("\n🔍 Testing Force Model Override...")
        
        success, response = self.run_test(
            "Force Model Override",
            "POST", 
            "route",
            200,
            data={
                "goal": "Write code",  # Would normally go to gpt-5.2
                "force_model": "gemini-3-flash"  # Force to gemini
            }
        )
        
        if success:
            actual_model = response.get("model")
            override_works = actual_model == "gemini-3-flash"
            
            self.log_test(
                "Model Override Functionality",
                override_works,
                f"Expected: gemini-3-flash, Got: {actual_model}"
            )

    def test_strategy_generation(self):
        """Test full strategy generation pipeline"""
        print("\n🔍 Testing Strategy Generation Pipeline...")
        
        test_goals = [
            {
                "goal": "Launch a new AI-powered mobile app",
                "context": "We have a team of 5 developers and $100k budget",
                "tone": "direct"
            },
            {
                "goal": "Optimize our database performance",
                "context": "PostgreSQL database with 1M+ records, slow queries",
                "tone": "technical"
            }
        ]
        
        for i, test_case in enumerate(test_goals):
            success, response = self.run_test(
                f"Strategy Generation {i+1}",
                "POST",
                "strategy", 
                200,
                data=test_case
            )
            
            if success:
                # Validate strategy response structure
                required_fields = ["summary", "steps", "risks", "resources", "next_action"]
                missing_fields = [f for f in required_fields if f not in response]
                
                structure_valid = len(missing_fields) == 0
                self.log_test(
                    f"Strategy Response Structure {i+1}",
                    structure_valid,
                    f"Missing fields: {missing_fields}" if missing_fields else "All required fields present"
                )
                
                if structure_valid:
                    # Validate field types and content
                    steps_valid = isinstance(response.get("steps"), list) and len(response["steps"]) >= 3
                    risks_valid = isinstance(response.get("risks"), list)
                    resources_valid = isinstance(response.get("resources"), list)
                    summary_valid = isinstance(response.get("summary"), str) and len(response["summary"]) > 50
                    next_action_valid = isinstance(response.get("next_action"), str) and len(response["next_action"]) > 20
                    
                    content_valid = all([steps_valid, risks_valid, resources_valid, summary_valid, next_action_valid])
                    
                    self.log_test(
                        f"Strategy Content Quality {i+1}",
                        content_valid,
                        f"Steps: {len(response.get('steps', []))}, Summary: {len(response.get('summary', ''))}, Next Action: {len(response.get('next_action', ''))}"
                    )

    def test_canon_enforcement(self):
        """Test that canon enforcer removes forbidden phrases"""
        print("\n🔍 Testing Canon Enforcement...")
        
        # Test with a goal that might trigger AI-like responses
        success, response = self.run_test(
            "Canon Enforcement Test",
            "POST",
            "strategy",
            200,
            data={
                "goal": "Help me understand artificial intelligence and machine learning",
                "tone": "helpful"
            }
        )
        
        if success:
            # Check for forbidden phrases in the response
            forbidden_phrases = [
                "As an AI", "As a language model", "I'm Claude", "I'm GPT", 
                "I'm Gemini", "Certainly!", "Sure!", "I'd be happy to",
                "Great question!", "I'm sorry, but"
            ]
            
            response_text = json.dumps(response).lower()
            found_phrases = [phrase for phrase in forbidden_phrases if phrase.lower() in response_text]
            
            canon_compliant = len(found_phrases) == 0
            
            self.log_test(
                "Canon Compliance Check",
                canon_compliant,
                f"Forbidden phrases found: {found_phrases}" if found_phrases else "No forbidden phrases detected"
            )

    def test_drift_monitoring(self):
        """Test drift monitoring endpoints"""
        print("\n🔍 Testing Drift Monitoring...")
        
        # Test drift report endpoint
        success, response = self.run_test(
            "Drift Report - All Models",
            "GET",
            "drift-report",
            200
        )
        
        if success:
            # Check drift report structure
            expected_fields = ["status", "sample_count"]
            has_required_fields = all(field in response for field in expected_fields)
            
            self.log_test(
                "Drift Report Structure",
                has_required_fields,
                f"Status: {response.get('status')}, Samples: {response.get('sample_count')}"
            )
        
        # Test specific model drift reports
        models = ["gpt-5.2", "claude-sonnet-4.5", "gemini-3-flash"]
        for model in models:
            success, response = self.run_test(
                f"Drift Report - {model}",
                "GET",
                f"drift-report/{model}",
                200
            )

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n🔍 Testing Error Handling...")
        
        # Test invalid model in drift report
        success, response = self.run_test(
            "Invalid Model Error",
            "GET",
            "drift-report/invalid-model",
            400
        )
        
        # Test empty strategy request
        success, response = self.run_test(
            "Empty Strategy Request",
            "POST",
            "strategy",
            422,  # Validation error
            data={}
        )
        
        # Test malformed route request
        success, response = self.run_test(
            "Malformed Route Request", 
            "POST",
            "route",
            422,  # Validation error
            data={"invalid_field": "test"}
        )

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Hybrid AI Stack Backend Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        try:
            self.test_health_endpoint()
            self.test_routing_decisions()
            self.test_force_model_routing()
            self.test_strategy_generation()
            self.test_canon_enforcement()
            self.test_drift_monitoring()
            self.test_error_handling()
            
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
        except Exception as e:
            print(f"\n💥 Unexpected error: {str(e)}")
        
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        # Show failed tests
        failed_tests = [t for t in self.test_results if not t["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test_name']}: {test['details']}")
        
        return 0 if self.tests_passed == self.tests_run else 1

def main():
    tester = HybridAITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())