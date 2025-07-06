#!/usr/bin/env python3
"""
Schema Sync Checker for BigCapitalPy
Check all model columns vs database columns to identify mismatches
"""

from packages.server.src.models import *
from sqlalchemy import inspect

def check_schema_sync():
    """Check if database schema matches SQLAlchemy models"""
    inspector = inspect(db.engine)
    
    # Get all tables from database
    db_tables = inspector.get_table_names()
    
    # Models to check (add more as needed)
    models_to_check = [
        ('journal_entries', JournalEntry),
        # Add other models here as needed
        # ('accounts', Account),
        # ('customers', Customer),
        # ('vendors', Vendor),
    ]
    
    print("=" * 60)
    print("DATABASE SCHEMA SYNC CHECK")
    print("=" * 60)
    
    all_good = True
    
    for table_name, model_class in models_to_check:
        print(f"\n📋 Checking table: {table_name}")
        print("-" * 40)
        
        # Check if table exists in database
        if table_name not in db_tables:
            print(f"❌ Table '{table_name}' does not exist in database!")
            all_good = False
            continue
            
        # Get columns from database
        table_columns = [col['name'] for col in inspector.get_columns(table_name)]
        
        # Get columns from model
        model_columns = [col.name for col in model_class.__table__.columns]
        
        # Find differences
        missing_in_db = set(model_columns) - set(table_columns)
        extra_in_db = set(table_columns) - set(model_columns)
        
        # Report results
        if missing_in_db:
            print(f"❌ Missing columns in database: {missing_in_db}")
            all_good = False
        
        if extra_in_db:
            print(f"⚠️  Extra columns in database: {extra_in_db}")
        
        if not missing_in_db and not extra_in_db:
            print("✅ Schema matches perfectly!")
        
        # Show column details for debugging
        print(f"📊 Model columns ({len(model_columns)}): {sorted(model_columns)}")
        print(f"📊 DB columns ({len(table_columns)}): {sorted(table_columns)}")
    
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 ALL SCHEMAS ARE IN SYNC!")
    else:
        print("⚠️  SCHEMA MISMATCHES FOUND - Run migrations to fix")
        print("\nTo fix:")
        print("1. make db-migrate MSG='Fix schema mismatches'")
        print("2. make db-upgrade")
    print("=" * 60)

def check_specific_table(table_name, model_class):
    """Check a specific table/model combination"""
    inspector = inspect(db.engine)
    
    print(f"\n🔍 Detailed check for {table_name}:")
    
    # Get column details from database
    db_columns = inspector.get_columns(table_name)
    model_columns = model_class.__table__.columns
    
    print(f"\n📋 Database columns:")
    for col in db_columns:
        print(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")
    
    print(f"\n📋 Model columns:")
    for col in model_columns:
        print(f"  - {col.name}: {col.type} (nullable: {col.nullable})")

if __name__ == "__main__":
    # Run the main check
    check_schema_sync()
    
    # Uncomment to get detailed info about journal_entries specifically
    # check_specific_table('journal_entries', JournalEntry)