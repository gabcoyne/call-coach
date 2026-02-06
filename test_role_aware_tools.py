"""
Test script for role-aware MCP tools.

Tests that role detection and role-aware filtering work correctly across all tools.
"""
import logging
from uuid import UUID

from coaching_mcp.tools.analyze_call import analyze_call_tool
from coaching_mcp.tools.search_calls import search_calls_tool
from db import fetch_one

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_analyze_call_with_role_detection():
    """Test analyze_call with automatic role detection."""
    print("\n" + "=" * 80)
    print("TEST 1: Analyze Call with Auto Role Detection")
    print("=" * 80)

    # Get a sample call from the database
    sample_call = fetch_one(
        """
        SELECT gong_call_id, id
        FROM calls
        WHERE processed_at IS NOT NULL
        LIMIT 1
        """
    )

    if not sample_call:
        print("❌ No processed calls found in database")
        return False

    call_id = sample_call["gong_call_id"]
    print(f"\n📞 Testing with call: {call_id}")

    try:
        # Test without role parameter (auto-detect)
        result = analyze_call_tool(
            call_id=call_id,
            dimensions=["discovery"],
            use_cache=True,
            include_transcript_snippets=False,
        )

        rep_analyzed = result.get("rep_analyzed")
        if rep_analyzed:
            evaluated_as_role = rep_analyzed.get("evaluated_as_role")
            print(f"✅ Auto-detected role: {evaluated_as_role}")
            print(f"   Rep: {rep_analyzed.get('name')} ({rep_analyzed.get('email')})")
        else:
            print("⚠️  No rep analyzed")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analyze_call_with_role_override():
    """Test analyze_call with manual role override."""
    print("\n" + "=" * 80)
    print("TEST 2: Analyze Call with Role Override")
    print("=" * 80)

    # Get a sample call
    sample_call = fetch_one(
        """
        SELECT gong_call_id
        FROM calls
        WHERE processed_at IS NOT NULL
        LIMIT 1
        """
    )

    if not sample_call:
        print("❌ No processed calls found")
        return False

    call_id = sample_call["gong_call_id"]
    print(f"\n📞 Testing with call: {call_id}")

    try:
        # Test with manual role override
        result = analyze_call_tool(
            call_id=call_id,
            dimensions=["discovery"],
            use_cache=True,
            include_transcript_snippets=False,
            role="se",  # Force SE evaluation
        )

        rep_analyzed = result.get("rep_analyzed")
        if rep_analyzed:
            evaluated_as_role = rep_analyzed.get("evaluated_as_role")
            print(f"✅ Forced role: se")
            print(f"   Evaluated as: {evaluated_as_role}")
            assert evaluated_as_role == "se", f"Expected 'se' but got '{evaluated_as_role}'"
        else:
            print("⚠️  No rep analyzed")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_calls_with_role_filter():
    """Test search_calls with role filtering."""
    print("\n" + "=" * 80)
    print("TEST 3: Search Calls with Role Filter")
    print("=" * 80)

    try:
        # Search for AE calls
        ae_calls = search_calls_tool(role="ae", limit=5)
        print(f"✅ Found {len(ae_calls)} AE calls")

        # Search for SE calls
        se_calls = search_calls_tool(role="se", limit=5)
        print(f"✅ Found {len(se_calls)} SE calls")

        # Search without role filter
        all_calls = search_calls_tool(limit=5)
        print(f"✅ Found {len(all_calls)} calls (no role filter)")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_role_detection_logic():
    """Test the role detection function directly."""
    print("\n" + "=" * 80)
    print("TEST 4: Role Detection Logic")
    print("=" * 80)

    from analysis.engine import detect_speaker_role

    # Get a sample call
    sample_call = fetch_one(
        """
        SELECT id
        FROM calls
        WHERE processed_at IS NOT NULL
        LIMIT 1
        """
    )

    if not sample_call:
        print("❌ No processed calls found")
        return False

    call_id = str(sample_call["id"])
    print(f"\n🔍 Testing role detection on call: {call_id}")

    try:
        detected_role = detect_speaker_role(call_id)
        print(f"✅ Detected role: {detected_role}")

        # Verify it's a valid role
        valid_roles = ["ae", "se", "csm"]
        assert detected_role in valid_roles, f"Invalid role: {detected_role}"

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("ROLE-AWARE MCP TOOLS TEST SUITE")
    print("=" * 80)

    tests = [
        test_role_detection_logic,
        test_analyze_call_with_role_detection,
        test_analyze_call_with_role_override,
        test_search_calls_with_role_filter,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
