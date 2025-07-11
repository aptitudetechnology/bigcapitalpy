import * as request from 'supertest';
import { faker } from '@faker-js/faker';
import { app, AuthorizationHeader, orgainzationId } from './init-app-test';

describe('Item Categories(e2e)', () => {
  it('/item-categories (POST)', () => {
    return request(app.getHttpServer())
      .post('/item-categories')
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .send({
        name: faker.person.fullName(),
        description: faker.lorem.sentence(),
      })
      .expect(201);
  });

  it('/item-categories/:id (GET)', async () => {
    const response = await request(app.getHttpServer())
      .post('/item-categories')
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .send({
        name: faker.person.fullName(),
        description: faker.lorem.sentence(),
      });
    const itemCategoryId = response.body.id;

    return request(app.getHttpServer())
      .get(`/item-categories/${itemCategoryId}`)
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .expect(200);
  });

  it('/item-categories/:id (DELETE)', async () => {
    const response = await request(app.getHttpServer())
      .post('/item-categories')
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .send({
        name: faker.person.fullName(),
        description: faker.lorem.sentence(),
      });

    const itemCategoryId = response.body.id;

    return request(app.getHttpServer())
      .delete(`/item-categories/${itemCategoryId}`)
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .expect(200);
  });
});
