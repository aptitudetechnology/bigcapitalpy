/* eslint-disable global-require */
import { Model } from 'objection';
import { castArray } from 'lodash';
import { AccountTypesUtils } from '@/libs/accounts-utils/AccountTypesUtils';
import { PlaidItem } from '@/modules/BankingPlaid/models/PlaidItem';
import { TenantBaseModel } from '@/modules/System/models/TenantBaseModel';

export class BankAccount extends TenantBaseModel {
  public name!: string;
  public slug!: string;
  public code!: string;
  public index!: number;
  public accountType!: string;
  public predefined!: boolean;
  public currencyCode!: string;
  public active!: boolean;
  public bankBalance!: number;
  public lastFeedsUpdatedAt!: string | null;
  public amount!: number;
  public plaidItemId!: number;

  public plaidItem!: PlaidItem;

  /**
   * Table name.
   */
  static get tableName() {
    return 'accounts';
  }

  /**
   * Timestamps columns.
   */
  static get timestamps() {
    return ['createdAt', 'updatedAt'];
  }

  /**
   * Virtual attributes.
   */
  static get virtualAttributes() {
    return ['accountTypeLabel'];
  }

  /**
   * Retrieve account type label.
   */
  get accountTypeLabel(): string {
    return AccountTypesUtils.getType(this.accountType, 'label');
  }

  /**
   * Allows to mark model as resourceable to viewable and filterable.
   */
  static get resourceable() {
    return true;
  }

  /**
   * Model modifiers.
   */
  static get modifiers() {
    return {
      /**
       * Inactive/Active mode.
       */
      inactiveMode(query, active = false) {
        query.where('accounts.active', !active);
      },
    };
  }

  /**
   * Relationship mapping.
   */
  static get relationMappings() {
    const AccountTransaction = require('models/AccountTransaction');

    return {
      /**
       * Account model may has many transactions.
       */
      transactions: {
        relation: Model.HasManyRelation,
        modelClass: AccountTransaction.default,
        join: {
          from: 'accounts.id',
          to: 'accounts_transactions.accountId',
        },
      },
    };
  }

  /**
   * Detarmines whether the given type equals the account type.
   * @param {string} accountType
   * @return {boolean}
   */
  isAccountType(accountType) {
    const types = castArray(accountType);
    return types.indexOf(this.accountType) !== -1;
  }

  /**
   * Detarmine whether the given parent type equals the account type.
   * @param {string} parentType
   * @return {boolean}
   */
  isParentType(parentType) {
    return AccountTypesUtils.isParentTypeEqualsKey(
      this.accountType,
      parentType,
    );
  }

  /**
   * Model search roles.
   */
  static get searchRoles() {
    return [
      { condition: 'or', fieldKey: 'name', comparator: 'contains' },
      { condition: 'or', fieldKey: 'code', comparator: 'like' },
    ];
  }
}
