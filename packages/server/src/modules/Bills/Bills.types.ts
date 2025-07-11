import { Knex } from 'knex';
import { IItemEntryDTO } from '../TransactionItemEntry/ItemEntry.types';
import { AttachmentLinkDTO } from '../Attachments/Attachments.types';
import { Bill } from './models/Bill';
import { IDynamicListFilter } from '../DynamicListing/DynamicFilter/DynamicFilter.types';
import { CreateBillDto, EditBillDto } from './dtos/Bill.dto';

export interface IBillDTO {
  vendorId: number;
  billNumber: string;
  billDate: Date;
  dueDate: Date;
  referenceNo: string;
  status: string;
  note: string;
  amount: number;
  paymentAmount: number;
  exchangeRate?: number;
  open: boolean;
  entries: IItemEntryDTO[];
  branchId?: number;
  warehouseId?: number;
  projectId?: number;
  isInclusiveTax?: boolean;
  attachments?: AttachmentLinkDTO[];
}

export interface IBillEditDTO {
  vendorId: number;
  billNumber: string;
  billDate: Date;
  dueDate: Date;
  referenceNo: string;
  status: string;
  note: string;
  amount: number;
  paymentAmount: number;
  open: boolean;
  entries: IItemEntryDTO[];

  branchId?: number;
  warehouseId?: number;
  projectId?: number;
  attachments?: AttachmentLinkDTO[];
}

export interface IBillsFilter extends IDynamicListFilter {
  stringifiedFilterRoles?: string;
  page: number;
  pageSize: number;
  filterQuery?: (q: any) => void;
}

export interface IBillCreatedPayload {
  bill: Bill;
  billDTO: CreateBillDto;
  trx?: Knex.Transaction;
}

export interface IBillCreatingPayload {
  billDTO: CreateBillDto;
  trx: Knex.Transaction;
}

export interface IBillEditingPayload {
  oldBill: Bill;
  billDTO: EditBillDto;
  trx: Knex.Transaction;
}
export interface IBillEditedPayload {
  oldBill: Bill;
  bill: Bill;
  billDTO: EditBillDto;
  trx?: Knex.Transaction;
}

export interface IBIllEventDeletedPayload {
  // tenantId: number;
  billId: number;
  oldBill: Bill;
  trx: Knex.Transaction;
}

export interface IBillEventDeletingPayload {
  // tenantId: number;
  oldBill: Bill;
  trx: Knex.Transaction;
}
export enum BillAction {
  Create = 'Create',
  Edit = 'Edit',
  Delete = 'Delete',
  View = 'View',
  NotifyBySms = 'NotifyBySms',
}

export interface IBillOpeningPayload {
  trx: Knex.Transaction;
  // tenantId: number;
  oldBill: Bill;
}

export interface IBillOpenedPayload {
  bill: Bill;
  oldBill: Bill;
  trx?: Knex.Transaction;
  // tenantId: number;
}
