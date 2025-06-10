import {
  Body,
  Controller,
  Delete,
  Get,
  Param,
  Patch,
  Post,
  Put,
  Query,
} from '@nestjs/common';
import { ManualJournalsApplication } from './ManualJournalsApplication.service';
import { ApiOperation, ApiParam, ApiResponse, ApiTags } from '@nestjs/swagger';
import {
  CreateManualJournalDto,
  EditManualJournalDto,
} from './dtos/ManualJournal.dto';
import { IManualJournalsFilter } from './types/ManualJournals.types';

@Controller('manual-journals')
@ApiTags('manual-journals')
export class ManualJournalsController {
  constructor(private manualJournalsApplication: ManualJournalsApplication) {}

  @Post()
  @ApiOperation({ summary: 'Create a new manual journal.' })
  public createManualJournal(@Body() manualJournalDTO: CreateManualJournalDto) {
    return this.manualJournalsApplication.createManualJournal(manualJournalDTO);
  }

  @Put(':id')
  @ApiOperation({ summary: 'Edit the given manual journal.' })
  @ApiResponse({
    status: 200,
    description: 'The manual journal has been successfully edited.',
  })
  @ApiResponse({ status: 404, description: 'The manual journal not found.' })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The manual journal id',
  })
  public editManualJournal(
    @Param('id') manualJournalId: number,
    @Body() manualJournalDTO: EditManualJournalDto,
  ) {
    return this.manualJournalsApplication.editManualJournal(
      manualJournalId,
      manualJournalDTO,
    );
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Delete the given manual journal.' })
  @ApiResponse({
    status: 200,
    description: 'The manual journal has been successfully deleted.',
  })
  @ApiResponse({ status: 404, description: 'The manual journal not found.' })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The manual journal id',
  })
  public deleteManualJournal(@Param('id') manualJournalId: number) {
    return this.manualJournalsApplication.deleteManualJournal(manualJournalId);
  }

  @Patch(':id/publish')
  @ApiOperation({ summary: 'Publish the given manual journal.' })
  @ApiResponse({
    status: 200,
    description: 'The manual journal has been successfully published.',
  })
  @ApiResponse({ status: 404, description: 'The manual journal not found.' })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The manual journal id',
  })
  public publishManualJournal(@Param('id') manualJournalId: number) {
    return this.manualJournalsApplication.publishManualJournal(manualJournalId);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Retrieves the manual journal details.' })
  @ApiResponse({
    status: 200,
    description: 'The manual journal details have been successfully retrieved.',
  })
  @ApiResponse({ status: 404, description: 'The manual journal not found.' })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The manual journal id',
  })
  public getManualJournal(@Param('id') manualJournalId: number) {
    return this.manualJournalsApplication.getManualJournal(manualJournalId);
  }

  @Get()
  @ApiOperation({ summary: 'Retrieves the manual journals paginated list.' })
  @ApiResponse({
    status: 200,
    description: 'The manual journal details have been successfully retrieved.',
  })
  @ApiResponse({ status: 404, description: 'The manual journal not found.' })
  public getManualJournals(@Query() filterDto: Partial<IManualJournalsFilter>) {
    return this.manualJournalsApplication.getManualJournals(filterDto);
  }
}
