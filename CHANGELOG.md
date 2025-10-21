# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Critical**: Resolved Python stdlib `logging` module shadowing issue
  - Renamed `duri_core/core/logging.py` to `duri_core/core/log_utils.py`
  - Deleted `duri_common/logging.py` to prevent module conflicts
  - Updated all import paths to use `log_utils` instead of `logging`
  - Added Dockerfile build-time verification to ensure stdlib logging is used
  - This fixes `AttributeError: module 'logging' has no attribute 'StreamHandler'` errors

### Added
- **CI/CD**: Added GitHub Actions workflow to prevent logging module shadowing
  - Automatically checks for `logging.py` files and `logging/` directories
  - Tests stdlib logging module availability
  - Prevents future shadowing issues
- **Testing**: Added `test_logging_shadowing.py` to verify stdlib logging functionality
- **Documentation**: Added `DEVELOPMENT_GUIDELINES.md` with module naming restrictions
- **Redis**: Enhanced Redis persistence with AOF (Append Only File) enabled
  - Added `--appendonly yes` and `--appendfsync everysec` configuration
  - Improved data durability and recovery capabilities

### Changed
- **Docker**: Updated `docker-compose.yml` to use unified Redis volume naming
  - Consolidated multiple Redis volumes into single `duriworkspace_duri_redis_data`
  - Improved volume management and reduced confusion
- **Docker**: Added build-time verification guards in `Dockerfile.core`
  - Ensures stdlib logging module is properly loaded during container builds
  - Prevents runtime errors caused by module shadowing

### Security
- **Module Safety**: Implemented comprehensive module shadowing prevention
  - Prevents accidental override of Python standard library modules
  - Reduces risk of runtime errors and security vulnerabilities

## [Previous Versions]

### [2025-10-21] - Initial Release
- Initial DuRi AI workspace setup
- Core services: duri_core, duri_brain, duri_evolution, duri_control
- PostgreSQL and Redis database integration
- Docker containerization and orchestration
