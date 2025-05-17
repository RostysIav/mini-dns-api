#!/bin/bash

# Base URL for the API
BASE_URL="http://localhost:8000/api/v1"

# Function to print a section header
section() {
    echo ""
    echo "=== $1 ==="
    echo ""
}

# 1. Create a new host
section "Creating a new host"
HOST_ID=$(curl -s -X POST "$BASE_URL/hosts" \
    -H "Content-Type: application/json" \
    -d '{"hostname": "example.com", "description": "Example domain"}' | jq -r '.id')
echo "Created host with ID: $HOST_ID"

# 2. List all hosts
section "Listing all hosts"
curl -s "$BASE_URL/hosts" | jq

# 3. Create an A record
section "Creating an A record"
RECORD_ID=$(curl -s -X POST "$BASE_URL/records" \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"A\", \"value\": \"192.168.1.1\", \"ttl\": 300, \"host_id\": $HOST_ID}" | jq -r '.id')
echo "Created A record with ID: $RECORD_ID"

# 4. Create a CNAME record
section "Creating a CNAME record"
CNAME_HOST_ID=$(curl -s -X POST "$BASE_URL/hosts" \
    -H "Content-Type: application/json" \
    -d '{"hostname": "www.example.com", "description": "WWW alias"}' | jq -r '.id')

echo "Created CNAME host with ID: $CNAME_HOST_ID"

curl -s -X POST "$BASE_URL/records" \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"CNAME\", \"value\": \"example.com\", \"ttl\": 300, \"host_id\": $CNAME_HOST_ID}" | jq

# 5. List all records
section "Listing all records"
curl -s "$BASE_URL/records" | jq

# 6. Resolve a hostname
section "Resolving a hostname"
curl -s "$BASE_URL/resolve/example.com" | jq

# 7. Get CNAME chain
section "Getting CNAME chain"
curl -s "$BASE_URL/cname-chain/www.example.com" | jq

# 8. Clean up (optional)
section "Cleaning up"
read -p "Do you want to delete the test data? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Deleting records..."
    curl -X DELETE "$BASE_URL/records/$RECORD_ID"
    curl -X DELETE "$BASE_URL/hosts/$HOST_ID"
    curl -X DELETE "$BASE_URL/hosts/$CNAME_HOST_ID"
    echo "Cleanup complete!"
fi

echo "\nAPI testing completed!"
