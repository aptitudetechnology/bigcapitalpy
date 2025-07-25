import { Response } from 'express';
import {
  Body,
  Controller,
  Delete,
  Get,
  Headers,
  HttpCode,
  Param,
  ParseIntPipe,
  Post,
  Put,
  Query,
  Res,
} from '@nestjs/common';
import {
  ISaleInvoiceWriteoffDTO,
  ISalesInvoicesFilter,
  SaleInvoiceMailState,
  SendInvoiceMailDTO,
} from './SaleInvoice.types';
import { SaleInvoiceApplication } from './SaleInvoices.application';
import {
  ApiOperation,
  ApiParam,
  ApiQuery,
  ApiResponse,
  ApiTags,
  ApiExtraModels,
  getSchemaPath,
} from '@nestjs/swagger';
import {
  CreateSaleInvoiceDto,
  EditSaleInvoiceDto,
} from './dtos/SaleInvoice.dto';
import { AcceptType } from '@/constants/accept-type';
import { SaleInvoiceResponseDto } from './dtos/SaleInvoiceResponse.dto';
import { PaginatedResponseDto } from '@/common/dtos/PaginatedResults.dto';
import { SaleInvoiceStateResponseDto } from './dtos/SaleInvoiceState.dto';
import { GenerateSaleInvoiceSharableLinkResponseDto } from './dtos/generateSaleInvoiceSharableLinkResponse.dto';
import { ApiCommonHeaders } from '@/common/decorators/ApiCommonHeaders';

@Controller('sale-invoices')
@ApiTags('Sale Invoices')
@ApiExtraModels(SaleInvoiceResponseDto)
@ApiExtraModels(PaginatedResponseDto)
@ApiExtraModels(SaleInvoiceStateResponseDto)
@ApiExtraModels(GenerateSaleInvoiceSharableLinkResponseDto)
@ApiCommonHeaders()
export class SaleInvoicesController {
  constructor(private saleInvoiceApplication: SaleInvoiceApplication) {}

  @Post()
  @ApiOperation({ summary: 'Create a new sale invoice.' })
  @ApiResponse({
    status: 201,
    description: 'Sale invoice created successfully',
  })
  createSaleInvoice(@Body() saleInvoiceDTO: CreateSaleInvoiceDto) {
    return this.saleInvoiceApplication.createSaleInvoice(saleInvoiceDTO);
  }

  @Put(':id/mail')
  @ApiOperation({ summary: 'Send the sale invoice mail.' })
  @ApiResponse({
    status: 200,
    description: 'Sale invoice mail sent successfully',
  })
  @ApiResponse({ status: 404, description: 'The sale invoice not found.' })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The sale invoice id',
  })
  sendSaleInvoiceMail(
    @Param('id', ParseIntPipe) id: number,
    @Body() messageDTO: SendInvoiceMailDTO,
  ) {
    return this.saleInvoiceApplication.sendSaleInvoiceMail(id, messageDTO);
  }

  @Put(':id')
  @ApiOperation({ summary: 'Edit the given sale invoice.' })
  @ApiResponse({
    status: 200,
    description: 'Sale invoice edited successfully',
  })
  @ApiResponse({ status: 404, description: 'The sale invoice not found.' })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The sale invoice id',
  })
  editSaleInvoice(
    @Param('id', ParseIntPipe) id: number,
    @Body() saleInvoiceDTO: EditSaleInvoiceDto,
  ) {
    return this.saleInvoiceApplication.editSaleInvoice(id, saleInvoiceDTO);
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Delete the given sale invoice.' })
  @ApiResponse({
    status: 200,
    description: 'The sale invoice has been successfully deleted.',
  })
  @ApiResponse({ status: 404, description: 'The sale invoice not found.' })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The sale invoice id',
  })
  deleteSaleInvoice(@Param('id', ParseIntPipe) id: number) {
    return this.saleInvoiceApplication.deleteSaleInvoice(id);
  }

  @Get('receivable')
  @ApiOperation({ summary: 'Retrieves the receivable sale invoices.' })
  @ApiResponse({
    status: 200,
    description:
      'The receivable sale invoices have been successfully retrieved.',
  })
  @ApiResponse({ status: 404, description: 'The customer not found.' })
  @ApiQuery({
    name: 'customerId',
    required: false,
    type: Number,
    description: 'The customer id',
  })
  getReceivableSaleInvoices(@Query('customerId') customerId?: number) {
    return this.saleInvoiceApplication.getReceivableSaleInvoices(customerId);
  }

  @Get('state')
  @ApiOperation({ summary: 'Retrieves the sale invoice state.' })
  @ApiResponse({
    status: 200,
    description: 'The sale invoice state has been successfully retrieved.',
    schema: {
      $ref: getSchemaPath(SaleInvoiceStateResponseDto),
    },
  })
  @ApiResponse({ status: 404, description: 'The sale invoice not found.' })
  getSaleInvoiceState() {
    return this.saleInvoiceApplication.getSaleInvoiceState();
  }

  @Get(':id')
  @ApiOperation({ summary: 'Retrieves the sale invoice details.' })
  @ApiResponse({
    status: 200,
    description: 'The sale invoice details have been successfully retrieved.',
    schema: {
      $ref: getSchemaPath(SaleInvoiceResponseDto),
    },
  })
  @ApiResponse({ status: 404, description: 'The sale invoice not found.' })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The sale invoice id',
  })
  async getSaleInvoice(
    @Param('id', ParseIntPipe) id: number,
    @Headers('accept') acceptHeader: string,
    @Res({ passthrough: true }) res: Response,
  ) {
    if (acceptHeader.includes(AcceptType.ApplicationPdf)) {
      const pdfContent = await this.saleInvoiceApplication.saleInvoicePdf(id);

      res.set({
        'Content-Type': 'application/pdf',
        'Content-Length': pdfContent.length,
      });
      res.send(pdfContent);
    } else if (acceptHeader.includes(AcceptType.ApplicationTextHtml)) {
      const htmlContent = await this.saleInvoiceApplication.saleInvoiceHtml(id);
      return { htmlContent };
    } else {
      return this.saleInvoiceApplication.getSaleInvoice(id);
    }
  }

  @Get()
  @ApiOperation({ summary: 'Retrieves the sale invoices.' })
  @ApiResponse({
    status: 200,
    description: 'The sale invoices have been successfully retrieved.',
    schema: {
      allOf: [
        { $ref: getSchemaPath(PaginatedResponseDto) },
        {
          properties: {
            data: {
              type: 'array',
              items: { $ref: getSchemaPath(SaleInvoiceResponseDto) },
            },
          },
        },
      ],
    },
  })
  getSaleInvoices(@Query() filterDTO: Partial<ISalesInvoicesFilter>) {
    return this.saleInvoiceApplication.getSaleInvoices(filterDTO);
  }

  @Put(':id/deliver')
  @ApiOperation({ summary: 'Deliver the given sale invoice.' })
  @ApiResponse({
    status: 200,
    description: 'The sale invoice has been successfully marked asdelivered.',
  })
  @ApiResponse({ status: 404, description: 'The sale invoice not found.' })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The sale invoice id',
  })
  @HttpCode(200)
  deliverSaleInvoice(@Param('id', ParseIntPipe) id: number) {
    return this.saleInvoiceApplication.deliverSaleInvoice(id);
  }

  @Post(':id/writeoff')
  @ApiOperation({ summary: 'Write off the given sale invoice.' })
  @HttpCode(200)
  @ApiResponse({
    status: 200,
    description: 'The sale invoice has been successfully written off.',
  })
  @ApiResponse({ status: 404, description: 'The sale invoice not found.' })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The sale invoice id',
  })
  writeOff(
    @Param('id', ParseIntPipe) id: number,
    @Body() writeoffDTO: ISaleInvoiceWriteoffDTO,
  ) {
    return this.saleInvoiceApplication.writeOff(id, writeoffDTO);
  }

  @Post(':id/cancel-writeoff')
  @ApiOperation({ summary: 'Cancel the written off sale invoice.' })
  @ApiResponse({
    status: 200,
    description:
      'The sale invoice has been successfully marked as not written off.',
  })
  @ApiResponse({ status: 404, description: 'The sale invoice not found.' })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The sale invoice id',
  })
  @HttpCode(200)
  cancelWrittenoff(@Param('id', ParseIntPipe) id: number) {
    return this.saleInvoiceApplication.cancelWrittenoff(id);
  }

  @Get(':id/payments')
  @ApiOperation({ summary: 'Retrieves the sale invoice payments.' })
  @ApiResponse({ status: 404, description: 'The sale invoice not found.' })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The sale invoice id',
  })
  getInvoicePayments(@Param('id', ParseIntPipe) id: number) {
    return this.saleInvoiceApplication.getInvoicePayments(id);
  }

  @Get(':id/html')
  @ApiOperation({ summary: 'Retrieves the sale invoice HTML.' })
  @ApiResponse({ status: 404, description: 'The sale invoice not found.' })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The sale invoice id',
  })
  saleInvoiceHtml(@Param('id', ParseIntPipe) id: number) {
    return this.saleInvoiceApplication.saleInvoiceHtml(id);
  }

  @Get(':id/mail')
  @ApiOperation({ summary: 'Retrieves the sale invoice mail state.' })
  @ApiResponse({
    status: 200,
    description: 'Sale invoice mail state retrieved successfully',
  })
  @ApiResponse({ status: 404, description: 'The sale invoice not found.' })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The sale invoice id',
  })
  getSaleInvoiceMailState(
    @Param('id', ParseIntPipe) id: number,
  ): Promise<SaleInvoiceMailState> {
    return this.saleInvoiceApplication.getSaleInvoiceMailState(id);
  }

  @Post(':id/generate-link')
  @ApiOperation({
    summary: 'Generate sharable sale invoice link (private or public)',
  })
  @ApiResponse({
    status: 201,
    description: 'The link has been generated successfully.',
    schema: {
      $ref: getSchemaPath(GenerateSaleInvoiceSharableLinkResponseDto),
    },
  })
  @ApiParam({
    name: 'id',
    required: true,
    type: Number,
    description: 'The sale invoice id',
  })
  generateSaleInvoiceSharableLink(@Param('id', ParseIntPipe) id: number) {
    return this.saleInvoiceApplication.generateSaleInvoiceSharableLink(id);
  }
}
