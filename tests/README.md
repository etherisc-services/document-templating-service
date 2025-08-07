# Tests

This directory contains all test files for the Document Template Processing Service.

## Test Structure

### Core Service Tests
- `test_docx_linter.py` - Unit tests for the DocX Jinja linter service
- `test_integrated_linting.py` - Integration tests for the linting workflow
- `test_with_existing_templates.py` - Tests with real template files

### Legacy Tests  
- `test_error_handling.py` - Error handling and edge cases
- `test_image_support.py` - Image processing functionality
- `test_undefined_variable_handling.py` - Variable handling tests

## Running Tests

### All Tests
```bash
pytest
```

### Specific Test Files
```bash
pytest tests/test_docx_linter.py -v
pytest tests/test_integrated_linting.py -v
```

### With Coverage
```bash
pytest --cov=. --cov-report=html
```

## Test Dependencies

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

Required dependencies:
- pytest
- pytest-asyncio
- pytest-html
- pytest-cov
- httpx (for API testing)

## Test Environment

Tests use:
- **FastAPI TestClient** for API endpoint testing
- **Async/await** for asynchronous operations
- **Temporary files** for document processing tests
- **Mock data** and **real template files** for validation

## Adding New Tests

1. Create test files with `test_` prefix
2. Use descriptive test function names with `test_` prefix
3. Include docstrings for complex test scenarios
4. Use fixtures for common setup/teardown
5. Test both success and failure cases