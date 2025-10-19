# BigCapitalPy API Key Management

## Overview
BigCapitalPy supports both session-based authentication (for web users) and API key authentication (for programmatic access).

## Generating an API Key

### Method 1: Web Interface
1. Log in to your BigCapitalPy account
2. Navigate to your user profile/settings
3. Click "Generate API Key"
4. Copy the generated key (it will only be shown once)

### Method 2: API Endpoint
```bash
# First, login to get a session
curl -X POST http://your-server.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your-email@example.com","password":"your-password"}' \
  --cookie-jar cookies.txt

# Then generate an API key
curl -X POST http://your-server.com/api/v1/auth/api-key \
  --cookie cookies.txt
```

## Using API Keys

Include the API key in your request headers:

```bash
# Using X-API-Key header
curl -X GET http://your-server.com/api/v1/customers \
  -H "X-API-Key: your-api-key-here"

# Using Authorization header
curl -X GET http://your-server.com/api/v1/customers \
  -H "Authorization: Bearer your-api-key-here"
```

## API Key Management

### Check API Key Status
```bash
curl -X GET http://your-server.com/api/v1/auth/api-key \
  --cookie cookies.txt
```

### Revoke API Key
```bash
curl -X DELETE http://your-server.com/api/v1/auth/api-key \
  --cookie cookies.txt
```

## Security Notes
- API keys provide full access to your account
- Store API keys securely (treat them like passwords)
- Regenerate keys if they may have been compromised
- Use different keys for different applications/services

## Database Migration
If upgrading an existing installation, run the migration script:
```bash
sqlite3 bigcapitalpy.db < add_api_key_migration.sql
```