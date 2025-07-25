"""
Tax & Compliance Reports module for BigCapitalPy
Contains Australian GST BAS Report, Tax Codes, and Tax Summary reports
"""

from flask import Blueprint, render_template, request, jsonify, make_response, current_app
from flask_login import login_required, current_user
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import func
import io
import csv

from packages.server.src.models import (
    Account, AccountType, TaxCode, TaxType, Invoice, InvoiceStatus,
    JournalEntry, JournalLineItem, InvoiceLineItem
)
from packages.server.src.database import db
# Old import path commented out: from .utils import get_date_range
# New import path for get_date_range from the more general utils directory
from packages.webapp.src.utils.date_utils import get_date_range 

tax_bp = Blueprint('tax', __name__)


class AustralianGSTBASReport:
    """
    Australian GST Business Activity Statement (BAS) Report Generator
    Calculates all required GST fields for ATO submission
    """
    
    def __init__(self, start_date, end_date, organization_id):
        self.start_date = start_date if isinstance(start_date, date) else datetime.strptime(start_date, '%Y-%m-%d').date()
        self.end_date = end_date if isinstance(end_date, date) else datetime.strptime(end_date, '%Y-%m-%d').date()
        self.organization_id = organization_id
        
        # Validate quarter alignment
        self.quarter = self._get_quarter()
        
        # GST rate constants
        self.GST_RATE = Decimal('0.10')  # 10% GST
        self.GST_DIVISOR = Decimal('11')  # 1 + GST rate for inclusive calculations
        
    def _get_quarter(self):
        """Get the BAS quarter from the end date"""
        month = self.end_date.month
        year = self.end_date.year
        
        if month in [1, 2, 3]:
            return f"{year}-Q1"
        elif month in [4, 5, 6]:
            return f"{year}-Q2"
        elif month in [7, 8, 9]:
            return f"{year}-Q3"
        else:
            return f"{year}-Q4"
    
    def _get_tax_codes_for_type(self, tax_type):
        """Get tax codes for a specific tax type"""
        return TaxCode.query.filter_by(
            organization_id=self.organization_id,
            tax_type=tax_type,
            is_active=True
        ).all()
    
    def calculate_g1(self):
        """
        G1 - Total Sales (GST Inclusive)
        Include all sales with GST
        """
        gst_tax_codes = self._get_tax_codes_for_type(TaxType.GST_STANDARD)
        tax_code_ids = [tc.id for tc in gst_tax_codes]
        
        # Get sales from invoices with GST
        invoice_total = db.session.query(func.sum(Invoice.total)).filter(
            Invoice.organization_id == self.organization_id,
            Invoice.invoice_date.between(self.start_date, self.end_date),
            Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PAID]),
            Invoice.line_items.any(InvoiceLineItem.tax_code_id.in_(tax_code_ids))
        ).scalar() or Decimal('0')
        
        # Get sales from journal entries with GST
        journal_sales = db.session.query(func.sum(JournalLineItem.credit)).join(
            JournalEntry
        ).join(Account).filter(
            JournalEntry.organization_id == self.organization_id,
            JournalEntry.date.between(self.start_date, self.end_date),
            Account.type == AccountType.INCOME,
            JournalLineItem.tax_code_id.in_(tax_code_ids)
        ).scalar() or Decimal('0')
        
        return round(invoice_total + journal_sales, 2)
    
    def calculate_g2(self):
        """
        G2 - Export Sales
        GST-free export sales
        """
        export_tax_codes = self._get_tax_codes_for_type(TaxType.EXPORT)
        tax_code_ids = [tc.id for tc in export_tax_codes]
        
        # Get export sales from invoices
        invoice_exports = db.session.query(func.sum(Invoice.total)).filter(
            Invoice.organization_id == self.organization_id,
            Invoice.invoice_date.between(self.start_date, self.end_date),
            Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PAID]),
            Invoice.line_items.any(InvoiceLineItem.tax_code_id.in_(tax_code_ids))
        ).scalar() or Decimal('0')
        
        # Get export sales from journal entries
        journal_exports = db.session.query(func.sum(JournalLineItem.credit)).join(
            JournalEntry
        ).join(Account).filter(
            JournalEntry.organization_id == self.organization_id,
            JournalEntry.date.between(self.start_date, self.end_date),
            Account.type == AccountType.INCOME,
            JournalLineItem.tax_code_id.in_(tax_code_ids)
        ).scalar() or Decimal('0')
        
        return round(invoice_exports + journal_exports, 2)
    
    def calculate_g3(self):
        """
        G3 - Other GST-Free Sales
        Domestic GST-free sales (excluding exports)
        """
        gst_free_tax_codes = self._get_tax_codes_for_type(TaxType.GST_FREE)
        tax_code_ids = [tc.id for tc in gst_free_tax_codes]
        
        # Get GST-free sales from invoices
        invoice_gst_free = db.session.query(func.sum(Invoice.total)).filter(
            Invoice.organization_id == self.organization_id,
            Invoice.invoice_date.between(self.start_date, self.end_date),
            Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PAID]),
            Invoice.line_items.any(InvoiceLineItem.tax_code_id.in_(tax_code_ids))
        ).scalar() or Decimal('0')
        
        # Get GST-free sales from journal entries
        journal_gst_free = db.session.query(func.sum(JournalLineItem.credit)).join(
            JournalEntry
        ).join(Account).filter(
            JournalEntry.organization_id == self.organization_id,
            JournalEntry.date.between(self.start_date, self.end_date),
            Account.type == AccountType.INCOME,
            JournalLineItem.tax_code_id.in_(tax_code_ids)
        ).scalar() or Decimal('0')
        
        return round(invoice_gst_free + journal_gst_free, 2)
    
    def calculate_g4(self):
        """
        G4 - Input Taxed Sales
        Input taxed sales (financial services, residential rent)
        """
        input_taxed_codes = self._get_tax_codes_for_type(TaxType.INPUT_TAXED)
        tax_code_ids = [tc.id for tc in input_taxed_codes]
        
        # Get input taxed sales from invoices
        invoice_input_taxed = db.session.query(func.sum(Invoice.total)).filter(
            Invoice.organization_id == self.organization_id,
            Invoice.invoice_date.between(self.start_date, self.end_date),
            Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PAID]),
            Invoice.line_items.any(InvoiceLineItem.tax_code_id.in_(tax_code_ids))
        ).scalar() or Decimal('0')
        
        # Get input taxed sales from journal entries
        journal_input_taxed = db.session.query(func.sum(JournalLineItem.credit)).join(
            JournalEntry
        ).join(Account).filter(
            JournalEntry.organization_id == self.organization_id,
            JournalEntry.date.between(self.start_date, self.end_date),
            Account.type == AccountType.INCOME,
            JournalLineItem.tax_code_id.in_(tax_code_ids)
        ).scalar() or Decimal('0')
        
        return round(invoice_input_taxed + journal_input_taxed, 2)
    
    def calculate_g10(self):
        """
        G10 - Capital Purchases (GST Inclusive)
        Capital purchases including GST
        """
        gst_tax_codes = self._get_tax_codes_for_type(TaxType.GST_STANDARD)
        capital_tax_codes = self._get_tax_codes_for_type(TaxType.CAPITAL_ACQUISITION)
        tax_code_ids = [tc.id for tc in gst_tax_codes + capital_tax_codes]
        
        # Get capital purchases from journal entries
        capital_purchases = db.session.query(func.sum(JournalLineItem.debit)).join(
            JournalEntry
        ).join(Account).filter(
            JournalEntry.organization_id == self.organization_id,
            JournalEntry.date.between(self.start_date, self.end_date),
            Account.type == AccountType.ASSET,
            JournalLineItem.tax_code_id.in_(tax_code_ids)
        ).scalar() or Decimal('0')
        
        return round(capital_purchases, 2)
    
    def calculate_g11(self):
        """
        G11 - Non-Capital Purchases (GST Inclusive)
        Operating expenses and inventory purchases with GST
        """
        gst_tax_codes = self._get_tax_codes_for_type(TaxType.GST_STANDARD)
        tax_code_ids = [tc.id for tc in gst_tax_codes]
        
        # Get non-capital purchases from journal entries
        non_capital_purchases = db.session.query(func.sum(JournalLineItem.debit)).join(
            JournalEntry
        ).join(Account).filter(
            JournalEntry.organization_id == self.organization_id,
            JournalEntry.date.between(self.start_date, self.end_date),
            Account.type == AccountType.EXPENSE,
            JournalLineItem.tax_code_id.in_(tax_code_ids)
        ).scalar() or Decimal('0')
        
        return round(non_capital_purchases, 2)
    
    def calculate_g13(self):
        """
        G13 - Credit Purchases for Input Taxed Sales
        Purchases related to making input taxed sales
        """
        # This requires specific allocation logic based on business rules
        # For now, return 0 unless specifically configured
        return Decimal('0')
    
    def calculate_g14(self):
        """
        G14 - Purchases Without GST
        GST-free purchases and imports
        """
        gst_free_tax_codes = self._get_tax_codes_for_type(TaxType.GST_FREE)
        export_tax_codes = self._get_tax_codes_for_type(TaxType.EXPORT)
        tax_code_ids = [tc.id for tc in gst_free_tax_codes + export_tax_codes]
        
        # Get GST-free purchases from journal entries
        gst_free_purchases = db.session.query(func.sum(JournalLineItem.debit)).join(
            JournalEntry
        ).join(Account).filter(
            JournalEntry.organization_id == self.organization_id,
            JournalEntry.date.between(self.start_date, self.end_date),
            Account.type.in_([AccountType.EXPENSE, AccountType.ASSET]),
            JournalLineItem.tax_code_id.in_(tax_code_ids)
        ).scalar() or Decimal('0')
        
        return round(gst_free_purchases, 2)
    
    def calculate_1a(self):
        """
        1A - GST on Sales
        GST collected on sales (extract from GST-inclusive amounts)
        """
        g1_total = self.calculate_g1()
        # For GST-inclusive amounts: GST = amount ÷ 11
        gst_on_sales = g1_total / self.GST_DIVISOR
        return round(gst_on_sales, 2)
    
    def calculate_1b(self):
        """
        1B - GST on Purchases (Input Tax Credits)
        GST paid on purchases that can be claimed as credits
        """
        g10_total = self.calculate_g10()
        g11_total = self.calculate_g11()
        total_gst_purchases = g10_total + g11_total
        
        # For GST-inclusive amounts: GST = amount ÷ 11
        gst_on_purchases = total_gst_purchases / self.GST_DIVISOR
        return round(gst_on_purchases, 2)
    
    def calculate_adjustments(self):
        """
        Calculate any BAS adjustments
        This would include corrections from previous periods
        """
        # For now, return 0 unless specific adjustments are recorded
        return Decimal('0')
    
    def calculate_net_gst(self):
        """
        Net GST position (amount owed to or refund from ATO)
        Positive = Amount owed to ATO
        Negative = Refund from ATO
        """
        gst_on_sales = self.calculate_1a()
        gst_on_purchases = self.calculate_1b()
        adjustments = self.calculate_adjustments()
        
        net_gst = gst_on_sales - gst_on_purchases + adjustments
        return round(net_gst, 2)
    
    def validate_bas_data(self):
        """
        Validate BAS calculations for accuracy
        """
        validations = []
        
        # Check G1 vs 1A relationship
        g1 = self.calculate_g1()
        one_a = self.calculate_1a()
        expected_1a = g1 / self.GST_DIVISOR
        
        if abs(one_a - expected_1a) > Decimal('0.01'):
            validations.append(f"1A calculation ({one_a}) doesn't match G1 ÷ 11 ({expected_1a})")
        
        # Check purchase GST calculation
        g10 = self.calculate_g10()
        g11 = self.calculate_g11()
        one_b = self.calculate_1b()
        expected_1b = (g10 + g11) / self.GST_DIVISOR
        
        if abs(one_b - expected_1b) > Decimal('0.01'):
            validations.append(f"1B calculation ({one_b}) doesn't match (G10 + G11) ÷ 11 ({expected_1b})")
        
        # Check for negative amounts (which shouldn't occur)
        fields_to_check = {
            'G1': g1, 'G10': g10, 'G11': g11,
            '1A': one_a, '1B': one_b
        }
        
        for field_name, value in fields_to_check.items():
            if value < 0:
                validations.append(f"{field_name} has negative value: {value}")
        
        # Check quarter alignment
        if self.end_date.month not in [3, 6, 9, 12]:
            validations.append("BAS period should end on a quarter end (March, June, September, December)")
        
        return validations
    
    def generate_bas_report(self):
        """
        Generate complete BAS report with all calculations
        """
        # Calculate all fields
        g1 = self.calculate_g1()
        g2 = self.calculate_g2()
        g3 = self.calculate_g3()
        g4 = self.calculate_g4()
        g7 = self.calculate_adjustments()
        
        g10 = self.calculate_g10()
        g11 = self.calculate_g11()
        g13 = self.calculate_g13()
        g14 = self.calculate_g14()
        
        one_a = self.calculate_1a()
        one_b = self.calculate_1b()
        net_gst = self.calculate_net_gst()
        
        validations = self.validate_bas_data()
        
        return {
            'period': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'quarter': self.quarter
            },
            'sales': {
                'G1': float(g1),
                'G2': float(g2),
                'G3': float(g3),
                'G4': float(g4),
                'G7': float(g7),
                'total_sales': float(g1 + g2 + g3 + g4)
            },
            'purchases': {
                'G10': float(g10),
                'G11': float(g11),
                'G13': float(g13),
                'G14': float(g14),
                'total_purchases': float(g10 + g11 + g13 + g14)
            },
            'gst': {
                '1A': float(one_a),
                '1B': float(one_b),
                'net_gst': float(net_gst),
                'gst_rate': float(self.GST_RATE),
                'status': 'refund' if net_gst < 0 else 'payable' if net_gst > 0 else 'nil'
            },
            'validation': {
                'errors': validations,
                'is_valid': len(validations) == 0
            },
            'summary': {
                'gst_inclusive_sales': float(g1),
                'gst_free_sales': float(g2 + g3 + g4),
                'gst_inclusive_purchases': float(g10 + g11),
                'gst_liability': float(net_gst),
                'quarter_display': self.quarter
            }
        }


@tax_bp.route('/australian-gst-bas')
@login_required
def australian_gst_bas():
    """Australian GST Business Activity Statement (BAS) Report"""
    period = request.args.get('period', 'this_quarter')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Get date range
    start_date, end_date = get_date_range(period, start_date, end_date)
    
    # Generate BAS report
    bas_generator = AustralianGSTBASReport(
        start_date=start_date,
        end_date=end_date,
        organization_id=current_user.organization_id
    )
    
    bas_data = bas_generator.generate_bas_report()
    
    # Get available tax codes for reference
    tax_codes = TaxCode.query.filter_by(
        organization_id=current_user.organization_id,
        is_active=True
    ).order_by(TaxCode.tax_type, TaxCode.code).all()
    
    return render_template('reports/tax-compliance/australian_gst_bas.html', 
                         bas_data=bas_data,
                         tax_codes=tax_codes,
                         period=period,
                         start_date=start_date,
                         end_date=end_date)


@tax_bp.route('/australian-gst-bas/export')
@login_required
def export_australian_gst_bas():
    """Export Australian GST BAS Report to CSV"""
    period = request.args.get('period', 'this_quarter')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Get date range
    start_date, end_date = get_date_range(period, start_date, end_date)

    # Generate BAS report
    bas_generator = AustralianGSTBASReport(
        start_date=start_date,
        end_date=end_date,
        organization_id=current_user.organization_id
    )

    bas_data = bas_generator.generate_bas_report()

    # Create CSV response
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(['Australian GST Business Activity Statement (BAS)'])
    writer.writerow([f"Period: {bas_data['period']['start_date']} to {bas_data['period']['end_date']}"])
    writer.writerow([f"Quarter: {bas_data['period']['quarter']}"])
    writer.writerow([])

    # Sales section
    writer.writerow(['SALES AND INCOME'])
    writer.writerow(['Field', 'Description', 'Amount (AUD)'])
    writer.writerow(['G1', 'Total sales (including GST)', f"${bas_data['sales']['G1']:,.2f}"])
    writer.writerow(['G2', 'Export sales (GST-free)', f"${bas_data['sales']['G2']:,.2f}"])
    writer.writerow(['G3', 'Other GST-free sales', f"${bas_data['sales']['G3']:,.2f}"])
    writer.writerow(['G4', 'Input taxed sales', f"${bas_data['sales']['G4']:,.2f}"])
    writer.writerow(['G7', 'Adjustments', f"${bas_data['sales']['G7']:,.2f}"])
    writer.writerow(['Total Sales', '', f"${bas_data['sales']['total_sales']:,.2f}"])
    writer.writerow([])

    # Purchases section
    writer.writerow(['PURCHASES AND EXPENSES'])
    writer.writerow(['Field', 'Description', 'Amount (AUD)'])
    writer.writerow(['G10', 'Capital purchases (GST inclusive)', f"${bas_data['purchases']['G10']:,.2f}"])
    writer.writerow(['G11', 'Non-capital purchases (GST inclusive)', f"${bas_data['purchases']['G11']:,.2f}"])
    writer.writerow(['G13', 'Purchases for input taxed sales', f"${bas_data['purchases']['G13']:,.2f}"])
    writer.writerow(['G14', 'Purchases without GST', f"${bas_data['purchases']['G14']:,.2f}"])
    writer.writerow(['Total Purchases', '', f"${bas_data['purchases']['total_purchases']:,.2f}"])
    writer.writerow([])

    # GST section
    writer.writerow(['GST SUMMARY'])
    writer.writerow(['Field', 'Description', 'Amount (AUD)'])
    writer.writerow(['1A', 'GST on sales', f"${bas_data['gst']['1A']:,.2f}"])
    writer.writerow(['1B', 'GST on purchases', f"${bas_data['gst']['1B']:,.2f}"])
    writer.writerow(['Net GST', 'Amount payable/refundable', f"${bas_data['gst']['net_gst']:,.2f}"])
    writer.writerow(['GST Status', '', bas_data['gst']['status']])
    writer.writerow([])

    # Validation section
    writer.writerow(['VALIDATION'])
    writer.writerow(['Is Valid', bas_data['validation']['is_valid']])
    if bas_data['validation']['errors']:
        writer.writerow(['Errors'])
        for err in bas_data['validation']['errors']:
            writer.writerow([err])

    # Prepare response
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=australian_gst_bas.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response
# Tax Codes Configuration Report
@tax_bp.route('/tax-codes')
@login_required
def tax_codes_report():
    """Tax Codes Configuration Report"""
    tax_codes = TaxCode.query.filter_by(
        organization_id=current_user.organization_id,
        is_active=True
    ).order_by(TaxCode.tax_type, TaxCode.code).all()
    return render_template('reports/tax_codes.html', tax_codes=tax_codes)

# Tax Summary Report
@tax_bp.route('/tax-summary')
@login_required
def tax_summary():
    """Tax Summary Report"""
    period = request.args.get('period', 'this_quarter')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    start_date, end_date = get_date_range(period, start_date, end_date)

    # Example summary: total GST collected and paid
    bas_generator = AustralianGSTBASReport(
        start_date=start_date,
        end_date=end_date,
        organization_id=current_user.organization_id
    )
    bas_data = bas_generator.generate_bas_report()

    return render_template('reports/tax_summary.html', bas_data=bas_data, period=period, start_date=start_date, end_date=end_date)

# API endpoint for seeding Australian tax codes
@tax_bp.route('/seed-australian-tax-codes', methods=['POST'])
@login_required
def seed_australian_tax_codes():
    """Seed Australian Tax Codes for organization"""
    # Example: Seed GST_STANDARD, GST_FREE, EXPORT, INPUT_TAXED, CAPITAL_ACQUISITION
    from packages.server.src.models import TaxType
    codes = [
        {'code': 'GST', 'name': 'GST 10%', 'tax_type': TaxType.GST_STANDARD},
        {'code': 'FRE', 'name': 'GST Free', 'tax_type': TaxType.GST_FREE},
        {'code': 'EXP', 'name': 'Export', 'tax_type': TaxType.EXPORT},
        {'code': 'INP', 'name': 'Input Taxed', 'tax_type': TaxType.INPUT_TAXED},
        {'code': 'CAP', 'name': 'Capital Acquisition', 'tax_type': TaxType.CAPITAL_ACQUISITION},
    ]
    created = 0
    for c in codes:
        existing = TaxCode.query.filter_by(
            organization_id=current_user.organization_id,
            code=c['code']
        ).first()
        if not existing:
            tc = TaxCode(
                code=c['code'],
                name=c['name'],
                tax_type=c['tax_type'],
                organization_id=current_user.organization_id,
                is_active=True
            )
            try:
                db.session.add(tc)
                db.session.commit()
                created += 1
            except Exception as e:
                db.session.rollback()
    return jsonify({'created': created})
