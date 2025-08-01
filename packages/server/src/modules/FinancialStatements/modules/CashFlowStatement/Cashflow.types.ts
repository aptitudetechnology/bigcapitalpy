import { Knex } from 'knex';
import { IFinancialSheetCommonMeta, INumberFormatQuery } from '../../types/Report.types';
import { Account } from '@/modules/Accounts/models/Account.model';
import { Ledger } from '@/modules/Ledger/Ledger';
import { IFinancialTable, ITableRow } from '../../types/Table.types';


export interface ICashFlowStatementQuery {
  fromDate: Date | string;
  toDate: Date | string;
  displayColumnsBy: string;
  displayColumnsType: string;
  noneZero: boolean;
  noneTransactions: boolean;
  numberFormat: INumberFormatQuery;
  basis: string;

  branchesIds?: number[];
}

export interface ICashFlowStatementTotal {
  amount: number;
  formattedAmount: string;
  currencyCode: string;
}

export interface ICashFlowStatementTotalPeriod {
  fromDate: Date;
  toDate: Date;
  total: ICashFlowStatementTotal;
}

export interface ICashFlowStatementCommonSection {
  id: string;
  label: string;
  total: ICashFlowStatementTotal;
  footerLabel?: string;
}

export interface ICashFlowStatementAccountMeta {
  id: number;
  label: string;
  code: string;
  total: ICashFlowStatementTotal;
  accountType: string;
  adjustmentType: string;
  sectionType: ICashFlowStatementSectionType.ACCOUNT;
}

export enum ICashFlowStatementSectionType {
  REGULAR = 'REGULAR',
  AGGREGATE = 'AGGREGATE',
  NET_INCOME = 'NET_INCOME',
  ACCOUNT = 'ACCOUNT',
  ACCOUNTS = 'ACCOUNTS',
  TOTAL = 'TOTAL',
  CASH_AT_BEGINNING = 'CASH_AT_BEGINNING',
}

export interface ICashFlowStatementAccountSection
  extends ICashFlowStatementCommonSection {
  sectionType: ICashFlowStatementSectionType.ACCOUNTS;
  children: ICashFlowStatementAccountMeta[];
  total: ICashFlowStatementTotal;
}

export interface ICashFlowStatementNetIncomeSection
  extends ICashFlowStatementCommonSection {
  sectionType: ICashFlowStatementSectionType.NET_INCOME;
}

export interface ICashFlowStatementTotalSection
  extends ICashFlowStatementCommonSection {
  sectionType: ICashFlowStatementSectionType.TOTAL;
}

export interface ICashFlowStatementAggregateSection
  extends ICashFlowStatementCommonSection {
  sectionType: ICashFlowStatementSectionType.AGGREGATE;
}

export interface ICashFlowCashBeginningNode
  extends ICashFlowStatementCommonSection {
  sectionType: ICashFlowStatementSectionType.CASH_AT_BEGINNING;
}

export type ICashFlowStatementSection =
  | ICashFlowStatementAccountSection
  | ICashFlowStatementNetIncomeSection
  | ICashFlowStatementTotalSection
  | ICashFlowStatementCommonSection;

export interface ICashFlowStatementColumn {}
export interface ICashFlowStatementMeta extends IFinancialSheetCommonMeta {
  formattedToDate: string;
  formattedFromDate: string;
  formattedDateRange: string;
}

export interface ICashFlowStatementDOO {
  data: ICashFlowStatementData;
  meta: ICashFlowStatementMeta;
  query: ICashFlowStatementQuery;
}

export interface ICashFlowStatementTable extends IFinancialTable {
  meta: ICashFlowStatementMeta;
  query: ICashFlowStatementQuery;
}

export interface ICashFlowStatementService {
  cashFlow(
    tenantId: number,
    query: ICashFlowStatementQuery
  ): Promise<ICashFlowStatementDOO>;
}

// CASH FLOW SCHEMA TYPES.
// -----------------------------
export interface ICashFlowSchemaCommonSection {
  id: string;
  label: string;
  children: ICashFlowSchemaSection[];
  footerLabel?: string;
}

export enum CASH_FLOW_ACCOUNT_RELATION {
  MINES = 'mines',
  PLUS = 'plus',
}

export enum CASH_FLOW_SECTION_ID {
  NET_INCOME = 'NET_INCOME',
  OPERATING = 'OPERATING',
  OPERATING_ACCOUNTS = 'OPERATING_ACCOUNTS',
  INVESTMENT = 'INVESTMENT',
  FINANCIAL = 'FINANCIAL',

  NET_OPERATING = 'NET_OPERATING',
  NET_INVESTMENT = 'NET_INVESTMENT',
  NET_FINANCIAL = 'NET_FINANCIAL',

  CASH_BEGINNING_PERIOD = 'CASH_BEGINNING_PERIOD',
  CASH_END_PERIOD = 'CASH_END_PERIOD',
  NET_CASH_INCREASE = 'NET_CASH_INCREASE',
}

export interface ICashFlowSchemaAccountsSection
  extends ICashFlowSchemaCommonSection {
  sectionType: ICashFlowStatementSectionType.ACCOUNT;
  accountsRelations: ICashFlowSchemaAccountRelation[];
}

export interface ICashFlowSchemaTotalSection
  extends ICashFlowStatementCommonSection {
  sectionType: ICashFlowStatementSectionType.TOTAL;
  equation: string;
}

export type ICashFlowSchemaSection =
  | ICashFlowSchemaAccountsSection
  | ICashFlowSchemaTotalSection
  | ICashFlowSchemaCommonSection;

export type ICashFlowStatementData = ICashFlowSchemaSection[];

export interface ICashFlowSchemaAccountRelation {
  type: string;
  direction: CASH_FLOW_ACCOUNT_RELATION.PLUS;
}

export interface ICashFlowSchemaSectionAccounts
  extends ICashFlowStatementCommonSection {
  type: ICashFlowStatementSectionType.ACCOUNT;
  accountsRelations: ICashFlowSchemaAccountRelation[];
}

export interface ICashFlowSchemaSectionTotal {
  type: ICashFlowStatementSectionType.TOTAL;
  totalEquation: string;
}

export interface ICashFlowDatePeriod {
  fromDate: ICashFlowDate;
  toDate: ICashFlowDate;
  total: ICashFlowStatementTotal;
}

export interface ICashFlowDate {
  formattedDate: string;
  date: Date;
}

export interface ICashFlowStatement {
  /**
   * Constructor method.
   * @constructor
   */
  constructor(
    accounts: Account[],
    ledger: Ledger,
    cashLedger: Ledger,
    netIncomeLedger: Ledger,
    query: ICashFlowStatementQuery,
    baseCurrency: string
  ): void;

  reportData(): ICashFlowStatementData;
}

export interface ICashFlowTable {
  constructor(reportStatement: ICashFlowStatement): void;
  tableRows(): ITableRow[];
}

export interface IDateRange {
  fromDate: Date;
  toDate: Date;
}

export interface ICashflowTransactionSchema {
  amount: number;
  date: Date;
  referenceNo?: string | null;
  transactionNumber: string;
  transactionType: string;
  creditAccountId: number;
  cashflowAccountId: number;
  userId: number;
  publishedAt?: Date | null;
  branchId?: number;
}

export interface ICashflowTransactionInput extends ICashflowTransactionSchema {}

export interface ICategorizeCashflowTransactioDTO {
  date: Date;
  creditAccountId: number;
  referenceNo: string;
  transactionNumber: string;
  transactionType: string;
  exchangeRate: number;
  description: string;
  branchId: number;
}

export interface IUncategorizedCashflowTransaction {
  id?: number;
  amount: number;
  date: Date;
  currencyCode: string;
  accountId: number;
  description: string;
  referenceNo: string;
  categorizeRefType: string;
  categorizeRefId: number;
  categorized: boolean;
}

export interface CreateUncategorizedTransactionDTO {
  date: Date | string;
  accountId: number;
  amount: number;
  currencyCode: string;
  payee?: string;
  description?: string;
  referenceNo?: string | null;
  plaidTransactionId?: string | null;
  pending?: boolean;
  pendingPlaidTransactionId?: string | null;
  batch?: string;
}

export interface IUncategorizedTransactionCreatingEventPayload {
  tenantId: number;
  createUncategorizedTransactionDTO: CreateUncategorizedTransactionDTO;
  trx: Knex.Transaction;
}

export interface IUncategorizedTransactionCreatedEventPayload {
  tenantId: number;
  uncategorizedTransaction: any;
  createUncategorizedTransactionDTO: CreateUncategorizedTransactionDTO;
  trx: Knex.Transaction;
}

export interface IPendingTransactionRemovingEventPayload {
  tenantId: number;
  uncategorizedTransactionId: number;
  pendingTransaction: IUncategorizedCashflowTransaction;
  trx?: Knex.Transaction;
}

export interface IPendingTransactionRemovedEventPayload {
  tenantId: number;
  uncategorizedTransactionId: number;
  pendingTransaction: IUncategorizedCashflowTransaction;
  trx?: Knex.Transaction;
}
