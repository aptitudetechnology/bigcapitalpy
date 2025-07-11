import { Model } from 'objection';
// import TenantModel from 'models/TenantModel';
import { BaseModel } from '@/models/Model';
import { Bill } from '@/modules/Bills/models/Bill';
import { BillPayment } from './BillPayment';

export class BillPaymentEntry extends BaseModel {
  public billPaymentId: number;
  public billId: number;
  public paymentAmount: number;
  public index: number;

  bill?: Bill;
  payment?: BillPayment;

  /**
   * Table name
   */
  static get tableName() {
    return 'bills_payments_entries';
  }

  /**
   * Timestamps columns.
   */
  get timestamps() {
    return [];
  }

  /**
   * Relationship mapping.
   */
  static get relationMappings() {
    const { Bill } = require('../../Bills/models/Bill');
    const { BillPayment } = require('../../BillPayments/models/BillPayment');

    return {
      payment: {
        relation: Model.BelongsToOneRelation,
        modelClass: BillPayment,
        join: {
          from: 'bills_payments_entries.billPaymentId',
          to: 'bills_payments.id',
        },
      },
      bill: {
        relation: Model.BelongsToOneRelation,
        modelClass: Bill,
        join: {
          from: 'bills_payments_entries.billId',
          to: 'bills.id',
        },
      },
    };
  }
}
