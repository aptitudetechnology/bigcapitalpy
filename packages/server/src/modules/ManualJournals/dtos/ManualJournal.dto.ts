import { ToNumber } from '@/common/decorators/Validators';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Type } from 'class-transformer';
import {
  IsArray,
  IsBoolean,
  IsDate,
  IsDateString,
  IsInt,
  IsNotEmpty,
  IsNumber,
  IsOptional,
  IsPositive,
  IsString,
  MaxLength,
  Min,
  ValidateNested,
} from 'class-validator';

export class ManualJournalEntryDto {
  @ApiProperty({ description: 'Entry index' })
  @IsInt()
  index: number;

  @ApiPropertyOptional({ description: 'Credit amount' })
  @ToNumber()
  @IsOptional()
  @IsNumber()
  @Min(0)
  credit?: number;

  @ApiPropertyOptional({ description: 'Debit amount' })
  @ToNumber()
  @IsOptional()
  @IsNumber()
  @Min(0)
  debit?: number;

  @ApiProperty({ description: 'Account ID' })
  @IsNotEmpty()
  @IsInt()
  accountId: number;

  @ApiPropertyOptional({ description: 'Entry note' })
  @IsOptional()
  @IsString()
  note?: string;

  @ApiPropertyOptional({ description: 'Contact ID' })
  @ToNumber()
  @IsInt()
  @IsOptional()
  contactId?: number;

  @ApiPropertyOptional({ description: 'Branch ID' })
  @ToNumber()
  @IsOptional()
  @IsInt()
  branchId?: number;

  @ApiPropertyOptional({ description: 'Project ID' })
  @ToNumber()
  @IsOptional()
  @IsInt()
  projectId?: number;
}

class AttachmentDto {
  @ApiProperty({ description: 'Attachment key' })
  @IsString()
  key: string;
}

export class CommandManualJournalDto {
  @ApiProperty({ description: 'Journal date' })
  @IsDateString()
  date: Date;

  @ApiPropertyOptional({ description: 'Currency code' })
  @IsOptional()
  @IsString()
  currencyCode?: string;

  @ApiPropertyOptional({ description: 'Exchange rate' })
  @ToNumber()
  @IsOptional()
  @IsNumber()
  @IsPositive()
  exchangeRate?: number;

  @ApiPropertyOptional({ description: 'Journal number' })
  @IsOptional()
  @IsString()
  @MaxLength(255)
  journalNumber?: string;

  @ApiPropertyOptional({ description: 'Journal type' })
  @IsOptional()
  @IsString()
  @MaxLength(255)
  journalType?: string;

  @ApiPropertyOptional({ description: 'Reference' })
  @IsOptional()
  @IsString()
  @MaxLength(255)
  reference?: string;

  @ApiPropertyOptional({ description: 'Description' })
  @IsOptional()
  @IsString()
  description?: string;

  @ApiPropertyOptional({ description: 'Branch ID' })
  @ToNumber()
  @IsOptional()
  @IsInt()
  branchId?: number;

  @ApiPropertyOptional({ description: 'Publish status' })
  @IsOptional()
  @IsBoolean()
  publish?: boolean;

  @ApiProperty({ description: 'Journal entries', type: [ManualJournalEntryDto] })
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => ManualJournalEntryDto)
  entries: ManualJournalEntryDto[];

  @ApiPropertyOptional({ description: 'Attachments', type: [AttachmentDto] })
  @IsOptional()
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => AttachmentDto)
  attachments?: AttachmentDto[];  
}

export class CreateManualJournalDto extends CommandManualJournalDto {}
export class EditManualJournalDto extends CommandManualJournalDto {}