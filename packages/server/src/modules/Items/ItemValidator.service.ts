import { Inject, Injectable } from '@nestjs/common';
import {
  ACCOUNT_PARENT_TYPE,
  ACCOUNT_ROOT_TYPE,
  ACCOUNT_TYPE,
} from '@/constants/accounts';
import { ServiceError } from './ServiceError';
import { ERRORS } from './Items.constants';
import { Item } from './models/Item';
import { Account } from '../Accounts/models/Account.model';
import { TaxRateModel } from '../TaxRates/models/TaxRate.model';
import { ItemEntry } from '../TransactionItemEntry/models/ItemEntry';
import { ItemCategory } from '../ItemCategories/models/ItemCategory.model';
import { AccountTransaction } from '../Accounts/models/AccountTransaction.model';
import { InventoryAdjustment } from '../InventoryAdjutments/models/InventoryAdjustment';
import { TenantModelProxy } from '../System/models/TenantBaseModel';
import { CreateItemDto, EditItemDto } from './dtos/Item.dto';

@Injectable()
export class ItemsValidators {
  /**
   * @param {typeof Item} itemModel - The Item model.
   * @param {typeof Account} accountModel - The Account model.
   * @param {typeof TaxRateModel} taxRateModel - The TaxRateModel model.
   * @param {typeof ItemEntry} itemEntryModel - The ItemEntry model.
   * @param {typeof ItemCategory} itemCategoryModel - The ItemCategory model.
   * @param {typeof AccountTransaction} accountTransactionModel - The AccountTransaction model.
   * @param {typeof InventoryAdjustment} inventoryAdjustmentEntryModel - The InventoryAdjustment model.
   */
  constructor(
    @Inject(Item.name) private itemModel: TenantModelProxy<typeof Item>,

    @Inject(Account.name)
    private accountModel: TenantModelProxy<typeof Account>,

    @Inject(TaxRateModel.name)
    private taxRateModel: TenantModelProxy<typeof TaxRateModel>,

    @Inject(ItemEntry.name)
    private itemEntryModel: TenantModelProxy<typeof ItemEntry>,

    @Inject(ItemCategory.name)
    private itemCategoryModel: TenantModelProxy<typeof ItemCategory>,

    @Inject(AccountTransaction.name)
    private accountTransactionModel: TenantModelProxy<
      typeof AccountTransaction
    >,

    @Inject(InventoryAdjustment.name)
    private inventoryAdjustmentEntryModel: TenantModelProxy<
      typeof InventoryAdjustment
    >,
  ) {}

  /**
   * Validate wether the given item name already exists on the storage.
   * @param  {string} itemName
   * @param  {number} notItemId
   * @return {Promise<void>}
   */
  public async validateItemNameUniquiness(
    itemName: string,
    notItemId?: number,
  ): Promise<void> {
    const foundItems = await this.itemModel()
      .query()
      .onBuild((builder: any) => {
        builder.where('name', itemName);
        if (notItemId) {
          builder.whereNot('id', notItemId);
        }
      });

    if (foundItems.length > 0) {
      throw new ServiceError(
        ERRORS.ITEM_NAME_EXISTS,
        'The item name is already exist.',
      );
    }
  }

  /**
   * Validate item COGS account existance and type.
   * @param {number} costAccountId
   * @return {Promise<void>}
   */
  public async validateItemCostAccountExistance(
    costAccountId: number,
  ): Promise<void> {
    const foundAccount = await this.accountModel()
      .query()
      .findById(costAccountId);

    if (!foundAccount) {
      throw new ServiceError(ERRORS.COST_ACCOUNT_NOT_FOUMD);

      // Detarmines the cost of goods sold account.
    } else if (!foundAccount.isParentType(ACCOUNT_PARENT_TYPE.EXPENSE)) {
      throw new ServiceError(ERRORS.COST_ACCOUNT_NOT_COGS);
    }
  }

  /**
   * Validate item sell account existance and type.
   * @param {number} sellAccountId - Sell account id.
   */
  public async validateItemSellAccountExistance(sellAccountId: number) {
    const foundAccount = await this.accountModel()
      .query()
      .findById(sellAccountId);

    if (!foundAccount) {
      throw new ServiceError(ERRORS.SELL_ACCOUNT_NOT_FOUND);
    } else if (!foundAccount.isParentType(ACCOUNT_ROOT_TYPE.INCOME)) {
      throw new ServiceError(ERRORS.SELL_ACCOUNT_NOT_INCOME);
    }
  }

  /**
   * Validates income account existance.
   * @param {number|null} sellable - Detarmines if the item sellable.
   * @param {number|null} incomeAccountId - Income account id.
   * @throws {ServiceError(ERRORS.INCOME_ACCOUNT_REQUIRED_WITH_SELLABLE_ITEM)}
   */
  public validateIncomeAccountExistance(
    sellable?: boolean,
    incomeAccountId?: number,
  ) {
    if (sellable && !incomeAccountId) {
      throw new ServiceError(
        ERRORS.INCOME_ACCOUNT_REQUIRED_WITH_SELLABLE_ITEM,
        'Income account is require with sellable item.',
      );
    }
  }

  /**
   * Validates the cost account existance.
   * @param {boolean|null} purchasable - Detarmines if the item purchasble.
   * @param {number|null} costAccountId - Cost account id.
   * @throws {ServiceError(ERRORS.COST_ACCOUNT_REQUIRED_WITH_PURCHASABLE_ITEM)}
   */
  public validateCostAccountExistance(
    purchasable: boolean,
    costAccountId?: number,
  ) {
    if (purchasable && !costAccountId) {
      throw new ServiceError(
        ERRORS.COST_ACCOUNT_REQUIRED_WITH_PURCHASABLE_ITEM,
        'The cost account is required with purchasable item.',
      );
    }
  }

  /**
   * Validate item inventory account existance and type.
   * @param {number} inventoryAccountId
   */
  public async validateItemInventoryAccountExistance(
    inventoryAccountId: number,
  ) {
    const foundAccount = await this.accountModel()
      .query()
      .findById(inventoryAccountId);

    if (!foundAccount) {
      throw new ServiceError(ERRORS.INVENTORY_ACCOUNT_NOT_FOUND);
    } else if (!foundAccount.isAccountType(ACCOUNT_TYPE.INVENTORY)) {
      throw new ServiceError(ERRORS.INVENTORY_ACCOUNT_NOT_INVENTORY);
    }
  }

  /**
   * Validate item category existance.
   * @param {number} itemCategoryId
   */
  public async validateItemCategoryExistance(itemCategoryId: number) {
    const foundCategory = await this.itemCategoryModel()
      .query()
      .findById(itemCategoryId);

    if (!foundCategory) {
      throw new ServiceError(ERRORS.ITEM_CATEOGRY_NOT_FOUND);
    }
  }

  /**
   * Validates the given item or items have no associated invoices or bills.
   * @param  {number|number[]} itemId - Item id.
   * @throws {ServiceError}
   */
  public async validateHasNoInvoicesOrBills(itemId: number[] | number) {
    const ids = Array.isArray(itemId) ? itemId : [itemId];
    const foundItemEntries = await this.itemEntryModel()
      .query()
      .whereIn('item_id', ids);

    if (foundItemEntries.length > 0) {
      throw new ServiceError(
        ids.length > 1
          ? ERRORS.ITEMS_HAVE_ASSOCIATED_TRANSACTIONS
          : ERRORS.ITEM_HAS_ASSOCIATED_TRANSACTINS,
      );
    }
  }

  /**
   * Validates the given item has no associated inventory adjustment transactions.
   * @param {number} itemId -
   */
  public async validateHasNoInventoryAdjustments(
    itemId: number[] | number,
  ): Promise<void> {
    const itemsIds = Array.isArray(itemId) ? itemId : [itemId];
    const inventoryAdjEntries = await this.inventoryAdjustmentEntryModel()
      .query()
      .whereIn('item_id', itemsIds);

    if (inventoryAdjEntries.length > 0) {
      throw new ServiceError(ERRORS.ITEM_HAS_ASSOCIATED_INVENTORY_ADJUSTMENT);
    }
  }

  /**
   * Validates edit item type from service/non-inventory to inventory.
   * Should item has no any relations with accounts transactions.
   * @param {number} itemId - Item id.
   */
  public async validateEditItemTypeToInventory(
    oldItem: Item,
    newItemDTO: CreateItemDto | EditItemDto,
  ) {
    // We have no problem in case the item type not modified.
    if (newItemDTO.type === oldItem.type || oldItem.type === 'inventory') {
      return;
    }
    // Retrieve all transactions that associated to the given item id.
    const itemTransactionsCount = await this.accountTransactionModel()
      .query()
      .where('item_id', oldItem.id)
      .count('item_id', { as: 'transactions' })
      .first();

    // @ts-ignore
    if (itemTransactionsCount.transactions > 0) {
      throw new ServiceError(
        ERRORS.TYPE_CANNOT_CHANGE_WITH_ITEM_HAS_TRANSACTIONS,
      );
    }
  }

  /**
   * Validate the item inventory account whether modified and item
   * has associated inventory transactions.
   * @param {Item} oldItem - Old item.
   * @param {CreateItemDto | EditItemDto} newItemDTO - New item DTO.
   * @returns {Promise<void>}
   */
  async validateItemInvnetoryAccountModified(
    oldItem: Item,
    newItemDTO: CreateItemDto | EditItemDto,
  ) {
    if (
      newItemDTO.type !== 'inventory' ||
      oldItem.inventoryAccountId === newItemDTO.inventoryAccountId
    ) {
      return;
    }
    // Inventory transactions associated to the given item id.
    const transactions = await this.accountTransactionModel().query().where({
      itemId: oldItem.id,
    });
    // Throw the service error in case item has associated inventory transactions.
    if (transactions.length > 0) {
      throw new ServiceError(ERRORS.INVENTORY_ACCOUNT_CANNOT_MODIFIED);
    }
  }

  /**
   * Validate edit item type from inventory to another type that not allowed.
   * @param {CreateItemDto | EditItemDto} itemDTO - Item DTO.
   * @param {IItem} oldItem - Old item.
   */
  public validateEditItemFromInventory(
    itemDTO: CreateItemDto | EditItemDto,
    oldItem: Item,
  ) {
    if (
      itemDTO.type &&
      oldItem.type === 'inventory' &&
      itemDTO.type !== oldItem.type
    ) {
      throw new ServiceError(ERRORS.ITEM_CANNOT_CHANGE_INVENTORY_TYPE);
    }
  }

  /**
   * Validate the purchase tax rate id existance.
   * @param {number} taxRateId - Tax rate id.
   */
  public async validatePurchaseTaxRateExistance(taxRateId: number) {
    const foundTaxRate = await this.taxRateModel().query().findById(taxRateId);

    if (!foundTaxRate) {
      throw new ServiceError(ERRORS.PURCHASE_TAX_RATE_NOT_FOUND);
    }
  }

  /**
   * Validate the sell tax rate id existance.
   * @param {number} taxRateId - Tax rate id.
   */
  public async validateSellTaxRateExistance(taxRateId: number) {
    const foundTaxRate = await this.taxRateModel().query().findById(taxRateId);

    if (!foundTaxRate) {
      throw new ServiceError(ERRORS.SELL_TAX_RATE_NOT_FOUND);
    }
  }
}
