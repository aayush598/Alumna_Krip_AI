# ==================== UPDATED API USAGE EXAMPLES ====================

import requests
import json

# Base URL for your API
BASE_URL = "http://localhost:8000"  # Change this to your deployed URL

# ==================== HELPER FUNCTIONS ====================

def print_separator(title=""):
    """Print a nice separator for better output formatting"""
    print("\n" + "="*60)
    if title:
        print(f" {title} ")
        print("="*60)

def print_response_details(response_data, step_name=""):
    """Print response details in a formatted way"""
    if step_name:
        print(f"\n--- {step_name} ---")
    
    print(f"Bot Response: {response_data.get('response', 'No response')}")
    print(f"Sufficient Info: {response_data.get('sufficient_info', False)}")
    
    # Print session info if available
    if 'session_id' in response_data:
        print(f"Session ID: {response_data['session_id']}")
    
    # Print profile summary
    profile = response_data.get('profile', {})
    if profile:
        filled_fields = {k: v for k, v in profile.items() if v is not None and v != {} and v != []}
        print(f"Profile Fields Filled: {len(filled_fields)}")
        if filled_fields:
            print("Current Profile Data:")
            for key, value in filled_fields.items():
                print(f"  - {key}: {value}")
    
    # Print recommendations if available
    recommendations = response_data.get('recommendations')
    if recommendations:
        print(f"\n🎯 RECOMMENDATIONS AVAILABLE: {len(recommendations)} colleges found")

def print_recommendations(recommendations, max_show=5):
    """Print college recommendations in a formatted way"""
    if not recommendations:
        print("No recommendations available yet.")
        return
    
    print_separator("COLLEGE RECOMMENDATIONS")
    print(f"Showing top {min(len(recommendations), max_show)} out of {len(recommendations)} recommendations:\n")
    
    for i, rec in enumerate(recommendations[:max_show], 1):
        print(f"{i}. {rec.get('name', 'Unknown College')}")
        print(f"   📍 Location: {rec.get('location', 'Not specified')}")
        print(f"   💰 Fees: ₹{rec.get('fees', 0):,}")
        print(f"   🎯 Match Score: {rec.get('match_score', 0):.1f}%")
        
        reasons = rec.get('match_reasons', [])
        if reasons:
            print(f"   ✅ Match Reasons: {', '.join(reasons)}")
        
        print()  # Empty line for spacing

# ==================== MAIN CONVERSATION EXAMPLE ====================

def example_chat_conversation():
    """Example of a complete counseling conversation with proper error handling"""
    
    print_separator("COLLEGE COUNSELING CONVERSATION EXAMPLE")
    
    session_id = None
    
    try:
        # ==================== STEP 1: START CONVERSATION ====================
        print("\n🚀 Starting new counseling conversation...")
        
        response1 = requests.post(f"{BASE_URL}/chat", json={
            "message": "Hi! I need help choosing colleges. I scored 92% in 12th grade and I'm interested in engineering."
        })
        
        if response1.status_code != 200:
            print(f"❌ Error: {response1.status_code} - {response1.text}")
            return
        
        data1 = response1.json()
        print_response_details(data1, "INITIAL RESPONSE")
        
        # Extract session_id (handle both possible response formats)
        session_id = data1.get("session_id")
        if not session_id:
            print("⚠️ No session_id in response. Creating new session for next request.")
        
        # ==================== STEP 2: PROVIDE MORE DETAILS ====================
        print("\n📝 Providing additional information...")
        
        message2 = "I got 5000 rank in JEE Mains and my budget is around 8 lakhs. I prefer colleges in South India."
        request_data = {"message": message2}
        
        if session_id:
            request_data["session_id"] = session_id
        
        response2 = requests.post(f"{BASE_URL}/chat", json=request_data)
        
        if response2.status_code != 200:
            print(f"❌ Error: {response2.status_code} - {response2.text}")
            return
        
        data2 = response2.json()
        print_response_details(data2, "DETAILED INFORMATION RESPONSE")
        
        # Update session_id if we got a new one
        if not session_id and 'session_id' in data2:
            session_id = data2['session_id']
        
        # ==================== STEP 3: PROVIDE SPECIFIC PREFERENCES ====================
        print("\n🎯 Providing specific preferences...")
        
        message3 = "I'm particularly interested in Computer Science Engineering. I prefer colleges with good placement records and modern infrastructure. I don't mind if it's a government or private college, but the quality of education should be excellent."
        request_data = {"message": message3}
        
        if session_id:
            request_data["session_id"] = session_id
        
        response3 = requests.post(f"{BASE_URL}/chat", json=request_data)
        
        if response3.status_code != 200:
            print(f"❌ Error: {response3.status_code} - {response3.text}")
            return
        
        data3 = response3.json()
        print_response_details(data3, "PREFERENCES RESPONSE")
        
        # Update session_id if we got a new one
        if not session_id and 'session_id' in data3:
            session_id = data3['session_id']
        
        # ==================== STEP 4: FINAL DETAILS ====================
        print("\n📋 Providing final details...")
        
        message4 = "I'm from Karnataka state and belong to the General category. I've participated in coding competitions and have basic knowledge of Python programming. I want to work in software development after graduation."
        request_data = {"message": message4}
        
        if session_id:
            request_data["session_id"] = session_id
        
        response4 = requests.post(f"{BASE_URL}/chat", json=request_data)
        
        if response4.status_code != 200:
            print(f"❌ Error: {response4.status_code} - {response4.text}")
            return
        
        data4 = response4.json()
        print_response_details(data4, "FINAL RESPONSE")
        
        # ==================== STEP 5: DISPLAY RECOMMENDATIONS ====================
        # Check the latest response for recommendations
        latest_data = data4
        if latest_data.get('sufficient_info') and latest_data.get('recommendations'):
            print_recommendations(latest_data['recommendations'])
        elif data3.get('recommendations'):
            print_recommendations(data3['recommendations'])
        elif data2.get('recommendations'):
            print_recommendations(data2['recommendations'])
        else:
            print("\n⏳ Recommendations not ready yet. Let's try to get them separately...")
            
            # Try to get recommendations using the recommendations endpoint
            if session_id:
                try:
                    rec_response = requests.post(f"{BASE_URL}/recommendations", json={
                        "session_id": session_id,
                        "max_results": 10
                    })
                    
                    if rec_response.status_code == 200:
                        rec_data = rec_response.json()
                        recommendations = rec_data.get('recommendations', [])
                        if recommendations:
                            print_recommendations(recommendations)
                        else:
                            print("❌ No recommendations found. Profile may need more information.")
                    else:
                        print(f"❌ Recommendations request failed: {rec_response.status_code}")
                except Exception as e:
                    print(f"❌ Error getting recommendations: {e}")
        
        # ==================== STEP 6: SHOW SESSION SUMMARY ====================
        if session_id:
            print_separator("SESSION SUMMARY")
            try:
                profile_response = requests.get(f"{BASE_URL}/profile/{session_id}")
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print(f"Session ID: {profile_data['session_id']}")
                    print(f"Sufficient Info Collected: {profile_data['sufficient_info']}")
                    print(f"Extraction History Steps: {len(profile_data.get('extraction_history', []))}")
                    
                    profile = profile_data.get('profile', {})
                    filled_fields = {k: v for k, v in profile.items() if v is not None and v != {} and v != []}
                    
                    print(f"\nFinal Profile Summary ({len(filled_fields)} fields filled):")
                    for key, value in filled_fields.items():
                        print(f"  ✅ {key}: {value}")
                        
                else:
                    print(f"❌ Could not fetch profile summary: {profile_response.status_code}")
            except Exception as e:
                print(f"❌ Error fetching profile: {e}")
        
        print_separator("CONVERSATION COMPLETED SUCCESSFULLY! 🎉")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to the API server.")
        print("   Make sure the server is running on http://localhost:8000")
        print("   Run: python test1.py (or your main API file)")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
        
    except KeyError as e:
        print(f"❌ DATA FORMAT ERROR: Missing expected field {e}")
        print("   The API response format may have changed.")
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

# ==================== ADDITIONAL TEST FUNCTIONS ====================

def test_api_endpoints():
    """Test various API endpoints"""
    
    print_separator("API ENDPOINTS TEST")
    
    try:
        # Test root endpoint
        print("🧪 Testing root endpoint...")
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            root_data = response.json()
            print(f"   API Version: {root_data.get('version', 'Unknown')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
        
        # Test sessions endpoint
        print("\n🧪 Testing sessions endpoint...")
        response = requests.get(f"{BASE_URL}/sessions")
        if response.status_code == 200:
            sessions = response.json()
            print(f"✅ Sessions endpoint working - Found {len(sessions)} sessions")
        else:
            print(f"❌ Sessions endpoint failed: {response.status_code}")
        
        # Test colleges endpoint
        print("\n🧪 Testing colleges endpoint...")
        response = requests.get(f"{BASE_URL}/colleges")
        if response.status_code == 200:
            colleges_data = response.json()
            college_count = colleges_data.get('total_count', 0)
            print(f"✅ Colleges endpoint working - Found {college_count} colleges")
        else:
            print(f"❌ Colleges endpoint failed: {response.status_code}")
        
        # Test analytics endpoint
        print("\n🧪 Testing analytics endpoint...")
        response = requests.get(f"{BASE_URL}/analytics")
        if response.status_code == 200:
            analytics = response.json()
            print("✅ Analytics endpoint working")
            print(f"   Total Sessions: {analytics.get('total_sessions', 0)}")
            print(f"   Active Sessions: {analytics.get('active_sessions', 0)}")
            print(f"   Completion Rate: {analytics.get('completion_rate', '0%')}")
        else:
            print(f"❌ Analytics endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Endpoint testing failed: {e}")

def quick_recommendation_test():
    """Quick test to get recommendations with custom profile data"""
    
    print_separator("QUICK RECOMMENDATION TEST")
    
    try:
        # Test with custom profile data
        custom_profile = {
            "grade_12_percentage": 92.0,
            "jee_score": 5000,
            "budget_max": 800000,
            "preferred_location": "South India",
            "preferred_stream": "Engineering",
            "specialization_interest": "Computer Science",
            "state_of_residence": "Karnataka",
            "category": "General"
        }
        
        print("🧪 Testing recommendations with custom profile...")
        response = requests.post(f"{BASE_URL}/recommendations", json={
            "profile_data": custom_profile,
            "max_results": 5
        })
        
        if response.status_code == 200:
            rec_data = response.json()
            recommendations = rec_data.get('recommendations', [])
            print(f"✅ Got {len(recommendations)} recommendations")
            
            if recommendations:
                print_recommendations(recommendations, max_show=3)
            else:
                print("⚠️ No recommendations found for the test profile")
        else:
            print(f"❌ Recommendations test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Quick recommendation test failed: {e}")

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    print("🚀 STARTING COMPREHENSIVE API TESTING")
    print("=====================================")
    
    # Run the main conversation example
    example_chat_conversation()
    
    # Test other endpoints
    test_api_endpoints()
    
    # Quick recommendation test
    quick_recommendation_test()
    
    print("\n🏁 ALL TESTS COMPLETED!")
    print("Check the output above for any errors or issues.")