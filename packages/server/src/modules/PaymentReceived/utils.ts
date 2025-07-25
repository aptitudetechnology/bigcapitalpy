// @ts-nocheck
import { PaymentReceived } from './models/PaymentReceived';
import {
  PaymentReceivedPdfTemplateAttributes,
} from './types/PaymentReceived.types';
import { contactAddressTextFormat } from '@/utils/address-text-format';

export const transformPaymentReceivedToPdfTemplate = (
  payment: PaymentReceived
): Partial<PaymentReceivedPdfTemplateAttributes> => {
  return {
    total: payment.formattedAmount,
    subtotal: payment.subtotalFormatted,
    paymentReceivedNumebr: payment.paymentReceiveNo,
    paymentReceivedDate: payment.formattedPaymentDate,
    customerName: payment.customer.displayName,
    lines: payment.entries.map((entry) => ({
      invoiceNumber: entry.invoice.invoiceNo,
      invoiceAmount: entry.invoice.totalFormatted,
      paidAmount: entry.paymentAmountFormatted,
    })),
    customerAddress: contactAddressTextFormat(payment.customer),
  };
};

export const transformPaymentReceivedToMailDataArgs = (payment: any) => {
  return {
    'Customer Name': payment.customer.displayName,
    'Payment Number': payment.paymentReceiveNo,
    'Payment Date': payment.formattedPaymentDate,
    'Payment Amount': payment.formattedAmount,
  };
};
