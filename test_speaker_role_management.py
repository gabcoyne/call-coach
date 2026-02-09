#!/usr/bin/env python3
"""
Integration tests for speaker role management API endpoints.
Run with: uv run python test_speaker_role_management.py
"""

import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "X-User-Email": "admin@prefect.io",
    "Content-Type": "application/json",
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, passed, message=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status}: {name}")
    if message:
        print(f"  {message}")

def test_list_speakers():
    """Test GET /speakers - List all speakers"""
    print(f"\n{Colors.BLUE}=== Test 1: GET /speakers ==={Colors.END}")

    try:
        response = requests.get(f"{BASE_URL}/speakers", headers=HEADERS)

        if response.status_code != 200:
            print_test("List speakers", False, f"Expected 200, got {response.status_code}")
            print(f"  Response: {response.text}")
            return None

        speakers = response.json()
        print_test("List speakers", True, f"Returned {len(speakers)} speakers")

        if speakers:
            sample = speakers[0]
            print(f"  Sample speaker: {sample.get('name', 'N/A')} ({sample.get('email')})")
            print(f"  Role: {sample.get('role', 'None')}")

        return speakers

    except Exception as e:
        print_test("List speakers", False, str(e))
        return None

def test_filter_by_role():
    """Test GET /speakers?role=ae - Filter speakers by role"""
    print(f"\n{Colors.BLUE}=== Test 2: Filter speakers by role ==={Colors.END}")

    try:
        response = requests.get(f"{BASE_URL}/speakers?role=ae", headers=HEADERS)

        if response.status_code != 200:
            print_test("Filter by role", False, f"Expected 200, got {response.status_code}")
            return False

        speakers = response.json()
        ae_speakers = [s for s in speakers if s.get('role') == 'ae']

        passed = len(ae_speakers) == len(speakers)
        print_test("Filter by role", passed, f"Returned {len(speakers)} AE speakers")

        return passed

    except Exception as e:
        print_test("Filter by role", False, str(e))
        return False

def test_get_speaker(speakers):
    """Test GET /speakers/{speaker_id} - Get specific speaker"""
    print(f"\n{Colors.BLUE}=== Test 3: GET /speakers/{{speaker_id}} ==={Colors.END}")

    if not speakers:
        print_test("Get speaker", False, "No speakers available for testing")
        return None

    speaker_id = speakers[0]['id']

    try:
        response = requests.get(f"{BASE_URL}/speakers/{speaker_id}", headers=HEADERS)

        if response.status_code != 200:
            print_test("Get speaker", False, f"Expected 200, got {response.status_code}")
            return None

        speaker = response.json()
        print_test("Get speaker", True, f"Retrieved {speaker.get('name', 'N/A')}")
        print(f"  Email: {speaker.get('email')}")
        print(f"  Role: {speaker.get('role', 'None')}")
        print(f"  Total calls: {speaker.get('total_calls', 'N/A')}")

        return speaker

    except Exception as e:
        print_test("Get speaker", False, str(e))
        return None

def test_update_role(speakers):
    """Test PUT /speakers/{speaker_id}/role - Update speaker role"""
    print(f"\n{Colors.BLUE}=== Test 4: PUT /speakers/{{speaker_id}}/role ==={Colors.END}")

    if not speakers:
        print_test("Update role", False, "No speakers available for testing")
        return False

    # Find a speaker to update (prefer one without a role)
    test_speaker = next((s for s in speakers if not s.get('role')), speakers[0])
    speaker_id = test_speaker['id']
    original_role = test_speaker.get('role')
    new_role = 'ae' if original_role != 'ae' else 'se'

    try:
        # Update role
        response = requests.put(
            f"{BASE_URL}/speakers/{speaker_id}/role",
            headers=HEADERS,
            json={"role": new_role}
        )

        if response.status_code != 200:
            print_test("Update role", False, f"Expected 200, got {response.status_code}")
            print(f"  Response: {response.text}")
            return False

        updated = response.json()
        success = updated.get('role') == new_role
        print_test("Update role", success,
                   f"Updated {test_speaker.get('name', 'N/A')} from {original_role} to {new_role}")

        # Restore original role
        if original_role:
            requests.put(
                f"{BASE_URL}/speakers/{speaker_id}/role",
                headers=HEADERS,
                json={"role": original_role}
            )

        return success

    except Exception as e:
        print_test("Update role", False, str(e))
        return False

def test_role_history(speakers):
    """Test GET /speakers/{speaker_id}/history - Get role change history"""
    print(f"\n{Colors.BLUE}=== Test 5: GET /speakers/{{speaker_id}}/history ==={Colors.END}")

    if not speakers:
        print_test("Role history", False, "No speakers available for testing")
        return False

    speaker_id = speakers[0]['id']

    try:
        response = requests.get(
            f"{BASE_URL}/speakers/{speaker_id}/history",
            headers=HEADERS
        )

        if response.status_code != 200:
            print_test("Role history", False, f"Expected 200, got {response.status_code}")
            return False

        history = response.json()
        print_test("Role history", True, f"Retrieved {len(history)} history entries")

        if history:
            latest = history[0]
            print(f"  Latest change: {latest.get('old_role')} → {latest.get('new_role')}")
            print(f"  Changed by: {latest.get('changed_by')}")

        return True

    except Exception as e:
        print_test("Role history", False, str(e))
        return False

def test_bulk_update(speakers):
    """Test POST /speakers/bulk-update-roles - Bulk role assignment"""
    print(f"\n{Colors.BLUE}=== Test 6: POST /speakers/bulk-update-roles ==={Colors.END}")

    if not speakers or len(speakers) < 2:
        print_test("Bulk update", False, "Need at least 2 speakers for testing")
        return False

    # Select 2 speakers for bulk update
    test_speakers = speakers[:2]
    updates = [
        {"speaker_id": test_speakers[0]['id'], "role": "ae"},
        {"speaker_id": test_speakers[1]['id'], "role": "se"},
    ]

    original_roles = [s.get('role') for s in test_speakers]

    try:
        response = requests.post(
            f"{BASE_URL}/speakers/bulk-update-roles",
            headers=HEADERS,
            json={"updates": updates}
        )

        if response.status_code != 200:
            print_test("Bulk update", False, f"Expected 200, got {response.status_code}")
            print(f"  Response: {response.text}")
            return False

        result = response.json()
        success = result.get('updated') == 2
        print_test("Bulk update", success,
                   f"Updated {result.get('updated')} speakers")

        # Restore original roles
        restore_updates = [
            {"speaker_id": test_speakers[i]['id'], "role": original_roles[i]}
            for i in range(len(test_speakers))
        ]
        requests.post(
            f"{BASE_URL}/speakers/bulk-update-roles",
            headers=HEADERS,
            json={"updates": restore_updates}
        )

        return success

    except Exception as e:
        print_test("Bulk update", False, str(e))
        return False

def test_rbac():
    """Test RBAC - non-manager should be denied"""
    print(f"\n{Colors.BLUE}=== Test 7: RBAC - Rep access denied ==={Colors.END}")

    rep_headers = {
        "X-User-Email": "rep@prefect.io",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(f"{BASE_URL}/speakers", headers=rep_headers)

        passed = response.status_code == 403
        print_test("RBAC check", passed,
                   f"Rep correctly {'denied' if passed else 'allowed'} access")

        if not passed:
            print(f"  Expected 403, got {response.status_code}")

        return passed

    except Exception as e:
        print_test("RBAC check", False, str(e))
        return False

def main():
    print(f"{Colors.YELLOW}{'=' * 60}{Colors.END}")
    print(f"{Colors.YELLOW}Testing Speaker Role Management API{Colors.END}")
    print(f"{Colors.YELLOW}{'=' * 60}{Colors.END}")
    print(f"\n{Colors.YELLOW}Make sure REST API server is running: uv run python api/rest_server.py{Colors.END}")

    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=2)
        if response.status_code != 200:
            print(f"\n{Colors.RED}✗ API server not responding{Colors.END}")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"\n{Colors.RED}✗ Cannot connect to API server at {BASE_URL}{Colors.END}")
        print(f"{Colors.YELLOW}Start the server with: uv run python api/rest_server.py{Colors.END}")
        sys.exit(1)

    results = []

    # Run tests
    speakers = test_list_speakers()
    results.append(("List speakers", speakers is not None))

    results.append(("Filter by role", test_filter_by_role()))
    results.append(("Get speaker", test_get_speaker(speakers) is not None))
    results.append(("Update role", test_update_role(speakers)))
    results.append(("Role history", test_role_history(speakers)))
    results.append(("Bulk update", test_bulk_update(speakers)))
    results.append(("RBAC check", test_rbac()))

    # Summary
    print(f"\n{Colors.YELLOW}{'=' * 60}{Colors.END}")
    print(f"{Colors.YELLOW}Test Summary{Colors.END}")
    print(f"{Colors.YELLOW}{'=' * 60}{Colors.END}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if result else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{status}: {test_name}")

    print(f"\n{Colors.BLUE}Total: {passed}/{total} tests passed{Colors.END}")

    if passed == total:
        print(f"{Colors.GREEN}All tests passed!{Colors.END}")
        sys.exit(0)
    else:
        print(f"{Colors.RED}Some tests failed{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
