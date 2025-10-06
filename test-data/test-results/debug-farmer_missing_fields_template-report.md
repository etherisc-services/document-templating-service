# 📋 DocX Jinja Template Linting Report

## Document Information

| Field | Value |
|-------|-------|
| **Document Name** | `farmer_missing_fields_template.docx` |
| **Report Generated** | 2025-10-06 16:37:30 |
| **Template Size** | 314 characters |
| **Lines Count** | 10 lines |
| **Jinja Tags** | 9 tags |
| **Processing Time** | 27.81ms |
| **Completeness Score** | 100.0% |

## Validation Status

✅ **PASSED** - Template validation successful


## 📊 Summary

| Issue Type | Count |
|------------|-------|
| ❌ **Errors** | 0 |
| ⚠️ **Warnings** | 3 |

💡 **Recommendations**: Consider addressing warnings to improve template quality.



<div class="page-break"></div>

# 🔍 Detailed Analysis

## ⚠️ Warnings

| Line | Template Text | Issue Description |
|------|---------------|-------------------|
| Unknown | N/A | **Undefined variable: summary**<br/>💡 *Ensure 'summary' is provided in template data* |
| Unknown | N/A | **Undefined variable: organization**<br/>💡 *Ensure 'organization' is provided in template data* |
| Unknown | N/A | **Undefined variable: farmer**<br/>💡 *Ensure 'farmer' is provided in template data* |



<div class="page-break"></div>

# 📄 Template Preview

```jinja2
Farmer Profile Report
Farmer Name: {{farmer.name}}
Farmer Code: {{farmer.farmerCode}}
Phone: {{farmer.phone}}
Email: {{farmer.email}}
Address: {{farmer.address}}
Organization: {{organization.name}}
Organization Type: {{organization.type}}
Total Quotes: {{summary.totalQuotes}}
Total Claims: {{summary.totalClaims}}
```
