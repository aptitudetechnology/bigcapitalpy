// @ts-nocheck
import * as R from 'ramda';
import { sumBy } from 'lodash';
import {
  IBalanceSheetQuery,
  IBalanceSheetAccountNode,
  IBalanceSheetTotalPeriod,
  IBalanceSheetCommonNode,
} from './BalanceSheet.types';
import { FinancialDatePeriods } from '../../common/FinancialDatePeriods';
import { IDateRange, IFormatNumberSettings } from '../../types/Report.types';
import { GConstructor } from '@/common/types/Constructor';
import { FinancialSheet } from '../../common/FinancialSheet';
import { BalanceSheetQuery } from './BalanceSheetQuery';

/**
 * Balance sheet date periods.
 */
export const BalanceSheetDatePeriods = <T extends GConstructor<FinancialSheet>>(
  Base: T,
) =>
  class BalanceSheetDatePeriods extends R.pipe(FinancialDatePeriods)(Base) {
    /**
     * @param {IBalanceSheetQuery}
     */
    public readonly query: BalanceSheetQuery;

    /**
     * Retrieves the date periods based on the report query.
     * @returns {IDateRange[]}
     */
    get datePeriods(): IDateRange[] {
      return this.getDateRanges(
        this.query.fromDate,
        this.query.toDate,
        this.query.displayColumnsBy,
      );
    }

    /**
     * Retrieves the date periods of the given node based on the report query.
     * @param   {IBalanceSheetCommonNode} node
     * @param   {Function} callback
     * @returns {}
     */
    public getReportNodeDatePeriods = (
      node: IBalanceSheetCommonNode,
      callback: (
        node: IBalanceSheetCommonNode,
        fromDate: Date,
        toDate: Date,
        index: number,
      ) => any,
    ) => {
      return this.getNodeDatePeriods(
        this.query.fromDate,
        this.query.toDate,
        this.query.displayColumnsBy,
        node,
        callback,
      );
    };

    /**
     * Retrieve the date period meta.
     * @param  {number} total - Total amount.
     * @param  {Date} fromDate - From date.
     * @param  {Date} toDate -  To date.
     * @return {ICashFlowDatePeriod}
     */
    public getDatePeriodTotalMeta = (
      total: number,
      fromDate: Date,
      toDate: Date,
      overrideSettings: IFormatNumberSettings = {},
    ): IBalanceSheetTotalPeriod => {
      return this.getDatePeriodMeta(total, fromDate, toDate, {
        money: true,
        ...overrideSettings,
      });
    };

    // --------------------------------
    // # Account
    // --------------------------------
    /**
     * Retrieve the given account date period total.
     * @param   {number} accountId
     * @param   {Date} toDate
     * @returns {number}
     */
    public getAccountDatePeriodTotal = (
      accountId: number,
      toDate: Date,
    ): number => {
      const periodTotalBetween = this.repository.periodsAccountsLedger
        .whereAccountId(accountId)
        .whereToDate(toDate)
        .getClosingBalance();

      const periodOpening = this.repository.periodsOpeningAccountLedger
        .whereAccountId(accountId)
        .getClosingBalance();

      return periodOpening + periodTotalBetween;
    };

    /**
     *
     * @param {IBalanceSheetAccountNode} node
     * @param {Date} fromDate
     * @param {Date} toDate
     * @returns {IBalanceSheetAccountNode}
     */
    public getAccountNodeDatePeriod = (
      node: IBalanceSheetAccountNode,
      fromDate: Date,
      toDate: Date,
    ): IBalanceSheetTotalPeriod => {
      const periodTotal = this.getAccountDatePeriodTotal(node.id, toDate);

      return this.getDatePeriodTotalMeta(periodTotal, fromDate, toDate);
    };

    /**
     * Retrieve total date periods of the given account node.
     * @param   {IBalanceSheetAccountNode} node
     * @returns {IBalanceSheetAccountNode}
     */
    public getAccountsNodeDatePeriods = (
      node: IBalanceSheetAccountNode,
    ): IBalanceSheetTotalPeriod[] => {
      return this.getReportNodeDatePeriods(node, this.getAccountNodeDatePeriod);
    };

    /**
     * Assoc total date periods to account node.
     * @param   {IBalanceSheetAccountNode} node
     * @returns {IBalanceSheetAccountNode}
     */
    public assocAccountNodeDatePeriods = (
      node: IBalanceSheetAccountNode,
    ): IBalanceSheetAccountNode => {
      const datePeriods = this.getAccountsNodeDatePeriods(node);

      return R.assoc('horizontalTotals', datePeriods, node);
    };

    // --------------------------------
    // # Aggregate
    // --------------------------------
    /**
     *
     * @param   {} node
     * @param   {number} index
     * @returns {number}
     */
    public getAggregateDatePeriodIndexTotal = (node, index) => {
      return sumBy(node.children, `horizontalTotals[${index}].total.amount`);
    };

    /**
     *
     * @param {IBalanceSheetAccountNode} node
     * @param {Date} fromDate
     * @param {Date} toDate
     * @returns
     */
    public getAggregateNodeDatePeriod = (
      node: IBalanceSheetAccountNode,
      fromDate: Date,
      toDate: Date,
      index: number,
    ) => {
      const periodTotal = this.getAggregateDatePeriodIndexTotal(node, index);

      return this.getDatePeriodTotalMeta(periodTotal, fromDate, toDate);
    };

    /**
     *
     * @param node
     * @returns
     */
    public getAggregateNodeDatePeriods = (node) => {
      return this.getReportNodeDatePeriods(
        node,
        this.getAggregateNodeDatePeriod,
      );
    };

    /**
     * Assoc total date periods to aggregate node.
     * @param node
     * @returns {}
     */
    public assocAggregateNodeDatePeriods = (node) => {
      const datePeriods = this.getAggregateNodeDatePeriods(node);

      return R.assoc('horizontalTotals', datePeriods, node);
    };

    /**
     *
     * @param node
     * @returns
     */
    public assocAccountsNodeDatePeriods = (node) => {
      return this.assocAggregateNodeDatePeriods(node);
    };
  };
