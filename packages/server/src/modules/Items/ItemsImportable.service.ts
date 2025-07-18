import { Injectable } from '@nestjs/common';
import { Knex } from 'knex';
import { Importable } from '../Import/Importable';
import { CreateItemService } from './CreateItem.service';
import { CreateItemDto } from './dtos/Item.dto';
import { ItemsSampleData } from './Items.constants';
import { ImportableService } from '../Import/decorators/Import.decorator';
import { Item } from './models/Item';

@Injectable()
@ImportableService({ name: Item.name })
export class ItemsImportable extends Importable {
  constructor(
    private readonly createItemService: CreateItemService,
  ) {
    super();
  }

  /**
   * Mapps the imported data to create a new item service.
   * @param {CreateItemDto} createDTO
   * @param {Knex.Transaction} trx
   * @returns {Promise<void>}
   */
  public async importable(
    createDTO: CreateItemDto,
    trx?: Knex.Transaction<any, any[]>
  ): Promise<void> {
    await this.createItemService.createItem(createDTO, trx);
  }

  /**
   * Retrieves the sample data of customers used to download sample sheet.
   */
  public sampleData(): any[] {
    return ItemsSampleData;
  }
}