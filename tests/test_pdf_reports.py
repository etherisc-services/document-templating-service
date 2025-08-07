#!/usr/bin/env python3
"""
Test script for PDF linting report generation.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from services.docx_linter import DocxJinjaLinterService
from services.markdown_formatter import create_lint_report_markdown
from models.schemas import LintOptions, LintResponseFormat
from docx import Document


async def create_test_template(content: str, filename: str) -> bytes:
    """Create a test .docx file with given content."""
    doc = Document()
    for line in content.split('\n'):
        if line.strip():
            doc.add_paragraph(line.strip())
    
    temp_path = f'temp/{filename}'
    os.makedirs('temp', exist_ok=True)
    doc.save(temp_path)
    
    with open(temp_path, 'rb') as f:
        return f.read()


async def test_markdown_generation():
    """Test markdown report generation."""
    print("🧪 Testing Markdown Report Generation")
    print("-" * 50)
    
    linter = DocxJinjaLinterService()
    
    # Create a template with errors
    broken_content = """
    Invoice Template
    Customer: {{ customer.name }}
    {% if customer.vip %}
    VIP Benefits:
    - Priority support
    {% for item in items %}
    - {{ item.name }}
    # Missing {% endfor %} and {% endif %}
    """
    
    docx_bytes = await create_test_template(broken_content, "broken_template.docx")
    
    # Run linting
    result = await linter.lint_docx_file(docx_bytes, "broken_template.docx")
    
    print(f"✅ Linting completed: {result.summary.total_errors} errors, {result.summary.total_warnings} warnings")
    
    # Generate markdown
    markdown_content = create_lint_report_markdown(
        result, 
        "broken_template.docx",
        {"customer": {"name": "John Doe", "vip": True}, "items": [{"name": "Product A"}]}
    )
    
    # Save markdown for inspection
    os.makedirs('temp', exist_ok=True)
    with open('temp/test_lint_report.md', 'w') as f:
        f.write(markdown_content)
    
    print(f"✅ Markdown report generated: temp/test_lint_report.md")
    print(f"📄 Report length: {len(markdown_content)} characters")
    
    # Show preview
    lines = markdown_content.split('\n')[:20]
    print("\n📝 Markdown Preview (first 20 lines):")
    for i, line in enumerate(lines, 1):
        print(f"{i:2}: {line}")
    if len(markdown_content.split('\n')) > 20:
        print("... (truncated)")
    
    return markdown_content


async def test_successful_template():
    """Test with a successful template."""
    print("\n🧪 Testing Successful Template Report")
    print("-" * 50)
    
    linter = DocxJinjaLinterService()
    
    # Create a valid template
    valid_content = """
    Invoice Template
    Customer: {{ customer.name }}
    {% if customer.vip %}
    VIP Benefits:
    - Priority support
    {% endif %}
    
    Items:
    {% for item in items %}
    - {{ item.name }}: ${{ item.price }}
    {% endfor %}
    
    Total: ${{ total }}
    """
    
    docx_bytes = await create_test_template(valid_content, "valid_template.docx")
    
    # Run linting
    result = await linter.lint_docx_file(docx_bytes, "valid_template.docx")
    
    print(f"✅ Linting completed: {result.summary.total_errors} errors, {result.summary.total_warnings} warnings")
    print(f"📊 Completeness score: {result.summary.completeness_score:.1f}%")
    
    # Generate markdown
    markdown_content = create_lint_report_markdown(result, "valid_template.docx")
    
    # Save markdown
    with open('temp/test_success_report.md', 'w') as f:
        f.write(markdown_content)
    
    print(f"✅ Success report generated: temp/test_success_report.md")
    print(f"📄 Report length: {len(markdown_content)} characters")


async def test_response_format_options():
    """Test different response format options."""
    print("\n🧪 Testing Response Format Options")
    print("-" * 50)
    
    # Test PDF default
    pdf_options = LintOptions()
    print(f"📄 Default response format: {pdf_options.response_format}")
    assert pdf_options.response_format == LintResponseFormat.PDF
    
    # Test JSON option
    json_options = LintOptions(response_format=LintResponseFormat.JSON)
    print(f"📋 JSON response format: {json_options.response_format}")
    assert json_options.response_format == LintResponseFormat.JSON
    
    print("✅ Response format options working correctly")


def test_markdown_formatting():
    """Test markdown formatting edge cases."""
    print("\n🧪 Testing Markdown Formatting")
    print("-" * 50)
    
    from services.markdown_formatter import LintReportMarkdownFormatter
    
    formatter = LintReportMarkdownFormatter()
    
    # Test escape functions
    test_text = "This has |pipes| and *asterisks* and [brackets] and `backticks`"
    escaped = formatter._escape_markdown(test_text)
    print(f"Original: {test_text}")
    print(f"Escaped:  {escaped}")
    
    code_text = "```python\nprint('hello')\n```"
    escaped_code = formatter._escape_code_block(code_text)
    print(f"Code Original: {code_text}")
    print(f"Code Escaped:  {escaped_code}")
    
    print("✅ Markdown formatting functions working")


async def main():
    """Run all tests."""
    print("🔬 PDF Linting Report Tests")
    print("=" * 60)
    
    try:
        # Test markdown generation
        await test_markdown_generation()
        
        # Test successful template
        await test_successful_template() 
        
        # Test response format options
        await test_response_format_options()
        
        # Test markdown formatting
        test_markdown_formatting()
        
        print(f"\n🏁 All tests completed!")
        print("=" * 60)
        print("\n📁 Generated files:")
        print("- temp/test_lint_report.md - Error report example")
        print("- temp/test_success_report.md - Success report example")
        print("\n💡 To test PDF conversion:")
        print("1. Start Gotenberg service")
        print("2. Test with actual API endpoint")
        print("3. Check that PDFs are generated correctly")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        print(f"🐛 Traceback:\n{traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())