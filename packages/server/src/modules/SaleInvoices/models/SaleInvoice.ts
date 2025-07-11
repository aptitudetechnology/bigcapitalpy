import * as moment from 'moment';
import * as R from 'ramda';
import { Model, raw } from 'objection';
import { castArray } from 'lodash';
import { MomentInput, unitOfTime } from 'moment';
import { defaultTo } from 'ramda';
import { TaxRateTransaction } from '@/modules/TaxRates/models/TaxRateTransaction.model';
import { ItemEntry } from '@/modules/TransactionItemEntry/models/ItemEntry';
import { Document } from '@/modules/ChromiumlyTenancy/models/Document';
import { DiscountType } from '@/common/types/Discount';
import { Account } from '@/modules/Accounts/models/Account.model';
import { ISearchRole } from '@/modules/DynamicListing/DynamicFilter/DynamicFilter.types';
import { TenantBaseModel } from '@/modules/System/models/TenantBaseModel';
import { TransactionPaymentServiceEntry } from '@/modules/PaymentServices/models/TransactionPaymentServiceEntry.model';
import { InjectAttachable } from '@/modules/Attachments/decorators/InjectAttachable.decorator';
import { ExportableModel } from '@/modules/Export/decorators/ExportableModel.decorator';
import { InjectModelMeta } from '@/modules/Tenancy/TenancyModels/decorators/InjectModelMeta.decorator';
import { SaleInvoiceMeta } from './SaleInvoice.meta';
import { InjectModelDefaultViews } from '@/modules/Views/decorators/InjectModelDefaultViews.decorator';
import { SaleInvoiceDefaultViews } from '../constants';

@InjectAttachable()
@ExportableModel()
@InjectModelMeta(SaleInvoiceMeta)
@InjectModelDefaultViews(SaleInvoiceDefaultViews)
export class SaleInvoice extends TenantBaseModel {
  public taxAmountWithheld: number;
  public balance: number;
  public paymentAmount: number;
  public exchangeRate: number;

  public creditedAmount: number;
  public isInclusiveTax: boolean;

  public dueDate: Date;
  public deliveredAt: Date | string;
  public currencyCode: string;
  public invoiceDate: Date;

  public createdAt?: Date;
  public updatedAt?: Date | null;

  public writtenoffExpenseAccountId: number;
  public writtenoffAmount: number;
  public writtenoffAt: Date;

  public discountType: DiscountType;
  public discount: number;
  public adjustment: number;

  public customerId: number;
  public invoiceNo: string;
  public referenceNo: string;

  public pdfTemplateId: number;
  public userId: number;

  public branchId: number;
  public warehouseId: number;

  public taxes!: TaxRateTransaction[];
  public entries!: ItemEntry[];
  public attachments!: Document[];
  public writtenoffExpenseAccount!: Account;
  public paymentMethods!: TransactionPaymentServiceEntry[];
  /**
   * Table name
   */
  static get tableName() {
    return 'sales_invoices';
  }

  /**
   * Timestamps columns.
   */
  get timestamps() {
    return ['created_at', 'updated_at'];
  }

  /**
   *
   */
  get pluralName() {
    return 'asdfsdf';
  }

  /**
   * Virtual attributes.
   */
  static get virtualAttributes() {
    return [
      'isDelivered',
      'isOverdue',
      'isPartiallyPaid',
      'isFullyPaid',
      'isWrittenoff',
      'isPaid',

      'dueAmount',
      'balanceAmount',
      'remainingDays',
      'overdueDays',

      'subtotal',
      'subtotalLocal',
      'subtotalExludingTax',

      'taxAmountWithheldLocal',
      'discountAmount',
      'discountAmountLocal',
      'discountPercentage',

      'total',
      'totalLocal',

      'writtenoffAmountLocal',
      'adjustmentLocal',
    ];
  }

  /**
   * Invoice amount.
   * @todo Sugger attribute to balance, we need to rename the balance to amount.
   * @returns {number}
   */
  get amount() {
    return this.balance;
  }

  /**
   * Invoice amount in base currency.
   * @returns {number}
   */
  get amountLocal() {
    return this.amount * this.exchangeRate;
  }

  /**
   * Subtotal. (Tax inclusive) if the tax inclusive is enabled.
   * @returns {number}
   */
  get subtotal() {
    return this.amount;
  }

  /**
   * Subtotal in base currency. (Tax inclusive) if the tax inclusive is enabled.
   * @returns {number}
   */
  get subtotalLocal() {
    return this.amountLocal;
  }

  /**
   * Sale invoice amount excluding tax.
   * @returns {number}
   */
  get subtotalExludingTax() {
    return this.isInclusiveTax
      ? this.subtotal - this.taxAmountWithheld
      : this.subtotal;
  }

  /**
   * Tax amount withheld in base currency.
   * @returns {number}
   */
  get taxAmountWithheldLocal() {
    return this.taxAmountWithheld * this.exchangeRate;
  }

  /**
   * Discount amount.
   * @returns {number}
   */
  get discountAmount() {
    return this.discountType === DiscountType.Amount
      ? this.discount
      : this.subtotal * (this.discount / 100);
  }

  /**
   * Local discount amount.
   * @returns {number | null}
   */
  get discountAmountLocal() {
    return this.discountAmount ? this.discountAmount * this.exchangeRate : null;
  }

  /**
   * Discount percentage.
   * @returns {number | null}
   */
  get discountPercentage(): number | null {
    return this.discountType === DiscountType.Percentage ? this.discount : null;
  }

  /**
   * Adjustment amount in local currency.
   * @returns {number | null}
   */
  get adjustmentLocal(): number | null {
    return this.adjustment ? this.adjustment * this.exchangeRate : null;
  }

  /**
   * Invoice total. (Tax included)
   * @returns {number}
   */
  get total() {
    const adjustmentAmount = defaultTo(this.adjustment, 0);

    return R.compose(
      R.add(adjustmentAmount),
      R.subtract(R.__, this.discountAmount),
      R.when(R.always(this.isInclusiveTax), R.add(this.taxAmountWithheld)),
    )(this.subtotal);
  }

  /**
   * Invoice total in local currency. (Tax included)
   * @returns {number}
   */
  get totalLocal() {
    return this.total * this.exchangeRate;
  }

  /**
   * Detarmines whether the invoice is delivered.
   * @return {boolean}
   */
  get isDelivered() {
    return !!this.deliveredAt;
  }

  /**
   * Detarmines the due date is over.
   * @return {boolean}
   */
  get isOverdue() {
    return this.overdueDays > 0;
  }

  /**
   * Retrieve the sale invoice balance.
   * @return {number}
   */
  get balanceAmount() {
    return this.paymentAmount + this.writtenoffAmount + this.creditedAmount;
  }

  /**
   * Retrieve the invoice due amount.
   * Equation (Invoice amount - payment amount = Due amount)
   * @return {boolean}
   */
  get dueAmount() {
    return Math.max(this.total - this.balanceAmount, 0);
  }

  /**
   * Detarmine whether the invoice paid partially.
   * @return {boolean}
   */
  get isPartiallyPaid() {
    return this.dueAmount !== this.total && this.dueAmount > 0;
  }

  /**
   * Deetarmine whether the invoice paid fully.
   * @return {boolean}
   */
  get isFullyPaid() {
    return this.dueAmount === 0;
  }

  /**
   * Detarmines whether the invoice paid fully or partially.
   * @return {boolean}
   */
  get isPaid() {
    return this.isPartiallyPaid || this.isFullyPaid;
  }

  /**
   * Detarmines whether the sale invoice is written-off.
   * @return {boolean}
   */
  get isWrittenoff() {
    return Boolean(this.writtenoffAt);
  }

  /**
   * Retrieve the remaining days in number
   * @return {number|null}
   */
  get remainingDays() {
    const dateMoment = moment();
    const dueDateMoment = moment(this.dueDate);

    return Math.max(dueDateMoment.diff(dateMoment, 'days'), 0);
  }

  /**
   * Written-off amount in local currency.
   * @returns {number}
   */
  get writtenoffAmountLocal() {
    return this.writtenoffAmount * this.exchangeRate;
  }

  /**
   * Retrieve the overdue days in number.
   * @return {number|null}
   */
  get overdueDays() {
    const dateMoment = moment();
    const dueDateMoment = moment(this.dueDate);

    return Math.max(dateMoment.diff(dueDateMoment, 'days'), 0);
  }

  /**
   * Model modifiers.
   */
  static get modifiers() {
    return {
      /**
       * Filters the due invoices.
       */
      dueInvoices(query) {
        query.where(
          raw(`
            COALESCE(BALANCE, 0) -
            COALESCE(PAYMENT_AMOUNT, 0) -
            COALESCE(WRITTENOFF_AMOUNT, 0) -
            COALESCE(CREDITED_AMOUNT, 0) > 0
        `),
        );
      },
      /**
       * Filters the invoices between the given date range.
       */
      filterDateRange(
        query,
        startDate: MomentInput,
        endDate?: MomentInput,
        type: unitOfTime.StartOf = 'day',
      ) {
        const dateFormat = 'YYYY-MM-DD';
        const fromDate = moment(startDate).startOf(type).format(dateFormat);
        const toDate = moment(endDate).endOf(type).format(dateFormat);

        if (startDate) {
          query.where('invoice_date', '>=', fromDate);
        }
        if (endDate) {
          query.where('invoice_date', '<=', toDate);
        }
      },
      /**
       * Filters the invoices in draft status.
       */
      draft(query) {
        query.where('delivered_at', null);
      },
      /**
       * Filters the published invoices.
       */
      published(query) {
        query.whereNot('delivered_at', null);
      },
      /**
       * Filters the delivered invoices.
       */
      delivered(query) {
        query.whereNot('delivered_at', null);
      },
      /**
       * Filters the unpaid invoices.
       */
      unpaid(query) {
        query.where(raw('PAYMENT_AMOUNT = 0'));
      },
      /**
       * Filters the overdue invoices.
       */
      overdue(query, asDate = moment().format('YYYY-MM-DD')) {
        query.where('due_date', '<', asDate);
      },
      /**
       * Filters the not overdue invoices.
       */
      notOverdue(query, asDate = moment().format('YYYY-MM-DD')) {
        query.where('due_date', '>=', asDate);
      },
      /**
       * Filters the partially invoices.
       */
      partiallyPaid(query) {
        query.whereNot('payment_amount', 0);
        query.whereNot(raw('`PAYMENT_AMOUNT` = `BALANCE`'));
      },
      /**
       * Filters the paid invoices.
       */
      paid(query) {
        query.where(raw('PAYMENT_AMOUNT = BALANCE'));
      },
      /**
       * Filters the sale invoices from the given date.
       */
      fromDate(query, fromDate) {
        query.where('invoice_date', '<=', fromDate);
      },
      /**
       * Sort the sale invoices by full-payment invoices.
       */
      sortByStatus(query, order) {
        query.orderByRaw(`PAYMENT_AMOUNT = BALANCE ${order}`);
      },

      /**
       * Sort the sale invoices by the due amount.
       */
      sortByDueAmount(query, order) {
        query.orderByRaw(`BALANCE - PAYMENT_AMOUNT ${order}`);
      },

      /**
       * Retrieve the max invoice
       */
      maxInvoiceNo(query, prefix, number) {
        query
          .select(raw(`REPLACE(INVOICE_NO, "${prefix}", "") AS INV_NUMBER`))
          .havingRaw('CHAR_LENGTH(INV_NUMBER) = ??', [number.length])
          .orderBy('invNumber', 'DESC')
          .limit(1)
          .first();
      },

      byPrefixAndNumber(query, prefix, number) {
        query.where('invoice_no', `${prefix}${number}`);
      },

      /**
       * Status filter.
       */
      statusFilter(query, filterType) {
        switch (filterType) {
          case 'draft':
            query.modify('draft');
            break;
          case 'delivered':
            query.modify('delivered');
            break;
          case 'unpaid':
            query.modify('unpaid');
            break;
          case 'overdue':
          default:
            query.modify('overdue');
            break;
          case 'partially-paid':
            query.modify('partiallyPaid');
            break;
          case 'paid':
            query.modify('paid');
            break;
        }
      },

      /**
       * Filters by branches.
       */
      filterByBranches(query, branchesIds) {
        const formattedBranchesIds = castArray(branchesIds);

        query.whereIn('branchId', formattedBranchesIds);
      },

      dueInvoicesFromDate(query, asDate = moment().format('YYYY-MM-DD')) {
        query.modify('dueInvoices');
        query.modify('notOverdue', asDate);
        query.modify('fromDate', asDate);
      },

      overdueInvoicesFromDate(query, asDate = moment().format('YYYY-MM-DD')) {
        query.modify('dueInvoices');
        query.modify('overdue', asDate);
        query.modify('fromDate', asDate);
      },
    };
  }

  /**
   * Relationship mapping.
   */
  static get relationMappings() {
    const {
      AccountTransaction,
    } = require('../../Accounts/models/AccountTransaction.model');
    const {
      ItemEntry,
    } = require('../../TransactionItemEntry/models/ItemEntry');
    const { Customer } = require('../../Customers/models/Customer');
    // const InventoryCostLotTracker = require('models/InventoryCostLotTracker');
    const {
      PaymentReceivedEntry,
    } = require('../../PaymentReceived/models/PaymentReceivedEntry');
    const { Branch } = require('../../Branches/models/Branch.model');
    const { Warehouse } = require('../../Warehouses/models/Warehouse.model');
    const { Account } = require('../../Accounts/models/Account.model');
    const {
      TaxRateTransaction,
    } = require('../../TaxRates/models/TaxRateTransaction.model');
    const { Document } = require('../../ChromiumlyTenancy/models/Document');
    const {
      MatchedBankTransaction,
    } = require('../../BankingMatching/models/MatchedBankTransaction');
    const {
      TransactionPaymentServiceEntry,
    } = require('../../PaymentServices/models/TransactionPaymentServiceEntry.model');
    const {
      PdfTemplateModel,
    } = require('../../PdfTemplate/models/PdfTemplate');

    return {
      /**
       * Sale invoice associated entries.
       */
      entries: {
        relation: Model.HasManyRelation,
        modelClass: ItemEntry,
        join: {
          from: 'sales_invoices.id',
          to: 'items_entries.referenceId',
        },
        filter(builder) {
          builder.where('reference_type', 'SaleInvoice');
          builder.orderBy('index', 'ASC');
        },
      },

      /**
       * Belongs to customer model.
       */
      customer: {
        relation: Model.BelongsToOneRelation,
        modelClass: Customer,
        join: {
          from: 'sales_invoices.customerId',
          to: 'contacts.id',
        },
        filter(query) {
          query.where('contact_service', 'Customer');
        },
      },

      /**
       * Invoice has associated account transactions.
       */
      transactions: {
        relation: Model.HasManyRelation,
        modelClass: AccountTransaction,
        join: {
          from: 'sales_invoices.id',
          to: 'accounts_transactions.referenceId',
        },
        filter(builder) {
          builder.where('reference_type', 'SaleInvoice');
        },
      },

      /**
       * Invoice may has associated cost transactions.
       */
      // costTransactions: {
      //   relation: Model.HasManyRelation,
      //   modelClass: InventoryCostLotTracker.default,
      //   join: {
      //     from: 'sales_invoices.id',
      //     to: 'inventory_cost_lot_tracker.transactionId',
      //   },
      //   filter(builder) {
      //     builder.where('transaction_type', 'SaleInvoice');
      //   },
      // },

      /**
       * Invoice may has associated payment entries.
       */
      paymentEntries: {
        relation: Model.HasManyRelation,
        modelClass: PaymentReceivedEntry,
        join: {
          from: 'sales_invoices.id',
          to: 'payment_receives_entries.invoiceId',
        },
      },

      /**
       * Invoice may has associated branch.
       */
      branch: {
        relation: Model.BelongsToOneRelation,
        modelClass: Branch,
        join: {
          from: 'sales_invoices.branchId',
          to: 'branches.id',
        },
      },

      /**
       * Invoice may has associated warehouse.
       */
      warehouse: {
        relation: Model.BelongsToOneRelation,
        modelClass: Warehouse,
        join: {
          from: 'sales_invoices.warehouseId',
          to: 'warehouses.id',
        },
      },

      /**
       * Invoice may has associated written-off expense account.
       */
      writtenoffExpenseAccount: {
        relation: Model.BelongsToOneRelation,
        modelClass: Account,
        join: {
          from: 'sales_invoices.writtenoffExpenseAccountId',
          to: 'accounts.id',
        },
      },

      /**
       * Invoice may has associated tax rate transactions.
       */
      taxes: {
        relation: Model.HasManyRelation,
        modelClass: TaxRateTransaction,
        join: {
          from: 'sales_invoices.id',
          to: 'tax_rate_transactions.referenceId',
        },
        filter(builder) {
          builder.where('reference_type', 'SaleInvoice');
        },
      },

      /**
       * Sale invoice transaction may has many attached attachments.
       */
      attachments: {
        relation: Model.ManyToManyRelation,
        modelClass: Document,
        join: {
          from: 'sales_invoices.id',
          through: {
            from: 'document_links.modelId',
            to: 'document_links.documentId',
          },
          to: 'documents.id',
        },
        filter(query) {
          query.where('model_ref', 'SaleInvoice');
        },
      },

      /**
       * Sale invocie may belongs to matched bank transaction.
       */
      matchedBankTransaction: {
        relation: Model.HasManyRelation,
        modelClass: MatchedBankTransaction,
        join: {
          from: 'sales_invoices.id',
          to: 'matched_bank_transactions.referenceId',
        },
        filter(query) {
          query.where('reference_type', 'SaleInvoice');
        },
      },

      /**
       * Sale invoice may belongs to payment methods entries.
       */
      paymentMethods: {
        relation: Model.HasManyRelation,
        modelClass: TransactionPaymentServiceEntry,
        join: {
          from: 'sales_invoices.id',
          to: 'transactions_payment_methods.referenceId',
        },
        beforeInsert: (model) => {
          model.referenceType = 'SaleInvoice';
        },
        filter: (query) => {
          query.where('reference_type', 'SaleInvoice');
        },
      },

      /**
       * Sale invoice may belongs to pdf branding template.
       */
      pdfTemplate: {
        relation: Model.BelongsToOneRelation,
        modelClass: PdfTemplateModel,
        join: {
          from: 'sales_invoices.pdfTemplateId',
          to: 'pdf_templates.id',
        },
      },
    };
  }

  /**
   * Change payment amount.
   * @param {Integer} invoiceId
   * @param {Numeric} amount
   */
  static async changePaymentAmount(invoiceId, amount, trx) {
    const changeMethod = amount > 0 ? 'increment' : 'decrement';

    await this.query(trx)
      .where('id', invoiceId)
      [changeMethod]('payment_amount', Math.abs(amount));
  }

  static dueAmountFieldSortQuery(query, role) {
    query.modify('sortByDueAmount', role.order);
  }

  /**
   * Model searchable.
   */
  static get searchable() {
    return true;
  }

  /**
   * Model search attributes.
   */
  static get searchRoles(): ISearchRole[] {
    return [
      { fieldKey: 'invoice_no', comparator: 'contains' },
      // { condition: 'or', fieldKey: 'reference_no', comparator: 'contains' },
      // { condition: 'or', fieldKey: 'amount', comparator: 'equals' },
    ];
  }

  /**
   * Prevents mutate base currency since the model is not empty.
   */
  static get preventMutateBaseCurrency() {
    return true;
  }
}
