#!/usr/bin/env python3
"""
BigCapitalPy MVP API Test Script

This script tests the core MVP APIs to ensure they work correctly.
Run this on your server after deploying the application.

Usage:
    python3 test_mvp_api.py --base-url http://your-server.com

Requirements:
    pip install requests
"""

import requests
import json
import sys
import argparse
from typing import Dict, Any, Optional

class MVPAPITester:
    def __init__(self, base_url: str, username: str = None, password: str = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.username = username or "admin"  # Default test user
        self.password = password or "password"  # Default test password

        # Test data
        self.test_customer_id = None
        self.test_invoice_id = None

    def log(self, message: str, level: str = "INFO"):
        """Log a message with level"""
        print(f"[{level}] {message}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> Dict:
        """Make an API request and return the response"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            self.log(f"{method} {endpoint} -> {response.status_code}")

            if response.status_code != expected_status:
                self.log(f"Expected status {expected_status}, got {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return None

            return response.json()

        except requests.RequestException as e:
            self.log(f"Request failed: {e}", "ERROR")
            return None

    def login(self) -> bool:
        """Login to establish session"""
        self.log("Logging in...")
        login_data = {
            "email": self.username,
            "password": self.password
        }

        response = self.make_request('POST', '/api/v1/auth/login', login_data, 200)
        if response and response.get('success'):
            self.log("Login successful", "SUCCESS")
            return True
        else:
            self.log("Login failed", "ERROR")
            return False

    def test_organizations_api(self) -> bool:
        """Test Organizations API"""
        self.log("\n=== Testing Organizations API ===")

        # Get organizations
        response = self.make_request('GET', '/api/v1/organizations')
        if not response or not response.get('success'):
            self.log("Failed to get organizations", "ERROR")
            return False

        orgs = response.get('data', {}).get('organizations', [])
        if not orgs:
            self.log("No organizations found", "WARNING")
            return False

        org_id = orgs[0]['id']
        self.log(f"Found organization ID: {org_id}", "SUCCESS")

        # Get specific organization
        response = self.make_request('GET', f'/api/v1/organizations/{org_id}')
        if not response or not response.get('success'):
            self.log("Failed to get specific organization", "ERROR")
            return False

        self.log("Organizations API test passed", "SUCCESS")
        return True

    def test_accounts_api(self) -> bool:
        """Test Accounts API"""
        self.log("\n=== Testing Accounts API ===")

        # Get accounts
        response = self.make_request('GET', '/api/v1/accounts')
        if not response or not response.get('success'):
            self.log("Failed to get accounts", "ERROR")
            return False

        accounts = response.get('data', {}).get('accounts', [])
        if not accounts:
            self.log("No accounts found", "WARNING")
            return False

        self.log(f"Found {len(accounts)} accounts", "SUCCESS")

        # Test hierarchy endpoint
        response = self.make_request('GET', '/api/v1/accounts/hierarchy')
        if not response or not response.get('success'):
            self.log("Failed to get account hierarchy", "ERROR")
            return False

        self.log("Accounts API test passed", "SUCCESS")
        return True

    def test_customers_api(self) -> bool:
        """Test Customers API"""
        self.log("\n=== Testing Customers API ===")

        # Create test customer
        customer_data = {
            "display_name": "Test Customer API",
            "company_name": "Test Company Inc",
            "email": "test@example.com",
            "phone": "+1-555-0123",
            "billing_address": "123 Test St",
            "billing_city": "Test City",
            "billing_state": "TS",
            "billing_postal_code": "12345",
            "billing_country": "USA"
        }

        response = self.make_request('POST', '/api/v1/customers', customer_data, 201)
        if not response or not response.get('success'):
            self.log("Failed to create customer", "ERROR")
            return False

        customer = response.get('data', {}).get('customer', {})
        self.test_customer_id = customer.get('id')
        self.log(f"Created customer ID: {self.test_customer_id}", "SUCCESS")

        # Get customers list
        response = self.make_request('GET', '/api/v1/customers')
        if not response or not response.get('success'):
            self.log("Failed to get customers list", "ERROR")
            return False

        # Get specific customer
        response = self.make_request('GET', f'/api/v1/customers/{self.test_customer_id}')
        if not response or not response.get('success'):
            self.log("Failed to get specific customer", "ERROR")
            return False

        # Update customer
        update_data = {"phone": "+1-555-0124"}
        response = self.make_request('PUT', f'/api/v1/customers/{self.test_customer_id}', update_data)
        if not response or not response.get('success'):
            self.log("Failed to update customer", "ERROR")
            return False

        self.log("Customers API test passed", "SUCCESS")
        return True

    def test_invoices_api(self) -> bool:
        """Test Invoices API"""
        self.log("\n=== Testing Invoices API ===")

        if not self.test_customer_id:
            self.log("No test customer available for invoice test", "ERROR")
            return False

        # Create test invoice
        from datetime import datetime, timedelta
        due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

        invoice_data = {
            "customer_id": self.test_customer_id,
            "invoice_date": datetime.now().strftime('%Y-%m-%d'),
            "due_date": due_date,
            "subtotal": 1000.00,
            "tax_amount": 100.00,
            "total": 1100.00,
            "line_items": [
                {
                    "description": "Test Service",
                    "quantity": 10,
                    "rate": 100.00,
                    "amount": 1000.00
                }
            ]
        }

        response = self.make_request('POST', '/api/v1/invoices', invoice_data, 201)
        if not response or not response.get('success'):
            self.log("Failed to create invoice", "ERROR")
            return False

        invoice = response.get('data', {}).get('invoice', {})
        self.test_invoice_id = invoice.get('id')
        invoice_number = invoice.get('invoice_number')
        self.log(f"Created invoice: {invoice_number} (ID: {self.test_invoice_id})", "SUCCESS")

        # Get invoices list
        response = self.make_request('GET', '/api/v1/invoices')
        if not response or not response.get('success'):
            self.log("Failed to get invoices list", "ERROR")
            return False

        # Get specific invoice
        response = self.make_request('GET', f'/api/v1/invoices/{self.test_invoice_id}')
        if not response or not response.get('success'):
            self.log("Failed to get specific invoice", "ERROR")
            return False

        # Test send invoice (may fail if email not configured, but API should work)
        response = self.make_request('POST', f'/api/v1/invoices/{self.test_invoice_id}/send', {}, 200)
        if response:  # Send may succeed or fail depending on email config
            self.log("Send invoice API responded (email config may vary)", "SUCCESS")
        else:
            self.log("Send invoice API failed", "WARNING")

        self.log("Invoices API test passed", "SUCCESS")
        return True

    def cleanup_test_data(self):
        """Clean up test data"""
        self.log("\n=== Cleaning up test data ===")

        # Delete test invoice
        if self.test_invoice_id:
            response = self.make_request('DELETE', f'/api/v1/invoices/{self.test_invoice_id}')
            if response and response.get('success'):
                self.log("Deleted test invoice", "SUCCESS")
            else:
                self.log("Failed to delete test invoice", "WARNING")

        # Delete test customer
        if self.test_customer_id:
            response = self.make_request('DELETE', f'/api/v1/customers/{self.test_customer_id}')
            if response and response.get('success'):
                self.log("Deleted test customer", "SUCCESS")
            else:
                self.log("Failed to delete test customer", "WARNING")

    def run_all_tests(self) -> bool:
        """Run all MVP API tests"""
        self.log("🚀 Starting BigCapitalPy MVP API Tests")
        self.log(f"Base URL: {self.base_url}")

        # Login first
        if not self.login():
            return False

        # Run tests
        tests = [
            ("Organizations API", self.test_organizations_api),
            ("Accounts API", self.test_accounts_api),
            ("Customers API", self.test_customers_api),
            ("Invoices API", self.test_invoices_api),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                self.log(f"Test {test_name} failed with exception: {e}", "ERROR")
                results.append((test_name, False))

        # Summary
        self.log("\n=== Test Results Summary ===")
        passed = 0
        total = len(results)

        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name}: {status}")
            if result:
                passed += 1

        success_rate = (passed / total) * 100
        self.log(f"\nOverall: {passed}/{total} tests passed ({success_rate:.1f}%)")

        # Cleanup
        self.cleanup_test_data()

        return passed == total


def main():
    parser = argparse.ArgumentParser(description='Test BigCapitalPy MVP APIs')
    parser.add_argument('--base-url', required=True, help='Base URL of the BigCapitalPy server')
    parser.add_argument('--username', default='admin', help='Login username')
    parser.add_argument('--password', default='password', help='Login password')

    args = parser.parse_args()

    tester = MVPAPITester(args.base_url, args.username, args.password)
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()