import { Transformer } from "../Transformer/Transformer";

export class CurrencyTransformer extends Transformer {
  /**
   * Include these attributes to sale invoice object.
   * @returns {Array}
   */
  public includeAttributes = (): string[] => {
    return ['isBaseCurrency'];
  };

  /**
   * Detarmines whether the currency is base currency.
   * @returns {boolean}
   */
  public isBaseCurrency(currency): boolean {
    return this.context.organization.baseCurrency === currency.currencyCode;
  }
}
