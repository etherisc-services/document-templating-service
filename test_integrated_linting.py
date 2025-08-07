#!/usr/bin/env python3
"""
Test script for the integrated linting workflow in the main document processing endpoint.
"""

import json
import tempfile
import os
from docx import Document
from fastapi.testclient import TestClient
from main import app

def create_test_docx(content: str, filename: str = "test.docx") -> str:
    """Create a test .docx file with given content."""
    doc = Document()
    for line in content.split('\n'):
        if line.strip():
            doc.add_paragraph(line.strip())
    
    temp_path = os.path.join('temp', filename)
    os.makedirs('temp', exist_ok=True)
    doc.save(temp_path)
    return temp_path

def test_valid_template():
    """Test processing a valid template - should return PDF."""
    print("🧪 Test 1: Valid template (should return PDF)")
    print("-" * 50)
    
    client = TestClient(app)
    
    # Create valid template
    content = """
    Invoice
    Customer: {{ customer_name }}
    Amount: ${{ amount }}
    """
    template_path = create_test_docx(content, "valid_template.docx")
    
    # Test data
    test_data = {
        "customer_name": "John Doe",
        "amount": 100.50
    }
    
    try:
        with open(template_path, 'rb') as f:
            response = client.post(
                "/api/v1/process-template-document",
                files={"file": ("valid_template.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"data": json.dumps(test_data)}
            )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            if response.headers.get('content-type') == 'application/pdf':
                print("✅ SUCCESS: Returned PDF as expected")
                print(f"PDF size: {len(response.content)} bytes")
            else:
                print("❌ FAIL: Expected PDF but got different content type")
                print(f"Response: {response.text[:200]}...")
        else:
            print(f"❌ FAIL: Expected 200 but got {response.status_code}")
            print(f"Response: {response.text[:500]}...")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print()

def test_invalid_template():
    """Test processing an invalid template - should return JSON error."""
    print("🧪 Test 2: Invalid template (should return JSON error)")
    print("-" * 50)
    
    client = TestClient(app)
    
    # Create invalid template with unclosed tag
    content = """
    Invoice
    Customer: {{ customer_name }}
    {% if vip_customer %}
    VIP Benefits
    Amount: ${{ amount }}
    """  # Missing {% endif %}
    
    template_path = create_test_docx(content, "invalid_template.docx")
    
    # Test data
    test_data = {
        "customer_name": "John Doe",
        "amount": 100.50,
        "vip_customer": True
    }
    
    try:
        with open(template_path, 'rb') as f:
            response = client.post(
                "/api/v1/process-template-document",
                files={"file": ("invalid_template.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"data": json.dumps(test_data)}
            )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 400:
            try:
                result = response.json()
                print("✅ SUCCESS: Returned JSON error as expected")
                print(f"Status: {result.get('status', 'unknown')}")
                print(f"Message: {result.get('message', 'No message')}")
                
                if 'linting_results' in result:
                    linting = result['linting_results']
                    print(f"Errors found: {linting['summary']['total_errors']}")
                    print(f"Warnings: {linting['summary']['total_warnings']}")
                    
                    if linting['errors']:
                        print("First error:")
                        error = linting['errors'][0]
                        print(f"  - Type: {error['error_type']}")
                        print(f"  - Message: {error['message']}")
                        print(f"  - Suggestion: {error.get('suggestion', 'None')}")
                else:
                    print("⚠️  No linting_results in response")
                    
            except json.JSONDecodeError:
                print("❌ FAIL: Response is not valid JSON")
                print(f"Response: {response.text[:200]}...")
        else:
            print(f"❌ FAIL: Expected 400 but got {response.status_code}")
            print(f"Response: {response.text[:500]}...")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print()

def test_enhanced_mode_with_linter_options():
    """Test enhanced mode with custom linter options."""
    print("🧪 Test 3: Enhanced mode with custom linter options")
    print("-" * 50)
    
    client = TestClient(app)
    
    # Create template with long lines (should trigger warnings)
    content = """
    Invoice
    Customer: {{ customer_name }}
    This is a very long line that should trigger a warning when we set the max_line_length to something small like 30 characters which should definitely exceed the limit.
    Amount: ${{ amount }}
    """
    
    template_path = create_test_docx(content, "long_line_template.docx")
    
    # Test data with custom linter options
    request_data = {
        "template_data": {
            "customer_name": "John Doe",
            "amount": 100.50
        },
        "linter_options": {
            "max_line_length": 50,
            "verbose": True,
            "fail_on_warnings": False
        }
    }
    
    try:
        with open(template_path, 'rb') as f:
            response = client.post(
                "/api/v1/process-template-document",
                files={"file": ("long_line_template.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"request_data": json.dumps(request_data)}
            )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            if response.headers.get('content-type') == 'application/pdf':
                print("✅ SUCCESS: Template passed linting with warnings, returned PDF")
                print(f"PDF size: {len(response.content)} bytes")
            else:
                print("❌ FAIL: Expected PDF but got different content type")
        else:
            print(f"Received {response.status_code} status")
            try:
                result = response.json()
                if 'linting_results' in result:
                    linting = result['linting_results']
                    print(f"Errors: {linting['summary']['total_errors']}")
                    print(f"Warnings: {linting['summary']['total_warnings']}")
                    if linting['warnings']:
                        print("Warnings found:")
                        for warning in linting['warnings'][:3]:
                            print(f"  - {warning['warning_type']}: {warning['message']}")
            except:
                print(f"Response: {response.text[:300]}...")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print()

def test_legacy_mode():
    """Test that legacy mode still works with integrated linting."""
    print("🧪 Test 4: Legacy mode compatibility")
    print("-" * 50)
    
    client = TestClient(app)
    
    # Create simple valid template
    content = """
    Simple Invoice
    Customer: {{ name }}
    Total: ${{ total }}
    """
    
    template_path = create_test_docx(content, "legacy_template.docx")
    
    try:
        with open(template_path, 'rb') as f:
            response = client.post(
                "/api/v1/process-template-document",
                files={"file": ("legacy_template.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"data": '{"name": "Jane Smith", "total": 250.00}'}
            )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
            print("✅ SUCCESS: Legacy mode works with integrated linting")
            print(f"PDF size: {len(response.content)} bytes")
        else:
            print(f"❌ FAIL: Expected PDF response")
            print(f"Response: {response.text[:300]}...")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print()

def main():
    """Run all integration tests."""
    print("🔬 Integrated Linting Workflow Tests")
    print("=" * 60)
    print()
    
    # Ensure temp directory exists
    os.makedirs('temp', exist_ok=True)
    
    # Run tests
    test_valid_template()
    test_invalid_template()
    test_enhanced_mode_with_linter_options()
    test_legacy_mode()
    
    print("🏁 Integration tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()