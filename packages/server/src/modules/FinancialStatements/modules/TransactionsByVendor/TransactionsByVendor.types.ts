
import { IFinancialSheetCommonMeta } from '../../types/Report.types';
import { IFinancialTable } from '../../types/Table.types';
import {
  ITransactionsByContactsAmount,
  ITransactionsByContactsTransaction,
  ITransactionsByContactsFilter,
} from '../TransactionsByContact/TransactionsByContact.types';

export interface ITransactionsByVendorsAmount
  extends ITransactionsByContactsAmount {}

export interface ITransactionsByVendorsTransaction
  extends ITransactionsByContactsTransaction {}

export interface ITransactionsByVendorsVendor {
  vendorName: string;
  openingBalance: ITransactionsByVendorsAmount;
  closingBalance: ITransactionsByVendorsAmount;
  transactions: ITransactionsByVendorsTransaction[];
}

export interface ITransactionsByVendorsFilter
  extends ITransactionsByContactsFilter {
  vendorsIds: number[];
}

export type ITransactionsByVendorsData = ITransactionsByVendorsVendor[];

export interface ITransactionsByVendorsStatement {
  data: ITransactionsByVendorsData;
  query: ITransactionsByVendorsFilter;
  meta: ITransactionsByVendorMeta;
}

export interface ITransactionsByVendorsService {
  transactionsByVendors(
    tenantId: number,
    filter: ITransactionsByVendorsFilter
  ): Promise<ITransactionsByVendorsStatement>;
}

export interface ITransactionsByVendorTable extends IFinancialTable {
  query: ITransactionsByVendorsFilter;
  meta: ITransactionsByVendorMeta;
}

export interface ITransactionsByVendorMeta extends IFinancialSheetCommonMeta {
  formattedFromDate: string;
  formattedToDate: string;
  formattedDateRange: string;
}
