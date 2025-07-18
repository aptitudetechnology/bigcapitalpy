import { Model } from 'objection';
import { BaseModel } from '@/models/Model';
import {
  getCashflowAccountTransactionsTypes,
  getCashflowTransactionType,
} from '../utils';
import { CASHFLOW_DIRECTION, CASHFLOW_TRANSACTION_TYPE } from '../constants';
import { BankTransactionLine } from './BankTransactionLine';
import { Account } from '@/modules/Accounts/models/Account.model';

export class BankTransaction extends BaseModel {
  transactionType: string;
  amount: number;
  exchangeRate: number;
  uncategorize: boolean;
  uncategorizedTransaction!: boolean;
  currencyCode: string;
  date: Date;
  transactionNumber: string;
  referenceNo: string;
  description: string;

  cashflowAccountId: number;
  creditAccountId: number;

  categorizeRefType: string;
  categorizeRefId: number;
  uncategorized: boolean;

  branchId: number;
  userId: number;

  publishedAt: Date;

  entries: BankTransactionLine[];
  cashflowAccount: Account;
  creditAccount: Account;

  uncategorizedTransactionId: number;

  /**
   * Table name.
   * @returns {string}
   */
  static get tableName() {
    return 'cashflow_transactions';
  }

  /**
   * Timestamps columns.
   * @returns {Array<string>}
   */
  static get timestamps() {
    return ['createdAt', 'updatedAt'];
  }

  /**
   * Virtual attributes.
   * @returns {Array<string>}
   */
  static get virtualAttributes() {
    return [
      'localAmount',
      'transactionTypeFormatted',
      'isPublished',
      'typeMeta',
      'isCashCredit',
      'isCashDebit',
    ];
  }

  /**
   * Retrieves the local amount of cashflow transaction.
   * @returns {number}
   */
  get localAmount() {
    return this.amount * this.exchangeRate;
  }

  /**
   * Detarmines whether the cashflow transaction is published.
   * @return {boolean}
   */
  get isPublished() {
    return !!this.publishedAt;
  }

  /**
   * Transaction type formatted.
   * @returns {string}
   */
  // get transactionTypeFormatted() {
  //   return getCashflowTransactionFormattedType(this.transactionType);
  // }

  get typeMeta() {
    return getCashflowTransactionType(
      this.transactionType as CASHFLOW_TRANSACTION_TYPE,
    );
  }

  /**
   * Detarmines whether the cashflow transaction cash credit type.
   * @returns {boolean}
   */
  get isCashCredit() {
    return this.typeMeta?.direction === CASHFLOW_DIRECTION.OUT;
  }

  /**
   * Detarmines whether the cashflow transaction cash debit type.
   * @returns {boolean}
   */
  get isCashDebit() {
    return this.typeMeta?.direction === CASHFLOW_DIRECTION.IN;
  }

  /**
   * Detarmines whether the transaction imported from uncategorized transaction.
   * @returns {boolean}
   */
  get isCategroizedTranasction() {
    return !!this.uncategorizedTransaction;
  }

  /**
   * Model modifiers.
   */
  static get modifiers() {
    return {
      /**
       * Filter the published transactions.
       */
      published(query) {
        query.whereNot('published_at', null);
      },

      /**
       * Filter the not categorized transactions.
       */
      notCategorized(query) {
        query.whereNull('cashflowTransactions.uncategorizedTransactionId');
      },

      /**
       * Filter the categorized transactions.
       */
      categorized(query) {
        query.whereNotNull('cashflowTransactions.uncategorizedTransactionId');
      },
    };
  }

  /**
   * Relationship mapping.
   */
  static get relationMappings() {
    const { BankTransactionLine } = require('./BankTransactionLine');
    const {
      AccountTransaction,
    } = require('../../Accounts/models/AccountTransaction.model');
    const { Account } = require('../../Accounts/models/Account.model');
    const {
      MatchedBankTransaction,
    } = require('../../BankingMatching/models/MatchedBankTransaction');

    return {
      /**
       * Cashflow transaction entries.
       */
      entries: {
        relation: Model.HasManyRelation,
        modelClass: BankTransactionLine,
        join: {
          from: 'cashflow_transactions.id',
          to: 'cashflow_transaction_lines.cashflowTransactionId',
        },
        filter: (query) => {
          query.orderBy('index', 'ASC');
        },
      },

      /**
       * Cashflow transaction has associated account transactions.
       */
      transactions: {
        relation: Model.HasManyRelation,
        modelClass: AccountTransaction,
        join: {
          from: 'cashflow_transactions.id',
          to: 'accounts_transactions.referenceId',
        },
        filter(builder) {
          builder.where('reference_type', 'CashflowTransaction');
        },
      },

      /**
       * Cashflow transaction may has associated cashflow account.
       */
      cashflowAccount: {
        relation: Model.BelongsToOneRelation,
        modelClass: Account,
        join: {
          from: 'cashflow_transactions.cashflowAccountId',
          to: 'accounts.id',
        },
      },

      /**
       * Cashflow transcation may has associated to credit account.
       */
      creditAccount: {
        relation: Model.BelongsToOneRelation,
        modelClass: Account,
        join: {
          from: 'cashflow_transactions.creditAccountId',
          to: 'accounts.id',
        },
      },

      /**
       * Cashflow transaction may belongs to matched bank transaction.
       */
      matchedBankTransaction: {
        relation: Model.HasManyRelation,
        modelClass: MatchedBankTransaction,
        join: {
          from: 'cashflow_transactions.id',
          to: 'matched_bank_transactions.referenceId',
        },
        filter: (query) => {
          const referenceTypes = getCashflowAccountTransactionsTypes();
          query.whereIn('reference_type', referenceTypes);
        },
      },
    };
  }
}
