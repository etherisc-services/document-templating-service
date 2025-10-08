#!/usr/bin/env python3
"""
EXACT test case as requested by user - DO NOT DELETE THIS FILE
"""

from jinja2 import DebugUndefined, Environment, StrictUndefined, Template, Undefined

# Try to import ChainableUndefined
try:
    from jinja2 import ChainableUndefined
    CHAINABLE_AVAILABLE = True
    print("✅ ChainableUndefined is available!")
except ImportError:
    CHAINABLE_AVAILABLE = False
    print("❌ ChainableUndefined is not available in this Jinja2 version")


def test_exact_user_case():
    """Test EXACTLY what the user specified"""
    print("🧪 EXACT User Test Case")
    print("=" * 50)

    # EXACT JSON as specified
    json_data = {
        "property": "value",
        "nested_object": {
            "nested_property": "nested-value"
        }
    }

    # EXACT template as specified
    template_str = """Text
{{ property }}
{{ nested_object.nested_property}}
{{ missing_property }}
{{ nested_object.missing_property }}
{{ missing_object.missing_property }}

{% if nested_object.missing_property %}
<should not happen>
{% else %}
<missing_property detected> 
{% endif %}

{% if missing_object.missing_property %}
<should not happen>
{% else %}
<missing_object.missing_property detected> 
{% endif %}

{{ missing_object.missing_property | default('N/A', true) }}

{% if missing_object is defined and missing_object.missing_property is defined %}
  {{ missing_object.missing_property }}
{% else %}
  N/A
{% endif %}

End_Text"""

    print("JSON:")
    print(json_data)
    print("\nTemplate:")
    print(repr(template_str))
    print("\nTemplate formatted:")
    print(template_str)
    print("\n" + "=" * 50)

    # Test with different undefined behaviors
    test_cases = [
        ("Default Undefined", Undefined),
        ("StrictUndefined", StrictUndefined),
        ("DebugUndefined", DebugUndefined)
    ]

    # Add ChainableUndefined if available
    if CHAINABLE_AVAILABLE:
        test_cases.append(("ChainableUndefined", ChainableUndefined))

    for name, undefined_class in test_cases:
        print(f"\n{'-'*20} {name} {'-'*20}")

        try:
            env = Environment(undefined=undefined_class)
            template = env.from_string(template_str)
            result = template.render(json_data)

            print("✅ SUCCESS")
            print("Raw result:")
            print(repr(result))
            print("\nFormatted result:")
            print(result)

        except Exception as e:
            print(f"❌ ERROR: {type(e).__name__}: {e}")

            # Show exactly where it fails
            print("\n🔍 Testing each line individually:")
            lines = [
                "{{ property }}",
                "{{ nested_object.nested_property}}",
                "{{ missing_property }}",
                "{{ nested_object.missing_property }}",
                "{{ missing_object.missing_property }}",
                "{% if nested_object.missing_property %}YES{% else %}NO{% endif %}",
                "{% if missing_object.missing_property %}YES{% else %}NO{% endif %}",
                "{{ missing_object.missing_property | default('N/A', true) }}",
                "{% if missing_object is defined and missing_object.missing_property is defined %}{{ missing_object.missing_property }}{% else %}N/A{% endif %}"
            ]

            for i, line in enumerate(lines, 1):
                try:
                    test_template = env.from_string(line)
                    test_result = test_template.render(json_data)
                    print(f"   Line {i}: {line} → '{test_result}' ✅")
                except Exception as line_error:
                    print(
                        f"   Line {i}: {line} → {type(line_error).__name__}: {line_error} ❌")
                    if i == 5:  # Only show "THIS IS WHERE IT FAILS" for the first failure
                        print(f"   ^^ THIS IS WHERE IT FAILS")
                    # Continue testing other lines instead of breaking


if __name__ == "__main__":
    test_exact_user_case()
