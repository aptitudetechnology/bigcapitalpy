import { Features } from '@/common/types/Features';
import { IFeatureConfiugration } from '@/common/types/Features';
import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class FeaturesConfigure {
  constructor(private readonly configService: ConfigService) {}

  /**
   * Get the feature configure.
   * @returns {IFeatureConfiugration[]}
   */

  getConfigure(): IFeatureConfiugration[] {
    return [
      {
        name: Features.BRANCHES,
        defaultValue: false,
      },
      {
        name: Features.WAREHOUSES,
        defaultValue: false,
      },
      {
        name: Features.BankSyncing,
        defaultValue: this.configService.get('bankfeed.enabled') ?? false,
      },
    ];
  }
}
