import * as request from 'supertest';
import { faker } from '@faker-js/faker';
import {
  app,
  authenticationToken,
  AuthorizationHeader,
  orgainzationId,
} from './init-app-test';

const makeItemRequest = () => ({
  name: faker.commerce.productName(),
  type: 'service',
});

describe('Items (e2e)', () => {
  it('/items (POST)', () => {
    return request(app.getHttpServer())
      .post('/items')
      .set('organization-id', orgainzationId)
      .set('Authorization', `Bearer ${authenticationToken}`)
      .send(makeItemRequest())
      .expect(201);
  });

  it('/items/:id (PUT)', async () => {
    const response = await request(app.getHttpServer())
      .post('/items')
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .send(makeItemRequest());
    const itemId = response.body.id;

    return request(app.getHttpServer())
      .put(`/items/${itemId}`)
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .send(makeItemRequest());
  });

  it('/items/:id/inactivate (PATCH)', async () => {
    const response = await request(app.getHttpServer())
      .post('/items')
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .send(makeItemRequest());
    const itemId = response.text;

    return request(app.getHttpServer())
      .patch(`/items/${itemId}/inactivate`)
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .expect(200);
  });

  it('/items/:id/activate (PATCH)', async () => {
    const response = await request(app.getHttpServer())
      .post('/items')
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .send(makeItemRequest());
    const itemId = response.text;

    return request(app.getHttpServer())
      .patch(`/items/${itemId}/activate`)
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .expect(200);
  });

  it('/items/:id (DELETE)', async () => {
    const response = await request(app.getHttpServer())
      .post('/items')
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .send(makeItemRequest());
    const itemId = response.text;

    return request(app.getHttpServer())
      .delete(`/items/${itemId}`)
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .expect(200);
  });

  it('/items/:id/invoices (GET)', async () => {
    const response = await request(app.getHttpServer())
      .post('/items')
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .send(makeItemRequest());

    const itemId = response.text;

    return request(app.getHttpServer())
      .get(`/items/${itemId}/invoices`)
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .expect(200);
  });

  it('/items/:id/bills (GET)', async () => {
    const response = await request(app.getHttpServer())
      .post('/items')
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .send(makeItemRequest());

    const itemId = response.text;

    return request(app.getHttpServer())
      .get(`/items/${itemId}/bills`)
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .expect(200);
  });

  it('/items/:id/estimates (GET)', async () => {
    const response = await request(app.getHttpServer())
      .post('/items')
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .send(makeItemRequest());

    const itemId = response.text;

    return request(app.getHttpServer())
      .get(`/items/${itemId}/estimates`)
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .expect(200);
  });

  it('/items/:id/receipts (GET)', async () => {
    const response = await request(app.getHttpServer())
      .post('/items')
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .send(makeItemRequest());

    const itemId = response.text;

    return request(app.getHttpServer())
      .get(`/items/${itemId}/receipts`)
      .set('organization-id', orgainzationId)
      .set('Authorization', AuthorizationHeader)
      .expect(200);
  });
});
