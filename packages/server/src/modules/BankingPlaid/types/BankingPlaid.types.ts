import { Knex } from 'knex';
import { RemovedTransaction, Transaction } from 'plaid';

export interface IPlaidTransactionsSyncedEventPayload {
  // tenantId: number;
  plaidAccountId: number;
  batch: string;
  trx?: Knex.Transaction;
}

export interface PlaidItemDTO {
  publicToken: string;
  institutionId: string;
}

export interface PlaidFetchedTransactionsUpdates {
  added: Transaction[];
  modified: Transaction[];
  removed: RemovedTransaction[];
  accessToken: string;
  cursor: string;
}

export interface IPlaidItemCreatedEventPayload {
  tenantId: number;
  plaidAccessToken: string;
  plaidItemId: string;
  plaidInstitutionId: string;
}

export const UpdateBankingPlaidTransitionsJob =
  'update-banking-plaid-transitions-job';

  export const UpdateBankingPlaidTransitionsQueueJob =
  'update-banking-plaid-transitions-query';


export interface PlaidFetchTransitonsEventPayload {
  plaidItemId: string;
}