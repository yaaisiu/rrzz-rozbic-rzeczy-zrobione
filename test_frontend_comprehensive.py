#!/usr/bin/env python3
"""
Comprehensive frontend testing script.
Tests all major functionality of the Streamlit frontend.
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional

API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"

def test_api_connectivity() -> bool:
    """Test if the API is accessible."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API connectivity failed: {e}")
        return False

def test_frontend_connectivity() -> bool:
    """Test if the frontend is accessible."""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Frontend connectivity failed: {e}")
        return False

def test_note_creation_workflow() -> bool:
    """Test the complete note creation workflow."""
    print("\n🔍 Testing Note Creation Workflow...")
    
    # Test 1: Create a simple note
    test_note_1 = {
        "content": "This is a test note for frontend validation. It contains information about AI and machine learning concepts.",
        "title": "Frontend Test Note 1",
        "tags": ["test", "frontend", "validation"]
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/notes", json=test_note_1, timeout=30)
        if response.status_code != 200:
            print(f"❌ Note creation failed: {response.status_code}")
            return False
        
        result_1 = response.json()
        print(f"✅ Note 1 created: {result_1.get('note_id')}")
        
        # Test 2: Create another note with different content
        test_note_2 = {
            "content": "Another test note about Python programming and data science. This note discusses pandas, numpy, and matplotlib.",
            "title": "Frontend Test Note 2",
            "tags": ["python", "data-science", "programming"]
        }
        
        response = requests.post(f"{API_BASE_URL}/notes", json=test_note_2, timeout=30)
        if response.status_code != 200:
            print(f"❌ Second note creation failed: {response.status_code}")
            return False
        
        result_2 = response.json()
        print(f"✅ Note 2 created: {result_2.get('note_id')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Note creation workflow failed: {e}")
        return False

def test_search_functionality() -> bool:
    """Test search functionality with different queries."""
    print("\n🔍 Testing Search Functionality...")
    
    search_tests = [
        {"query": "test", "expected_min": 1},
        {"query": "python", "expected_min": 1},
        {"query": "AI", "expected_min": 1},
        {"query": "nonexistent", "expected_min": 0}
    ]
    
    for test in search_tests:
        try:
            payload = {"query": test["query"], "limit": 10}
            response = requests.post(f"{API_BASE_URL}/notes/search", json=payload, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Search failed for '{test['query']}': {response.status_code}")
                return False
            
            results = response.json()
            print(f"✅ Search '{test['query']}': Found {len(results)} notes")
            
            if len(results) < test["expected_min"]:
                print(f"⚠️  Search '{test['query']}' returned fewer results than expected")
                
        except Exception as e:
            print(f"❌ Search test failed for '{test['query']}': {e}")
            return False
    
    return True

def test_note_retrieval() -> bool:
    """Test retrieving specific notes by ID."""
    print("\n🔍 Testing Note Retrieval...")
    
    try:
        # First, create a note to get its ID
        test_note = {
            "content": "Test note for retrieval testing",
            "title": "Retrieval Test",
            "tags": ["retrieval", "test"]
        }
        
        response = requests.post(f"{API_BASE_URL}/notes", json=test_note, timeout=30)
        if response.status_code != 200:
            print("❌ Failed to create note for retrieval test")
            return False
        
        note_id = response.json().get('note_id')
        
        # Now retrieve the note
        response = requests.get(f"{API_BASE_URL}/notes/{note_id}", timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to retrieve note {note_id}")
            return False
        
        retrieved_note = response.json()
        print(f"✅ Successfully retrieved note: {retrieved_note.get('content', '')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Note retrieval test failed: {e}")
        return False

def test_system_health() -> bool:
    """Test system health endpoint."""
    print("\n🔍 Testing System Health...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        health_data = response.json()
        print(f"✅ System Health: {health_data}")
        
        # Check if all services are healthy
        if health_data.get("status") != "ok":
            print("❌ System status is not OK")
            return False
        
        if health_data.get("neo4j") != "healthy":
            print("❌ Neo4j is not healthy")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_error_handling() -> bool:
    """Test error handling scenarios."""
    print("\n🔍 Testing Error Handling...")
    
    # Test 1: Invalid note ID
    try:
        response = requests.get(f"{API_BASE_URL}/notes/invalid-id", timeout=5)
        if response.status_code != 404:
            print(f"❌ Expected 404 for invalid note ID, got {response.status_code}")
            return False
        print("✅ Invalid note ID handled correctly")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    # Test 2: Empty note content
    try:
        empty_note = {"content": "", "title": "Empty Test"}
        response = requests.post(f"{API_BASE_URL}/notes", json=empty_note, timeout=10)
        # This should either succeed (if empty content is allowed) or return an error
        print(f"✅ Empty note test completed (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Empty note test failed: {e}")
        return False
    
    return True

def test_performance() -> bool:
    """Test basic performance metrics."""
    print("\n🔍 Testing Performance...")
    
    # Test API response time
    start_time = time.time()
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        response_time = time.time() - start_time
        
        if response_time > 2.0:
            print(f"⚠️  Health check took {response_time:.2f}s (slow)")
        else:
            print(f"✅ Health check response time: {response_time:.2f}s")
        
        # Test note creation time
        start_time = time.time()
        test_note = {
            "content": "Performance test note",
            "title": "Performance Test",
            "tags": ["performance", "test"]
        }
        
        response = requests.post(f"{API_BASE_URL}/notes", json=test_note, timeout=30)
        creation_time = time.time() - start_time
        
        if creation_time > 10.0:
            print(f"⚠️  Note creation took {creation_time:.2f}s (slow)")
        else:
            print(f"✅ Note creation time: {creation_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run comprehensive frontend tests."""
    print("🧪 Comprehensive Frontend Testing")
    print("=" * 60)
    
    tests = [
        ("API Connectivity", test_api_connectivity),
        ("Frontend Connectivity", test_frontend_connectivity),
        ("System Health", test_system_health),
        ("Note Creation Workflow", test_note_creation_workflow),
        ("Search Functionality", test_search_functionality),
        ("Note Retrieval", test_note_retrieval),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<25} {status}")
        if result:
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Frontend is working perfectly!")
        print("\n🌐 Your application is ready for use:")
        print("   - Streamlit Frontend: http://localhost:8501")
        print("   - FastAPI Backend: http://localhost:8000")
        print("   - Neo4j Browser: http://localhost:7474")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    print("\n" + "=" * 60)
    return passed == total

if __name__ == "__main__":
    main() 