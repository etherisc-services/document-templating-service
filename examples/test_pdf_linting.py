#!/usr/bin/env python3
"""
Example script demonstrating PDF linting report generation.
"""

import requests
import json
import os


def test_pdf_linting():
    """Test the PDF linting endpoint with examples."""
    
    print("📋 Testing PDF Linting Reports")
    print("=" * 50)
    
    # Ensure we have test templates
    base_url = "http://localhost:8000"
    
    # Test 1: Default PDF response
    print("\n🧪 Test 1: Default PDF Response")
    print("-" * 30)
    
    if os.path.exists("test_image_files/simple_template.docx"):
        try:
            with open("test_image_files/simple_template.docx", "rb") as f:
                response = requests.post(
                    f"{base_url}/api/v1/lint-docx-template",
                    files={"document": ("simple_template.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
                )
            
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                if response.headers.get('content-type') == 'application/pdf':
                    print("✅ SUCCESS: Received PDF report")
                    print(f"📄 PDF size: {len(response.content)} bytes")
                    
                    # Save PDF
                    with open("temp/simple_template_lint_report.pdf", "wb") as f:
                        f.write(response.content)
                    print("📁 Saved as: temp/simple_template_lint_report.pdf")
                else:
                    print("❌ FAIL: Expected PDF but got different content type")
            else:
                print(f"❌ FAIL: HTTP {response.status_code}")
                print(response.text[:300])
                
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
        except FileNotFoundError:
            print("❌ Test template file not found")
    
    # Test 2: JSON response option
    print("\n🧪 Test 2: JSON Response Option")
    print("-" * 30)
    
    if os.path.exists("test_image_files/simple_template.docx"):
        try:
            with open("test_image_files/simple_template.docx", "rb") as f:
                data = {
                    "options": json.dumps({
                        "response_format": "json",
                        "verbose": True
                    })
                }
                response = requests.post(
                    f"{base_url}/api/v1/lint-docx-template",
                    files={"document": ("simple_template.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                    data=data
                )
            
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                if response.headers.get('content-type') == 'application/json':
                    print("✅ SUCCESS: Received JSON response")
                    result = response.json()
                    print(f"📊 Errors: {result.get('summary', {}).get('total_errors', 'N/A')}")
                    print(f"📊 Warnings: {result.get('summary', {}).get('total_warnings', 'N/A')}")
                    print(f"📊 Score: {result.get('summary', {}).get('completeness_score', 'N/A')}%")
                else:
                    print("❌ FAIL: Expected JSON but got different content type")
            else:
                print(f"❌ FAIL: HTTP {response.status_code}")
                
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
    
    # Test 3: Test with broken template if available
    print("\n🧪 Test 3: Error Report (if broken template exists)")
    print("-" * 50)
    
    if os.path.exists("temp/truly_broken.docx"):
        try:
            with open("temp/truly_broken.docx", "rb") as f:
                response = requests.post(
                    f"{base_url}/api/v1/lint-docx-template",
                    files={"document": ("truly_broken.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
                )
            
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                print("✅ SUCCESS: Received error report PDF")
                print(f"📄 PDF size: {len(response.content)} bytes")
                
                with open("temp/broken_template_lint_report.pdf", "wb") as f:
                    f.write(response.content)
                print("📁 Saved as: temp/broken_template_lint_report.pdf")
            else:
                print(f"❌ Response: HTTP {response.status_code}")
                
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
    else:
        print("⚠️  No broken template found (temp/truly_broken.docx)")
    
    print(f"\n🏁 Testing completed!")
    print("=" * 50)
    print("\n📋 Summary:")
    print("- Default response format is now PDF")
    print("- JSON format available with options.response_format = 'json'")
    print("- PDF reports include formatted error tables")
    print("- Both success and error reports are generated")


def show_curl_examples():
    """Show curl examples for the new PDF functionality."""
    print("\n🌐 Curl Examples")
    print("=" * 30)
    
    print("\n1. Default PDF Report:")
    print("curl -X POST 'http://localhost:8000/api/v1/lint-docx-template' \\")
    print("     -F 'document=@template.docx' \\")
    print("     -o 'lint_report.pdf'")
    
    print("\n2. JSON Response:")
    print("curl -X POST 'http://localhost:8000/api/v1/lint-docx-template' \\")
    print("     -F 'document=@template.docx' \\")
    print("     -F 'options={\"response_format\": \"json\", \"verbose\": true}' \\")
    print("     | jq '.summary'")
    
    print("\n3. Verbose PDF Report:")
    print("curl -X POST 'http://localhost:8000/api/v1/lint-docx-template' \\")
    print("     -F 'document=@template.docx' \\") 
    print("     -F 'options={\"verbose\": true, \"max_line_length\": 100}' \\")
    print("     -o 'detailed_lint_report.pdf'")


if __name__ == "__main__":
    print("📋 PDF Linting Report Test")
    print("🚀 Make sure the service is running on http://localhost:8000")
    print()
    
    try:
        test_pdf_linting()
        show_curl_examples()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()