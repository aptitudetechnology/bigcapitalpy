import * as Multer from 'multer';
import * as path from 'path';
import { ServiceError } from '../Items/ServiceError';

export const getImportsStoragePath = () => {
  return path.join(global.__static_dirname, `/imports`);
};

export function allowSheetExtensions(req, file, cb) {
  if (
    file.mimetype !== 'text/csv' &&
    file.mimetype !== 'application/vnd.ms-excel' &&
    file.mimetype !==
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ) {
    cb(new ServiceError('IMPORTED_FILE_EXTENSION_INVALID'));
    return;
  }
  cb(null, true);
}

const storage = Multer.diskStorage({
  destination: function (req, file, cb) {
    const path = getImportsStoragePath();
    cb(null, path);
  },
  filename: function (req, file, cb) {
    // Add the creation timestamp to clean up temp files later.
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    cb(null, uniqueSuffix);
  },
});

export const uploadImportFileMulterOptions = {
  storage,
  limits: { fileSize: 5 * 1024 * 1024 },
  // fileFilter: allowSheetExtensions,
};