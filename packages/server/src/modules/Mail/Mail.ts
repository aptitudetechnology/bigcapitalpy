import * as fs from 'fs';
import * as Mustache from 'mustache';
import * as path from 'path';
import { IMailAttachment } from './Mail.types';

export class Mail {
  view: string;
  subject: string = '';
  content: string = '';
  to: string | string[];
  cc: string | string[];
  bcc: string | string[];
  replyTo: string | string[];
  from: string = `${process.env.MAIL_FROM_NAME} ${process.env.MAIL_FROM_ADDRESS}`;
  data: { [key: string]: string | number };
  attachments: IMailAttachment[];

  /**
   * Mail options.
   */
  public get mailOptions() {
    return {
      to: this.to,
      from: this.from,
      cc: this.cc,
      bcc: this.bcc,
      subject: this.subject,
      html: this.html,
      attachments: this.attachments,
      replyTo: this.replyTo,
    };
  }

  /**
   * Retrieves the html content of the mail.
   * @returns {string}
   */
  public get html() {
    return this.view ? Mail.render(this.view, this.data) : this.content;
  }

  /**
   * Set send mail to address.
   * @param {string} to -
   */
  setTo(to: string | string[]) {
    this.to = to;
    return this;
  }

  setCC(cc: string | string[]) {
    this.cc = cc;
    return this;
  }

  setBCC(bcc: string | string[]) {
    this.bcc = bcc;
    return this;
  }

  setReplyTo(replyTo: string | string[]) {
    this.replyTo = replyTo;
    return this;
  }

  /**
   * Sets from address to the mail.
   * @param {string} from
   * @return {}
   */
  setFrom(from: string) {
    this.from = from;
    return this;
  }

  /**
   * Set attachments to the mail.
   * @param {IMailAttachment[]} attachments
   * @returns {Mail}
   */
  setAttachments(attachments: IMailAttachment[]) {
    this.attachments = attachments;
    return this;
  }

  /**
   * Set mail subject.
   * @param {string} subject
   */
  setSubject(subject: string) {
    this.subject = subject;
    return this;
  }

  /**
   * Set view directory.
   * @param {string} view
   */
  setView(view: string) {
    this.view = view;
    return this;
  }

  setData(data) {
    this.data = data;
    return this;
  }

  setContent(content: string) {
    this.content = content;
    return this;
  }

  /**
   * Renders the view template with the given data.
   * @param  {object} data
   * @return {string}
   */
  static render(view: string, data: Record<string, any>): string {
    const viewContent = Mail.getViewContent(view);
    return Mustache.render(viewContent, data);
  }

  /**
   * Retrieve view content from the view directory.
   */
  static getViewContent(view: string): string {
    const filePath = path.join(__dirname, '../../..', `static/${view}`);
    return fs.readFileSync(filePath, 'utf8');
  }
}
