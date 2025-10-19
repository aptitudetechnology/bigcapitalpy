#!/bin/bash
# BigCapitalPy MVP API Test Runner
# Run this script on your server to test the MVP APIs

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_SCRIPT="$SCRIPT_DIR/test_mvp_api.py"

# Default values
BASE_URL="${BASE_URL:-http://localhost:5000}"
USERNAME="${API_USERNAME:-admin}"
PASSWORD="${API_PASSWORD:-password}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if requests library is available
if ! python3 -c "import requests" &> /dev/null; then
    warning "requests library not found. Installing..."
    pip3 install requests
fi

# Check if test script exists
if [ ! -f "$TEST_SCRIPT" ]; then
    error "Test script not found: $TEST_SCRIPT"
    exit 1
fi

log "🚀 Starting BigCapitalPy MVP API Tests"
log "Base URL: $BASE_URL"
log "Username: $USERNAME"

# Run the test script
log "Running API tests..."
if python3 "$TEST_SCRIPT" --base-url "$BASE_URL" --username "$USERNAME" --password "$PASSWORD"; then
    success "All MVP API tests passed!"
    exit 0
else
    error "Some MVP API tests failed!"
    exit 1
fi