import { IsNotEmpty, IsString } from 'class-validator';

export class ExportQuery {
  @IsString()
  @IsNotEmpty()
  resource: string;
}
