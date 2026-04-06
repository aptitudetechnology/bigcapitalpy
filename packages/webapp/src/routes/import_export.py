"""
Import/Export routes for BigCapitalPy
Handles CSV import and export for customers, vendors, and items.
"""

import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user

from packages.server.src.models import Customer, Vendor, Item
from packages.server.src.database import db

import_export_bp = Blueprint('import_export', __name__)


# --- Export Routes ---

@import_export_bp.route('/')
@login_required
def index():
    """Import/Export dashboard"""
    return render_template('import_export/index.html')


@import_export_bp.route('/export/customers')
@login_required
def export_customers():
    """Export customers to CSV"""
    customers = Customer.query.filter(
        Customer.organization_id == current_user.organization_id
    ).order_by(Customer.display_name).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Display Name', 'First Name', 'Last Name', 'Company Name',
        'Email', 'Phone', 'Currency', 'Tax Number',
        'Billing Address', 'Billing City', 'Billing State',
        'Billing Postal Code', 'Billing Country', 'Notes', 'Active'
    ])

    for c in customers:
        writer.writerow([
            c.display_name, getattr(c, 'first_name', ''), getattr(c, 'last_name', ''),
            getattr(c, 'company_name', ''), getattr(c, 'email', ''),
            getattr(c, 'phone', ''), getattr(c, 'currency', 'USD'),
            getattr(c, 'tax_number', ''),
            getattr(c, 'billing_address', ''), getattr(c, 'billing_city', ''),
            getattr(c, 'billing_state', ''), getattr(c, 'billing_postal_code', ''),
            getattr(c, 'billing_country', ''), getattr(c, 'notes', ''),
            'Yes' if getattr(c, 'is_active', True) else 'No'
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=customers.csv'}
    )


@import_export_bp.route('/export/vendors')
@login_required
def export_vendors():
    """Export vendors to CSV"""
    vendors = Vendor.query.filter(
        Vendor.organization_id == current_user.organization_id
    ).order_by(Vendor.display_name).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Display Name', 'First Name', 'Last Name', 'Company Name',
        'Email', 'Phone', 'Currency', 'Tax Number',
        'Address', 'City', 'State', 'Postal Code', 'Country',
        'Notes', 'Active'
    ])

    for v in vendors:
        writer.writerow([
            v.display_name, getattr(v, 'first_name', ''), getattr(v, 'last_name', ''),
            getattr(v, 'company_name', ''), getattr(v, 'email', ''),
            getattr(v, 'phone', ''), getattr(v, 'currency', 'USD'),
            getattr(v, 'tax_number', ''),
            getattr(v, 'address', ''), getattr(v, 'city', ''),
            getattr(v, 'state', ''), getattr(v, 'postal_code', ''),
            getattr(v, 'country', ''), getattr(v, 'notes', ''),
            'Yes' if getattr(v, 'is_active', True) else 'No'
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=vendors.csv'}
    )


@import_export_bp.route('/export/items')
@login_required
def export_items():
    """Export items to CSV"""
    items = Item.query.filter(
        Item.organization_id == current_user.organization_id
    ).order_by(Item.name).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Name', 'SKU', 'Description', 'Type', 'Category',
        'Sell Price', 'Cost Price', 'Quantity On Hand',
        'Reorder Level', 'Unit', 'Active'
    ])

    for item in items:
        writer.writerow([
            item.name, item.sku or '', item.description or '',
            item.type or '', item.category or '',
            str(item.sell_price or 0), str(item.cost_price or 0),
            str(item.quantity_on_hand or 0), str(item.reorder_level or 0),
            item.unit or '',
            'Yes' if item.is_active else 'No'
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=items.csv'}
    )


# --- Import Routes ---

@import_export_bp.route('/import/customers', methods=['GET', 'POST'])
@login_required
def import_customers():
    """Import customers from CSV"""
    if request.method == 'POST':
        file = request.files.get('csv_file')
        if not file or not file.filename.endswith('.csv'):
            flash('Please upload a valid CSV file.', 'error')
            return redirect(url_for('import_export.import_customers'))

        try:
            stream = io.StringIO(file.stream.read().decode('utf-8'))
            reader = csv.DictReader(stream)

            imported = 0
            skipped = 0
            errors = []

            for row_num, row in enumerate(reader, start=2):
                display_name = row.get('Display Name', '').strip()
                if not display_name:
                    skipped += 1
                    continue

                # Check for duplicate
                existing = Customer.query.filter(
                    Customer.organization_id == current_user.organization_id,
                    Customer.display_name == display_name
                ).first()

                if existing:
                    skipped += 1
                    errors.append(f"Row {row_num}: '{display_name}' already exists (skipped)")
                    continue

                customer = Customer(
                    organization_id=current_user.organization_id,
                    display_name=display_name,
                    first_name=row.get('First Name', '').strip(),
                    last_name=row.get('Last Name', '').strip(),
                    company_name=row.get('Company Name', '').strip(),
                    email=row.get('Email', '').strip(),
                    phone=row.get('Phone', '').strip(),
                    currency=row.get('Currency', 'USD').strip() or 'USD',
                    notes=row.get('Notes', '').strip()
                )

                # Set optional address fields if they exist on the model
                for field, csv_col in [
                    ('billing_address', 'Billing Address'),
                    ('billing_city', 'Billing City'),
                    ('billing_state', 'Billing State'),
                    ('billing_postal_code', 'Billing Postal Code'),
                    ('billing_country', 'Billing Country'),
                    ('tax_number', 'Tax Number'),
                ]:
                    if hasattr(customer, field) and csv_col in row:
                        setattr(customer, field, row[csv_col].strip())

                db.session.add(customer)
                imported += 1

            db.session.commit()

            if errors:
                flash(f'Imported {imported} customers, skipped {skipped}. Details: {"; ".join(errors[:5])}', 'warning')
            else:
                flash(f'Successfully imported {imported} customers!', 'success')

            return redirect(url_for('import_export.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error importing customers: {str(e)}', 'error')

    return render_template('import_export/import_form.html',
                         entity_type='customers',
                         sample_headers='Display Name,First Name,Last Name,Company Name,Email,Phone,Currency,Notes')


@import_export_bp.route('/import/vendors', methods=['GET', 'POST'])
@login_required
def import_vendors():
    """Import vendors from CSV"""
    if request.method == 'POST':
        file = request.files.get('csv_file')
        if not file or not file.filename.endswith('.csv'):
            flash('Please upload a valid CSV file.', 'error')
            return redirect(url_for('import_export.import_vendors'))

        try:
            stream = io.StringIO(file.stream.read().decode('utf-8'))
            reader = csv.DictReader(stream)

            imported = 0
            skipped = 0
            errors = []

            for row_num, row in enumerate(reader, start=2):
                display_name = row.get('Display Name', '').strip()
                if not display_name:
                    skipped += 1
                    continue

                existing = Vendor.query.filter(
                    Vendor.organization_id == current_user.organization_id,
                    Vendor.display_name == display_name
                ).first()

                if existing:
                    skipped += 1
                    errors.append(f"Row {row_num}: '{display_name}' already exists (skipped)")
                    continue

                vendor = Vendor(
                    organization_id=current_user.organization_id,
                    display_name=display_name,
                    first_name=row.get('First Name', '').strip(),
                    last_name=row.get('Last Name', '').strip(),
                    company_name=row.get('Company Name', '').strip(),
                    email=row.get('Email', '').strip(),
                    phone=row.get('Phone', '').strip(),
                    currency=row.get('Currency', 'USD').strip() or 'USD',
                    notes=row.get('Notes', '').strip()
                )

                for field, csv_col in [
                    ('address', 'Address'),
                    ('city', 'City'),
                    ('state', 'State'),
                    ('postal_code', 'Postal Code'),
                    ('country', 'Country'),
                    ('tax_number', 'Tax Number'),
                ]:
                    if hasattr(vendor, field) and csv_col in row:
                        setattr(vendor, field, row[csv_col].strip())

                db.session.add(vendor)
                imported += 1

            db.session.commit()

            if errors:
                flash(f'Imported {imported} vendors, skipped {skipped}. Details: {"; ".join(errors[:5])}', 'warning')
            else:
                flash(f'Successfully imported {imported} vendors!', 'success')

            return redirect(url_for('import_export.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error importing vendors: {str(e)}', 'error')

    return render_template('import_export/import_form.html',
                         entity_type='vendors',
                         sample_headers='Display Name,First Name,Last Name,Company Name,Email,Phone,Currency,Notes')


@import_export_bp.route('/import/items', methods=['GET', 'POST'])
@login_required
def import_items():
    """Import items from CSV"""
    if request.method == 'POST':
        file = request.files.get('csv_file')
        if not file or not file.filename.endswith('.csv'):
            flash('Please upload a valid CSV file.', 'error')
            return redirect(url_for('import_export.import_items'))

        try:
            stream = io.StringIO(file.stream.read().decode('utf-8'))
            reader = csv.DictReader(stream)

            imported = 0
            skipped = 0
            errors = []

            for row_num, row in enumerate(reader, start=2):
                name = row.get('Name', '').strip()
                if not name:
                    skipped += 1
                    continue

                sku = row.get('SKU', '').strip() or None
                if sku:
                    existing = Item.query.filter(
                        Item.organization_id == current_user.organization_id,
                        Item.sku == sku
                    ).first()
                    if existing:
                        skipped += 1
                        errors.append(f"Row {row_num}: SKU '{sku}' already exists (skipped)")
                        continue

                item = Item(
                    organization_id=current_user.organization_id,
                    name=name,
                    sku=sku,
                    description=row.get('Description', '').strip(),
                    type=row.get('Type', 'inventory').strip() or 'inventory',
                    category=row.get('Category', '').strip(),
                    sell_price=float(row.get('Sell Price', 0) or 0),
                    cost_price=float(row.get('Cost Price', 0) or 0),
                    quantity_on_hand=float(row.get('Quantity On Hand', 0) or 0),
                    reorder_level=float(row.get('Reorder Level', 0) or 0),
                    unit=row.get('Unit', '').strip()
                )

                db.session.add(item)
                imported += 1

            db.session.commit()

            if errors:
                flash(f'Imported {imported} items, skipped {skipped}. Details: {"; ".join(errors[:5])}', 'warning')
            else:
                flash(f'Successfully imported {imported} items!', 'success')

            return redirect(url_for('import_export.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error importing items: {str(e)}', 'error')

    return render_template('import_export/import_form.html',
                         entity_type='items',
                         sample_headers='Name,SKU,Description,Type,Category,Sell Price,Cost Price,Quantity On Hand,Reorder Level,Unit')
