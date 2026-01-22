# Changelog

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0]

### Added

- **Tools**:
  - `listEntities()` - Browse the DX software catalog with pagination and filtering
  - `getEntityDetails()` - Get comprehensive entity information including tasks and scorecards

### Environment Variables

- Catalog related tools require `WEB_API_TOKEN` environment variable

## [1.0.0] - Initial Release

### Added

- Initial release with `queryData()` tool for SQL queries against DX Data Cloud

### Environment Variables

- Requires `DB_URL` environment variable for database connections