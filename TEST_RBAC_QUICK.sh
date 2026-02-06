#!/bin/bash
# Quick RBAC API test
# Run after restarting the API server

API_URL="http://localhost:8000"

echo "========================================="
echo "Quick RBAC API Test"
echo "========================================="
echo

echo "1. Testing GET /api/v1/users/me (as rep):"
curl -s -H "X-User-Email: trent@prefect.io" "$API_URL/api/v1/users/me" | jq -r '"\(.email) - \(.role)"' 2>/dev/null || echo "  ⚠ Server not running or route not registered"
echo

echo "2. Testing GET /api/v1/users/me (as manager):"
curl -s -H "X-User-Email: ann@prefect.io" "$API_URL/api/v1/users/me" | jq -r '"\(.email) - \(.role)"' 2>/dev/null || echo "  ⚠ Server not running or route not registered"
echo

echo "3. Testing GET /api/v1/team/reps (as rep - should fail):"
status=$(curl -s -o /dev/null -w "%{http_code}" -H "X-User-Email: trent@prefect.io" "$API_URL/api/v1/team/reps")
if [ "$status" = "403" ]; then
    echo "  ✓ Correctly forbidden (403)"
elif [ "$status" = "404" ]; then
    echo "  ⚠ Route not found (404) - server needs restart"
else
    echo "  ✗ Unexpected status: $status"
fi
echo

echo "4. Testing GET /api/v1/team/reps (as manager - should work):"
count=$(curl -s -H "X-User-Email: ann@prefect.io" "$API_URL/api/v1/team/reps" | jq 'length' 2>/dev/null)
if [ "$count" != "null" ] && [ "$count" != "" ]; then
    echo "  ✓ Success - returned $count reps"
elif [ "$count" = "null" ]; then
    echo "  ⚠ Route not found - server needs restart"
else
    echo "  ✗ Failed"
fi
echo

echo "5. Testing GET /api/v1/calls (as rep):"
count=$(curl -s -H "X-User-Email: trent@prefect.io" "$API_URL/api/v1/calls?limit=5" | jq 'length' 2>/dev/null)
if [ "$count" != "null" ] && [ "$count" != "" ]; then
    echo "  ✓ Success - returned $count calls"
elif [ "$count" = "null" ]; then
    echo "  ⚠ Route not found - server needs restart"
else
    echo "  ✗ Failed"
fi
echo

echo "========================================="
echo "If you see '⚠ Route not found' messages,"
echo "restart the API server:"
echo "  ps aux | grep rest_server"
echo "  kill <PID>"
echo "  python api/rest_server.py"
echo "========================================="
