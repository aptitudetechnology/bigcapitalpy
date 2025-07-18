import * as moment from 'moment';
import { Inject, Injectable } from '@nestjs/common';
import { EventEmitter2 } from '@nestjs/event-emitter';
import { Knex } from 'knex';
import { SaleEstimate } from '../models/SaleEstimate';
import { events } from '@/common/events/events';
import { TenantModelProxy } from '@/modules/System/models/TenantBaseModel';

@Injectable()
export class ConvertSaleEstimate {
  constructor(
    private readonly eventPublisher: EventEmitter2,

    @Inject(SaleEstimate.name)
    private readonly saleEstimateModel: TenantModelProxy<typeof SaleEstimate>,
  ) {}

  /**
   * Converts estimate to invoice.
   * @param {number} estimateId -
   * @return {Promise<void>}
   */
  public async convertEstimateToInvoice(
    estimateId: number,
    invoiceId: number,
    trx?: Knex.Transaction,
  ): Promise<void> {
    // Retrieve details of the given sale estimate.
    const saleEstimate = await this.saleEstimateModel()
      .query()
      .findById(estimateId)
      .throwIfNotFound();

    // Marks the estimate as converted from the givne invoice.
    await this.saleEstimateModel().query(trx).where('id', estimateId).patch({
      convertedToInvoiceId: invoiceId,
      convertedToInvoiceAt: moment().toMySqlDateTime(),
    });

    // Triggers `onSaleEstimateConvertedToInvoice` event.
    await this.eventPublisher.emitAsync(
      events.saleEstimate.onConvertedToInvoice,
      {},
    );
  }
}
