import { Inject, Injectable } from '@nestjs/common';
import { Knex } from 'knex';
import { IBranchDeletedPayload, IBranchDeletePayload } from '../Branches.types';
import { BranchCommandValidator } from './BranchCommandValidator.service';
import { ERRORS } from '../constants';
import { Branch } from '../models/Branch.model';
import { UnitOfWork } from '../../Tenancy/TenancyDB/UnitOfWork.service';
import { EventEmitter2 } from '@nestjs/event-emitter';
import { events } from '@/common/events/events';
import { TenantModelProxy } from '@/modules/System/models/TenantBaseModel';

@Injectable()
export class DeleteBranchService {
  constructor(
    @Inject(Branch.name)
    private readonly branchModel: TenantModelProxy<typeof Branch>,
    private readonly uow: UnitOfWork,
    private readonly eventPublisher: EventEmitter2,
    private readonly validator: BranchCommandValidator,
  ) {}

  /**
   * Validates the branch deleting.
   * @param   {number} branchId
   * @returns {Promise<void>}
   */
  private authorize = async (branchId: number): Promise<void> => {
    await this.validator.validateBranchNotOnlyWarehouse(branchId);
  };

  /**
   * Deletes branch.
   * @param {number} branchId
   * @returns {Promise<void>}
   */
  public deleteBranch = async (branchId: number): Promise<void> => {
    // Retrieves the old branch or throw not found service error.
    const oldBranch = await this.branchModel()
      .query()
      .findById(branchId)
      .throwIfNotFound();

    // Authorize the branch before deleting.
    await this.authorize(branchId);

    // Deletes branch under unit-of-work.
    return this.uow.withTransaction(async (trx: Knex.Transaction) => {
      // Triggers `onBranchCreate` event.
      await this.eventPublisher.emitAsync(events.warehouse.onEdit, {
        oldBranch,
        trx,
      } as IBranchDeletePayload);

      await this.branchModel().query().findById(branchId).deleteIfNoRelations({
        type: ERRORS.BRANCH_HAS_ASSOCIATED_TRANSACTIONS,
        message: 'Branch has associated transactions',
      });
      // Triggers `onBranchCreate` event.
      await this.eventPublisher.emitAsync(events.warehouse.onEdited, {
        oldBranch,
        trx,
      } as IBranchDeletedPayload);
    });
  };
}
