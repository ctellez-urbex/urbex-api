#!/bin/bash

echo "🚀 API Testing Tool for Urbex API"
echo "================================="

# Base URL
BASE_URL="http://localhost:8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4

    echo -e "\n${BLUE}🔍 Testing: $description${NC}"
    echo -e "${YELLOW}$method $BASE_URL$endpoint${NC}"

    if [ -n "$data" ]; then
        echo -e "${YELLOW}Data: $data${NC}"
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            --data-raw "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint")
    fi

    # Extract status code (last line)
    status_code=$(echo "$response" | tail -n1)
    # Extract response body (all lines except last)
    body=$(echo "$response" | head -n -1)

    if [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
        echo -e "${GREEN}✅ Status: $status_code${NC}"
    else
        echo -e "${RED}❌ Status: $status_code${NC}"
    fi

    echo -e "${YELLOW}Response:${NC}"
    echo "$body" | jq . 2>/dev/null || echo "$body"
}

# Test health check
test_endpoint "GET" "/health" "" "Health Check"

# Test contact form
test_endpoint "POST" "/api/v1/contact/" '{
    "full_name": "Test User",
    "email": "test@example.com",
    "phone": "+1234567890",
    "message": "This is a test message from the API testing tool with more than 10 characters."
}' "Contact Form"

# Test user registration
test_endpoint "POST" "/api/v1/auth/register" '{
    "username": "testuser'$(date +%s)'@example.com",
    "email": "testuser'$(date +%s)'@example.com",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
}' "User Registration"

# Test user login
test_endpoint "POST" "/api/v1/auth/login" '{
    "username": "carloss.tellezz@gmail.com",
    "password": "4p0C4l1ps1s"
}' "User Login"

echo -e "\n${GREEN}🎉 API Testing Complete!${NC}"
echo -e "\n${BLUE}📝 Notes:${NC}"
echo -e "• Login requires valid credentials"
echo -e "• Registration requires email confirmation"
echo -e "• Contact form sends emails to admin"
echo -e "• All endpoints are protected with API key in production"
