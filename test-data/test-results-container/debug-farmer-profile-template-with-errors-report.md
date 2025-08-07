# 📋 DocX Jinja Template Linting Report

## Document Information

| Field | Value |
|-------|-------|
| **Document Name** | `farmer-profile-template-with-errors.docx` |
| **Report Generated** | 2025-08-07 15:09:14 |
| **Template Size** | 8,552 characters |
| **Lines Count** | 160 lines |
| **Jinja Tags** | 178 tags |
| **Processing Time** | 80.95ms |
| **Completeness Score** | 80.0% |

## Validation Status

❌ **FAILED** - Template validation failed


## 📊 Summary

| Issue Type | Count |
|------------|-------|
| ❌ **Errors** | 1 |
| ⚠️ **Warnings** | 0 |

🚨 **Action Required**: Errors must be fixed before template can be processed.



<div class="page-break"></div>

# 🔍 Detailed Analysis

## ❌ Errors

| Line | Template Text | Issue Description |
|------|---------------|-------------------|
| 111 | <code>Email Address \| {%p if farmer\.email %}{{ farmer\.email }}{% else %}</code> | **LintErrorType.SYNTAX_ERROR**<br/>Template syntax error: Unexpected end of template\. Jinja was looking for the following tags: 'endif'\. The innermost block that needs to be closed is 'if'\.<br/>💡 *Check for unmatched tags, missing endif/endfor statements, or invalid Jinja2 syntax* |



<div class="page-break"></div>

# 📄 Template Preview

```jinja2
Farmer Profile Report
This is a template for creating a Word document (.docx) for comprehensive farmer profile PDF generation. Convert this markdown to a Word document and save as farmer-profile-template.docx.
{{ farmer.name }} - Farmer Profile
Report ID: {{ farmer.farmerCode }}-PROFILE-{{ generatedAt }}
Executive Summary
This comprehensive farmer profile provides detailed information about {{ farmer.name }}, including personal details, agricultural activities, location information, organization...
```
