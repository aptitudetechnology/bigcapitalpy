import { Model, mixin } from 'objection';
// import TenantModel from 'models/TenantModel';
// import { formatNumber } from 'utils';
// import ModelSetting from './ModelSetting';
// import ManualJournalSettings from './ManualJournal.Settings';
// import CustomViewBaseModel from './CustomViewBaseModel';
// import { DEFAULT_VIEWS } from '@/services/ManualJournals/constants';
// import ModelSearchable from './ModelSearchable';
import { ManualJournalEntry } from './ManualJournalEntry';
import { Document } from '@/modules/ChromiumlyTenancy/models/Document';
import { TenantBaseModel } from '@/modules/System/models/TenantBaseModel';
import { ExportableModel } from '@/modules/Export/decorators/ExportableModel.decorator';
import { InjectModelMeta } from '@/modules/Tenancy/TenancyModels/decorators/InjectModelMeta.decorator';
import { ManualJournalMeta } from './ManualJournal.meta';
import { ImportableModel } from '@/modules/Import/decorators/Import.decorator';

@ExportableModel()
@ImportableModel()
@InjectModelMeta(ManualJournalMeta)
export class ManualJournal extends TenantBaseModel {
  date: Date;
  journalNumber: string;
  journalType: string;
  reference: string;
  amount: number;
  currencyCode: string;
  exchangeRate: number | null;
  publishedAt: Date | string | null;
  description: string;
  userId?: number;

  createdAt?: Date;
  updatedAt?: Date;

  entries!: ManualJournalEntry[];
  attachments!: Document[];

  branchId?: number;

  /**
   * Table name.
   */
  static get tableName() {
    return 'manual_journals';
  }

  /**
   * Model timestamps.
   */
  get timestamps() {
    return ['createdAt', 'updatedAt'];
  }

  /**
   * Virtual attributes.
   */
  static get virtualAttributes() {
    return ['isPublished', 'amountFormatted'];
  }

  /**
   * Retrieve the amount formatted value.
   */
  // get amountFormatted() {
  //   return formatNumber(this.amount, { currencyCode: this.currencyCode });
  // }

  /**
   * Detarmines whether the invoice is published.
   * @return {boolean}
   */
  get isPublished() {
    return !!this.publishedAt;
  }

  /**
   * Model modifiers.
   */
  static get modifiers() {
    return {
      /**
       * Sort by status query.
       */
      sortByStatus(query, order) {
        query.orderByRaw(`PUBLISHED_AT IS NULL ${order}`);
      },

      /**
       * Filter by draft status.
       */
      filterByDraft(query) {
        query.whereNull('publishedAt');
      },

      /**
       * Filter by published status.
       */
      filterByPublished(query) {
        query.whereNotNull('publishedAt');
      },

      /**
       * Filter by the given status.
       */
      filterByStatus(query, filterType) {
        switch (filterType) {
          case 'draft':
            query.modify('filterByDraft');
            break;
          case 'published':
          default:
            query.modify('filterByPublished');
            break;
        }
      },
    };
  }

  /**
   * Relationship mapping.
   */
  static get relationMappings() {
    const { AccountTransaction } = require('../../Accounts/models/AccountTransaction.model');
    const { ManualJournalEntry } = require('./ManualJournalEntry');
    const { Document } = require('../../ChromiumlyTenancy/models/Document');
    const { MatchedBankTransaction } = require('../../BankingMatching/models/MatchedBankTransaction');

    return {
      entries: {
        relation: Model.HasManyRelation,
        modelClass: ManualJournalEntry,
        join: {
          from: 'manual_journals.id',
          to: 'manual_journals_entries.manualJournalId',
        },
        filter(query) {
          query.orderBy('index', 'ASC');
        },
      },
      transactions: {
        relation: Model.HasManyRelation,
        modelClass: AccountTransaction,
        join: {
          from: 'manual_journals.id',
          to: 'accounts_transactions.referenceId',
        },
        filter: (query) => {
          query.where('referenceType', 'Journal');
        },
      },

      /**
       * Manual journal may has many attached attachments.
       */
      attachments: {
        relation: Model.ManyToManyRelation,
        modelClass: Document,
        join: {
          from: 'manual_journals.id',
          through: {
            from: 'document_links.modelId',
            to: 'document_links.documentId',
          },
          to: 'documents.id',
        },
        filter(query) {
          query.where('model_ref', 'ManualJournal');
        },
      },

      /**
       * Manual journal may belongs to matched bank transaction.
       */
      matchedBankTransaction: {
        relation: Model.BelongsToOneRelation,
        modelClass: MatchedBankTransaction,
        join: {
          from: 'manual_journals.id',
          to: 'matched_bank_transactions.referenceId',
        },
        filter(query) {
          query.where('reference_type', 'ManualJournal');
        },
      },
    };
  }

  // static get meta() {
  //   return ManualJournalSettings;
  // }

  // /**
  //  * Retrieve the default custom views, roles and columns.
  //  */
  // static get defaultViews() {
  //   return DEFAULT_VIEWS;
  // }

  /**
   * Model search attributes.
   */
  static get searchRoles() {
    return [
      { fieldKey: 'journal_number', comparator: 'contains' },
      { condition: 'or', fieldKey: 'reference', comparator: 'contains' },
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
