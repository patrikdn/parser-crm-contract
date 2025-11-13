# Parser-CRM Contract

**Public API Contract** for data exchange between Yandex Maps Parser and CRM system.

**Status:** 📝 Design Phase
**Version:** 1.0.0 (not yet released)
**Format:** OpenAPI 3.0.3

## Repository

- **GitHub:** https://github.com/patrikdn/parser-crm-contract.git
- **Visibility:** 🌍 Public
- **Branch:** main
- **First Release:** 2025-11-13 (ab20d02)
- **Clone:** `git clone https://github.com/patrikdn/parser-crm-contract.git`

## Overview

This repository contains the **OpenAPI 3.0 specification** that defines the contract for synchronizing organization data from Parser to CRM. Both systems validate their data against this contract to ensure compatibility.

## Purpose

- **Single Source of Truth**: One canonical definition of data structures
- **Contract-First Development**: Define API before implementing
- **Automatic Validation**: Both systems validate against this spec
- **Version Control**: Semantic versioning with changelog
- **Documentation**: Auto-generated API docs from spec

## Architecture

```
┌───────────────┐                  ┌─────────────────────┐                  ┌─────────────┐
│    Parser     │                  │  parser-crm-contract │                  │     CRM     │
│               │                  │                     │                  │             │
│  Celery Beat  │ ── Validate ──▶  │  openapi-contract   │ ◀── Validate ─── │   REST API  │
│  (every 5min) │     outgoing     │     .yaml           │      incoming    │             │
│               │                  │                     │                  │             │
│  Send Data ───┼──────────────────┼─────────────────────┼──────────────────▶ Receive    │
│               │   POST /api/     │   Version: 1.0.0    │   Validate +     │    Data     │
│               │   integration/   │                     │   Store          │             │
└───────────────┘   organizations  └─────────────────────┘                  └─────────────┘
```

## Contract Files

### Primary Contract
- **openapi-contract.yaml** - OpenAPI 3.0 specification

### Supporting Files
- **CHANGELOG.md** - Version history and changes
- **examples/** - Request/response examples
- **validators/** - Validation scripts for both systems
- **schemas/** - Reusable JSON schemas

## Data Model

### Organization Object

**Required fields:**
- `external_id` (UUID v7) - Unique identifier, time-ordered
- `name` (string) - Organization name
- `category` (string) - Business category

**Optional fields:**
- `address` (string) - Full address
- `district_id` (integer) - Moscow district ID
- `phones` (array of strings) - Phone numbers
- `emails` (array of strings) - Email addresses
- `website` (string, URL) - Website
- `social_media` (object) - Social media links
- `yandex_url` (string, URL) - Yandex Maps URL
- `rating` (number, 0-5) - Rating
- `review_count` (integer) - Number of reviews
- `description` (string) - Full description
- `working_hours` (string) - Working hours
- `partnership_status` (enum) - Partner status

**Metadata (read-only):**
- `last_synced_at` (datetime) - Last sync timestamp from Parser

### Partnership Status Enum

```yaml
partnership_status:
  type: string
  enum:
    - partner                    # Партнер
    - potential_partner          # Потенциальный партнер
    - previously_cooperated      # Ранее сотрудничали
    - low_cost                   # Лоу Кост
    - high_cost                  # Хай Кост
    - not_interested             # Не заинтересованы
    - gov_schools_gardens        # Гос. школы и сады
    - gov_children_centers       # Гос. детские центры
```

## API Endpoint

### Import Organization

**Endpoint:**
```
POST /api/integration/parser/organizations
```

**Request:**
```json
{
  "external_id": "01934c8e-7890-7abc-def0-123456789012",
  "name": "Кафе Пушкин",
  "category": "Кафе",
  "address": "Москва, Тверской бульвар, 26А",
  "district_id": 5,
  "phones": ["+7 495 123-45-67", "+7 495 765-43-21"],
  "emails": ["info@cafe-pushkin.ru"],
  "website": "https://cafe-pushkin.ru",
  "social_media": {
    "instagram": "https://instagram.com/cafepushkin",
    "vk": "https://vk.com/cafepushkin"
  },
  "yandex_url": "https://yandex.ru/maps/org/123456",
  "rating": 4.7,
  "review_count": 342,
  "partnership_status": "partner",
  "last_synced_at": "2025-11-11T12:34:56Z"
}
```

**Response (Success - 200):**
```json
{
  "status": "success",
  "operation": "created",
  "organization_id": 123,
  "external_id": "01934c8e-7890-7abc-def0-123456789012"
}
```

**Response (Updated - 200):**
```json
{
  "status": "success",
  "operation": "updated",
  "organization_id": 123,
  "external_id": "01934c8e-7890-7abc-def0-123456789012"
}
```

**Response (Validation Error - 422):**
```json
{
  "detail": [
    {
      "loc": ["body", "external_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Versioning

**Semantic Versioning:** MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backward-compatible)
- **PATCH**: Bug fixes (backward-compatible)

### Version History

- **1.0.0** (Planned) - Initial release
  - Basic organization import endpoint
  - Core fields: external_id, name, category, contact info
  - 8 partnership status types

### Upgrading Between Versions

**When MAJOR version changes:**
- Both Parser and CRM must update simultaneously
- Database migrations may be required
- Testing required before production deployment

**When MINOR version changes:**
- New optional fields added
- Backward-compatible with previous MINOR versions
- Update at convenience

**When PATCH version changes:**
- Documentation fixes, clarifications
- No code changes required

## Validation

### Parser-Side Validation (Outgoing)

Before sending data to CRM, Parser validates:

```python
from app.services.contract_validator import ContractValidator

validator = ContractValidator(contract_version="1.0.0")

# Validate organization data
is_valid, errors = validator.validate_organization(org_data)

if not is_valid:
    logger.error(f"Contract validation failed: {errors}")
    # Don't send to CRM, log to sync_history
else:
    # Send to CRM
    response = crm_client.import_organization(org_data)
```

### CRM-Side Validation (Incoming)

CRM validates incoming requests:

```python
from app.services.contract_validator import ContractValidator
from fastapi import HTTPException

@router.post("/integration/parser/organizations")
async def import_organization(data: dict):
    validator = ContractValidator(contract_version="1.0.0")
    is_valid, errors = validator.validate_organization(data)

    if not is_valid:
        raise HTTPException(status_code=422, detail=errors)

    # Process validated data
    # ...
```

## Usage Examples

See `examples/` directory for:

- `create-organization.json` - Create new organization
- `update-organization.json` - Update existing organization
- `minimal-organization.json` - Minimal required fields only
- `full-organization.json` - All fields populated

## Testing

### Validate Against Contract

```bash
# Install validator
pip install openapi-spec-validator

# Validate OpenAPI spec
openapi-spec-validator openapi-contract.yaml

# Test with example data
python validators/validate_example.py examples/create-organization.json
```

### Contract Tests

Both Parser and CRM should have integration tests that validate against this contract:

**Parser test:**
```python
def test_sync_data_matches_contract():
    """Test that sync data matches contract schema"""
    org = create_test_organization()
    sync_data = prepare_sync_data(org)

    validator = ContractValidator()
    is_valid, errors = validator.validate_organization(sync_data)

    assert is_valid, f"Contract validation failed: {errors}"
```

**CRM test:**
```python
def test_api_endpoint_validates_contract():
    """Test that API endpoint accepts valid contract data"""
    valid_payload = load_example("create-organization.json")

    response = client.post("/api/integration/parser/organizations", json=valid_payload)

    assert response.status_code == 200
```

## Contributing

### Making Changes to Contract

1. **Create feature branch:**
   ```bash
   git checkout -b feature/add-new-field
   ```

2. **Edit openapi-contract.yaml:**
   - Add new fields
   - Update descriptions
   - Add examples

3. **Update CHANGELOG.md:**
   - Document all changes
   - Increment version number

4. **Validate spec:**
   ```bash
   openapi-spec-validator openapi-contract.yaml
   ```

5. **Update examples:**
   - Add examples for new fields
   - Update existing examples if needed

6. **Create pull request:**
   - Describe changes
   - Note version impact (MAJOR/MINOR/PATCH)
   - Get approval from both Parser and CRM teams

7. **Merge and tag:**
   ```bash
   git tag -a v1.1.0 -m "Add social_media field"
   git push origin v1.1.0
   ```

### Breaking Changes

**CRITICAL:** Breaking changes require coordination:

1. Announce breaking change in advance
2. Create migration guide
3. Update both Parser and CRM code
4. Test integration thoroughly
5. Deploy both systems simultaneously

## Implementation Checklist

### Parser Implementation
- [ ] Contract validator service
- [ ] Sync data preparation matches contract
- [ ] Validation before sending to CRM
- [ ] Error handling for validation failures
- [ ] Tests with contract validation

### CRM Implementation
- [ ] Contract validator service
- [ ] API endpoint validates incoming data
- [ ] OpenAPI schema in FastAPI route
- [ ] Error responses match contract
- [ ] Tests with contract examples

## Resources

- **OpenAPI 3.0 Specification:** https://spec.openapis.org/oas/v3.0.3
- **OpenAPI Generator:** https://openapi-generator.tech/
- **Swagger Editor:** https://editor.swagger.io/
- **JSON Schema Validator:** https://www.jsonschemavalidator.net/

## FAQ

**Q: Why OpenAPI instead of Protobuf?**
A: OpenAPI provides better human readability, easier validation in Python/JavaScript, and wider tooling support for REST APIs.

**Q: Can we add custom fields?**
A: Yes, but they must be added to this contract first. Update the spec, increment version, then implement in systems.

**Q: What happens if validation fails?**
A: Parser logs error and doesn't send data. CRM returns 422 error. Both systems log to sync_history for debugging.

**Q: How do we handle schema evolution?**
A: Use semantic versioning. Add optional fields for MINOR versions. Breaking changes require MAJOR version bump and coordinated deployment.

**Q: Do we support batch imports?**
A: Version 1.0.0 supports single organization per request. Batch endpoint may be added in future MINOR version.

## Support

- **Issues**: https://github.com/patrikdn/parser-crm-contract/issues
- **Discussions**: https://github.com/patrikdn/parser-crm-contract/discussions
- **Pull Requests**: https://github.com/patrikdn/parser-crm-contract/pulls

## License

TBD

## Related Repositories

- **Parser**: https://github.com/patrikdn/parser.git (Private, Production)
- **CRM**: https://github.com/patrikdn/crm.git (Private, Design Phase)
- **Ecosystem**: See parent directory `/Users/dpatrikeev/itisinteresting/CLAUDE.md`
