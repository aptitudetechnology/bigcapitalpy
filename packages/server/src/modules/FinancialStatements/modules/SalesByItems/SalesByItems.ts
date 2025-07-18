import { get, sumBy } from 'lodash';
import * as R from 'ramda';
import {
  ISalesByItemsReportQuery,
  ISalesByItemsItem,
  ISalesByItemsTotal,
  ISalesByItemsSheetData,
} from './SalesByItems.types';
import { ModelObject } from 'objection';
import { FinancialSheet } from '../../common/FinancialSheet';
import { Item } from '@/modules/Items/models/Item';
import { transformToMap } from '@/utils/transform-to-key';
import { allPassedConditionsPass } from '@/utils/all-conditions-passed';
import { InventoryTransaction } from '@/modules/InventoryCost/models/InventoryTransaction';

export class SalesByItemsReport extends FinancialSheet {
  readonly baseCurrency: string;
  readonly items: Item[];
  readonly itemsTransactions: Map<number, ModelObject<InventoryTransaction>[]>;
  readonly query: ISalesByItemsReportQuery;

  /**
   * Constructor method.
   * @param {ISalesByItemsReportQuery} query
   * @param {IItem[]} items
   * @param {IAccountTransaction[]} itemsTransactions
   * @param {string} baseCurrency
   */
  constructor(
    query: ISalesByItemsReportQuery,
    items: Item[],
    itemsTransactions: ModelObject<InventoryTransaction>[],
    baseCurrency: string,
  ) {
    super();

    this.baseCurrency = baseCurrency;
    this.items = items;
    this.itemsTransactions = transformToMap(itemsTransactions, 'itemId');
    this.query = query;
    this.numberFormat = this.query.numberFormat;
  }

  /**
   * Retrieve the item purchase item, cost and average cost price.
   * @param {number} itemId - Item id.
   */
  getItemTransaction(itemId: number): {
    quantity: number;
    cost: number;
    average: number;
  } {
    const transaction = this.itemsTransactions.get(itemId);

    const quantity = get(transaction, 'quantity', 0);
    const cost = get(transaction, 'cost', 0);

    const average = cost / quantity;

    return { quantity, cost, average };
  }

  /**
   * Mapping the given item section.
   * @param {ISalesByItemsItem} item
   * @returns
   */
  private itemSectionMapper = (item: Item): ISalesByItemsItem => {
    const meta = this.getItemTransaction(item.id);

    return {
      id: item.id,
      name: item.name,
      code: item.code,
      quantitySold: meta.quantity,
      soldCost: meta.cost,
      averageSellPrice: meta.average,
      quantitySoldFormatted: this.formatNumber(meta.quantity, {
        money: false,
      }),
      soldCostFormatted: this.formatNumber(meta.cost),
      averageSellPriceFormatted: this.formatNumber(meta.average),
      currencyCode: this.baseCurrency,
    };
  };

  /**
   * Detarmines whether the given sale node is has transactions.
   * @param {ISalesByItemsItem} node -
   * @returns {boolean}
   */
  private filterSaleNoneTransactions = (node: ISalesByItemsItem) => {
    return this.itemsTransactions.get(node.id);
  };

  /**
   * Detarmines whether the given sale by item node is active.
   * @param {ISalesByItemsItem} node
   * @returns {boolean}
   */
  private filterSaleOnlyActive = (node: ISalesByItemsItem): boolean => {
    return node.quantitySold !== 0 || node.soldCost !== 0;
  };

  /**
   * Filters sales by items nodes based on the report query.
   * @param {ISalesByItemsItem} saleItem -
   * @return {boolean}
   */
  private itemSaleFilter = (saleItem: ISalesByItemsItem): boolean => {
    const { noneTransactions, onlyActive } = this.query;

    const conditions = [
      [noneTransactions, this.filterSaleNoneTransactions],
      [onlyActive, this.filterSaleOnlyActive],
    ];
    return allPassedConditionsPass(conditions)(saleItem);
  };

  /**
   * Mappes the given items to sales by items nodes.
   * @param {IItem[]} items -
   * @returns {ISalesByItemsItem[]}
   */
  private itemsMapper = (items: Item[]): ISalesByItemsItem[] => {
    return items.map(this.itemSectionMapper);
  };

  /**
   * Filters sales by items sections.
   * @param items
   * @returns
   */
  private itemsFilters = (nodes: ISalesByItemsItem[]): ISalesByItemsItem[] => {
    return nodes.filter(this.itemSaleFilter);
  };

  /**
   * Retrieve the items sections.
   * @returns {ISalesByItemsItem[]}
   */
  private itemsSection(): ISalesByItemsItem[] {
    return R.compose(this.itemsFilters, this.itemsMapper)(this.items);
  }

  /**
   * Retrieve the total section of the sheet.
   * @param {IInventoryValuationItem[]} items
   * @returns {IInventoryValuationTotal}
   */
  private totalSection(items: ISalesByItemsItem[]): ISalesByItemsTotal {
    const quantitySold = sumBy(items, (item) => item.quantitySold);
    const soldCost = sumBy(items, (item) => item.soldCost);

    return {
      quantitySold,
      soldCost,
      quantitySoldFormatted: this.formatTotalNumber(quantitySold, {
        money: false,
      }),
      soldCostFormatted: this.formatTotalNumber(soldCost),
      currencyCode: this.baseCurrency,
    };
  }

  /**
   * Retrieve the sheet data.
   * @returns {ISalesByItemsSheetData}
   */
  public reportData(): ISalesByItemsSheetData {
    const items = this.itemsSection();
    const total = this.totalSection(items);

    return { items, total };
  }
}
