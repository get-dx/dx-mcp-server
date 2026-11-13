# Changelog

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0]

### Added

- **Tools**:
  - `getSnapshotComments()` - Driver comments for a snapshot, newest first, with commenter identities removed
  - `compareSnapshotScores()` - Compare DXI, driver, or workflow scores between two snapshots, matched by id, with the change, direction, and distance from the p50 benchmark computed server-side
- **Skills**:
  - `snapshot-summary` - Summarizes the latest completed snapshot against the previous one. Served as `skill://snapshot-summary/SKILL.md`. Uses `compareSnapshotScores()` for the arithmetic and includes examples, common issues, and a description with team and negative triggers
- **Prompts**:
  - `summarizeSnapshot` - Runs the `snapshot-summary` skill, with an optional `team` argument

### Changed

- Requires `fastmcp>=4.1.1` (was `>=2.14.3`) for the skills provider that serves `skill://` resources

## [1.4.0]

### Added

- **Tools**:
  - `listSnapshots()` - List completed snapshots with participation counts
  - `listSnapshotBranches()` - List snapshot branches
  - `listSnapshotTeams()` - List the teams captured in a snapshot with manager and hierarchy fields
  - `getSnapshotScores()` - Aggregate driver, workflow, impact, CSAT, DXI, or allocation scores for a snapshot, filterable by teams, snapshot teams, groups, attributes, and branches
  - `getSnapshotScoresBreakdown()` - Break a single score down by snapshot team, group, branch, or attribute value

## [1.3.0]

### Changed

- **Performance Improvements**:
  - Updated default pagination limits from 50 to 20 for `listEntities()`, `listInitiatives()`, `getInitiativeDetails()`, and `listScorecards()` for better performance/reduced payload size
  - Added `search_term` parameter to `listEntities()` tool to enable efficient entity search and discovery
  - Updated `reviewTasks` prompt to encourage use of the new search functionality

## [1.2.0]

### Added

- **Tools**:
  - `listTeams()` - List all teams in DX
  - `getTeamDetails()` - Retrieve details for an individual team by team_id, reference_id, or team_emails
  - `listInitiatives()` - List all initiatives with summary information and filtering options
  - `getInitiativeDetails()` - Get comprehensive initiative details including info and progress report
  - `listScorecards()` - List all active scorecards with pagination
  - `getScorecardInfo()` - Retrieve detailed scorecard information including levels and checks
  - `reviewTasks()` - Tool for reviewing and resolving outstanding DX tasks/failing checks

- **Prompts**:
  - `reviewTasks` - Comprehensive workflow prompt for identifying, analyzing, and resolving failing DX scorecard checks with EXECUTE/PLAN/BLOCKED decision framework

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
