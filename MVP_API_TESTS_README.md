# BigCapitalPy MVP API Test Scripts

These scripts test the core MVP APIs to ensure they work correctly on your server.

## Files

- `test_mvp_api.py` - Main Python test script
- `test_mvp_api.sh` - Shell script wrapper for easy execution

## Quick Start

### Option 1: Use the shell script (recommended)

```bash
# Set environment variables (optional)
export BASE_URL="https://your-server.com"
export API_USERNAME="your-admin-user"
export API_PASSWORD="your-password"

# Run the tests
./test_mvp_api.sh
```

### Option 2: Run Python script directly

```bash
# Install requests if needed
pip3 install requests

# Run with default settings
python3 test_mvp_api.py --base-url https://your-server.com

# Or specify credentials
python3 test_mvp_api.py \
  --base-url https://your-server.com \
  --username admin \
  --password yourpassword
```

## What the Tests Do

The test script performs these operations:

1. **Login** - Establishes session authentication
2. **Organizations API** - Lists and retrieves organization details
3. **Accounts API** - Lists accounts and tests hierarchy endpoint
4. **Customers API** - Creates, reads, updates, and deletes a test customer
5. **Invoices API** - Creates an invoice for the test customer and tests sending
6. **Cleanup** - Removes test data created during testing

## Expected Output

```
🚀 Starting BigCapitalPy MVP API Tests
Base URL: https://your-server.com
[INFO] Logging in...
[INFO] POST /api/v1/auth/login -> 200
[SUCCESS] Login successful
...
[INFO] Organizations API test passed
[SUCCESS] Accounts API test passed
[SUCCESS] Customers API test passed
[SUCCESS] Invoices API test passed
...
[SUCCESS] All MVP API tests passed!
```

## Configuration

### Environment Variables

- `BASE_URL` - Your BigCapitalPy server URL (default: http://localhost:5000)
- `API_USERNAME` - Admin username (default: admin)
- `API_PASSWORD` - Admin password (default: password)

### Command Line Options

- `--base-url` - Server URL (required)
- `--username` - Login username (default: admin)
- `--password` - Login password (default: password)

## Troubleshooting

### Login Issues
- Ensure the admin user exists and password is correct
- Check that the server is running and accessible

### API Failures
- Verify all MVP APIs are implemented and routes are registered
- Check server logs for detailed error messages
- Ensure database is properly set up with required tables

### Network Issues
- Confirm the BASE_URL is correct and server is reachable
- Check firewall settings and SSL certificates if using HTTPS

## Test Data

The script creates temporary test data:
- **Customer**: "Test Customer API" with test@example.com
- **Invoice**: $1,100 invoice with one line item

All test data is automatically cleaned up after testing.

## Requirements

- Python 3.6+
- `requests` library (`pip3 install requests`)
- Access to a running BigCapitalPy server
- Admin user credentials

## MVP Success Criteria

The tests validate that your MVP implementation meets these requirements:

✅ Can create customer via API  
✅ Can create invoice for customer via API  
✅ Can send invoice via API  
✅ All endpoints return proper JSON responses  
✅ Session-based authentication works  
✅ Basic CRUD operations function correctly  

When all tests pass, your BigCapitalPy MVP API is ready for use!