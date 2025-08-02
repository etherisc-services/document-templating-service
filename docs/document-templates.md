---
layout: default
title: Document Templates
nav_order: 5
description: "Guide to creating Word document templates with Jinja2 syntax and template examples."
---

# Document Templates
{: .no_toc }

Learn how to create Word document templates using Jinja2 templating syntax for dynamic content generation.

<details open markdown="block">
  <summary>
    Table of Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

---

## Overview

Templates use **Jinja2** syntax for dynamic content. The service injects your data into template variables and generates a PDF output.

## Basic Variable Substitution

Replace static text with dynamic variables using double curly braces:

**Template:**
```
Customer: {{customer_name}}
Amount: ${{amount}}
Date: {{invoice_date}}
```

**JSON Data:**
```json
{
  "customer_name": "John Doe",
  "amount": 150.00,
  "invoice_date": "2023-12-01"
}
```

**Result:**
```
Customer: John Doe
Amount: $150.00
Date: 2023-12-01
```

## Conditional Logic (If/Then/Else)

Show different content based on conditions:

**Template:**
```
{% raw %}Dear {{customer_name}},

{% if amount > 100 %}
Thank you for your significant purchase of ${{amount}}.
As a valued customer, you qualify for our premium support.
{% else %}
Thank you for your purchase of ${{amount}}.
{% endif %}

{% if payment_method == "credit_card" %}
Your credit card will be charged within 24 hours.
{% elif payment_method == "paypal" %}
Please check your PayPal account for the transaction.
{% else %}
Please proceed with bank transfer using the details below.
{% endif %}{% endraw %}
```

**JSON Data:**
```json
{
  "customer_name": "Jane Smith",
  "amount": 250.00,
  "payment_method": "credit_card"
}
```

## Loops (For Each)

Iterate over arrays to generate repeated content:

**Template:**
```
{% raw %}Order Summary:

{% for item in items %}
- {{item.name}}: ${{item.price}} (Qty: {{item.quantity}})
{% endfor %}

Total Items: {{items|length}}{% endraw %}
```

**JSON Data:**
```json
{
  "items": [
    {"name": "Widget A", "price": 25.00, "quantity": 2},
    {"name": "Widget B", "price": 15.00, "quantity": 1},
    {"name": "Widget C", "price": 35.00, "quantity": 3}
  ]
}
```

## Advanced Examples

### Nested Loops with Conditions

**Template:**
```
{% raw %}Sales Report by Region:

{% for region in regions %}
## {{region.name}}

{% if region.sales %}
{% for sale in region.sales %}
  {% if sale.amount > 1000 %}
  ⭐ {{sale.product}}: ${{sale.amount}} (HIGH VALUE)
  {% else %}
  • {{sale.product}}: ${{sale.amount}}
  {% endif %}
{% endfor %}

Region Total: ${{region.sales|sum(attribute='amount')}}
{% else %}
No sales recorded for this region.
{% endif %}

{% endfor %}{% endraw %}
```

### Table Generation

**Template (in Word table):**
```
{% raw %}{% for product in products %}
{{product.id}} | {{product.name}} | ${{product.price}} | {{product.category}}
{% endfor %}{% endraw %}
```

### Date Formatting

**Template:**
```
{% raw %}Invoice Date: {{invoice_date|strftime('%B %d, %Y')}}
Due Date: {{due_date|strftime('%m/%d/%Y')}}{% endraw %}
```

## Template Syntax Reference

| Syntax | Purpose | Example |
|--------|---------|---------|
| `{% raw %}{{variable}}{% endraw %}` | Variable substitution | `{% raw %}{{customer_name}}{% endraw %}` |
| `{% raw %}{% if condition %}{% endraw %}` | Conditional logic | `{% raw %}{% if amount > 100 %}{% endraw %}` |
| `{% raw %}{% for item in list %}{% endraw %}` | Loop iteration | `{% raw %}{% for product in products %}{% endraw %}` |
| `{% raw %}{{variable|filter}}{% endraw %}` | Apply filter | `{% raw %}{{date|date_format('%Y-%m-%d')}}{% endraw %}` |
| `{% raw %}{{image_variable}}{% endraw %}` | Image insertion | `{% raw %}{{company_logo}}{% endraw %}` |

## Image Support in Templates

🎯 **Available in:** `/api/v1/process-template-document` endpoint (Enhanced Mode with `request_data` parameter)

Images can be embedded directly in templates using the enhanced endpoint. Images are provided as Base64-encoded PNG data and referenced in templates using standard Jinja2 variable syntax.

**Template Example:**
```
Company Logo: {{company_logo}}
```

**Request Data with Images:**
```json
{
  "template_data": {
    "company_name": "Acme Corp",
    "company_logo": "{{logo_image}}"
  },
  "images": {
    "logo_image": {
      "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
      "width_mm": 50,
      "height_mm": 20
    }
  }
}
```

For detailed image support documentation, see the **[Image Support Guide](image-support.md)**.

## Data Types

The service supports various JSON data types:

| Type | Example | Template Usage |
|------|---------|----------------|
| String | `"John Doe"` | `{% raw %}{{name}}{% endraw %}` |
| Number | `150.00` | `{% raw %}${{amount}}{% endraw %}` |
| Boolean | `true` | `{% raw %}{% if is_premium %}{% endraw %}` |
| Array | `["A", "B", "C"]` | `{% raw %}{% for item in list %}{% endraw %}` |
| Object | `{"name": "John"}` | `{% raw %}{{user.name}}{% endraw %}` |
| Null | `null` | `{% raw %}{{optional_field|default('N/A')}}{% endraw %}` |

## Best Practices

### Template Design
1. **Use descriptive variable names**: `customer_name` instead of `name`
2. **Provide fallbacks**: `{% raw %}{{optional_field|default('N/A')}}{% endraw %}`
3. **Test edge cases**: Empty arrays, missing fields, null values
4. **Keep templates simple**: Complex logic should be in your application

### Data Preparation
1. **Validate data structure** before sending to the service
2. **Format dates** in your application before template processing
3. **Handle null/undefined values** gracefully
4. **Use consistent data types** throughout your templates

### Performance
1. **Minimize template complexity** for faster processing
2. **Optimize image sizes** when using image support
3. **Structure data efficiently** to reduce processing time
4. **Cache templates** when possible in your application

## Troubleshooting

### Common Issues

1. **Variable not displaying**: Check spelling and ensure variable exists in data
2. **Syntax errors**: Verify Jinja2 syntax is correct
3. **Missing conditions**: Ensure all `{% raw %}{% if %}{% endraw %}` have matching `{% raw %}{% endif %}{% endraw %}`
4. **Loop issues**: Verify array structure and use correct iteration syntax

### Testing Templates

Use online Jinja2 testers or create minimal test cases:

```json
{
  "test_var": "Hello World",
  "test_array": [1, 2, 3],
  "test_object": {"nested": "value"}
}
```

For comprehensive error handling, see the **[Error Handling](error-handling.md)** guide.