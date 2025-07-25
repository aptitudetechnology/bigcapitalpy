import { Inject, Injectable } from '@nestjs/common';
import { Warehouse } from '../models/Warehouse.model';
import { TenantModelProxy } from '@/modules/System/models/TenantBaseModel';

@Injectable()
export class GetWarehouse {
  constructor(
    @Inject(Warehouse.name)
    private readonly warehouseModel: TenantModelProxy<typeof Warehouse>,
  ) {}
  /**
   * Retrieves warehouse details.
   * @param {number} warehouseId
   * @returns {Promise<IWarehouse>}
   */
  public getWarehouse = async (warehouseId: number) => {
    const warehouse = await this.warehouseModel()
      .query()
      .findById(warehouseId)
      .throwIfNotFound();

    return warehouse;
  };
}
