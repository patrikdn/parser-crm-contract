#!/usr/bin/env python3
"""
Валидатор примеров против OpenAPI контракта.

Использование:
    python validators/validate_example.py examples/create-organization.json
    python validators/validate_example.py examples/minimal-organization.json
"""

import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Tuple, List


def load_openapi_spec(spec_path: Path) -> Dict[str, Any]:
    """Загрузить OpenAPI спецификацию из YAML файла."""
    with open(spec_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_example(example_path: Path) -> Dict[str, Any]:
    """Загрузить JSON пример."""
    with open(example_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_required_fields(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Проверить наличие обязательных полей."""
    errors = []
    required_fields = schema.get('required', [])

    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    return len(errors) == 0, errors


def validate_field_types(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Проверить типы полей."""
    errors = []
    properties = schema.get('properties', {})

    for field_name, field_value in data.items():
        if field_name not in properties:
            errors.append(f"Unknown field: {field_name}")
            continue

        field_schema = properties[field_name]
        expected_type = field_schema.get('type')

        # Проверка типа
        if expected_type == 'string':
            if not isinstance(field_value, str):
                errors.append(f"Field '{field_name}' must be string, got {type(field_value).__name__}")
        elif expected_type == 'integer':
            if not isinstance(field_value, int):
                errors.append(f"Field '{field_name}' must be integer, got {type(field_value).__name__}")
        elif expected_type == 'number':
            if not isinstance(field_value, (int, float)):
                errors.append(f"Field '{field_name}' must be number, got {type(field_value).__name__}")
        elif expected_type == 'array':
            if not isinstance(field_value, list):
                errors.append(f"Field '{field_name}' must be array, got {type(field_value).__name__}")
        elif expected_type == 'object':
            if not isinstance(field_value, dict):
                errors.append(f"Field '{field_name}' must be object, got {type(field_value).__name__}")

        # Проверка enum
        if 'enum' in field_schema:
            if field_value not in field_schema['enum']:
                errors.append(f"Field '{field_name}' value '{field_value}' not in allowed values: {field_schema['enum']}")

        # Проверка формата
        if 'format' in field_schema:
            format_type = field_schema['format']
            if format_type == 'uuid' and not is_valid_uuid(field_value):
                errors.append(f"Field '{field_name}' is not a valid UUID")
            elif format_type == 'email' and '@' not in field_value:
                errors.append(f"Field '{field_name}' is not a valid email")
            elif format_type == 'uri' and not field_value.startswith(('http://', 'https://')):
                errors.append(f"Field '{field_name}' is not a valid URI")

        # Проверка длины строки
        if expected_type == 'string':
            if 'minLength' in field_schema and len(field_value) < field_schema['minLength']:
                errors.append(f"Field '{field_name}' too short (min: {field_schema['minLength']})")
            if 'maxLength' in field_schema and len(field_value) > field_schema['maxLength']:
                errors.append(f"Field '{field_name}' too long (max: {field_schema['maxLength']})")

        # Проверка диапазона чисел
        if expected_type in ('integer', 'number'):
            if 'minimum' in field_schema and field_value < field_schema['minimum']:
                errors.append(f"Field '{field_name}' below minimum (min: {field_schema['minimum']})")
            if 'maximum' in field_schema and field_value > field_schema['maximum']:
                errors.append(f"Field '{field_name}' above maximum (max: {field_schema['maximum']})")

    return len(errors) == 0, errors


def is_valid_uuid(value: str) -> bool:
    """Проверить валидность UUID."""
    import re
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, value.lower()))


def validate_organization(data: Dict[str, Any], spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Валидировать организацию против схемы из контракта."""
    # Получить схему Organization из компонентов
    organization_schema = spec['components']['schemas']['Organization']

    all_errors = []

    # Проверка обязательных полей
    valid, errors = validate_required_fields(data, organization_schema)
    all_errors.extend(errors)

    # Проверка типов полей
    valid, errors = validate_field_types(data, organization_schema)
    all_errors.extend(errors)

    return len(all_errors) == 0, all_errors


def main():
    """Основная функция."""
    if len(sys.argv) != 2:
        print("Usage: python validators/validate_example.py <example_file.json>")
        print()
        print("Examples:")
        print("  python validators/validate_example.py examples/create-organization.json")
        print("  python validators/validate_example.py examples/minimal-organization.json")
        sys.exit(1)

    # Пути к файлам
    project_root = Path(__file__).parent.parent
    spec_path = project_root / "openapi-contract.yaml"
    example_path = Path(sys.argv[1])

    if not spec_path.exists():
        print(f"❌ Error: OpenAPI spec not found at {spec_path}")
        sys.exit(1)

    if not example_path.exists():
        print(f"❌ Error: Example file not found at {example_path}")
        sys.exit(1)

    # Загрузить спецификацию и пример
    try:
        spec = load_openapi_spec(spec_path)
        data = load_example(example_path)
    except Exception as e:
        print(f"❌ Error loading files: {e}")
        sys.exit(1)

    # Валидация
    print(f"Validating: {example_path.name}")
    print(f"Against contract version: {spec['info']['version']}")
    print()

    is_valid, errors = validate_organization(data, spec)

    if is_valid:
        print("✅ Validation successful!")
        print()
        print("Organization details:")
        print(f"  - external_id: {data.get('external_id')}")
        print(f"  - name: {data.get('name')}")
        print(f"  - category: {data.get('category')}")
        print(f"  - partnership_status: {data.get('partnership_status', 'N/A')}")
        sys.exit(0)
    else:
        print("❌ Validation failed!")
        print()
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
