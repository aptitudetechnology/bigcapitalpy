import {
  Controller,
  Post,
  Get,
  Delete,
  Param,
  Body,
  Res,
  Next,
  HttpStatus,
  ParseIntPipe,
} from '@nestjs/common';
import { Response, NextFunction } from 'express';
import { CreateRoleDto, EditRoleDto } from './dtos/Role.dto';
import { RolesApplication } from './Roles.application';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiParam,
  ApiBody,
  getSchemaPath,
  ApiExtraModels,
} from '@nestjs/swagger';
import { RoleResponseDto } from './dtos/RoleResponse.dto';

@ApiTags('Roles')
@Controller('roles')
@ApiExtraModels(RoleResponseDto)
export class RolesController {
  constructor(private readonly rolesApp: RolesApplication) {}

  @Post()
  @ApiOperation({ summary: 'Create a new role' })
  @ApiBody({ type: CreateRoleDto })
  @ApiResponse({
    status: HttpStatus.OK,
    description: 'Role created successfully',
  })
  async createRole(
    @Next() next: NextFunction,
    @Body() createRoleDto: CreateRoleDto,
  ) {
    const role = await this.rolesApp.createRole(createRoleDto);

    return {
      data: { roleId: role.id },
      message: 'The role has been created successfully.',
    };
  }

  @Post(':id')
  @ApiOperation({ summary: 'Edit an existing role' })
  @ApiParam({ name: 'id', description: 'Role ID' })
  @ApiBody({ type: EditRoleDto })
  @ApiResponse({
    status: HttpStatus.OK,
    description: 'Role updated successfully',
  })
  async editRole(
    @Param('id', ParseIntPipe) roleId: number,
    @Body() editRoleDto: EditRoleDto,
  ) {
    const role = await this.rolesApp.editRole(roleId, editRoleDto);

    return {
      data: { roleId },
      message: 'The given role has been updated successfully.',
    };
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Delete a role' })
  @ApiParam({ name: 'id', description: 'Role ID' })
  @ApiResponse({
    status: HttpStatus.OK,
    description: 'Role deleted successfully',
  })
  async deleteRole(@Param('id', ParseIntPipe) roleId: number) {
    await this.rolesApp.deleteRole(roleId);

    return {
      data: { roleId },
      message: 'The given role has been deleted successfully.',
    };
  }

  @Get('permissions/schema')
  @ApiOperation({ summary: 'Get role permissions schema' })
  @ApiResponse({
    status: HttpStatus.OK,
    description: 'Role permissions schema',
  })
  async getRolePermissionsSchema() {
    const schema = this.rolesApp.getRolePermissionsSchema();

    return schema;
  }

  @Get()
  @ApiOperation({ summary: 'Get all roles' })
  @ApiResponse({
    status: HttpStatus.OK,
    description: 'List of all roles',
    schema: {
      type: 'array',
      items: { $ref: getSchemaPath(RoleResponseDto) },
    },
  })
  async getRoles() {
    const roles = await this.rolesApp.getRoles();

    return roles;
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get a specific role by ID' })
  @ApiParam({ name: 'id', description: 'Role ID' })
  @ApiResponse({
    status: HttpStatus.OK,
    description: 'Role details',
    schema: {
      $ref: getSchemaPath(RoleResponseDto),
    },
  })
  async getRole(@Param('id', ParseIntPipe) roleId: number) {
    const role = await this.rolesApp.getRole(roleId);

    return role;
  }
}
