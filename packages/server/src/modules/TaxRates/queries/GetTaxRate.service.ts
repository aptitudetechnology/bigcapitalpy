import { Inject, Injectable } from '@nestjs/common';
import { TransformerInjectable } from '@/modules/Transformer/TransformerInjectable.service';
import { TaxRateTransformer } from './TaxRate.transformer';
import { TaxRateModel } from '../models/TaxRate.model';
import { CommandTaxRatesValidators } from '../commands/CommandTaxRatesValidator.service';
import { TenantModelProxy } from '@/modules/System/models/TenantBaseModel';

@Injectable()
export class GetTaxRateService {
  /**
   * @param {typeof TaxRateModel} taxRateModel - The tax rate model.
   * @param {CommandTaxRatesValidators} validators - The tax rates validators.
   * @param {TransformerInjectable} transformer - The transformer.
   */
  constructor(
    @Inject(TaxRateModel.name)
    private readonly taxRateModel: TenantModelProxy<typeof TaxRateModel>,
    private readonly validators: CommandTaxRatesValidators,
    private readonly transformer: TransformerInjectable,
  ) {}

  /**
   * Retrieves the given tax rate.
   * @param {number} taxRateId
   * @returns {Promise<ITaxRate>}
   */
  public async getTaxRate(taxRateId: number) {
    const taxRate = await this.taxRateModel().query().findById(taxRateId);

    // Validates the tax rate existance.
    this.validators.validateTaxRateExistance(taxRate);

    // Transforms the tax rate.
    return this.transformer.transform(taxRate, new TaxRateTransformer());
  }
}
