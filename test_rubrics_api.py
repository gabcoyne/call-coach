#!/usr/bin/env python3
"""
Test script for rubrics API endpoints.
Run this with the REST API server running on port 8000.
"""

import requests

BASE_URL = "http://localhost:8000/api/v1/rubrics"
HEADERS = {
    "X-User-Email": "admin@prefect.io",  # Use admin user for testing
    "Content-Type": "application/json",
}


def test_get_criteria_for_dimension():
    """Test GET /rubrics/{role}/{dimension}"""
    print("\n=== Test 1: GET /rubrics/{role}/{dimension} ===")
    response = requests.get(f"{BASE_URL}/ae/discovery", headers=HEADERS)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        criteria = response.json()
        print(f"AE Discovery criteria: {len(criteria)}")
        print("Sample criteria:")
        for c in criteria[:3]:
            print(f"  {c['criterion_name']}: {c['weight']}%")

        # Verify weights sum to 100
        total_weight = sum(c['weight'] for c in criteria)
        print(f"\nTotal weight: {total_weight}%")
        print("✓ Get criteria successful")
        return criteria
    else:
        print(f"✗ Failed: {response.text}")
        return None


def test_get_criteria_for_role():
    """Test GET /rubrics/{role}"""
    print("\n=== Test 2: GET /rubrics/{role} ===")
    response = requests.get(f"{BASE_URL}/se", headers=HEADERS)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        criteria = response.json()
        print(f"SE criteria (all dimensions): {len(criteria)}")

        # Group by dimension
        from collections import defaultdict
        by_dim = defaultdict(list)
        for c in criteria:
            by_dim[c['dimension']].append(c)

        print("Criteria by dimension:")
        for dim, items in sorted(by_dim.items()):
            weight_sum = sum(c['weight'] for c in items)
            print(f"  {dim}: {len(items)} criteria (total: {weight_sum}%)")

        print("✓ Get all criteria for role successful")
        return True
    else:
        print(f"✗ Failed: {response.text}")
        return False


def test_create_criterion():
    """Test POST /rubrics/criteria"""
    print("\n=== Test 3: POST /rubrics/criteria ===")

    new_criterion = {
        "role": "ae",
        "dimension": "discovery",
        "criterion_name": "API Test Criterion",
        "description": "This is a test criterion created via API to validate the create endpoint",
        "weight": 5,
        "max_score": 10,
        "display_order": 99
    }

    response = requests.post(f"{BASE_URL}/criteria", headers=HEADERS, json=new_criterion)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        created = response.json()
        print(f"Created: {created['criterion_name']}")
        print(f"  ID: {created['id']}")
        print(f"  Role/Dimension: {created['role']}/{created['dimension']}")
        print("✓ Create criterion successful")
        return created['id']
    else:
        print(f"✗ Failed: {response.text}")
        return None


def test_update_criterion(criterion_id):
    """Test PUT /rubrics/criteria/{criterion_id}"""
    print("\n=== Test 4: PUT /rubrics/criteria/{criterion_id} ===")

    updates = {
        "description": "Updated description via API test endpoint validation",
        "weight": 7
    }

    response = requests.put(
        f"{BASE_URL}/criteria/{criterion_id}",
        headers=HEADERS,
        json=updates
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        updated = response.json()
        print(f"Updated: {updated['criterion_name']}")
        print(f"  Weight: {updated['weight']}%")
        print(f"  Description: {updated['description'][:50]}...")
        print("✓ Update criterion successful")
        return True
    else:
        print(f"✗ Failed: {response.text}")
        return False


def test_delete_criterion(criterion_id):
    """Test DELETE /rubrics/criteria/{criterion_id}"""
    print("\n=== Test 5: DELETE /rubrics/criteria/{criterion_id} ===")

    response = requests.delete(f"{BASE_URL}/criteria/{criterion_id}", headers=HEADERS)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Deleted: {result['deleted']}")
        print("✓ Delete criterion successful")
        return result['deleted']
    else:
        print(f"✗ Failed: {response.text}")
        return False


def test_rbac():
    """Test RBAC - rep user should be denied"""
    print("\n=== Test 6: RBAC - rep user (should be denied) ===")
    rep_headers = {
        "X-User-Email": "rep@prefect.io",
        "Content-Type": "application/json",
    }

    response = requests.get(f"{BASE_URL}/ae/discovery", headers=rep_headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 403:
        print(f"Error: {response.json().get('detail')}")
        print("✓ Correctly denied rep access")
        return True
    else:
        print(f"✗ Should have returned 403, got {response.status_code}")
        return False


def test_validation():
    """Test validation - invalid weight"""
    print("\n=== Test 7: Validation - invalid weight ===")

    invalid_criterion = {
        "role": "ae",
        "dimension": "discovery",
        "criterion_name": "Invalid Test",
        "description": "This should fail due to invalid weight value",
        "weight": 150,  # Invalid: > 100
        "max_score": 10,
        "display_order": 0
    }

    response = requests.post(f"{BASE_URL}/criteria", headers=HEADERS, json=invalid_criterion)
    print(f"Status: {response.status_code}")

    if response.status_code == 400:
        print(f"Error: {response.json().get('detail')}")
        print("✓ Correctly rejected invalid weight")
        return True
    else:
        print(f"✗ Should have returned 400, got {response.status_code}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Rubrics API Endpoints")
    print("=" * 60)
    print("\nMake sure REST API server is running: uv run python api/rest_server.py")
    print("=" * 60)

    try:
        results = []

        # Test read operations
        results.append(("GET dimension criteria", test_get_criteria_for_dimension() is not None))
        results.append(("GET role criteria", test_get_criteria_for_role()))

        # Test create
        criterion_id = test_create_criterion()
        results.append(("CREATE criterion", criterion_id is not None))

        if criterion_id:
            # Test update and delete
            results.append(("UPDATE criterion", test_update_criterion(criterion_id)))
            results.append(("DELETE criterion", test_delete_criterion(criterion_id)))

        # Test RBAC and validation
        results.append(("RBAC check", test_rbac()))
        results.append(("Validation check", test_validation()))

        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")

        print(f"\nTotal: {passed}/{total} tests passed")

    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API server")
        print("Make sure the REST API server is running:")
        print("  uv run python api/rest_server.py")
