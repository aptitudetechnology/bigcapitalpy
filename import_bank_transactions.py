#!/usr/bin/env python3
"""
Bank Transaction Import Script for BigCapitalPy

This script analyzes and optionally imports transaction data from CSV files
into the BigCapitalPy banking system.

Usage:
    python import_bank_transactions.py <csv_file_path> [--preview] [--import] [--account-name NAME]

Requirements:
    - BigCapitalPy banking models (BankAccount, BankTransaction)
    - SQLAlchemy database setup

Examples:
    python import_bank_transactions.py bank/fy_2024_25_bank_transactions.csv --preview
    python import_bank_transactions.py bank/fy_2024_25_bank_transactions.csv --import --account-name "My Bank Account"
"""

import sys
import csv
import argparse
from datetime import datetime
from flask import Flask
from packages.server.src.database import db
from packages.server.src.models import BankAccount, BankTransaction, Organization, User

def parse_amount(amount_str):
    """Parse amount string, handling commas and empty values"""
    if not amount_str or amount_str.strip() == '' or amount_str.lower() == 'nan':
        return 0.0
    return float(amount_str.replace(',', '').strip())

def analyze_csv(csv_path):
    """Analyze CSV file and return summary statistics"""
    print(f"📊 Analyzing CSV file: {csv_path}")

    transactions = []
    dates = []
    credits = 0.0
    debits = 0.0

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse transaction data
            transaction_date = datetime.strptime(row['parsed_date'], '%Y-%m-%d').date()
            dates.append(transaction_date)

            debit_amount = parse_amount(row.get('debit_net_amount', ''))
            credit_amount = parse_amount(row.get('credit_net_amount', ''))

            if debit_amount > 0:
                amount = -debit_amount
                debits += debit_amount
            elif credit_amount > 0:
                amount = credit_amount
                credits += credit_amount
            else:
                continue

            transactions.append({
                'date': transaction_date,
                'description': row.get('description', '').strip()[:100],
                'amount': amount,
                'reference': row.get('transaction_id', '').strip()
            })

    # Calculate summary
    summary = {
        'total_transactions': len(transactions),
        'date_range': (min(dates), max(dates)) if dates else (None, None),
        'total_credits': credits,
        'total_debits': debits,
        'net_amount': credits - debits,
        'sample_transactions': transactions[:5]  # First 5 transactions
    }

    return summary

def preview_import(summary, account_name):
    """Display import preview and get user confirmation"""
    print("\n" + "="*60)
    print("📋 IMPORT PREVIEW")
    print("="*60)

    print(f"🏦 Account Name: {account_name}")
    print(f"📊 Transactions to Import: {summary['total_transactions']}")

    if summary['date_range'][0]:
        print(f"📅 Date Range: {summary['date_range'][0]} to {summary['date_range'][1]}")

    print(f"💰 Total Credits: ${summary['total_credits']:,.2f}")
    print(f"💸 Total Debits: ${summary['total_debits']:,.2f}")
    print(f"🏦 Expected Final Balance: ${summary['net_amount']:,.2f}")

    print("\n📝 Sample Transactions:")
    print("-" * 60)
    for i, tx in enumerate(summary['sample_transactions'], 1):
        print(f"{i}. {tx['date']} | {tx['description'][:50]}... | ${tx['amount']:,.2f}")

    print("\n" + "="*60)

    while True:
        response = input("Do you want to proceed with the import? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")

def import_bank_transactions(csv_path, account_name="Airwallex AUD Account", account_type="bank"):
    """
    Import bank transactions from CSV into BigCapitalPy

    Args:
        csv_path (str): Path to CSV file
        account_name (str): Name for the bank account
        account_type (str): Type of account (cash, bank, credit-card)
    """

    # Create Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bigcapitalpy.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        # Get or create default organization
        org = Organization.query.first()
        if not org:
            org = Organization(
                name='Default Organization',
                currency='AUD',
                fiscal_year_start='07-01',  # July 1st
                timezone='Australia/Perth'
            )
            db.session.add(org)
            db.session.commit()
            print("✅ Created default organization")

        # Get or create default user
        user = User.query.first()
        if not user:
            user = User(
                email='admin@bigcapitalpy.com',
                first_name='Admin',
                last_name='User',
                password_hash='dummy_hash',  # In real app, use proper hashing
                is_active=True,
                role='admin',
                organization_id=org.id
            )
            db.session.add(user)
            db.session.commit()
            print("✅ Created default user")

        # Check if account already exists
        existing_account = BankAccount.query.filter_by(
            name=account_name,
            organization_id=org.id
        ).first()

        if existing_account:
            print(f"⚠️  Account '{account_name}' already exists.")
            response = input("Do you want to update the existing account? (y/n): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Import cancelled.")
                return
            account = existing_account
        else:
            # Create bank account
            account = BankAccount(
                name=account_name,
                account_type=account_type,
                currency='AUD',
                balance=0.0,  # Will be calculated from transactions
                is_active=True,
                organization_id=org.id
            )
            db.session.add(account)
            db.session.commit()
            print(f"✅ Created bank account: {account_name}")

        # Read and process CSV
        print(f"📖 Reading transactions from {csv_path}")
        transactions_imported = 0
        total_credits = 0.0
        total_debits = 0.0

        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        print(f"📊 Processing {len(rows)} transactions...")

        for row in rows:
            try:
                # Parse transaction data
                transaction_date = datetime.strptime(row['parsed_date'], '%Y-%m-%d').date()

                # Determine transaction type and amount
                debit_amount = parse_amount(row.get('debit_net_amount', ''))
                credit_amount = parse_amount(row.get('credit_net_amount', ''))

                if debit_amount > 0:
                    amount = -debit_amount
                    transaction_type = 'debit'
                    total_debits += debit_amount
                elif credit_amount > 0:
                    amount = credit_amount
                    transaction_type = 'credit'
                    total_credits += credit_amount
                else:
                    continue  # Skip zero-amount transactions

                # Get description
                description = row.get('description', '').strip()
                if not description:
                    description = f"{row.get('type', 'Unknown')} transaction"

                # Get balance after transaction
                balance = parse_amount(row.get('account_balance', '0'))

                # Check if transaction already exists (by reference if available)
                reference = row.get('transaction_id', '').strip()
                if reference:
                    existing_transaction = BankTransaction.query.filter_by(
                        reference=reference,
                        account_id=account.id
                    ).first()
                    if existing_transaction:
                        continue  # Skip duplicate

                # Create transaction record
                transaction = BankTransaction(
                    account_id=account.id,
                    transaction_date=transaction_date,
                    amount=amount,
                    description=description[:500],  # Truncate if too long
                    reference=reference,
                    balance=balance,
                    status='unmatched',  # Default status
                    organization_id=org.id
                )

                db.session.add(transaction)
                transactions_imported += 1

                # Print progress every 10 transactions
                if transactions_imported % 10 == 0:
                    print(f"  Imported {transactions_imported} transactions...")

            except Exception as e:
                print(f"❌ Error processing transaction: {e}")
                print(f"   Row data: {row}")
                continue

        # Commit all transactions
        db.session.commit()

        # Update account balance
        final_balance = parse_amount(rows[-1]['account_balance']) if rows else 0.0
        account.balance = final_balance
        db.session.commit()

        # Print summary
        print("
✅ Import completed successfully!"        print(f"🏦 Account: {account_name}")
        print(f"📊 Transactions imported: {transactions_imported}")
        print(f"💰 Total credits: ${total_credits:.2f}")
        print(f"💸 Total debits: ${total_debits:.2f}")
        print(f"🏦 Final balance: ${final_balance:.2f}")
        print(f"📅 Date range: {rows[0]['parsed_date']} to {rows[-1]['parsed_date']}")

def main():
    parser = argparse.ArgumentParser(description='Analyze and import bank transactions into BigCapitalPy')
    parser.add_argument('csv_file', help='Path to CSV file containing transactions')
    parser.add_argument('--preview', action='store_true', help='Show preview of what will be imported')
    parser.add_argument('--import', action='store_true', help='Perform the actual import')
    parser.add_argument('--account-name', default='Airwallex AUD Account',
                       help='Name for the bank account (default: Airwallex AUD Account)')
    parser.add_argument('--account-type', default='bank',
                       choices=['cash', 'bank', 'credit-card'],
                       help='Type of account (default: bank)')

    args = parser.parse_args()

    # Validate arguments
    if not args.preview and not args.import:
        print("❌ Please specify either --preview or --import")
        print("Use --preview to see what will be imported")
        print("Use --import to actually perform the import")
        sys.exit(1)

    try:
        # Analyze the CSV first
        summary = analyze_csv(args.csv_file)

        if args.preview:
            # Just show preview
            preview_import(summary, args.account_name)
        elif args.import:
            # Show preview and ask for confirmation
            if preview_import(summary, args.account_name):
                import_bank_transactions(args.csv_file, args.account_name, args.account_type)
            else:
                print("Import cancelled by user.")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
        # Get or create default organization
        org = Organization.query.first()
        if not org:
            org = Organization(
                name='Default Organization',
                currency='AUD',
                fiscal_year_start='07-01',  # July 1st
                timezone='Australia/Perth'
            )
            db.session.add(org)
            db.session.commit()
            print("✅ Created default organization")

        # Get or create default user
        user = User.query.first()
        if not user:
            user = User(
                email='admin@bigcapitalpy.com',
                first_name='Admin',
                last_name='User',
                password_hash='dummy_hash',  # In real app, use proper hashing
                is_active=True,
                role='admin',
                organization_id=org.id
            )
            db.session.add(user)
            db.session.commit()
            print("✅ Created default user")

        # Check if account already exists
        existing_account = BankAccount.query.filter_by(
            name=account_name,
            organization_id=org.id
        ).first()

        if existing_account:
            print(f"⚠️  Account '{account_name}' already exists. Skipping account creation.")
            account = existing_account
        else:
            # Create bank account
            account = BankAccount(
                name=account_name,
                account_type=account_type,
                currency='AUD',
                balance=0.0,  # Will be calculated from transactions
                is_active=True,
                organization_id=org.id
            )
            db.session.add(account)
            db.session.commit()
            print(f"✅ Created bank account: {account_name}")

        # Read and process CSV
        print(f"📖 Reading transactions from {csv_path}")
        transactions_imported = 0
        total_credits = 0.0
        total_debits = 0.0

        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        print(f"📊 Processing {len(rows)} transactions...")

        for row in rows:
            try:
                # Parse transaction data
                transaction_date = datetime.strptime(row['parsed_date'], '%Y-%m-%d').date()

                # Determine transaction type and amount
                debit_amount = parse_amount(row.get('debit_net_amount', ''))
                credit_amount = parse_amount(row.get('credit_net_amount', ''))

                if debit_amount > 0:
                    amount = -debit_amount  # Negative for debits
                    transaction_type = 'debit'
                    total_debits += debit_amount
                elif credit_amount > 0:
                    amount = credit_amount  # Positive for credits
                    transaction_type = 'credit'
                    total_credits += credit_amount
                else:
                    continue  # Skip zero-amount transactions

                # Get description
                description = row.get('description', '').strip()
                if not description:
                    description = f"{row.get('type', 'Unknown')} transaction"

                # Get balance after transaction
                balance = parse_amount(row.get('account_balance', '0'))

                # Check if transaction already exists (by reference if available)
                reference = row.get('transaction_id', '').strip()
                if reference:
                    existing_transaction = BankTransaction.query.filter_by(
                        reference=reference,
                        account_id=account.id
                    ).first()
                    if existing_transaction:
                        continue  # Skip duplicate

                # Create transaction record
                transaction = BankTransaction(
                    account_id=account.id,
                    transaction_date=transaction_date,
                    amount=amount,
                    description=description[:500],  # Truncate if too long
                    reference=reference,
                    balance=balance,
                    status='unmatched',  # Default status
                    organization_id=org.id
                )

                db.session.add(transaction)
                transactions_imported += 1

                # Print progress every 10 transactions
                if transactions_imported % 10 == 0:
                    print(f"  Imported {transactions_imported} transactions...")

            except Exception as e:
                print(f"❌ Error processing transaction: {e}")
                print(f"   Row data: {row}")
                continue

        # Commit all transactions
        db.session.commit()

        # Update account balance
        final_balance = parse_amount(rows[-1]['account_balance']) if rows else 0.0
        account.balance = final_balance
        db.session.commit()

        # Print summary
        print("\n✅ Import completed successfully!")
        print(f"🏦 Account: {account_name}")
        print(f"📊 Transactions imported: {transactions_imported}")
        print(f"💰 Total credits: ${total_credits:.2f}")
        print(f"💸 Total debits: ${total_debits:.2f}")
        print(f"🏦 Final balance: ${final_balance:.2f}")
        print(f"📅 Date range: {rows[0]['parsed_date']} to {rows[-1]['parsed_date']}")

def main():
    parser = argparse.ArgumentParser(description='Import bank transactions into BigCapitalPy')
    parser.add_argument('csv_file', help='Path to CSV file containing transactions')
    parser.add_argument('--account-name', default='Airwallex AUD Account',
                       help='Name for the bank account (default: Airwallex AUD Account)')
    parser.add_argument('--account-type', default='bank',
                       choices=['cash', 'bank', 'credit-card'],
                       help='Type of account (default: bank)')

    args = parser.parse_args()

    try:
        import_bank_transactions(args.csv_file, args.account_name, args.account_type)
    except Exception as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()