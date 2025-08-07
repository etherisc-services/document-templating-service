"""
Markdown formatter for DocX Jinja linting results.

This module creates formatted markdown documents from linting results
that can be converted to PDF using Gotenberg.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from models.schemas import LintResult, LintError, LintWarning


class LintReportMarkdownFormatter:
    """
    Formats linting results into professional markdown reports.
    """
    
    def __init__(self):
        """Initialize the markdown formatter."""
        pass
    
    def format_lint_report(
        self, 
        lint_result: LintResult, 
        document_name: str,
        template_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format a complete linting report as markdown.
        
        Args:
            lint_result: The linting results to format
            document_name: Name of the original document
            template_data: Optional template data used for validation
            
        Returns:
            Formatted markdown string ready for PDF conversion
        """
        # Start building the markdown report
        markdown_parts = []
        
        # Header section
        markdown_parts.append(self._create_header(lint_result, document_name, template_data))
        
        # Summary section
        markdown_parts.append(self._create_summary(lint_result))
        
        # New page for detailed results
        markdown_parts.append('\n<div class="page-break"></div>\n')
        
        # Detailed results section
        if lint_result.errors or lint_result.warnings:
            markdown_parts.append(self._create_detailed_results(lint_result))
        else:
            markdown_parts.append(self._create_success_message())
        
        # Template preview if available
        if lint_result.template_preview:
            markdown_parts.append('\n<div class="page-break"></div>\n')
            markdown_parts.append(self._create_template_preview(lint_result.template_preview))
        
        return "\n".join(markdown_parts)
    
    def _create_header(
        self, 
        lint_result: LintResult, 
        document_name: str,
        template_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create the report header with metadata."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        header = f"""# 📋 DocX Jinja Template Linting Report

## Document Information

| Field | Value |
|-------|-------|
| **Document Name** | `{document_name}` |
| **Report Generated** | {current_time} |
| **Template Size** | {lint_result.summary.template_size:,} characters |
| **Lines Count** | {lint_result.summary.lines_count:,} lines |
| **Jinja Tags** | {lint_result.summary.jinja_tags_count} tags |
| **Processing Time** | {lint_result.summary.processing_time_ms:.2f}ms |
| **Completeness Score** | {lint_result.summary.completeness_score:.1f}% |

## Validation Status

"""
        
        if lint_result.success:
            header += "✅ **PASSED** - Template validation successful\n\n"
        else:
            header += "❌ **FAILED** - Template validation failed\n\n"
        
        # Add template data if provided
        if template_data:
            header += "## Template Data Summary\n\n"
            header += "```json\n"
            header += json.dumps(template_data, indent=2, default=str)
            header += "\n```\n\n"
        
        return header
    
    def _create_summary(self, lint_result: LintResult) -> str:
        """Create the summary section."""
        summary = "## 📊 Summary\n\n"
        
        if lint_result.summary.total_errors == 0 and lint_result.summary.total_warnings == 0:
            summary += "🎉 **Perfect Template!** No errors or warnings found.\n\n"
        else:
            summary += "| Issue Type | Count |\n"
            summary += "|------------|-------|\n"
            summary += f"| ❌ **Errors** | {lint_result.summary.total_errors} |\n"
            summary += f"| ⚠️ **Warnings** | {lint_result.summary.total_warnings} |\n\n"
            
            if lint_result.summary.total_errors > 0:
                summary += "🚨 **Action Required**: Errors must be fixed before template can be processed.\n\n"
            elif lint_result.summary.total_warnings > 0:
                summary += "💡 **Recommendations**: Consider addressing warnings to improve template quality.\n\n"
        
        return summary
    
    def _create_detailed_results(self, lint_result: LintResult) -> str:
        """Create the detailed results table."""
        details = "# 🔍 Detailed Analysis\n\n"
        
        if lint_result.errors:
            details += "## ❌ Errors\n\n"
            details += self._create_issues_table(lint_result.errors, "error")
            details += "\n"
        
        if lint_result.warnings:
            details += "## ⚠️ Warnings\n\n"
            details += self._create_issues_table(lint_result.warnings, "warning")
            details += "\n"
        
        return details
    
    def _create_issues_table(self, issues, issue_type: str) -> str:
        """Create a table for errors or warnings."""
        table = "| Line | Template Text | Issue Description |\n"
        table += "|------|---------------|-------------------|\n"
        
        for issue in issues:
            # Format line number
            line_info = str(issue.line_number) if issue.line_number else "Unknown"
            if hasattr(issue, 'column') and issue.column:
                line_info += f":{issue.column}"
            
            # Format template text with context
            template_text = "N/A"
            if hasattr(issue, 'context') and issue.context:
                template_text = f"`{self._escape_markdown(issue.context[:50])}`"
                if len(issue.context) > 50:
                    template_text += "..."
            
            # Format description with type and suggestion
            description = f"**{issue.error_type if hasattr(issue, 'error_type') else issue.warning_type}**<br/>"
            description += self._escape_markdown(issue.message)
            
            if issue.suggestion:
                description += f"<br/>💡 *{self._escape_markdown(issue.suggestion)}*"
            
            table += f"| {line_info} | {template_text} | {description} |\n"
        
        return table
    
    def _create_success_message(self) -> str:
        """Create a success message for templates with no issues."""
        return """# ✅ Validation Successful

🎉 **Congratulations!** Your template has passed all validation checks.

## What this means:
- ✅ All Jinja2 syntax is correct
- ✅ All template tags are properly matched
- ✅ Template structure is valid
- ✅ No quality issues detected

Your template is ready for production use!
"""
    
    def _create_template_preview(self, template_preview: str) -> str:
        """Create the template preview section."""
        preview = "# 📄 Template Preview\n\n"
        preview += "```jinja2\n"
        preview += self._escape_code_block(template_preview)
        preview += "\n```\n"
        return preview
    
    def _escape_markdown(self, text: str) -> str:
        """Escape special markdown characters."""
        if not text:
            return ""
        
        # Escape common markdown characters
        chars_to_escape = ['|', '*', '_', '`', '\\', '[', ']', '(', ')', '#', '+', '-', '.', '!']
        
        for char in chars_to_escape:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    def _escape_code_block(self, text: str) -> str:
        """Escape text for code blocks."""
        if not text:
            return ""
        
        # Escape triple backticks to prevent breaking code blocks
        return text.replace('```', '\\`\\`\\`')


def create_lint_report_markdown(
    lint_result: LintResult,
    document_name: str,
    template_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convenience function to create a markdown linting report.
    
    Args:
        lint_result: The linting results
        document_name: Name of the document
        template_data: Optional template data
        
    Returns:
        Formatted markdown string
    """
    formatter = LintReportMarkdownFormatter()
    return formatter.format_lint_report(lint_result, document_name, template_data)