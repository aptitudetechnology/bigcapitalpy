import { Controller, Get, Headers, Query, Res } from '@nestjs/common';
import { Response } from 'express';
import { AcceptType } from '@/constants/accept-type';
import { JournalSheetApplication } from './JournalSheetApplication';
import {
  ApiOperation,
  ApiProduces,
  ApiResponse,
  ApiTags,
} from '@nestjs/swagger';
import { JournalSheetQueryDto } from './JournalSheetQuery.dto';

@Controller('/reports/journal')
@ApiTags('Reports')
export class JournalSheetController {
  constructor(private readonly journalSheetApp: JournalSheetApplication) {}

  @Get('/')
  @ApiResponse({ status: 200, description: 'Journal report' })
  @ApiOperation({ summary: 'Journal report' })
  @ApiProduces(
    AcceptType.ApplicationJson,
    AcceptType.ApplicationJsonTable,
    AcceptType.ApplicationPdf,
    AcceptType.ApplicationXlsx,
    AcceptType.ApplicationCsv,
  )
  async journalSheet(
    @Query() query: JournalSheetQueryDto,
    @Res({ passthrough: true }) res: Response,
    @Headers('accept') acceptHeader: string,
  ) {
    // Retrieves the json table format.
    if (acceptHeader.includes(AcceptType.ApplicationJsonTable)) {
      return this.journalSheetApp.table(query);

      // Retrieves the csv format.
    } else if (acceptHeader.includes(AcceptType.ApplicationCsv)) {
      const buffer = await this.journalSheetApp.csv(query);

      res.setHeader('Content-Disposition', 'attachment; filename=output.csv');
      res.setHeader('Content-Type', 'text/csv');

      res.send(buffer);
      // Retrieves the xlsx format.
    } else if (acceptHeader.includes(AcceptType.ApplicationXlsx)) {
      const buffer = await this.journalSheetApp.xlsx(query);

      res.setHeader('Content-Disposition', 'attachment; filename=output.xlsx');
      res.setHeader(
        'Content-Type',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      );
      res.send(buffer);
      // Retrieves the json format.
    } else if (acceptHeader.includes(AcceptType.ApplicationPdf)) {
      const pdfContent = await this.journalSheetApp.pdf(query);

      res.set({
        'Content-Type': 'application/pdf',
        'Content-Length': pdfContent.length,
      });
      res.send(pdfContent);
    } else {
      return this.journalSheetApp.sheet(query);
    }
  }
}
