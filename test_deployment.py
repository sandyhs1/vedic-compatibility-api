#!/usr/bin/env python3
import requests
import json

# Test the deployed API
API_URL = "https://vedic-compatibility-api.onrender.com"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_compatibility():
    """Test the compatibility endpoint"""
    test_data = {
        "partner1": {
            "date": "1990-01-01",
            "time": "12:00",
            "place": "mumbai"
        },
        "partner2": {
            "date": "1992-05-15",
            "time": "18:30",
            "place": "delhi"
        }
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/compatibility",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_data),
            timeout=30
        )
        print(f"Compatibility test: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(f"Overall Score: {result.get('compatibility', {}).get('overall_score', 'N/A')}")
            print(f"Level: {result.get('compatibility', {}).get('compatibility_level', 'N/A')}")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Vedic Compatibility API deployment...")
    print("=" * 50)
    
    health_ok = test_health()
    print()
    
    if health_ok:
        compatibility_ok = test_compatibility()
        print()
        
        if compatibility_ok:
            print("✅ All tests passed! API is working correctly.")
        else:
            print("❌ Compatibility test failed.")
    else:
        print("❌ Health check failed.")
    
    print("=" * 50) 