#!/usr/bin/env python3
"""
Test script to validate the linter with existing template files in the repository.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from services.docx_linter import DocxJinjaLinterService
from models.schemas import LintOptions


async def test_existing_templates():
    """Test the linter with existing template files in the repository."""
    linter = DocxJinjaLinterService()
    
    # Define paths to existing template files
    template_files = [
        'test_image_files/simple_template.docx',
        'test_image_files/image_test_template.docx'
    ]
    
    print("=" * 80)
    print("Testing DocX Jinja Linter with Existing Template Files")
    print("=" * 80)
    
    for template_path in template_files:
        if not os.path.exists(template_path):
            print(f"⚠️  Template file not found: {template_path}")
            continue
        
        print(f"\n📄 Testing: {template_path}")
        print("-" * 40)
        
        try:
            # Read the template file
            with open(template_path, 'rb') as f:
                file_content = f.read()
            
            # Test with default options
            print("🔍 Linting with default options...")
            options = LintOptions()
            result = await linter.lint_docx_file(file_content, template_path, options)
            
            # Print results
            print(f"✅ Success: {result.success}")
            print(f"📊 Summary:")
            print(f"   - Errors: {result.summary.total_errors}")
            print(f"   - Warnings: {result.summary.total_warnings}")
            print(f"   - Template size: {result.summary.template_size} chars")
            print(f"   - Lines: {result.summary.lines_count}")
            print(f"   - Jinja tags: {result.summary.jinja_tags_count}")
            print(f"   - Completeness score: {result.summary.completeness_score:.1f}%")
            print(f"   - Processing time: {result.summary.processing_time_ms:.2f}ms")
            
            # Show template preview
            if result.template_preview:
                print(f"📝 Template preview:")
                preview_lines = result.template_preview.split('\n')[:5]
                for i, line in enumerate(preview_lines):
                    if line.strip():
                        print(f"   {i+1}: {line[:80]}{'...' if len(line) > 80 else ''}")
                if len(result.template_preview.split('\n')) > 5:
                    print("   ... (truncated)")
            
            # Show errors if any
            if result.errors:
                print(f"❌ Errors found:")
                for i, error in enumerate(result.errors[:5], 1):  # Show first 5 errors
                    location = f"Line {error.line_number}" if error.line_number else "Unknown location"
                    print(f"   {i}. [{error.error_type}] {location}: {error.message}")
                    if error.suggestion:
                        print(f"      💡 {error.suggestion}")
                if len(result.errors) > 5:
                    print(f"   ... and {len(result.errors) - 5} more errors")
            
            # Show warnings if any
            if result.warnings:
                print(f"⚠️  Warnings found:")
                for i, warning in enumerate(result.warnings[:3], 1):  # Show first 3 warnings
                    location = f"Line {warning.line_number}" if warning.line_number else "Unknown location"
                    print(f"   {i}. [{warning.warning_type}] {location}: {warning.message}")
                    if warning.suggestion:
                        print(f"      💡 {warning.suggestion}")
                if len(result.warnings) > 3:
                    print(f"   ... and {len(result.warnings) - 3} more warnings")
            
            # Test with verbose options
            print(f"\n🔍 Linting with verbose options...")
            verbose_options = LintOptions(
                verbose=True,
                max_line_length=100,
                fail_on_warnings=False
            )
            verbose_result = await linter.lint_docx_file(file_content, template_path, verbose_options)
            
            if verbose_result.template_content:
                print(f"📋 Full template content extracted ({len(verbose_result.template_content)} chars)")
                # Show first few lines of actual content
                content_lines = [line for line in verbose_result.template_content.split('\n') if line.strip()][:10]
                for i, line in enumerate(content_lines, 1):
                    print(f"   {i}: {line[:100]}{'...' if len(line) > 100 else ''}")
                if len(content_lines) > 10:
                    print("   ... (truncated)")
            
        except Exception as e:
            print(f"❌ Error testing {template_path}: {str(e)}")
            import traceback
            print(f"🐛 Traceback:\n{traceback.format_exc()}")
    
    print(f"\n" + "=" * 80)
    print("Testing completed!")
    print("=" * 80)


def print_service_info():
    """Print information about the linter service."""
    print("📋 DocX Jinja Linter Service Information")
    print("-" * 40)
    
    linter = DocxJinjaLinterService()
    
    print(f"🏷️  Paired tags: {', '.join(sorted(linter.paired_tags))}")
    print(f"🔖 Standalone tags: {', '.join(sorted(linter.standalone_tags))}")
    print(f"🔍 Tag patterns: {len(linter.tag_patterns)} patterns configured")
    
    print(f"\n📐 Default LintOptions:")
    default_options = LintOptions()
    print(f"   - verbose: {default_options.verbose}")
    print(f"   - check_undefined_vars: {default_options.check_undefined_vars}")
    print(f"   - max_line_length: {default_options.max_line_length}")
    print(f"   - fail_on_warnings: {default_options.fail_on_warnings}")
    print(f"   - check_tag_matching: {default_options.check_tag_matching}")
    print(f"   - check_nested_structure: {default_options.check_nested_structure}")


if __name__ == "__main__":
    print_service_info()
    print()
    asyncio.run(test_existing_templates())