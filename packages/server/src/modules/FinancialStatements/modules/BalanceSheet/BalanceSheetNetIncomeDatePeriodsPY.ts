// @ts-nocheck
import * as R from 'ramda';
import { BalanceSheetComparsionPreviousYear } from './BalanceSheetComparsionPreviousYear';
import { FinancialPreviousPeriod } from '../../common/FinancialPreviousPeriod';
import { FinancialHorizTotals } from '../../common/FinancialHorizTotals';
import {
  IBalanceSheetNetIncomeNode,
  IBalanceSheetTotal,
} from './BalanceSheet.types';
import { BalanceSheetQuery } from './BalanceSheetQuery';
import { BalanceSheetRepository } from './BalanceSheetRepository';
import { GConstructor } from '@/common/types/Constructor';
import { FinancialSheet } from '../../common/FinancialSheet';

export const BalanceSheetNetIncomeDatePeriodsPY = <
  T extends GConstructor<FinancialSheet>,
>(
  Base: T,
) =>
  class extends R.pipe(
    BalanceSheetComparsionPreviousYear,
    FinancialPreviousPeriod,
    FinancialHorizTotals,
  )(Base) {
    query: BalanceSheetQuery;
    repository: BalanceSheetRepository;

    /**
     * Retrieves the PY total income of the given date period.
     * @param {Date} toDate -
     * @return {number}
     */
    public getPYIncomeDatePeriodTotal = R.curry((toDate: Date) => {
      const PYPeriodsTotal = this.repository.incomePYPeriodsAccountsLedger
        .whereToDate(toDate)
        .getClosingBalance();

      const PYPeriodsOpeningTotal =
        this.repository.incomePYPeriodsOpeningAccountLedger.getClosingBalance();

      return PYPeriodsOpeningTotal + PYPeriodsTotal;
    });

    /**
     * Retrieves the PY total expense of the given date period.
     * @param {Date} toDate -
     * @returns {number}
     */
    public getPYExpenseDatePeriodTotal = R.curry((toDate: Date) => {
      const PYPeriodsTotal = this.repository.expensePYPeriodsAccountsLedger
        .whereToDate(toDate)
        .getClosingBalance();

      const PYPeriodsOpeningTotal =
        this.repository.expensePYPeriodsOpeningAccountLedger.getClosingBalance();

      return PYPeriodsOpeningTotal + PYPeriodsTotal;
    });

    /**
     * Retrieve the given net income total of the given period.
     * @param {Date} toDate - To date.
     * @returns {number}
     */
    public getPYNetIncomeDatePeriodTotal = R.curry((toDate: Date) => {
      const income = this.getPYIncomeDatePeriodTotal(toDate);
      const expense = this.getPYExpenseDatePeriodTotal(toDate);

      return income - expense;
    });

    /**
     * Assoc preivous year to account horizontal total node.
     * @param {IBalanceSheetAccountNode} node
     * @returns {}
     */
    public assocPreviousYearNetIncomeHorizTotal = R.curry(
      (node: IBalanceSheetNetIncomeNode, totalNode) => {
        const total = this.getPYNetIncomeDatePeriodTotal(
          totalNode.previousYearToDate.date,
        );
        return R.assoc('previousYear', this.getAmountMeta(total), totalNode);
      },
    );

    /**
     * Compose PY to net income horizontal nodes.
     * @param {IBalanceSheetTotal} node
     * @returns {IBalanceSheetTotal}
     */
    public previousYearNetIncomeHorizNodeComposer = R.curry(
      (
        node: IBalanceSheetNetIncomeNode,
        horiontalTotalNode: IBalanceSheetTotal,
      ): IBalanceSheetTotal => {
        return R.compose(
          R.when(
            this.query.isPreviousYearPercentageActive,
            this.assocPreviousYearTotalPercentageNode,
          ),
          R.when(
            this.query.isPreviousYearChangeActive,
            this.assocPreviousYearTotalChangeNode,
          ),
          R.when(
            this.query.isPreviousYearActive,
            this.assocPreviousYearNetIncomeHorizTotal(node),
          ),
          R.when(
            this.query.isPreviousYearActive,
            this.assocPreviousYearHorizNodeFromToDates,
          ),
        )(horiontalTotalNode);
      },
    );

    /**
     * Associate the PY to net income horizontal nodes.
     * @param   {IBalanceSheetCommonNode} node
     * @returns {IBalanceSheetCommonNode}
     */
    public assocPreviousYearNetIncomeHorizNode = (
      node: IBalanceSheetNetIncomeNode,
    ): IBalanceSheetNetIncomeNode => {
      const horizontalTotals = R.addIndex(R.map)(
        this.previousYearNetIncomeHorizNodeComposer(node),
        node.horizontalTotals,
      ) as IBalanceSheetTotal[];

      return R.assoc('horizontalTotals', horizontalTotals, node);
    };
  };
