#!/usr/bin/env python3
"""
Bank Data Extraction Script for BigCapitalPy

This script extracts transaction data from PDF bank statements and filters
for Australian Financial Year 2024-25 (July 1, 2024 - June 30, 2025).

Usage:
    python extract_bank_data.py <pdf_file_path>

Requirements:
    - pdfplumber
    - pandas

Install dependencies:
    pip install pdfplumber pandas
"""

import sys
import pdfplumber
import pandas as pd
from datetime import datetime
import os

def extract_bank_data(pdf_path):
    """
    Extract transaction data from Airwallex PDF bank statement.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        pd.DataFrame: DataFrame containing transaction data
    """
    print(f"Extracting data from: {pdf_path}")

    all_transactions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            print(f"Processing page {page_num + 1}/{len(pdf.pages)}")

            # Extract tables from the page
            tables = page.extract_tables()

            for table_idx, table in enumerate(tables):
                if not table:
                    continue

                # Convert table to DataFrame for easier processing
                df = pd.DataFrame(table)

                # Look for transaction data (typically has Date, Description, Amount columns)
                # Airwallex format seems to have headers in the first row
                if len(df.columns) >= 3:
                    # Check if first row looks like headers
                    first_row = df.iloc[0].astype(str).str.lower()

                    # Look for date, description, amount patterns
                    has_date = any('date' in str(cell).lower() for cell in df.iloc[0])
                    has_amount = any('amount' in str(cell).lower() or 'debit' in str(cell).lower() or 'credit' in str(cell).lower() for cell in df.iloc[0])

                    if has_date and has_amount:
                        print(f"Found transaction table on page {page_num + 1}, table {table_idx + 1}")

                        # Skip header row and process data rows
                        for idx, row in df.iloc[1:].iterrows():
                            try:
                                # Extract date, description, and amount
                                date_str = str(row[0]).strip() if len(row) > 0 else ""
                                description = str(row[1]).strip() if len(row) > 1 else ""
                                amount_str = str(row[2]).strip() if len(row) > 2 else ""

                                # Skip empty rows
                                if not date_str or date_str.lower() in ['nan', 'none', '']:
                                    continue

                                # Parse date
                                try:
                                    # Try different date formats
                                    for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y']:
                                        try:
                                            transaction_date = datetime.strptime(date_str, fmt)
                                            break
                                        except ValueError:
                                            continue
                                    else:
                                        print(f"Could not parse date: {date_str}")
                                        continue
                                except Exception as e:
                                    print(f"Error parsing date '{date_str}': {e}")
                                    continue

                                # Parse amount
                                try:
                                    # Remove currency symbols and commas
                                    amount_clean = amount_str.replace('$', '').replace(',', '').replace(' ', '')
                                    if amount_clean.startswith('(') and amount_clean.endswith(')'):
                                        # Negative amount in parentheses
                                        amount_clean = '-' + amount_clean[1:-1]
                                    amount = float(amount_clean)
                                except (ValueError, AttributeError):
                                    print(f"Could not parse amount: {amount_str}")
                                    continue

                                # Create transaction record
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'description': description,
                                    'amount': amount,
                                    'source': 'Airwallex'
                                }

                                all_transactions.append(transaction)

                            except Exception as e:
                                print(f"Error processing row {idx}: {e}")
                                continue

    return pd.DataFrame(all_transactions)

def filter_australian_fy_2024_25(df):
    """
    Filter transactions for Australian Financial Year 2024-25
    (July 1, 2024 - June 30, 2025)

    Args:
        df (pd.DataFrame): DataFrame with transaction data

    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    if 'date' not in df.columns:
        print("No 'date' column found in data")
        return df

    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Define FY dates
    fy_start = pd.Timestamp('2024-07-01')
    fy_end = pd.Timestamp('2025-06-30')

    # Filter for FY 2024-25
    mask = (df['date'] >= fy_start) & (df['date'] <= fy_end)
    filtered_df = df[mask].copy()

    print(f"Filtered {len(filtered_df)} transactions for FY 2024-25 (out of {len(df)} total)")

    return filtered_df

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_bank_data.py <pdf_file_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' does not exist")
        sys.exit(1)

    if not pdf_path.lower().endswith('.pdf'):
        print(f"Error: File '{pdf_path}' is not a PDF file")
        sys.exit(1)

    try:
        # Extract data from PDF
        df = extract_bank_data(pdf_path)

        if df.empty:
            print("No transaction data found in the PDF")
            sys.exit(1)

        print(f"Extracted {len(df)} transactions")

        # Filter for Australian FY 2024-25
        fy_df = filter_australian_fy_2024_25(df)

        if fy_df.empty:
            print("No transactions found for FY 2024-25")
            sys.exit(1)

        # Sort by date
        fy_df = fy_df.sort_values('date')

        # Save to CSV
        output_file = "bank_transactions_fy_2024_25.csv"
        fy_df.to_csv(output_file, index=False)

        print(f"Saved {len(fy_df)} transactions to {output_file}")

        # Print summary
        total_credits = fy_df[fy_df['amount'] > 0]['amount'].sum()
        total_debits = fy_df[fy_df['amount'] < 0]['amount'].sum()
        net_amount = fy_df['amount'].sum()

        print(f"\nSummary for FY 2024-25:")
        print(f"Total Credits: ${total_credits:.2f}")
        print(f"Total Debits: ${total_debits:.2f}")
        print(f"Net Amount: ${net_amount:.2f}")

    except Exception as e:
        print(f"Error processing PDF: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()