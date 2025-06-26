import { Injectable } from '@nestjs/common';
import { Knex } from 'knex';
import { CreateVendorService } from './commands/CreateVendor.service';
import { EditVendorService } from './commands/EditVendor.service';
import { DeleteVendorService } from './commands/DeleteVendor.service';
import { EditOpeningBalanceVendorService } from './commands/EditOpeningBalanceVendor.service';
import { GetVendorService } from './queries/GetVendor';
import {
  IVendorOpeningBalanceEditDTO,
  IVendorsFilter,
} from './types/Vendors.types';
import { GetVendorsService } from './queries/GetVendors.service';
import { CreateVendorDto } from './dtos/CreateVendor.dto';
import { EditVendorDto } from './dtos/EditVendor.dto';
import { GetVendorsQueryDto } from './dtos/GetVendorsQuery.dto';

@Injectable()
export class VendorsApplication {
  constructor(
    private createVendorService: CreateVendorService,
    private editVendorService: EditVendorService,
    private deleteVendorService: DeleteVendorService,
    private editOpeningBalanceService: EditOpeningBalanceVendorService,
    private getVendorService: GetVendorService,
    private getVendorsService: GetVendorsService,
  ) {}

  /**
   * Creates a new vendor.
   * @param  {IVendorNewDTO} vendorDTO
   * @return {Promise<void>}
   */
  public createVendor(vendorDTO: CreateVendorDto, trx?: Knex.Transaction) {
    return this.createVendorService.createVendor(vendorDTO, trx);
  }

  /**
   * Edits details of the given vendor.
   * @param {number} vendorId -
   * @param {IVendorEditDTO} vendorDTO -
   * @returns {Promise<IVendor>}
   */
  public editVendor(vendorId: number, vendorDTO: EditVendorDto) {
    return this.editVendorService.editVendor(vendorId, vendorDTO);
  }

  /**
   * Deletes the given vendor.
   * @param {number} vendorId
   * @return {Promise<void>}
   */
  public deleteVendor(vendorId: number) {
    return this.deleteVendorService.deleteVendor(vendorId);
  }

  /**
   * Changes the opening balance of the given customer.
   * @param   {number} vendorId
   * @param   {IVendorOpeningBalanceEditDTO} openingBalanceEditDTO
   * @returns {Promise<IVendor>}
   */
  public editOpeningBalance(
    vendorId: number,
    openingBalanceEditDTO: IVendorOpeningBalanceEditDTO,
  ) {
    return this.editOpeningBalanceService.editOpeningBalance(
      vendorId,
      openingBalanceEditDTO,
    );
  }

  /**
   * Retrieves the vendor details.
   * @param {number} vendorId - Vendor ID.
   * @returns
   */
  public getVendor(vendorId: number) {
    return this.getVendorService.getVendor(vendorId);
  }

  /**
   * Retrieves the vendors paginated list.
   * @param {Partial<IVendorsFilter>} filterDTO
   * @returns {Promise<{ vendors: Vendor[], pagination: IPaginationMeta, filterMeta: IFilterMeta }>>}
   */
  public getVendors(filterDTO: GetVendorsQueryDto) {
    return this.getVendorsService.getVendorsList(filterDTO);
  }
}
