# Mini DNS API - Testing Guide

This document serves as a comprehensive testing guide for the Mini DNS API. It outlines all test cases, scenarios, and validation points to ensure the application functions as expected.

## Table of Contents
1. [Environment Setup](#environment-setup)
2. [API Endpoints](#api-endpoints)
3. [Test Cases](#test-cases)
   - [Host Management](#host-management)
   - [Record Management](#record-management)
   - [DNS Resolution](#dns-resolution)
   - [Validation Rules](#validation-rules)
   - [Error Handling](#error-handling)
   - [Background Tasks](#background-tasks)
4. [Integration Testing](#integration-testing)
5. [Performance Testing](#performance-testing)
6. [Security Testing](#security-testing)
7. [Test Data](#test-data)

## Environment Setup

### Prerequisites
- Python 3.13.3
- pip (Python package manager)
- SQLite (default) / PostgreSQL / MySQL
- Redis (for background tasks in production)

### Test Environment
1. Create and activate virtual environment:
   ```bash
   python -m venv .venv313
   .venv313\Scripts\activate  # Windows
   ```

2. Install test dependencies:
   ```bash
   pip install -e ".[test]"
   ```

3. Set up environment variables (create `.env` file):
   ```env
   ENVIRONMENT=testing
   SQLALCHEMY_DATABASE_URI=sqlite:///./test.db
   DEBUG=true
   ```

4. Initialize test database:
   ```bash
   python -c "from app.core.database import init_db; init_db()"
   ```

## API Endpoints

### Base URL
- `http://localhost:8000` (development)
- `http://api.example.com` (production)

### Available Endpoints

#### Host Management
- `POST /api/hosts/` - Create a new host
- `GET /api/hosts/` - List all hosts

#### Record Management
- `POST /api/records/` - Create a new DNS record
- `GET /api/records/` - List all DNS records

#### DNS Resolution
- `GET /api/resolve/{hostname}` - Resolve a hostname
- `GET /api/cname-chain/{hostname}` - Get CNAME chain

#### System
- `GET /health` - Health check
- `GET /status` - System status
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Test Cases

### Host Management

#### 1. Create Host
**Test Case ID**: HOST-001  
**Description**: Create a new host with valid data  
**Preconditions**: None  
**Test Steps**:
1. Send POST request to `/api/hosts/` with valid hostname
2. Verify response status code is 201
3. Verify response contains created host data
4. Verify host exists in database

**Test Data**:
```json
{
  "hostname": "example.com"
}
```

**Expected Results**:
- Status: 201 Created
- Response contains host data with ID
- Host is stored in database

---

**Test Case ID**: HOST-002  
**Description**: Create host with duplicate name  
**Preconditions**: Host 'example.com' exists  
**Test Steps**:
1. Send POST request to create host 'example.com'
2. Verify response status code is 409
3. Verify error message indicates duplicate host

**Expected Results**:
- Status: 409 Conflict
- Error message indicates duplicate host
- No new host created

---

### Record Management

#### 1. Create A Record
**Test Case ID**: RECORD-001  
**Description**: Create a new A record  
**Preconditions**: Host exists  
**Test Steps**:
1. Send POST request to `/api/records/` with A record data
2. Verify response status code is 201
3. Verify response contains created record
4. Verify record exists in database

**Test Data**:
```json
{
  "host_id": 1,
  "type": "A",
  "value": "192.168.1.1",
  "ttl": 3600
}
```

**Expected Results**:
- Status: 201 Created
- Response contains record with ID
- Record is stored in database

---

#### 2. Create CNAME Record
**Test Case ID**: RECORD-002  
**Description**: Create a new CNAME record  
**Preconditions**: Host exists  
**Test Steps**:
1. Send POST request to `/api/records/` with CNAME record data
2. Verify response status code is 201
3. Verify response contains created record
4. Verify record exists in database

**Test Data**:
```json
{
  "host_id": 1,
  "type": "CNAME",
  "value": "www.example.com",
  "ttl": 3600
}
```

**Expected Results**:
- Status: 201 Created
- Response contains CNAME record
- Record is stored in database

---

### DNS Resolution

#### 1. Resolve Hostname
**Test Case ID**: RESOLVE-001  
**Description**: Resolve a hostname with A record  
**Preconditions**: Host with A record exists  
**Test Steps**:
1. Send GET request to `/api/resolve/example.com`
2. Verify response status code is 200
3. Verify response contains correct A record

**Expected Results**:
- Status: 200 OK
- Response contains A record with correct IP
- TTL is included in response

---

#### 2. Follow CNAME Chain
**Test Case ID**: RESOLVE-002  
**Description**: Resolve hostname with CNAME chain  
**Preconditions**: Host with CNAME record exists  
**Test Steps**:
1. Send GET request to `/api/resolve/example.com`
2. Verify response status code is 200
3. Verify response follows CNAME chain
4. Verify final record is returned

**Expected Results**:
- Status: 200 OK
- Response follows CNAME chain
- Final record is returned

---

### Validation Rules

#### 1. Hostname Validation
- [ ] Accepts valid hostnames (e.g., "example.com", "sub.domain.co.uk")
- [ ] Rejects invalid hostnames (e.g., "-invalid.", "test@test")
- [ ] Handles IDN (Internationalized Domain Names)
- [ ] Enforces maximum length (253 characters)

#### 2. IP Address Validation
- [ ] Validates IPv4 addresses
- [ ] Rejects invalid IPs
- [ ] Handles edge cases (e.g., "0.0.0.0", "255.255.255.255")

#### 3. Record Type Validation
- [ ] Accepts valid record types (A, CNAME, MX)
- [ ] Rejects invalid record types
- [ ] Validates record-specific fields (e.g., priority for MX)

### Error Handling

#### 1. Not Found (404)
- [ ] Non-existent host
- [ ] Non-existent record
- [ ] Invalid endpoint

#### 2. Bad Request (400)
- [ ] Invalid JSON
- [ ] Missing required fields
- [ ] Invalid field values

#### 3. Conflict (409)
- [ ] Duplicate hostname
- [ ] Conflicting record types
- [ ] CNAME with other records

### Background Tasks

#### 1. Record Expiry
- [ ] Records past TTL are detected
- [ ] Expired records are handled correctly
- [ ] Logs are generated for expired records

#### 2. Statistics Collection
- [ ] Record counts are accurate
- [ ] Stats are updated periodically
- [ ] Performance impact is minimal

## Integration Testing

### Test Scenarios
1. **Full DNS Resolution Flow**
   - Create host
   - Add A record
   - Add CNAME record
   - Resolve hostname
   - Verify chain resolution

2. **Error Recovery**
   - Test with invalid data
   - Verify proper error responses
   - Check application remains stable

## Performance Testing

### Test Cases
1. **Load Testing**
   - 1000 requests per second
   - Measure response times
   - Monitor resource usage

2. **Concurrent Connections**
   - 100+ concurrent users
   - Verify no data corruption
   - Check connection handling

## Security Testing

### Test Cases
1. **Input Validation**
   - SQL injection attempts
   - XSS attempts
   - Path traversal attempts

2. **Authentication**
   - Unauthorized access attempts
   - Rate limiting
   - Session management

## Test Data

### Sample Hosts
```json
{
  "hostname": "example.com"
}
```

### Sample Records
```json
{
  "host_id": 1,
  "type": "A",
  "value": "192.168.1.1",
  "ttl": 3600
}

{
  "host_id": 1,
  "type": "CNAME",
  "value": "www.example.com",
  "ttl": 3600
}

{
  "host_id": 1,
  "type": "MX",
  "value": "mail.example.com",
  "priority": 10,
  "ttl": 3600
}
```

## Test Automation

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_hosts.py

# Run with coverage report
pytest --cov=app tests/
```

### Test Reports
- HTML coverage report: `htmlcov/index.html`
- JUnit XML report: `test-results.xml`
- Coverage report: `coverage.xml`

## Monitoring and Logging

### Log Files
- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Access logs: `logs/access.log`

### Metrics
- Request/response times
- Error rates
- Database query performance
- Background task execution times

## Deployment Checklist

### Pre-Deployment
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Backup existing data
- [ ] Notify stakeholders

### Post-Deployment
- [ ] Verify health check
- [ ] Smoke test critical paths
- [ ] Monitor error rates
- [ ] Performance metrics within thresholds
