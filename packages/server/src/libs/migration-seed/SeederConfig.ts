import { DEFAULT_LOAD_EXTENSIONS, FsMigrations } from './FsMigrations';

const CONFIG_DEFAULT = Object.freeze({
  extension: 'js',
  loadExtensions: DEFAULT_LOAD_EXTENSIONS,
  tableName: 'bigcapital_seeds',
  schemaName: null,
  directory: './migrations',
  disableTransactions: false,
  disableMigrationsListValidation: false,
  sortDirsSeparately: false,
});

export default function getMergedConfig(config, currentConfig) {
  // config is the user specified config, mergedConfig has defaults and current config
  // applied to it.
  const mergedConfig = {
    ...CONFIG_DEFAULT,
    ...(currentConfig || {}),
    ...config,
  };

  if (
    config &&
    // If user specifies any FS related config,
    // clear specified migrationSource to avoid ambiguity
    (config.directory ||
      config.sortDirsSeparately !== undefined ||
      config.loadExtensions)
  ) {
    mergedConfig.migrationSource = null;
  }

  // If the user has not specified any configs, we need to
  // default to fs migrations to maintain compatibility
  if (!mergedConfig.migrationSource) {
    mergedConfig.migrationSource = new FsMigrations(
      mergedConfig.directory,
      mergedConfig.sortDirsSeparately,
      mergedConfig.loadExtensions
    );
  }
  return mergedConfig;
}
