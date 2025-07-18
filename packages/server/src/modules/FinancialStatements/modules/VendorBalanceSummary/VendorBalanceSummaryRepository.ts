import * as R from 'ramda';
import { isEmpty, map } from 'lodash';
import { Inject, Injectable, Scope } from '@nestjs/common';
import { Ledger } from '@/modules/Ledger/Ledger';
import { IVendorBalanceSummaryQuery } from './VendorBalanceSummary.types';
import { AccountTransaction } from '@/modules/Accounts/models/AccountTransaction.model';
import { Vendor } from '@/modules/Vendors/models/Vendor';
import { Account } from '@/modules/Accounts/models/Account.model';
import { ILedgerEntry } from '@/modules/Ledger/types/Ledger.types';
import { ModelObject } from 'objection';
import { ACCOUNT_TYPE } from '@/constants/accounts';
import { TenantModelProxy } from '@/modules/System/models/TenantBaseModel';

@Injectable({ scope: Scope.TRANSIENT })
export class VendorBalanceSummaryRepository {
  @Inject(AccountTransaction.name)
  private readonly accountTransactionModel: TenantModelProxy<
    typeof AccountTransaction
  >;

  @Inject(Vendor.name)
  private readonly vendorModel: TenantModelProxy<typeof Vendor>;

  @Inject(Account.name)
  private readonly accountModel: TenantModelProxy<typeof Account>;

  /**
   * Filter.
   * @param {IVendorBalanceSummaryQuery} filter
   */
  public filter: IVendorBalanceSummaryQuery;

  /**
   * Vendors entries.
   * @param {Array<ILedgerEntry>} vendorEntries
   */
  public vendorEntries: Array<ILedgerEntry>;

  /**
   * Vendors list.
   * @param {Array<ModelObject<Vendor>>} vendors
   */
  public vendors: Array<ModelObject<Vendor>>;

  /**
   * Ledger instance.
   */
  public ledger: Ledger;

  /**
   * Base currency.
   */
  public baseCurrency: string;

  /**
   * Set the filter.
   * @param {IVendorBalanceSummaryQuery} filter
   */
  public setFilter(filter: IVendorBalanceSummaryQuery) {
    this.filter = filter;
  }

  /**
   * Initialize the vendor balance summary repository.
   */
  async asyncInit() {
    await this.initVendors();
    await this.initVendorsEntries();
    await this.initLedger();
  }

  /**
   * Initialize the vendors.
   */
  async initVendors() {
    const vendors = await this.getVendors(this.filter.vendorsIds);
    this.vendors = vendors;
  }

  /**
   * Initialize the vendors entries.
   */
  async initVendorsEntries() {
    const vendorsEntries = await this.getReportVendorsEntries(
      this.filter.asDate,
    );
    this.vendorEntries = vendorsEntries;
  }

  /**
   * Initialize the ledger.
   */
  async initLedger() {
    this.ledger = new Ledger(this.vendorEntries);
  }

  /**
   * Retrieve the report vendors.
   * @param {number[]} vendorsIds - Vendors ids.
   * @returns {IVendor[]}
   */
  public async getVendors(
    vendorsIds?: number[],
  ): Promise<ModelObject<Vendor>[]> {
    const vendorQuery = this.vendorModel().query().orderBy('displayName');

    if (!isEmpty(vendorsIds)) {
      vendorQuery.whereIn('id', vendorsIds);
    }
    return vendorQuery;
  }

  /**
   * Retrieve the payable accounts.
   * @param {number} tenantId
   * @returns {Promise<IAccount[]>}
   */
  public async getPayableAccounts(): Promise<ModelObject<Account>[]> {
    return this.accountModel()
      .query()
      .where('accountType', ACCOUNT_TYPE.ACCOUNTS_PAYABLE);
  }

  /**
   * Retrieve the vendors transactions.
   * @param {number} tenantId
   * @param {Date} asDate
   * @returns
   */
  public async getVendorsTransactions(asDate: Date | string) {
    // Retrieve payable accounts .
    const payableAccounts = await this.getPayableAccounts();
    const payableAccountsIds = map(payableAccounts, 'id');

    // Retrieve the customers transactions of A/R accounts.
    const customersTranasctions = await this.accountTransactionModel()
      .query()
      .onBuild((query) => {
        query.whereIn('accountId', payableAccountsIds);
        query.modify('filterDateRange', null, asDate);
        query.groupBy('contactId');
        query.sum('credit as credit');
        query.sum('debit as debit');
        query.select('contactId');
      });
    return customersTranasctions;
  }

  /**
   *
   * Retrieve the vendors ledger entrjes.
   * @param {number} tenantId -
   * @param {Date|string} date -
   * @returns {Promise<ILedgerEntry>}
   */
  private async getReportVendorsEntries(
    date: Date | string,
  ): Promise<ILedgerEntry[]> {
    const transactions = await this.getVendorsTransactions(date);
    const commonProps = { accountNormal: 'credit' };

    return R.map(R.mergeRight(commonProps))(transactions) as ILedgerEntry[];
  }
}
