#!/usr/bin/env python3
"""
Transform Airwallex CSV export to BigCapitalPy import format
"""

import pandas as pd
from datetime import datetime

def transform_airwallex_csv(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)
    print(f'Loaded {len(df)} transactions')
    print('Columns:', list(df.columns))
    print()

    # Transform to the expected format
    transformed_data = []

    for idx, row in df.iterrows():
        # Parse the date from 'Created At' or 'Time'
        date_str = str(row.get('Created At', row.get('Time', '')))
        if date_str and date_str != 'nan':
            try:
                # Parse ISO format date
                parsed_date = datetime.fromisoformat(date_str.replace('+1100', '+11:00').replace('+1000', '+10:00')).date()
                parsed_date_str = parsed_date.strftime('%Y-%m-%d')
            except:
                parsed_date_str = ''
        else:
            parsed_date_str = ''

        # Get amounts
        debit_net = str(row.get('Debit Net Amount', '')).strip()
        credit_net = str(row.get('Credit Net Amount', '')).strip()

        # Clean amounts (remove commas)
        if debit_net and debit_net != 'nan':
            debit_net = debit_net.replace(',', '')
        else:
            debit_net = ''

        if credit_net and credit_net != 'nan':
            credit_net = credit_net.replace(',', '')
        else:
            credit_net = ''

        # Get balance
        balance = str(row.get('Account Balance', '')).strip()
        if balance and balance != 'nan':
            balance = balance.replace(',', '')
        else:
            balance = ''

        # Clean description
        description = str(row.get('Description', '')).strip()
        if description and description != 'nan':
            # Remove common Airwallex identifiers
            description = description.replace('| GA TYPE1CIV PTY LTD | 612082265 | 7773cc16-5dd5-484e-96b1-dcbdf76dc8a9', '')
            description = description.replace('GA TYPE1CIV PTY LTD | 612082265 | 7773cc16-5dd5-484e-96b1-dcbdf76dc8a9', '')
            description = description.replace('| 612082265 | 7773cc16-5dd5-484e-96b1-dcbdf76dc8a9', '')
            description = description.strip(' |')
        else:
            description = str(row.get('Type', 'Unknown'))

        # Get transaction type
        transaction_type = str(row.get('Type', 'Unknown'))

        # Get transaction ID
        transaction_id = str(row.get('Transaction Id', '')).strip()

        transformed_data.append({
            'parsed_date': parsed_date_str,
            'description': description[:500],  # Limit length
            'debit_net_amount': debit_net,
            'credit_net_amount': credit_net,
            'account_balance': balance,
            'transaction_id': transaction_id,
            'type': transaction_type
        })

    # Create new DataFrame
    transformed_df = pd.DataFrame(transformed_data)

    # Filter out rows without dates
    transformed_df = transformed_df[transformed_df['parsed_date'] != '']
    transformed_df = transformed_df.sort_values('parsed_date')

    print(f'Transformed to {len(transformed_df)} valid transactions')

    # Save the transformed CSV
    transformed_df.to_csv(output_file, index=False)

    print(f'Saved to {output_file}')

    # Show sample
    print('\nSample of transformed data:')
    print(transformed_df.head())

    # Summary
    total_credits = 0
    total_debits = 0

    for _, row in transformed_df.iterrows():
        if row['credit_net_amount']:
            try:
                total_credits += float(row['credit_net_amount'])
            except:
                pass
        if row['debit_net_amount']:
            try:
                total_debits += float(row['debit_net_amount'])
            except:
                pass

    print('\nSummary:')
    print(f'Total Credits: ${total_credits:.2f}')
    print(f'Total Debits: ${total_debits:.2f}')
    print(f'Net Amount: ${total_credits - total_debits:.2f}')

if __name__ == "__main__":
    input_file = 'bank/Balance_Activity_Report_2025-10-17(2).csv'
    output_file = 'bank_transactions_import_ready.csv'
    transform_airwallex_csv(input_file, output_file)