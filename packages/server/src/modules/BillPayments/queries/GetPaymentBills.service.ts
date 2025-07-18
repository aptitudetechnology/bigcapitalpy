import { Inject, Injectable } from '@nestjs/common';
import { Bill } from '@/modules/Bills/models/Bill';
import { BillPayment } from '../models/BillPayment';
import { TenantModelProxy } from '@/modules/System/models/TenantBaseModel';

@Injectable()
export class GetPaymentBills {
  /**
   * @param {typeof Bill} billModel
   * @param {typeof BillPayment} billPaymentModel
   */
  constructor(
    @Inject(Bill.name)
    private readonly billModel: TenantModelProxy<typeof Bill>,

    @Inject(BillPayment.name)
    private readonly billPaymentModel: TenantModelProxy<typeof BillPayment>,
  ) {}

  /**
   * Retrieve payment made associated bills.
   * @param {number} billPaymentId - Bill payment id.
   */
  public async getPaymentBills(billPaymentId: number) {
    const billPayment = await this.billPaymentModel()
      .query()
      .findById(billPaymentId)
      .throwIfNotFound();

    const paymentBillsIds = billPayment.entries.map((entry) => entry.id);

    const bills = await this.billModel().query().whereIn('id', paymentBillsIds);

    return bills;
  }
}
