# Changelog

All notable changes to the Parser-CRM API contract will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v1.0.0
- Initial OpenAPI 3.0 contract specification
- POST /api/integration/parser/organizations endpoint
- Organization schema with required and optional fields
- Partnership status enum (8 types)
- Request/response examples
- Validation guidelines

## Version Guidelines

### MAJOR Version (X.0.0)
**Breaking changes** - Requires coordinated deployment of Parser and CRM

Examples:
- Removing required fields
- Changing field types (string → integer)
- Renaming fields
- Removing enum values
- Changing endpoint URLs
- Removing endpoints

### MINOR Version (1.X.0)
**New features** - Backward-compatible additions

Examples:
- Adding optional fields
- Adding new enum values
- Adding new endpoints
- Expanding validation rules (making them less strict)

### PATCH Version (1.0.X)
**Bug fixes and documentation** - No code changes required

Examples:
- Fixing typos in descriptions
- Clarifying field descriptions
- Adding examples
- Improving documentation
- Correcting OpenAPI syntax errors

## Migration Guide Template

When releasing breaking changes (MAJOR version), include migration guide:

```markdown
## Migration from vX.0.0 to vY.0.0

### Breaking Changes
1. Field `old_name` renamed to `new_name`
2. Field `some_field` type changed from string to integer

### Required Actions

#### Parser Changes
- Update field name in sync data preparation
- Convert field type before sending

#### CRM Changes
- Update database schema (migration required)
- Update API endpoint validation
- Update validators

### Testing Checklist
- [ ] Parser sends data with new field names
- [ ] CRM accepts and validates new format
- [ ] Database migration tested
- [ ] Integration tests pass
- [ ] Production deployment plan ready

### Deployment Plan
1. Deploy CRM first (supports both old and new format)
2. Test CRM accepts old format
3. Deploy Parser (sends new format)
4. Test end-to-end sync
5. Monitor for 24 hours
6. Remove old format support from CRM
```

## Versioning Examples

### Adding Optional Field (MINOR)

**Before (v1.0.0):**
```yaml
organization:
  properties:
    name:
      type: string
    category:
      type: string
```

**After (v1.1.0):**
```yaml
organization:
  properties:
    name:
      type: string
    category:
      type: string
    founded_year:      # NEW optional field
      type: integer
```

**Impact:** Parser can optionally send, CRM accepts but doesn't require

### Removing Required Field (MAJOR)

**Before (v1.0.0):**
```yaml
organization:
  required:
    - name
    - category
    - address
```

**After (v2.0.0):**
```yaml
organization:
  required:
    - name
    - category
    # address removed from required
```

**Impact:** BREAKING - CRM must update validation, Parser must handle missing addresses

### Expanding Enum (MINOR)

**Before (v1.0.0):**
```yaml
partnership_status:
  enum:
    - partner
    - potential_partner
```

**After (v1.1.0):**
```yaml
partnership_status:
  enum:
    - partner
    - potential_partner
    - previously_cooperated  # NEW value
```

**Impact:** Parser can send new values, CRM must support them. Old values still valid.

## Notes

- **Release Date Format:** ISO 8601 (YYYY-MM-DD)
- **Changelog Updates:** Update this file before releasing new version
- **Git Tags:** Tag releases as `v1.0.0`, `v1.1.0`, etc.
- **Backward Compatibility:** Maintain for at least one MAJOR version
