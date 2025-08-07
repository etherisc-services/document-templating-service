# 📋 DocX Jinja Template Linting Report

## Document Information

| Field | Value |
|-------|-------|
| **Document Name** | `farmer-profile-template.docx` |
| **Report Generated** | 2025-08-07 15:10:10 |
| **Template Size** | 8,523 characters |
| **Lines Count** | 154 lines |
| **Jinja Tags** | 179 tags |
| **Processing Time** | 279.54ms |
| **Completeness Score** | 100.0% |

## Validation Status

✅ **PASSED** - Template validation successful


## 📊 Summary

| Issue Type | Count |
|------------|-------|
| ❌ **Errors** | 0 |
| ⚠️ **Warnings** | 5 |

💡 **Recommendations**: Consider addressing warnings to improve template quality.



<div class="page-break"></div>

# 🔍 Detailed Analysis

## ⚠️ Warnings

| Line | Template Text | Issue Description |
|------|---------------|-------------------|
| Unknown | N/A | **Undefined variable: user**<br/>💡 *Ensure 'user' is provided in template data* |
| 4 | N/A | **Undefined variable: generatedAt**<br/>💡 *Ensure 'generatedAt' is provided in template data* |
| 104 | N/A | **Undefined variable: systemVersion**<br/>💡 *Ensure 'systemVersion' is provided in template data* |
| Unknown | N/A | **Undefined variable: farmer**<br/>💡 *Ensure 'farmer' is provided in template data* |
| 154 | N/A | **Undefined variable: daysSinceRegistration**<br/>💡 *Ensure 'daysSinceRegistration' is provided in template data* |



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
