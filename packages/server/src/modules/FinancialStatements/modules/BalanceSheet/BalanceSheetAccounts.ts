// @ts-nocheck
import * as R from 'ramda';
import { defaultTo, toArray } from 'lodash';
import { I18nService } from 'nestjs-i18n';
import { FinancialSheetStructure } from '../../common/FinancialSheetStructure';
import {
  BALANCE_SHEET_SCHEMA_NODE_TYPE,
  IBalanceSheetAccountNode,
  IBalanceSheetAccountsNode,
  IBalanceSheetDataNode,
  IBalanceSheetSchemaAccountNode,
  IBalanceSheetSchemaNode,
} from './BalanceSheet.types';
import { BalanceSheetNetIncome } from './BalanceSheetNetIncome';
import { BalanceSheetFiltering } from './BalanceSheetFiltering';
import { BalanceSheetDatePeriods } from './BalanceSheetDatePeriods';
import { BalanceSheetComparsionPreviousPeriod } from './BalanceSheetComparsionPreviousPeriod';
import { BalanceSheetComparsionPreviousYear } from './BalanceSheetComparsionPreviousYear';
import { BalanceSheetPercentage } from './BalanceSheetPercentage';
import { BalanceSheetSchema } from './BalanceSheetSchema';
import { BalanceSheetBase } from './BalanceSheetBase';
import { BalanceSheetQuery } from './BalanceSheetQuery';
import { BalanceSheetRepository } from './BalanceSheetRepository';
import { GConstructor } from '@/common/types/Constructor';
import { INumberFormatQuery } from '../../types/Report.types';
import { Account } from '@/modules/Accounts/models/Account.model';
import { flatToNestedArray } from '@/utils/flat-to-nested-array';
import { FinancialSheet } from '../../common/FinancialSheet';

export const BalanceSheetAccounts = <T extends GConstructor<FinancialSheet>>(
  Base: T,
) =>
  class extends R.pipe(
    BalanceSheetNetIncome,
    BalanceSheetFiltering,
    BalanceSheetDatePeriods,
    BalanceSheetComparsionPreviousPeriod,
    BalanceSheetComparsionPreviousYear,
    BalanceSheetPercentage,
    BalanceSheetSchema,
    BalanceSheetBase,
    FinancialSheetStructure,
  )(Base) {
    /**
     * Balance sheet query.
     * @param {BalanceSheetQuery}
     */
    readonly query: BalanceSheetQuery;

    /**
     * Balance sheet number format query.
     * @param {INumberFormatQuery}
     */
    readonly numberFormat: INumberFormatQuery;

    /**
     * Base currency of the organization.
     * @param {string}
     */
    readonly baseCurrency: string;

    /**
     * Localization.
     */
    readonly i18n: I18nService;

    /**
     * Balance sheet repository.
     */
    readonly repository: BalanceSheetRepository;

    /**
     * Retrieve the accounts node of accounts types.
     * @param   {string} accountsTypes
     * @returns {IAccount[]}
     */
    private getAccountsByAccountTypes = (
      accountsTypes: string[],
    ): Account[] => {
      const mapAccountsByTypes = R.map((accountType) =>
        defaultTo(this.repository.accountsByType.get(accountType), []),
      );
      return R.compose(R.flatten, mapAccountsByTypes)(accountsTypes);
    };

    /**
     * Mappes the account model to report account node.
     * @param   {Account} account
     * @returns {IBalanceSheetAccountNode}
     */
    private reportSchemaAccountNodeMapper = (
      account: Account,
    ): IBalanceSheetAccountNode => {
      const childrenAccountsIds = this.repository.accountsGraph.dependenciesOf(
        account.id,
      );
      const accountIds = R.uniq(R.append(account.id, childrenAccountsIds));
      const total = this.repository.totalAccountsLedger
        .whereAccountsIds(accountIds)
        .getClosingBalance();

      return {
        id: account.id,
        index: account.index,
        name: account.name,
        code: account.code,
        total: this.getAmountMeta(total),
        nodeType: BALANCE_SHEET_SCHEMA_NODE_TYPE.ACCOUNT,
      };
    };

    /**
     * Mappes the given account model to the balance sheet account node.
     * @param {IAccount} account
     * @returns {IBalanceSheetAccountNode}
     */
    private reportSchemaAccountNodeComposer = (
      account: Account,
    ): IBalanceSheetAccountNode => {
      return R.compose(
        R.when(
          this.query.isPreviousYearActive,
          this.previousYearAccountNodeComposer,
        ),
        R.when(
          this.query.isPreviousPeriodActive,
          this.previousPeriodAccountNodeComposer,
        ),
        R.when(
          this.query.isDatePeriodsColumnsType,
          this.assocAccountNodeDatePeriods,
        ),
        this.reportSchemaAccountNodeMapper,
      )(account);
    };

    // -----------------------------
    // - Accounts Node Praser
    // -----------------------------
    /**
     * Retrieve the report accounts node by the given accounts types.
     * @param {string[]} accountsTypes
     * @returns {IBalanceSheetAccountNode[]}
     */
    private getAccountsNodesByAccountTypes = (
      accountsTypes: string[],
    ): IBalanceSheetAccountNode[] => {
      // Retrieves accounts from the given defined node account types.
      const accounts = this.getAccountsByAccountTypes(accountsTypes);

      // Converts the flatten accounts to tree.
      const accountsTree = flatToNestedArray(accounts, {
        id: 'id',
        parentId: 'parentAccountId',
      });
      // Maps over the accounts tree.
      return this.mapNodesDeep(
        accountsTree,
        this.reportSchemaAccountNodeComposer,
      );
    };

    /**
     * Mappes the accounts schema node type.
     * @param   {IBalanceSheetSchemaNode} node - Schema node.
     * @returns {IBalanceSheetAccountNode}
     */
    private reportSchemaAccountsNodeMapper = (
      node: IBalanceSheetSchemaAccountNode,
    ): IBalanceSheetAccountsNode => {
      const accounts = this.getAccountsNodesByAccountTypes(node.accountsTypes);
      const children = toArray(node?.children);

      return {
        id: node.id,
        name: this.i18n.t(node.name),
        nodeType: BALANCE_SHEET_SCHEMA_NODE_TYPE.ACCOUNTS,
        type: BALANCE_SHEET_SCHEMA_NODE_TYPE.ACCOUNTS,
        children: [...accounts, ...children],
        total: this.getTotalAmountMeta(0),
      };
    };

    /**
     * Mappes the given report schema node.
     * @param {IBalanceSheetSchemaNode | IBalanceSheetDataNode} node - Schema node.
     * @return {IBalanceSheetSchemaNode | IBalanceSheetDataNode}
     */
    private reportAccountSchemaParser = (
      node: IBalanceSheetSchemaNode | IBalanceSheetDataNode,
    ): IBalanceSheetSchemaNode | IBalanceSheetDataNode => {
      return R.compose(
        R.when(
          this.isSchemaNodeType(BALANCE_SHEET_SCHEMA_NODE_TYPE.ACCOUNTS),
          this.reportSchemaAccountsNodeMapper,
        ),
      )(node);
    };

    /**
     * Parses the report accounts schema nodes.
     * @param {IBalanceSheetSchemaNode[]} nodes -
     * @return {IBalanceSheetStructureSection[]}
     */
    public accountsSchemaParser = (
      nodes: (IBalanceSheetSchemaNode | IBalanceSheetDataNode)[],
    ): (IBalanceSheetDataNode | IBalanceSheetSchemaNode)[] => {
      return this.mapNodesDeepReverse(nodes, this.reportAccountSchemaParser);
    };
  };
