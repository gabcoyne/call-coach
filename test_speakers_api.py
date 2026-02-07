#!/usr/bin/env python3
"""
Test script for speakers API endpoints.
Run this with the REST API server running on port 8000.
"""

import requests
from uuid import UUID

BASE_URL = "http://localhost:8000/api/v1/speakers"
HEADERS = {
    "X-User-Email": "admin@prefect.io",  # Use admin user for testing
    "Content-Type": "application/json",
}

# Test speaker IDs (from database)
TEST_SPEAKER_ID = "3ac09243-b318-4935-9ae8-f51f8c3fc6a2"  # Mason Menges
TEST_SPEAKER_ID_2 = "6ebc2380-cf19-4c07-81ae-f39d2e961a97"  # Unknown Rep


def test_get_speaker():
    """Test GET /speakers/{speaker_id}"""
    print("\n=== Test 1: GET /speakers/{speaker_id} ===")
    response = requests.get(f"{BASE_URL}/{TEST_SPEAKER_ID}", headers=HEADERS)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Speaker: {data.get('name')} ({data.get('email')})")
        print(f"Role: {data.get('role')}")
        print("✓ GET speaker successful")
        return data
    else:
        print(f"✗ Failed: {response.text}")
        return None


def test_update_role():
    """Test PUT /speakers/{speaker_id}/role"""
    print("\n=== Test 2: PUT /speakers/{speaker_id}/role ===")

    # Update to SE
    response = requests.put(
        f"{BASE_URL}/{TEST_SPEAKER_ID}/role",
        headers=HEADERS,
        json={"role": "se"}
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Updated role to: {data.get('role')}")
        print("✓ Update role successful")

        # Restore to AE
        restore = requests.put(
            f"{BASE_URL}/{TEST_SPEAKER_ID}/role",
            headers=HEADERS,
            json={"role": "ae"}
        )
        print(f"Restored to: {restore.json().get('role')}")
        return True
    else:
        print(f"✗ Failed: {response.text}")
        return False


def test_get_history():
    """Test GET /speakers/{speaker_id}/history"""
    print("\n=== Test 3: GET /speakers/{speaker_id}/history ===")
    response = requests.get(
        f"{BASE_URL}/{TEST_SPEAKER_ID}/history?limit=5",
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        history = response.json()
        print(f"Found {len(history)} history entries")
        if history:
            print("Recent changes:")
            for entry in history[:3]:
                print(f"  {entry['old_role']} → {entry['new_role']} by {entry['changed_by']}")
        print("✓ Get history successful")
        return True
    else:
        print(f"✗ Failed: {response.text}")
        return False


def test_bulk_update():
    """Test POST /speakers/bulk-update-roles"""
    print("\n=== Test 4: POST /speakers/bulk-update-roles ===")

    # Bulk update 2 speakers
    response = requests.post(
        f"{BASE_URL}/bulk-update-roles",
        headers=HEADERS,
        json={
            "updates": [
                {"speaker_id": TEST_SPEAKER_ID, "role": "csm"},
                {"speaker_id": TEST_SPEAKER_ID_2, "role": "se"},
            ]
        }
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Updated: {result['updated']} speakers")
        print(f"Failed: {len(result['failed'])} speakers")
        print("✓ Bulk update successful")

        # Restore original roles
        restore = requests.post(
            f"{BASE_URL}/bulk-update-roles",
            headers=HEADERS,
            json={
                "updates": [
                    {"speaker_id": TEST_SPEAKER_ID, "role": "ae"},
                    {"speaker_id": TEST_SPEAKER_ID_2, "role": None},
                ]
            }
        )
        print(f"Restored {restore.json()['updated']} speakers")
        return True
    else:
        print(f"✗ Failed: {response.text}")
        return False


def test_invalid_role():
    """Test invalid role validation"""
    print("\n=== Test 5: Invalid role (should fail) ===")
    response = requests.put(
        f"{BASE_URL}/{TEST_SPEAKER_ID}/role",
        headers=HEADERS,
        json={"role": "invalid_role"}
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 400:
        print(f"Error message: {response.json().get('detail')}")
        print("✓ Correctly rejected invalid role")
        return True
    else:
        print(f"✗ Should have returned 400, got {response.status_code}")
        return False


def test_unauthorized():
    """Test RBAC - rep user should be denied"""
    print("\n=== Test 6: RBAC - rep user (should be denied) ===")
    rep_headers = {
        "X-User-Email": "rep@prefect.io",
        "Content-Type": "application/json",
    }

    response = requests.get(f"{BASE_URL}/{TEST_SPEAKER_ID}", headers=rep_headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 403:
        print(f"Error: {response.json().get('detail')}")
        print("✓ Correctly denied rep access")
        return True
    else:
        print(f"✗ Should have returned 403, got {response.status_code}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Speakers API Endpoints")
    print("=" * 60)
    print("\nMake sure REST API server is running: uv run python api/rest_server.py")
    print("=" * 60)

    try:
        results = []
        results.append(("GET speaker", test_get_speaker() is not None))
        results.append(("UPDATE role", test_update_role()))
        results.append(("GET history", test_get_history()))
        results.append(("BULK update", test_bulk_update()))
        results.append(("Invalid role", test_invalid_role()))
        results.append(("RBAC check", test_unauthorized()))

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
