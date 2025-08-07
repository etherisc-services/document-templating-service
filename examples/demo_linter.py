#!/usr/bin/env python3
"""
Demonstration script for the DocX Jinja Linter Service.

This script shows how to use the linter API endpoint with curl commands
and provides example templates with various types of errors.
"""

import json
import os
import tempfile
from docx import Document


def create_demo_templates():
    """Create demonstration templates with different types of issues."""
    templates = {}
    
    # 1. Perfect template - no errors
    perfect_content = """
    Invoice Template
    
    Customer: {{ customer.name }}
    Company: {{ customer.company }}
    Email: {{ customer.email }}
    
    {% if items %}
    Items:
    {% for item in items %}
    - {{ item.name }}: ${{ item.price }}
    {% endfor %}
    
    Total: ${{ total }}
    {% else %}
    No items in this invoice.
    {% endif %}
    
    Thank you for your business!
    """
    templates['perfect'] = perfect_content.strip()
    
    # 2. Template with unclosed tags
    unclosed_content = """
    Invoice Template
    
    Customer: {{ customer.name }}
    
    {% if customer.vip %}
    VIP Customer Benefits:
    - Priority support
    - Discount pricing
    # Missing {% endif %}
    
    {% for item in items %}
    - {{ item.name }}
    {% endfor %}
    """
    templates['unclosed'] = unclosed_content.strip()
    
    # 3. Template with mismatched tags
    mismatched_content = """
    Report Template
    
    {% if show_details %}
    Details section:
    {% for detail in details %}
    {{ detail }}
    {% endif %}  # Should be {% endfor %}
    {% endfor %}  # Should be {% endif %}
    """
    templates['mismatched'] = mismatched_content.strip()
    
    # 4. Template with syntax errors
    syntax_error_content = """
    Error Template
    
    Name: {{ name }  # Missing closing brace
    Age: { age }}    # Extra space and wrong opening
    
    {% if condition %  # Missing closing brace
    Content here
    {% endif %}
    """
    templates['syntax_error'] = syntax_error_content.strip()
    
    # 5. Template with excessive nesting
    nested_content = """
    Deep Nesting Template
    
    {% if level1 %}
        {% if level2 %}
            {% if level3 %}
                {% if level4 %}
                    {% if level5 %}
                        {% if level6 %}
                            {% if level7 %}
                                {% if level8 %}
                                    {% if level9 %}
                                        {% if level10 %}
                                            {% if level11 %}
                                                Too deep!
                                            {% endif %}
                                        {% endif %}
                                    {% endif %}
                                {% endif %}
                            {% endif %}
                        {% endif %}
                    {% endif %}
                {% endif %}
            {% endif %}
        {% endif %}
    {% endif %}
    """
    templates['nested'] = nested_content.strip()
    
    return templates


def create_docx_file(content: str, filename: str) -> str:
    """Create a .docx file with the given content."""
    doc = Document()
    
    # Split content into paragraphs
    paragraphs = content.split('\n')
    for paragraph_text in paragraphs:
        doc.add_paragraph(paragraph_text)
    
    # Save to temp directory
    temp_dir = 'temp/demo'
    os.makedirs(temp_dir, exist_ok=True)
    
    filepath = os.path.join(temp_dir, filename)
    doc.save(filepath)
    return filepath


def generate_curl_examples():
    """Generate curl command examples for testing the API."""
    
    print("🌐 API Testing Examples")
    print("=" * 50)
    print()
    print("1. Basic linting with default options:")
    print("curl -X POST 'http://localhost:8000/api/v1/lint-docx-template' \\")
    print("     -F 'document=@temp/demo/perfect.docx'")
    print()
    
    print("2. Linting with custom options:")
    print("curl -X POST 'http://localhost:8000/api/v1/lint-docx-template' \\")
    print("     -F 'document=@temp/demo/unclosed.docx' \\")
    print("     -F 'options={\"verbose\": true, \"max_line_length\": 50, \"fail_on_warnings\": false}'")
    print()
    
    print("3. Test all demo files:")
    demo_files = ['perfect.docx', 'unclosed.docx', 'mismatched.docx', 'syntax_error.docx', 'nested.docx']
    for filename in demo_files:
        print(f"curl -X POST 'http://localhost:8000/api/v1/lint-docx-template' \\")
        print(f"     -F 'document=@temp/demo/{filename}' | jq '.summary'")
    print()


def main():
    """Main demonstration script."""
    print("📋 DocX Jinja Linter Demonstration")
    print("=" * 50)
    print()
    
    # Create demo templates
    print("🏗️  Creating demonstration templates...")
    templates = create_demo_templates()
    
    created_files = []
    for name, content in templates.items():
        filename = f"{name}.docx"
        filepath = create_docx_file(content, filename)
        created_files.append(filepath)
        print(f"   ✓ Created: {filepath}")
    
    print(f"\n📁 Created {len(created_files)} demo template files in temp/demo/")
    print()
    
    # Show template summaries
    print("📝 Template Summaries:")
    print("-" * 30)
    
    descriptions = {
        'perfect': "✅ Perfect template with no errors or warnings",
        'unclosed': "❌ Template with unclosed {% if %} tag",
        'mismatched': "❌ Template with mismatched tag pairs",
        'syntax_error': "❌ Template with Jinja syntax errors",
        'nested': "⚠️  Template with excessive nesting depth"
    }
    
    for name, description in descriptions.items():
        print(f"   {name}.docx: {description}")
    
    print()
    
    # Generate API examples
    generate_curl_examples()
    
    # Show how to start the server
    print("🚀 Starting the Server:")
    print("-" * 20)
    print("uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print()
    
    # Show OpenAPI docs
    print("📚 API Documentation:")
    print("-" * 20)
    print("Swagger UI: http://localhost:8000/docs")
    print("ReDoc:      http://localhost:8000/redoc")
    print("OpenAPI:    http://localhost:8000/openapi.json")
    print()
    
    # Show Python usage example
    print("🐍 Python Usage Example:")
    print("-" * 24)
    print("""
import httpx
import asyncio

async def test_linter():
    async with httpx.AsyncClient() as client:
        with open('temp/demo/perfect.docx', 'rb') as f:
            files = {'document': ('perfect.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = await client.post(
                'http://localhost:8000/api/v1/lint-docx-template',
                files=files
            )
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Errors: {result['summary']['total_errors']}")
            print(f"Warnings: {result['summary']['total_warnings']}")

# Run the test
asyncio.run(test_linter())
    """)
    
    print("🎯 Key Features Demonstrated:")
    print("-" * 30)
    features = [
        "✓ Jinja2 syntax validation",
        "✓ Tag matching (if/endif, for/endfor, etc.)",
        "✓ Nested structure validation", 
        "✓ Template quality scoring",
        "✓ Comprehensive error reporting",
        "✓ Configurable linting options",
        "✓ Processing time metrics",
        "✓ Template content extraction"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print(f"\n✨ Demo setup complete! Test the API with the examples above.")


if __name__ == "__main__":
    main()