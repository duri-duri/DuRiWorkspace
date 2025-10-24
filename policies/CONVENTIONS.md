# Policy Verification Conventions

## Overview
This document defines the conventions and rules for policy verification in the auto-code loop system.

## Path Normalization Rules

1. **Repository Root**: All paths are normalized relative to the repository root
2. **Leading `./` Removal**: Leading `./` is automatically removed from paths
3. **Absolute Path Resolution**: Uses `realpath -m` for consistent path resolution
4. **Security Boundary**: All paths must be within the repository root (prevents directory traversal)

## Pattern Matching Rules

### Globstar Patterns (`**`)
- **0-Directory Support**: `docs/**/*.md` matches both `docs/file.md` and `docs/sub/file.md`
- **Recursive Matching**: `**` matches any number of directories (0 or more)
- **Fallback Logic**: If direct match fails, tries simplified pattern (`/ ** /` → `/`)

### Priority Order
1. **Blacklist First**: Blacklist patterns are checked before whitelist
2. **Whitelist Second**: Only files not in blacklist are checked against whitelist
3. **Default Deny**: Files not explicitly allowed are denied

### Pattern Format
- **Relative Paths Only**: All patterns must be relative to repository root
- **No Leading `./`**: Patterns should not start with `./`
- **Case Sensitivity**: Patterns are case-sensitive
- **Standard Glob**: Supports `*`, `?`, `**`, `[abc]` patterns

## Security Requirements

### Path Validation
- **Repository Boundary**: All files must be within repository root
- **Symbolic Link Protection**: Prevents access to files outside repository via symlinks
- **Directory Traversal Prevention**: Blocks `../` attempts to escape repository

### Input Validation
- **JSON Schema**: Plan files must conform to expected schema
- **Dependency Checks**: Required tools (`jq`, `realpath`) must be available
- **Environment Hardening**: Uses `LC_ALL=C` for consistent locale behavior

## Environment Requirements

### Required Tools
- `bash` 5.x or higher
- `jq` for JSON processing
- `realpath` (GNU coreutils) for path resolution
- `sha256sum` for policy checksums

### Environment Variables
- `LC_ALL=C`: Ensures consistent locale behavior
- `IFS=$'\n\t'`: Proper field separation for file lists

## Usage Examples

### Basic Verification
```bash
bash tools/policy_verify.sh --policy policies/auto_code_loop/gate_policy.yaml --plan logs/plan.json
```

### Debug Mode
```bash
bash tools/policy_verify.sh --policy policies/auto_code_loop/gate_policy.yaml --plan logs/plan.json --explain
```

### Dry Run
```bash
bash tools/policy_verify.sh --policy policies/auto_code_loop/gate_policy.yaml --plan logs/plan.json --dry-run
```

## Error Handling

### Exit Codes
- `0`: All files allowed
- `1`: Policy verification failed (some files denied)
- `2`: Invalid arguments or missing dependencies
- `3`: Invalid plan schema

### Error Messages
- `[DENY] outside repo: <path>`: File path outside repository boundary
- `[DENY] blacklisted: <path> (pattern: <pattern>)`: File matches blacklist pattern
- `[DENY] not whitelisted: <path>`: File not in whitelist
- `[ALLOW] <path> (pattern: <pattern>)`: File allowed by whitelist pattern

## Testing

### Regression Tests
Run comprehensive tests with:
```bash
bash tests/policy/test_policy_verify.sh
```

### Test Cases Covered
1. 0-directory globstar patterns
2. 1+ directory globstar patterns
3. Blacklist validation
4. Non-whitelisted file rejection
5. Security boundary enforcement
6. Unicode filename handling
7. Case sensitivity validation

## Maintenance

### Policy Updates
- Update patterns in `policies/auto_code_loop/gate_policy.yaml`
- Run regression tests after changes
- Update this document if conventions change

### Version Compatibility
- Policy format version is tracked in YAML
- Backward compatibility maintained within major versions
- Breaking changes require major version increment
