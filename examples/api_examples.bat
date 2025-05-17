@echo off
setlocal enabledelayedexpansion

:: Base URL for the API
set BASE_URL=http://localhost:8000/api/v1

:: Function to print a section header
:section
echo.
echo === %~1 ===
echo.
goto :eof

:: 1. Create a new host
call :section "Creating a new host"
for /f "tokens=*" %%a in ('curl -s -X POST "%BASE_URL%/hosts" ^
    -H "Content-Type: application/json" ^
    -d "{\"hostname\": \"example.com\", \"description\": \"Example domain\"}" ^| jq -r .id') do set "HOST_ID=%%a"
echo Created host with ID: %HOST_ID%

:: 2. List all hosts
call :section "Listing all hosts"
curl -s "%BASE_URL%/hosts" | jq

:: 3. Create an A record
call :section "Creating an A record"
for /f "tokens=*" %%a in ('curl -s -X POST "%BASE_URL%/records" ^
    -H "Content-Type: application/json" ^
    -d "{\"type\": \"A\", \"value\": \"192.168.1.1\", \"ttl\": 300, \"host_id\": %HOST_ID%}" ^| jq -r .id') do set "RECORD_ID=%%a"
echo Created A record with ID: %RECORD_ID%

:: 4. Create a CNAME record
call :section "Creating a CNAME record"
for /f "tokens=*" %%a in ('curl -s -X POST "%BASE_URL%/hosts" ^
    -H "Content-Type: application/json" ^
    -d "{\"hostname\": \"www.example.com\", \"description\": \"WWW alias\"}" ^| jq -r .id') do set "CNAME_HOST_ID=%%a"

echo Created CNAME host with ID: %CNAME_HOST_ID%

curl -s -X POST "%BASE_URL%/records" ^
    -H "Content-Type: application/json" ^
    -d "{\"type\": \"CNAME\", \"value\": \"example.com\", \"ttl\": 300, \"host_id\": %CNAME_HOST_ID%}" | jq

:: 5. List all records
call :section "Listing all records"
curl -s "%BASE_URL%/records" | jq

:: 6. Resolve a hostname
call :section "Resolving a hostname"
curl -s "%BASE_URL%/resolve/example.com" | jq

:: 7. Get CNAME chain
call :section "Getting CNAME chain"
curl -s "%BASE_URL%/cname-chain/www.example.com" | jq

:: 8. Clean up (optional)
call :section "Cleaning up"
set /p CLEANUP=Do you want to delete the test data? [y/N] 
if /i "!CLEANUP!"=="y" (
    echo Deleting records...
    curl -X DELETE "%BASE_URL%/records/%RECORD_ID%"
    curl -X DELETE "%BASE_URL%/hosts/%HOST_ID%"
    curl -X DELETE "%BASE_URL%/hosts/%CNAME_HOST_ID%"
    echo Cleanup complete!
)

echo.
echo API testing completed!
pause
