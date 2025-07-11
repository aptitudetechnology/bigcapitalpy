import { mixin, Model, raw } from 'objection';
// import TenantModel from 'models/TenantModel';
// import ModelSearchable from './ModelSearchable';
// import SoftDeleteQueryBuilder from '@/collection/SoftDeleteQueryBuilder';
// import TaxRateMeta from './TaxRate.settings';
// import ModelSetting from './ModelSetting';
import { BaseModel } from '@/models/Model';
import { ExportableModel } from '@/modules/Export/decorators/ExportableModel.decorator';

@ExportableModel()
export class TaxRateModel extends BaseModel {
  active!: boolean;
  code!: string;
  name!: string;
  rate!: number;
  description?: string;

  /**
   * Table name
   */
  static get tableName() {
    return 'tax_rates';
  }

  /**
   * Soft delete query builder.
   */
  // static get QueryBuilder() {
  // return SoftDeleteQueryBuilder;
  // }

  /**
   * Timestamps columns.
   */
  get timestamps() {
    return ['createdAt', 'updatedAt'];
  }

  /**
   * Retrieves the tax rate meta.
   */
  // static get meta() {
  // return TaxRateMeta;
  // }

  /**
   * Virtual attributes.
   */
  static get virtualAttributes() {
    return [];
  }

  /**
   * Model modifiers.
   */
  static get modifiers() {
    return {};
  }

  /**
   * Relationship mapping.
   */
  static get relationMappings() {
    return {};
  }
}
