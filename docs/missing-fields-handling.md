# Missing Fields Handling

The Document Template Processing Service now provides robust handling of missing fields in JSON data, preventing errors and allowing graceful degradation when template variables reference non-existent properties.

## Problem Solved

Previously, when a Word document template referenced a field that didn't exist in the provided JSON data, the processor would throw an `UndefinedError` and fail to generate the document. This was particularly problematic when:

- Templates were created with fields that might not always be present
- JSON data structures varied between different data sources
- Optional fields were referenced in templates

## Solution

The service now supports four different behaviors for handling missing fields, configurable via the `undefined_behavior` parameter:

### 1. Silent Mode (`"silent"`) - Default
Missing fields are replaced with empty strings.

**Example:**
- Template: `Email: {{farmer.email}}`
- Missing field result: `Email: `

### 2. Property Missing Mode (`"property_missing"`)
Missing fields are replaced with `<property missing in json>`.

**Example:**
- Template: `Email: {{farmer.email}}`
- Missing field result: `Email: <property missing in json>`

### 3. Debug Mode (`"debug"`)
Missing fields show detailed variable names for debugging.

**Example:**
- Template: `Email: {{farmer.email}}`
- Missing field result: `Email: [Missing variable: farmer.email]`

### 4. Strict Mode (`"strict"`)
Missing fields throw errors (original behavior).

**Example:**
- Template: `Email: {{farmer.email}}`
- Result: HTTP 400 error with detailed error message

## Usage

### Using the Enhanced API

```bash
curl -X POST "http://localhost:8000/api/v1/process-template-document" \
  -F "file=@template.docx" \
  -F 'request_data={
    "template_data": {
      "farmer": {
        "name": "John Doe",
        "phone": "+1234567890"
      }
    },
    "undefined_behavior": "silent"
  }'
```

### Using Environment Variable

Set the default behavior for all requests:

```bash
export UNDEFINED_BEHAVIOR=silent
```

### Using Legacy API

The legacy `data` parameter continues to work with the default behavior:

```bash
curl -X POST "http://localhost:8000/api/v1/process-template-document" \
  -F "file=@template.docx" \
  -F 'data={"farmer": {"name": "John Doe"}}'
```

## Behavior Comparison

| Behavior | Missing Field Output | Use Case |
|----------|---------------------|----------|
| `silent` | (empty string) | Production documents where missing fields should be invisible |
| `property_missing` | `<property missing in json>` | Documents where missing fields should be clearly indicated |
| `debug` | `[Missing variable: field.name]` | Development and debugging templates |
| `strict` | Error thrown | Validation and ensuring all required fields are present |

## Examples

### Template with Missing Fields

```
Farmer Profile Report

Name: {{farmer.name}}
Email: {{farmer.email}}          # Missing field
Phone: {{farmer.phone}}
Address: {{farmer.address}}      # Missing field
Organization: {{organization.name}}
Type: {{organization.type}}      # Missing field
```

### JSON Data

```json
{
  "farmer": {
    "name": "John Doe",
    "phone": "+1234567890"
  },
  "organization": {
    "name": "Farm Co-op"
  }
}
```

### Results by Behavior

**Silent (`"silent"`):**
```
Farmer Profile Report

Name: John Doe
Email: 
Phone: +1234567890
Address: 
Organization: Farm Co-op
Type: 
```

**Property Missing (`"property_missing"`):**
```
Farmer Profile Report

Name: John Doe
Email: <property missing in json>
Phone: +1234567890
Address: <property missing in json>
Organization: Farm Co-op
Type: <property missing in json>
```

**Debug (`"debug"`):**
```
Farmer Profile Report

Name: John Doe
Email: [Missing variable: farmer.email]
Phone: +1234567890
Address: [Missing variable: farmer.address]
Organization: Farm Co-op
Type: [Missing variable: organization.type]
```

**Strict (`"strict"`):**
```
HTTP 400 Error:
{
  "message": "Undefined variable in template: 'main.DictToObject object' has no attribute 'email'",
  "error_type": "undefined_variable",
  "details": {
    "file": "template.docx",
    "undefined_variable": "'main.DictToObject object' has no attribute 'email'",
    "suggestion": "Check your template variables match the provided data"
  }
}
```

## Implementation Details

The solution uses custom Jinja2 `Undefined` classes:

- `SilentUndefined`: Returns empty strings for missing variables
- `PropertyMissingUndefined`: Returns `<property missing in json>` for missing variables  
- `DebugUndefined`: Returns `[Missing variable: name]` for missing variables
- `StrictUndefined`: Throws `UndefinedError` for missing variables (Jinja2 default)

These classes properly handle nested attribute access and dictionary-style access, ensuring that missing fields at any level are handled gracefully.

## Migration Guide

### For Existing Users

- **No breaking changes**: Existing API calls continue to work unchanged
- **Default behavior**: Uses `silent` mode by default (missing fields show as empty)
- **Environment override**: Set `UNDEFINED_BEHAVIOR` environment variable to change default

### For New Implementations

- **Recommended**: Use `request_data` parameter with explicit `undefined_behavior`
- **Production**: Use `"silent"` or `"property_missing"` for end-user documents
- **Development**: Use `"debug"` for template development and testing
- **Validation**: Use `"strict"` when all fields must be present

## Testing

The solution includes comprehensive tests:

```bash
# Test with farmer data
python test_farmer_missing_fields.py

# Test all behaviors
python test_missing_fields_solution.py

# Run existing test suite
python -m pytest tests/test_undefined_variable_handling.py -v
```

## Error Handling

The service maintains backward compatibility with existing error handling while adding the new graceful degradation options. When using `strict` mode, errors are still thrown with detailed information about missing fields, helping developers identify and fix template issues.
