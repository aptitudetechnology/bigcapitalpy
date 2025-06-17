import { Model } from 'objection';
import { BillPaymentEntry } from './BillPaymentEntry';
import { Vendor } from '@/modules/Vendors/models/Vendor';
import { Document } from '@/modules/ChromiumlyTenancy/models/Document';
import { ImportableModel } from '@/modules/Import/decorators/Import.decorator';
import { ExportableModel } from '@/modules/Export/decorators/ExportableModel.decorator';
import { InjectModelMeta } from '@/modules/Tenancy/TenancyModels/decorators/InjectModelMeta.decorator';
import { BillPaymentMeta } from './BillPayment.meta';
import { TenantBaseModel } from '@/modules/System/models/TenantBaseModel';
import { InjectModelDefaultViews } from '@/modules/Views/decorators/InjectModelDefaultViews.decorator';
import { BillPaymentDefaultViews } from '../constants';

@ImportableModel()
@ExportableModel()
@InjectModelMeta(BillPaymentMeta)
@InjectModelDefaultViews(BillPaymentDefaultViews)
export class BillPayment extends TenantBaseModel {
  vendorId: number;
  amount: number;
  currencyCode: string;
  paymentAccountId: number;
  paymentNumber: string;
  paymentDate: string;
  paymentMethod: string;
  reference: string;
  userId: number;
  statement: string;
  exchangeRate: number;

  createdAt?: Date;
  updatedAt?: Date;

  branchId?: number;

  entries?: BillPaymentEntry[];
  vendor?: Vendor;
  attachments?: Document[];

  /**
   * Table name
   */
  static get tableName() {
    return 'bills_payments';
  }

  /**
   * Timestamps columns.
   */
  get timestamps() {
    return ['createdAt', 'updatedAt'];
  }

  /**
   * Virtual attributes.
   */
  static get virtualAttributes() {
    return ['localAmount'];
  }

  /**
   * Payment amount in local currency.
   * @returns {number}
   */
  get localAmount() {
    return this.amount * this.exchangeRate;
  }

  /**
   * Relationship mapping.
   */
  static get relationMappings() {
    const { BillPaymentEntry } = require('./BillPaymentEntry');
    const {
      AccountTransaction,
    } = require('../../Accounts/models/AccountTransaction.model');
    const { Vendor } = require('../../Vendors/models/Vendor');
    const { Account } = require('../../Accounts/models/Account.model');
    const { Branch } = require('../../Branches/models/Branch.model');
    const { Document } = require('../../ChromiumlyTenancy/models/Document');

    return {
      entries: {
        relation: Model.HasManyRelation,
        modelClass: BillPaymentEntry,
        join: {
          from: 'bills_payments.id',
          to: 'bills_payments_entries.billPaymentId',
        },
        filter: (query) => {
          query.orderBy('index', 'ASC');
        },
      },

      vendor: {
        relation: Model.BelongsToOneRelation,
        modelClass: Vendor,
        join: {
          from: 'bills_payments.vendorId',
          to: 'contacts.id',
        },
        filter(query) {
          query.where('contact_service', 'vendor');
        },
      },

      paymentAccount: {
        relation: Model.BelongsToOneRelation,
        modelClass: Account,
        join: {
          from: 'bills_payments.paymentAccountId',
          to: 'accounts.id',
        },
      },

      transactions: {
        relation: Model.HasManyRelation,
        modelClass: AccountTransaction,
        join: {
          from: 'bills_payments.id',
          to: 'accounts_transactions.referenceId',
        },
        filter(builder) {
          builder.where('reference_type', 'BillPayment');
        },
      },

      /**
       * Bill payment may belongs to branch.
       */
      branch: {
        relation: Model.BelongsToOneRelation,
        modelClass: Branch,
        join: {
          from: 'bills_payments.branchId',
          to: 'branches.id',
        },
      },

      /**
       * Bill payment may has many attached attachments.
       */
      attachments: {
        relation: Model.ManyToManyRelation,
        modelClass: Document,
        join: {
          from: 'bills_payments.id',
          through: {
            from: 'document_links.modelId',
            to: 'document_links.documentId',
          },
          to: 'documents.id',
        },
        filter(query) {
          query.where('model_ref', 'BillPayment');
        },
      },
    };
  }

  /**
   * Model search attributes.
   */
  static get searchRoles() {
    return [
      { fieldKey: 'payment_number', comparator: 'contains' },
      { condition: 'or', fieldKey: 'reference_no', comparator: 'contains' },
      { condition: 'or', fieldKey: 'amount', comparator: 'equals' },
    ];
  }

  /**
   * Prevents mutate base currency since the model is not empty.
   */
  static get preventMutateBaseCurrency() {
    return true;
  }
}
