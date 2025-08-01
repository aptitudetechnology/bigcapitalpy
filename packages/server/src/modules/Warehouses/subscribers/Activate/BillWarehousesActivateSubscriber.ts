import { BillActivateWarehouses } from '../../Activate/BillWarehousesActivate';
import { OnEvent } from '@nestjs/event-emitter';
import { Injectable } from '@nestjs/common';
import { events } from '@/common/events/events';
import { IWarehousesActivatedPayload } from '../../Warehouse.types';

@Injectable()
export class BillsActivateWarehousesSubscriber {
  constructor(
    private readonly billsActivateWarehouses: BillActivateWarehouses,
  ) {}

  /**
   * Updates all inventory transactions with the primary warehouse once
   * multi-warehouses feature is activated.
   * @param {IWarehousesActivatedPayload}
   */
  @OnEvent(events.warehouse.onActivated)
  async  updateBillsWithWarehouseOnActivated ({
    primaryWarehouse,
  }: IWarehousesActivatedPayload) {
    await this.billsActivateWarehouses.updateBillsWithWarehouse(
      primaryWarehouse
    );
  };
}
