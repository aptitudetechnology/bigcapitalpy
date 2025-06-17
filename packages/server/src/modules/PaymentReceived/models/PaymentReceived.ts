import { Model } from 'objection';
import { PaymentReceivedEntry } from './PaymentReceivedEntry';
import { TenantBaseModel } from '@/modules/System/models/TenantBaseModel';
import { ExportableModel } from '@/modules/Export/decorators/ExportableModel.decorator';
import { ImportableModel } from '@/modules/Import/decorators/Import.decorator';
import { InjectModelMeta } from '@/modules/Tenancy/TenancyModels/decorators/InjectModelMeta.decorator';
import { PaymentReceivedMeta } from './PaymentReceived.meta';
import { InjectModelDefaultViews } from '@/modules/Views/decorators/InjectModelDefaultViews.decorator';
import { PaymentReceivedDefaultViews } from '../constants';

@ExportableModel()
@ImportableModel()
@InjectModelMeta(PaymentReceivedMeta)
@InjectModelDefaultViews(PaymentReceivedDefaultViews)
export class PaymentReceived extends TenantBaseModel {
  customerId: number;
  paymentDate: string;
  amount: number;
  currencyCode: string;
  referenceNo: string;
  depositAccountId: number;
  paymentReceiveNo: string;
  exchangeRate: number;
  statement: string;

  userId: number;
  branchId: number;
  pdfTemplateId: number;

  createdAt: string;
  updatedAt: string;

  entries?: PaymentReceivedEntry[];

  /**
   * Table name.
   */
  static get tableName() {
    return 'payment_receives';
  }

  /**
   * Timestamps columns.
   */
  get timestamps() {
    return ['created_at', 'updated_at'];
  }

  /**
   * Virtual attributes.
   */
  static get virtualAttributes() {
    return ['localAmount'];
  }

  /**
   * Payment receive amount in local currency.
   * @returns {number}
   */
  get localAmount() {
    return this.amount * this.exchangeRate;
  }

  /**
   * Resourcable model.
   */
  static get resourceable() {
    return true;
  }

  /*
   * Relationship mapping.
   */
  static get relationMappings() {
    const { PaymentReceivedEntry } = require('./PaymentReceivedEntry');
    const {
      AccountTransaction,
    } = require('../../Accounts/models/AccountTransaction.model');
    const { Customer } = require('../../Customers/models/Customer');
    const { Account } = require('../../Accounts/models/Account.model');
    const { Branch } = require('../../Branches/models/Branch.model');
    const {
      DocumentModel,
    } = require('../../Attachments/models/Document.model');
    const {
      PdfTemplateModel,
    } = require('../../PdfTemplate/models/PdfTemplate');

    return {
      customer: {
        relation: Model.BelongsToOneRelation,
        modelClass: Customer,
        join: {
          from: 'payment_receives.customerId',
          to: 'contacts.id',
        },
        filter: (query) => {
          query.where('contact_service', 'customer');
        },
      },

      depositAccount: {
        relation: Model.BelongsToOneRelation,
        modelClass: Account,
        join: {
          from: 'payment_receives.depositAccountId',
          to: 'accounts.id',
        },
      },

      entries: {
        relation: Model.HasManyRelation,
        modelClass: PaymentReceivedEntry,
        join: {
          from: 'payment_receives.id',
          to: 'payment_receives_entries.paymentReceiveId',
        },
        filter: (query) => {
          query.orderBy('index', 'ASC');
        },
      },

      transactions: {
        relation: Model.HasManyRelation,
        modelClass: AccountTransaction,
        join: {
          from: 'payment_receives.id',
          to: 'accounts_transactions.referenceId',
        },
        filter: (builder) => {
          builder.where('reference_type', 'PaymentReceive');
        },
      },

      /**
       * Payment receive may belongs to branch.
       */
      branch: {
        relation: Model.BelongsToOneRelation,
        modelClass: Branch,
        join: {
          from: 'payment_receives.branchId',
          to: 'branches.id',
        },
      },

      /**
       * Payment transaction may has many attached attachments.
       */
      attachments: {
        relation: Model.ManyToManyRelation,
        modelClass: DocumentModel,
        join: {
          from: 'payment_receives.id',
          through: {
            from: 'document_links.modelId',
            to: 'document_links.documentId',
          },
          to: 'documents.id',
        },
        filter(query) {
          query.where('model_ref', 'PaymentReceive');
        },
      },

      /**
       * Payment received may belongs to pdf branding template.
       */
      pdfTemplate: {
        relation: Model.BelongsToOneRelation,
        modelClass: PdfTemplateModel,
        join: {
          from: 'payment_receives.pdfTemplateId',
          to: 'pdf_templates.id',
        },
      },
    };
  }

  /**
   * Model search attributes.
   */
  static get searchRoles() {
    return [
      { fieldKey: 'payment_receive_no', comparator: 'contains' },
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
