import { Injectable } from '@nestjs/common';
import * as xlsx from 'xlsx';
import * as R from 'ramda';
import { get } from 'lodash';
import { sanitizeResourceName } from '../Import/_utils';
import { Errors, ExportFormat } from './common';
import { flatDataCollections, getDataAccessor } from './utils';
import { ExportPdf } from './ExportPdf';
import { ExportAls } from './ExportAls';
import { IModelMeta, IModelMetaColumn } from '@/interfaces/Model';
import { ServiceError } from '../Items/ServiceError';
import { ResourceService } from '../Resource/ResourceService';
import { getExportableService } from './decorators/ExportableModel.decorator';
import { ContextIdFactory, ModuleRef } from '@nestjs/core';

@Injectable()
export class ExportResourceService {
  constructor(
    private readonly exportAls: ExportAls,
    private readonly exportPdf: ExportPdf,
    private readonly resourceService: ResourceService,
    private readonly moduleRef: ModuleRef,
  ) {}

  /**
   * @param {string} resourceName
   * @param {ExportFormat} format
   * @returns
   */
  public async export(
    resourceName: string,
    format: ExportFormat = ExportFormat.Csv,
  ) {
    return this.exportAls.run(() => this.exportAlsRun(resourceName, format));
  }

  /**
   * Exports the given resource data through csv, xlsx or pdf.
   * @param {string} resourceName - Resource name.
   * @param {ExportFormat} format - File format.
   */
  public async exportAlsRun(
    resourceName: string,
    format: ExportFormat = ExportFormat.Csv,
  ) {
    const resource = sanitizeResourceName(resourceName);
    const resourceMeta = this.getResourceMeta(resource);

    const resourceColumns = this.resourceService.getResourceColumns(resource);
    this.validateResourceMeta(resourceMeta);

    const data = await this.getExportableData(resource);
    const transformed = this.transformExportedData(resource, data);

    // Returns the csv, xlsx format.
    if (format === ExportFormat.Csv || format === ExportFormat.Xlsx) {
      const exportableColumns = this.getExportableColumns(resourceColumns);
      const workbook = this.createWorkbook(transformed, exportableColumns);

      return this.exportWorkbook(workbook, format);
      // Returns the pdf format.
    } else if (format === ExportFormat.Pdf) {
      const printableColumns = this.getPrintableColumns(resourceMeta);

      return this.exportPdf.pdf(
        printableColumns,
        transformed,
        resourceMeta?.print?.pageTitle,
      );
    }
  }

  /**
   * Retrieves metadata for a specific resource.
   * @param {number} tenantId - The tenant identifier.
   * @param {string} resource - The name of the resource.
   * @returns The metadata of the resource.
   */
  private getResourceMeta(resource: string) {
    return this.resourceService.getResourceMeta(resource);
  }

  /**
   * Validates if the resource metadata is exportable.
   * @param {any} resourceMeta - The metadata of the resource.
   * @throws {ServiceError} If the resource is not exportable or lacks columns.
   */
  private validateResourceMeta(resourceMeta: any) {
    if (!resourceMeta.exportable || !resourceMeta.columns) {
      throw new ServiceError(Errors.RESOURCE_NOT_EXPORTABLE);
    }
  }

  /**
   * Transforms the exported data based on the resource metadata.
   * If the resource metadata specifies a flattening attribute (`exportFlattenOn`),
   * the data will be flattened based on this attribute using the `flatDataCollections` utility function.
   * @param {string} resource - The name of the resource.
   * @param {Array<Record<string, any>>} data - The original data to be transformed.
   * @returns {Array<Record<string, any>>} - The transformed data.
   */
  private transformExportedData(
    resource: string,
    data: Array<Record<string, any>>,
  ): Array<Record<string, any>> {
    const resourceMeta = this.getResourceMeta(resource);

    return R.when<Array<Record<string, any>>, Array<Record<string, any>>>(
      R.always(Boolean(resourceMeta.exportFlattenOn)),
      (data) => flatDataCollections(data, resourceMeta.exportFlattenOn),
      data,
    );
  }
  /**
   * Fetches exportable data for a given resource.
   * @param {number} tenantId - The tenant identifier.
   * @param {string} resource - The name of the resource.
   * @returns A promise that resolves to the exportable data.
   */
  private async getExportableData(resource: string) {
    const exportable = getExportableService(resource);
    const contextId = ContextIdFactory.create();
    const exportableInstance = await this.moduleRef.resolve(
      exportable,
      contextId,
      { strict: false },
    );
    return exportableInstance.exportable({});
  }

  /**
   * Extracts columns that are marked as exportable from the resource metadata.
   * @param {IModelMeta} resourceMeta - The metadata of the resource.
   * @returns An array of exportable columns.
   */
  private getExportableColumns(resourceColumns: any) {
    const processColumns = (
      columns: { [key: string]: IModelMetaColumn },
      parent = '',
    ) => {
      return Object.entries(columns)
        .filter(([_, value]) => value.exportable !== false)
        .flatMap(([key, value]) => {
          if (value.type === 'collection' && value.collectionOf === 'object') {
            return processColumns(value.columns, key);
          } else {
            const group = parent;
            return [
              {
                name: value.name,
                type: value.type || 'text',
                accessor: value.accessor || key,
                group,
              },
            ];
          }
        });
    };
    return processColumns(resourceColumns);
  }

  private getPrintableColumns(resourceMeta: IModelMeta) {
    const processColumns = (
      columns: { [key: string]: IModelMetaColumn },
      parent = '',
    ) => {
      return Object.entries(columns)
        // @ts-expect-error
        .filter(([_, value]) => value.printable !== false)
        .flatMap(([key, value]) => {
          if (value.type === 'collection' && value.collectionOf === 'object') {
            return processColumns(value.columns, key);
          } else {
            const group = parent;
            return [
              {
                name: value.name,
                type: value.type || 'text',
                accessor: value.accessor || key,
                group,
              },
            ];
          }
        });
    };
    return processColumns(resourceMeta.columns);
  }

  /**
   * Creates a workbook from the provided data and columns.
   * @param {any[]} data - The data to be included in the workbook.
   * @param {any[]} exportableColumns - The columns to be included in the workbook.
   * @returns The created workbook.
   */
  private createWorkbook(data: any[], exportableColumns: any[]) {
    const workbook = xlsx.utils.book_new();
    const worksheetData = data.map((item) =>
      exportableColumns.map((col) => get(item, getDataAccessor(col))),
    );
    worksheetData.unshift(exportableColumns.map((col) => col.name));

    const worksheet = xlsx.utils.aoa_to_sheet(worksheetData);
    xlsx.utils.book_append_sheet(workbook, worksheet, 'Exported Data');

    return workbook;
  }

  /**
   * Exports the workbook in the specified format.
   * @param {any} workbook - The workbook to be exported.
   * @param {string} format - The format to export the workbook in.
   * @returns The exported workbook data.
   */
  private exportWorkbook(workbook: any, format: string) {
    if (format.toLowerCase() === 'csv') {
      return xlsx.write(workbook, { type: 'buffer', bookType: 'csv' });
    } else if (format.toLowerCase() === 'xlsx') {
      return xlsx.write(workbook, { type: 'buffer', bookType: 'xlsx' });
    }
  }
}
