"""
Test different Gong API authentication methods to find which one works.
"""

import httpx

# Credentials provided
ACCESS_KEY = "UQ4SK2LPUPBCFN7QHVLH6JRYEFSXEQML"
SECRET_JWT = "eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwODU1ODI2NTIsImFjY2Vzc0tleSI6IlVRNFNLMkxQVVBCQ0ZON1FIVkxINkpSWUVGU1hFUU1MIn0.2nO1ro56goeglnBVwY5gRtfxMAfc2W-8QY-gtMfgZeY"

BASE_URL = "https://api.gong.io/v2"
TEST_ENDPOINT = f"{BASE_URL}/calls"
TEST_PARAMS = {
    "fromDateTime": "2025-01-01T00:00:00Z",
    "toDateTime": "2025-01-31T23:59:59Z",
}


def test_auth_method(name: str, **kwargs):
    """Test an authentication method."""
    print(f"\n{'=' * 60}")
    print(f"Testing: {name}")
    print("=" * 60)

    try:
        response = httpx.get(TEST_ENDPOINT, params=TEST_PARAMS, timeout=10.0, **kwargs)
        print(f"Status: {response.status_code}")
        print(f"Headers sent: {kwargs.get('headers', {}).get('Authorization', 'N/A')[:50]}...")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ SUCCESS! Retrieved {len(data.get('calls', []))} calls")
            return True
        else:
            print(f"✗ FAILED: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


if __name__ == "__main__":
    results = {}

    # Method 1: Basic Auth with Access Key
    results["Basic Auth (access key)"] = test_auth_method(
        "Basic Auth with Access Key as username",
        auth=(ACCESS_KEY, ""),
        headers={"Accept": "application/json"},
    )

    # Method 2: Bearer token with JWT
    results["Bearer JWT"] = test_auth_method(
        "Bearer Token with JWT Secret",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {SECRET_JWT}",
        },
    )

    # Method 3: Bearer token with Access Key
    results["Bearer Access Key"] = test_auth_method(
        "Bearer Token with Access Key",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {ACCESS_KEY}",
        },
    )

    # Method 4: Basic Auth with JWT
    results["Basic Auth (JWT)"] = test_auth_method(
        "Basic Auth with JWT as username",
        auth=(SECRET_JWT, ""),
        headers={"Accept": "application/json"},
    )

    # Method 5: Access-Key header (custom)
    results["Access-Key header"] = test_auth_method(
        "Custom Access-Key Header",
        headers={
            "Accept": "application/json",
            "Access-Key": ACCESS_KEY,
        },
    )

    # Method 6: Access-Key + Secret-Key headers
    results["Access-Key + Secret headers"] = test_auth_method(
        "Custom Access-Key + Secret-Key Headers",
        headers={
            "Accept": "application/json",
            "Access-Key": ACCESS_KEY,
            "Secret-Key": SECRET_JWT,
        },
    )

    # Summary
    print("\n" + "=" * 60)
    print("AUTHENTICATION TEST SUMMARY")
    print("=" * 60)
    for method, success in results.items():
        status = "✓ WORKS" if success else "✗ FAILED"
        print(f"{status:12} {method}")

    if not any(results.values()):
        print("\n⚠️  All authentication methods failed!")
        print("The credentials may be invalid or expired.")
        print("Please verify credentials at: https://gong.app.gong.io/settings/api/authentication")
