from fastapi import Body, FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import Json
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import aiofiles
from utils import remove_temporary_files, get_env
import requests
import os
import traceback
import json
import base64
import tempfile
from typing import Dict, Any, Optional
from jinja2 import TemplateSyntaxError, UndefinedError, TemplateRuntimeError, TemplateNotFound, StrictUndefined, Undefined
from jinja2.exceptions import TemplateError
from docx.opc.exceptions import PackageNotFoundError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Utility class to convert dictionaries to objects with dot notation
class DictToObject:
    """Convert dictionary to object with dot notation access while preserving dict methods"""
    def __init__(self, dictionary):
        # Store original dictionary for dict methods
        self._original_dict = dictionary.copy()
        
        for key, value in dictionary.items():
            if isinstance(value, dict):
                value = DictToObject(value)
            elif isinstance(value, list):
                value = [DictToObject(item) if isinstance(item, dict) else item for item in value]
            setattr(self, key, value)
    
    def items(self):
        """Return items like a dictionary"""
        return self._original_dict.items()
    
    def keys(self):
        """Return keys like a dictionary"""
        return self._original_dict.keys()
    
    def values(self):
        """Return values like a dictionary (but converted to objects)"""
        return [getattr(self, key) for key in self._original_dict.keys()]
    
    def get(self, key, default=None):
        """Get value like a dictionary"""
        return getattr(self, key, default)
    
    def __getitem__(self, key):
        """Support dict[key] syntax"""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)
    
    def __contains__(self, key):
        """Support 'key in dict' syntax"""
        return hasattr(self, key)
    
    def __len__(self):
        """Support len(dict) syntax"""
        return len(self._original_dict)
    
    def __iter__(self):
        """Support iteration over keys"""
        return iter(self._original_dict.keys())

def convert_dict_to_object(data):
    """Recursively convert dictionaries to objects for dot notation access"""
    if isinstance(data, dict):
        return DictToObject(data)
    elif isinstance(data, list):
        return [convert_dict_to_object(item) for item in data]
    else:
        return data

# Custom Undefined classes for graceful variable handling
class SilentUndefined(Undefined):
    """
    An undefined that silently ignores missing variables by rendering as empty string.
    This allows templates to be more forgiving of missing data.
    """
    def __str__(self):
        return ''
    
    def __unicode__(self):
        return u''
    
    def __bool__(self):
        return False
    
    def __nonzero__(self):  # Python 2 compatibility
        return False
    
    def __getattr__(self, name):
        return self.__class__(name=name)
    
    def __getitem__(self, name):
        return self.__class__(name=name)


class DebugUndefined(Undefined):
    """
    An undefined that outputs a clear message showing the missing variable name.
    This helps identify which variables are missing in the template.
    """
    def __str__(self):
        if self._undefined_name:
            return '[Missing variable: %s]' % self._undefined_name
        return '[Missing variable: undefined]'
    
    def __unicode__(self):
        if self._undefined_name:
            return u'[Missing variable: %s]' % self._undefined_name
        return u'[Missing variable: undefined]'
    
    def __bool__(self):
        return False
    
    def __nonzero__(self):  # Python 2 compatibility
        return False
    
    def __getattr__(self, name):
        # For nested attributes, show the full path
        if self._undefined_name:
            full_name = f"{self._undefined_name}.{name}"
        else:
            full_name = name
        return self.__class__(name=full_name)
    
    def __getitem__(self, name):
        # For dictionary access, show the full path
        if self._undefined_name:
            full_name = f"{self._undefined_name}[{name}]"
        else:
            full_name = f"[{name}]"
        return self.__class__(name=full_name)

# Custom exception classes for structured error handling
class DocumentProcessingError(Exception):
    """Base class for document processing errors"""
    def __init__(self, message: str, error_type: str, details: Dict[str, Any] = None):
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)

class TemplateProcessingError(DocumentProcessingError):
    """Errors related to template processing"""
    pass

class FileProcessingError(DocumentProcessingError):
    """Errors related to file operations"""
    pass

class PDFConversionError(DocumentProcessingError):
    """Errors related to PDF conversion"""
    pass

# Pydantic models for API request/response
from pydantic import BaseModel

# Import linter service and models
from services.docx_linter import DocxJinjaLinterService
from services.markdown_formatter import create_lint_report_markdown
from models.schemas import LintOptions, LintResult, LintResponseFormat

class ImageData(BaseModel):
    """Model for inline image data"""
    data: str  # Base64 encoded image data
    width_mm: Optional[float] = None  # Width in millimeters
    height_mm: Optional[float] = None  # Height in millimeters
    width_px: Optional[int] = None  # Width in pixels (alternative to mm)
    height_px: Optional[int] = None  # Height in pixels (alternative to mm)

class TemplateRequest(BaseModel):
    """Model for the complete template processing request"""
    template_data: Dict[str, Any]  # The data to inject into the template
    images: Optional[Dict[str, ImageData]] = None  # Optional images referenced in template
    undefined_behavior: Optional[str] = None  # Override undefined variable behavior: "debug", "silent", "strict"
    linter_options: Optional[LintOptions] = None  # Optional linter configuration

def create_error_response(error: DocumentProcessingError, status_code: int = 500) -> JSONResponse:
    """Create a structured error response"""
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "error_type": error.error_type,
            "message": error.message,
            "details": error.details
        }
    )

def handle_template_error(e: Exception, file_path: str) -> TemplateProcessingError:
    """Convert Jinja2/docxtpl errors to structured template errors"""
    if isinstance(e, TemplateSyntaxError):
        return TemplateProcessingError(
            message=f"Template syntax error: {str(e)}",
            error_type="template_syntax_error",
            details={
                "file": file_path,
                "line": getattr(e, 'lineno', None),
                "column": getattr(e, 'colno', None),
                "template_name": getattr(e, 'name', None),
                "syntax_error": str(e)
            }
        )
    elif isinstance(e, UndefinedError):
        error_message = str(e)
        suggestion = "Check your template variables match the provided data"
        
        # Handle specific case of accessing attributes on dict objects
        if "dict object" in error_message and "has no attribute" in error_message:
            # Extract the attribute name from the error message
            parts = error_message.split("has no attribute")
            if len(parts) > 1:
                attr_name = parts[1].strip().strip("'\"")
                suggestion = f"The template is trying to access '.{attr_name}' on a dictionary. Use bracket notation like {{{{data['{attr_name}']}}}} instead of {{{{data.{attr_name}}}}} or ensure your data structure provides objects with attributes rather than dictionaries."
        
        return TemplateProcessingError(
            message=f"Undefined variable in template: {error_message}",
            error_type="undefined_variable",
            details={
                "file": file_path,
                "undefined_variable": error_message,
                "suggestion": suggestion
            }
        )
    elif isinstance(e, TemplateRuntimeError):
        return TemplateProcessingError(
            message=f"Template runtime error: {str(e)}",
            error_type="template_runtime_error",
            details={
                "file": file_path,
                "runtime_error": str(e)
            }
        )
    elif isinstance(e, TemplateNotFound):
        return TemplateProcessingError(
            message=f"Template not found: {str(e)}",
            error_type="template_not_found",
            details={
                "file": file_path,
                "template_name": str(e)
            }
        )
    elif isinstance(e, TemplateError):
        return TemplateProcessingError(
            message=f"Template error: {str(e)}",
            error_type="template_error",
            details={
                "file": file_path,
                "template_error": str(e)
            }
        )
    elif isinstance(e, PackageNotFoundError):
        return TemplateProcessingError(
            message=f"Document format issue: The template file appears to be corrupted or incompatible. {str(e)}",
            error_type="template_document_corruption",
            details={
                "file": file_path,
                "docx_error": str(e),
                "suggestion": "The template may have been generated incorrectly or corrupted. Try recreating the template with proper Jinja2 syntax in a standard Word document."
            }
        )
    elif isinstance(e, (TypeError, ValueError, ZeroDivisionError, ArithmeticError)):
        return TemplateProcessingError(
            message=f"Template runtime error: {str(e)}",
            error_type="template_runtime_error",
            details={
                "file": file_path,
                "runtime_error": str(e),
                "error_class": type(e).__name__,
                "suggestion": "Check that template variables have the correct data types and values"
            }
        )
    else:
        return TemplateProcessingError(
            message=f"Unknown template processing error: {str(e)}",
            error_type="unknown_template_error",
            details={
                "file": file_path,
                "error": str(e),
                "error_class": type(e).__name__
            }
        )

# Image processing functions
def process_base64_image(image_data: ImageData, doc: DocxTemplate, image_name: str) -> InlineImage:
    """
    Process base64 image data and create an InlineImage object for docxtpl.
    
    Args:
        image_data: ImageData object containing base64 data and dimensions
        doc: DocxTemplate instance 
        image_name: Name/identifier for the image
        
    Returns:
        InlineImage object ready for template rendering
        
    Raises:
        FileProcessingError: If image processing fails
    """
    try:
        # Decode base64 image data
        image_bytes = base64.b64decode(image_data.data)
        
        # Create temporary file for the image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(image_bytes)
            temp_file_path = temp_file.name
        
        # Determine dimensions - prioritize mm over px
        width = None
        height = None
        
        if image_data.width_mm is not None:
            width = Mm(image_data.width_mm)
        elif image_data.width_px is not None:
            # Convert pixels to mm (assuming 96 DPI: 1 inch = 25.4mm, 96px = 25.4mm)
            width = Mm(image_data.width_px * 25.4 / 96)
            
        if image_data.height_mm is not None:
            height = Mm(image_data.height_mm)
        elif image_data.height_px is not None:
            height = Mm(image_data.height_px * 25.4 / 96)
        
        # Create InlineImage object
        if width and height:
            inline_image = InlineImage(doc, temp_file_path, width=width, height=height)
        elif width:
            inline_image = InlineImage(doc, temp_file_path, width=width)
        elif height:
            inline_image = InlineImage(doc, temp_file_path, height=height)
        else:
            # Use default size if no dimensions specified
            inline_image = InlineImage(doc, temp_file_path)
        
        # Store temp file path for later cleanup (don't delete immediately)
        inline_image._temp_file_path = temp_file_path
        
        logger.info(f"Successfully processed image: {image_name}")
        return inline_image
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            
        raise FileProcessingError(
            message=f"Failed to process image '{image_name}': {str(e)}",
            error_type="image_processing_error", 
            details={
                "image_name": image_name,
                "error": str(e),
                "error_class": type(e).__name__,
                "suggestion": "Ensure image data is valid base64 encoded PNG"
            }
        )

def process_images(images_data: Optional[Dict[str, ImageData]], doc: DocxTemplate) -> Dict[str, InlineImage]:
    """
    Process all images in the request and return a dictionary of InlineImage objects.
    
    Args:
        images_data: Dictionary of image data from the request
        doc: DocxTemplate instance
        
    Returns:
        Dictionary mapping image names to InlineImage objects
    """
    if not images_data:
        return {}
    
    processed_images = {}
    
    for image_name, image_data in images_data.items():
        try:
            processed_images[image_name] = process_base64_image(image_data, doc, image_name)
            logger.info(f"Processed image: {image_name}")
        except Exception as e:
            logger.error(f"Failed to process image {image_name}: {str(e)}")
            raise  # Re-raise to be handled by the main error handling
    
    logger.info(f"Successfully processed {len(processed_images)} images")
    return processed_images

app = FastAPI(
    title="Document Template Processing Service",
    description="""
        This is the documentation of the REST API exposed by the document template processing microservice.
        This will allow you to inject data in a specific word document template and get the pdf format as a result. 🚀🚀🚀
        
        New features:
        - DocX Jinja Template Linting: Validate Jinja2 syntax in Word documents
    """,
    version="1.3.0"
)

# Initialize linter service
linter_service = DocxJinjaLinterService()

SERVICE_STATUS = {'status': 'Service is healthy !'}

@app.get('/')
async def livenessprobe():
    remove_temporary_files()
    return SERVICE_STATUS

@app.get('/health-check')
async def healthcheck():
    remove_temporary_files()
    return SERVICE_STATUS


@app.post('/api/v1/lint-docx-template')
async def lint_docx_template(
    document: UploadFile = File(..., description="DocX file containing Jinja2 template to lint"),
    options: LintOptions = Body(default=LintOptions(), description="Linting configuration options")
):
    """
    Lint a DocX file containing Jinja2 templates for syntax errors and structural issues.
    
    This endpoint validates:
    - Jinja2 syntax correctness
    - Matching tag pairs (if/endif, for/endfor, etc.)
    - Template structure and nesting
    - Code quality and best practices
    
    Response formats:
    - PDF (default): Professional linting report as PDF document
    - JSON (optional): Structured data for programmatic use
    
    Set options.response_format = "json" for JSON response.
    """
    try:
        # Input validation
        if not document or not document.filename or document.filename == '':
            error = FileProcessingError(
                message="No file provided or filename is empty",
                error_type="missing_file",
                details={"requirement": "A valid .docx file must be uploaded"}
            )
            return create_error_response(error, 400)
        
        if not document.filename.lower().endswith('.docx'):
            error = FileProcessingError(
                message="Invalid file type. Only .docx files are supported for linting",
                error_type="invalid_file_type",
                details={
                    "provided_filename": document.filename,
                    "supported_types": [".docx"],
                    "requirement": "Upload a Microsoft Word .docx file containing Jinja2 templates"
                }
            )
            return create_error_response(error, 400)
        
        # Check file size (reasonable limit for linting)
        file_content = await document.read()
        file_size = len(file_content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB limit for linting
            error = FileProcessingError(
                message="File too large for linting. Maximum size is 10MB",
                error_type="file_too_large",
                details={
                    "max_size_mb": 10, 
                    "file_size_bytes": file_size,
                    "suggestion": "Try linting smaller sections of the document"
                }
            )
            return create_error_response(error, 400)
        
        if file_size == 0:
            error = FileProcessingError(
                message="Uploaded file is empty",
                error_type="empty_file",
                details={"requirement": "File must contain content to lint"}
            )
            return create_error_response(error, 400)
        
        logger.info(f"Starting linting process for {document.filename} ({file_size} bytes)")
        
        # Perform linting
        lint_result = await linter_service.lint_docx_file(
            file_content=file_content,
            filename=document.filename,
            options=options
        )
        
        logger.info(f"Linting completed for {document.filename}: "
                   f"{lint_result.summary.total_errors} errors, "
                   f"{lint_result.summary.total_warnings} warnings")
        
        # Return response based on requested format
        if options.response_format == LintResponseFormat.JSON:
            return lint_result
        else:
            # Generate PDF report
            return await _generate_lint_pdf_report(lint_result, document.filename)
        
    except FileProcessingError as e:
        logger.error(f"File processing error during linting: {e.message}")
        return create_error_response(e, 400)
        
    except Exception as e:
        logger.error(f"Unexpected error during linting: {str(e)}")
        logger.error(traceback.format_exc())
        
        error = DocumentProcessingError(
            message=f"An unexpected error occurred during linting: {str(e)}",
            error_type="linting_error",
            details={
                "filename": document.filename if document else "unknown",
                "error": str(e),
                "error_class": type(e).__name__
            }
        )
        return create_error_response(error, 500)


async def _generate_lint_pdf_report(lint_result: LintResult, document_name: str) -> FileResponse:
    """
    Generate a PDF report from linting results.
    
    Args:
        lint_result: The linting results
        document_name: Name of the original document
        
    Returns:
        FileResponse with the PDF report
    """
    try:
        # Create markdown report
        markdown_content = create_lint_report_markdown(lint_result, document_name)
        
        # Ensure temp directory exists
        os.makedirs('temp', exist_ok=True)
        
        # Create temporary markdown file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, dir='temp') as md_file:
            md_file.write(markdown_content)
            md_file_path = md_file.name
        
        # Generate PDF filename
        base_name = os.path.splitext(document_name)[0]
        pdf_filename = f"{base_name}_lint_report.pdf"
        pdf_file_path = f"temp/{pdf_filename}"
        
        # Convert to PDF using Gotenberg
        gotenberg_url = get_env('GOTENBERG_API_URL')
        if not gotenberg_url:
            raise PDFConversionError(
                message="Gotenberg service URL not configured",
                error_type="gotenberg_not_configured",
                details={"env_var": "GOTENBERG_API_URL"}
            )
        
        resource_url = f'{gotenberg_url}/forms/chromium/convert/markdown'
        
        logger.info(f"Converting lint report to PDF via Gotenberg: {resource_url}")
        
        with open(md_file_path, 'rb') as md_file:
            files = {'files': (os.path.basename(md_file_path), md_file, 'text/markdown')}
            
            # Make request to Gotenberg with timeout
            response = requests.post(
                url=resource_url,
                files=files,
                timeout=30  # 30 second timeout for reports
            )
        
        # Check Gotenberg response
        if response.status_code != 200:
            error_details = {
                "gotenberg_url": resource_url,
                "status_code": response.status_code,
                "response_headers": dict(response.headers)
            }
            
            # Try to extract error message from response
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    error_data = response.json()
                    error_details["error_data"] = error_data
                else:
                    error_details["response_text"] = response.text[:500]
            except:
                error_details["response_text"] = response.text[:500] if response.text else "No response text"
            
            raise PDFConversionError(
                message=f"Gotenberg linting report conversion failed with status {response.status_code}",
                error_type="gotenberg_conversion_failed",
                details=error_details
            )
        
        # Validate response content
        if not response.content or not response.content.startswith(b'%PDF'):
            raise PDFConversionError(
                message="Gotenberg returned invalid PDF for linting report",
                error_type="invalid_pdf_response",
                details={
                    "gotenberg_url": resource_url,
                    "content_type": response.headers.get('content-type'),
                    "content_start": response.content[:100].decode('utf-8', errors='ignore') if response.content else "Empty"
                }
            )
        
        # Save PDF response
        async with aiofiles.open(pdf_file_path, 'wb') as out_file:
            await out_file.write(response.content)
        
        logger.info(f"Lint report PDF generated successfully: {pdf_file_path} ({len(response.content)} bytes)")
        
        # Clean up markdown file
        try:
            os.unlink(md_file_path)
        except:
            pass
        
        # Return PDF file
        return FileResponse(
            pdf_file_path,
            media_type='application/pdf',
            filename=pdf_filename
        )
        
    except Exception as e:
        # Clean up files on error
        try:
            if 'md_file_path' in locals() and os.path.exists(md_file_path):
                os.unlink(md_file_path)
            if 'pdf_file_path' in locals() and os.path.exists(pdf_file_path):
                os.unlink(pdf_file_path)
        except:
            pass
        
        logger.error(f"Failed to generate lint report PDF: {str(e)}")
        
        # Return JSON fallback if PDF generation fails
        return JSONResponse(
            status_code=500,
            content={
                "status": "pdf_generation_failed",
                "message": f"Could not generate PDF report: {str(e)}",
                "fallback_data": {
                    "success": lint_result.success,
                    "errors": [
                        {
                            "line_number": error.line_number,
                            "error_type": error.error_type,
                            "message": error.message,
                            "suggestion": error.suggestion
                        }
                        for error in lint_result.errors
                    ],
                    "summary": {
                        "total_errors": lint_result.summary.total_errors,
                        "total_warnings": lint_result.summary.total_warnings,
                        "completeness_score": lint_result.summary.completeness_score
                    }
                }
            }
        )


@app.post('/api/v1/process-template-document')
async def process_document_template(
    data: Json = Body(None), 
    request_data: str = Body(None),
    file: UploadFile = File(...)
):
    """
    Process a Word document template with data injection and convert to PDF.
    
    Supports two usage modes:
    1. Simple mode: Use 'data' parameter with JSON object (legacy format)
    2. Enhanced mode: Use 'request_data' parameter with template_data, images, and linter_options
    
    Enhanced mode enables inline image support via base64 encoded PNGs and custom linter configuration.
    
    **NEW: Integrated Template Linting**
    - Templates are automatically validated before processing (strict mode by default)
    - If validation fails, comprehensive error details are returned as JSON instead of PDF
    - Linter options can be customized in enhanced mode via 'linter_options' field
    - Processing only continues if template validation passes
    
    Handles all stages with comprehensive error reporting:
    - File validation and upload
    - Template linting and syntax validation (NEW)
    - Data injection with variable checking
    - Image processing (when images provided)
    - PDF conversion with Gotenberg
    """
    file_path = None
    pdf_file_path = None
    
    try:
        # Input validation
        if not file or not file.filename or file.filename == '':
            error = FileProcessingError(
                message="No file provided or filename is empty",
                error_type="missing_file",
                details={"requirement": "A valid .docx file must be uploaded"}
            )
            return create_error_response(error, 400)
        
        if not file.filename.lower().endswith('.docx'):
            error = FileProcessingError(
                message="Invalid file type. Only .docx files are supported",
                error_type="invalid_file_type",
                details={
                    "provided_filename": file.filename,
                    "supported_types": [".docx"],
                    "requirement": "Upload a Microsoft Word .docx file"
                }
            )
            return create_error_response(error, 400)
        
        # Smart parameter detection - determine usage mode
        if request_data is not None:
            # Enhanced mode: process request_data with potential images
            try:
                parsed_request = json.loads(request_data)
                request_obj = TemplateRequest(**parsed_request)
                template_data = request_obj.template_data
                images_data = request_obj.images
                api_undefined_behavior = request_obj.undefined_behavior
                api_linter_options = request_obj.linter_options
                logger.info(f"Enhanced mode: Processing with {len(template_data)} data keys and {len(images_data or {})} images")
            except json.JSONDecodeError as e:
                error = TemplateProcessingError(
                    message=f"Invalid JSON in request_data: {str(e)}",
                    error_type="invalid_json",
                    details={
                        "json_error": str(e),
                        "suggestion": "Ensure request_data is valid JSON with template_data and optional images"
                    }
                )
                return create_error_response(error, 400)
            except Exception as e:
                error = TemplateProcessingError(
                    message=f"Invalid request structure: {str(e)}",
                    error_type="invalid_request_structure",
                    details={
                        "error": str(e),
                        "suggestion": "Ensure request follows TemplateRequest model structure"
                    }
                )
                return create_error_response(error, 400)
        elif data is not None:
            # Legacy mode: simple data parameter
            template_data = data
            images_data = None
            api_undefined_behavior = None
            api_linter_options = None
            logger.info(f"Legacy mode: Processing with {len(template_data) if isinstance(template_data, dict) else 'non-dict'} data")
        else:
            # No data provided at all
            error = TemplateProcessingError(
                message="No template data provided. Use either 'data' parameter (legacy) or 'request_data' parameter (enhanced with images)",
                error_type="missing_template_data",
                details={
                    "requirement": "Provide either 'data' (JSON object) or 'request_data' (JSON string)",
                    "examples": {
                        "legacy": '{"name": "John Doe"}',
                        "enhanced": '{"template_data": {"name": "John Doe"}, "images": {}}'
                    }
                }
            )
            return create_error_response(error, 400)
        
        if template_data is None or (isinstance(template_data, (list, dict)) and len(template_data) == 0):
            error = TemplateProcessingError(
                message="No template data provided",
                error_type="missing_template_data",
                details={
                    "requirement": "Provide JSON data for template variable injection",
                    "example": '{"name": "John", "company": "Acme Corp"}'
                }
            )
            return create_error_response(error, 400)
        
        # Additional validation for legacy mode only (enhanced mode already validated)
        if request_data is None:
            try:
                if isinstance(template_data, str):
                    template_data = json.loads(template_data)
            except json.JSONDecodeError as e:
                error = TemplateProcessingError(
                    message=f"Invalid JSON data: {str(e)}",
                    error_type="invalid_json",
                    details={
                        "json_error": str(e),
                        "line": getattr(e, 'lineno', None),
                        "column": getattr(e, 'colno', None),
                        "suggestion": "Ensure the data parameter contains valid JSON"
                    }
                )
                return create_error_response(error, 400)
        
        # Setup file paths
        sanitized_filename = "".join(c for c in file.filename if c.isalnum() or c in '._-')
        base_name = os.path.splitext(sanitized_filename)[0]
        file_path = f'temp/{sanitized_filename}'
        pdf_file_path = f'temp/{base_name}.pdf'
        
        # Ensure temp directory exists
        os.makedirs('temp', exist_ok=True)
        
        # Stage 1: File Upload and Validation
        try:
            # Check file size (optional limit)
            file_size = 0
            async with aiofiles.open(file_path, 'wb') as out_file:
                while chunk := await file.read(1024):
                    file_size += len(chunk)
                    if file_size > 50 * 1024 * 1024:  # 50MB limit
                        raise FileProcessingError(
                            message="File too large. Maximum size is 50MB",
                            error_type="file_too_large",
                            details={"max_size_mb": 50, "file_size_bytes": file_size}
                        )
                    await out_file.write(chunk)
            
            logger.info(f"File uploaded successfully: {file_size} bytes")
            
        except IOError as e:
            error = FileProcessingError(
                message=f"Failed to save uploaded file: {str(e)}",
                error_type="file_save_error",
                details={
                    "file_path": file_path,
                    "io_error": str(e)
                }
            )
            return create_error_response(error, 500)
        
        # Stage 1.5: Template Linting (Pre-validation)
        try:
            # Configure linting options - strict by default
            if api_linter_options is not None:
                linter_options = api_linter_options
                logger.info("Using API-provided linter options")
            else:
                # Default to strict linting
                linter_options = LintOptions(
                    verbose=False,
                    check_undefined_vars=True,
                    max_line_length=200,
                    fail_on_warnings=False,  # Only fail on errors, not warnings
                    check_tag_matching=True,
                    check_nested_structure=True
                )
                logger.info("Using default strict linter options")
            
            # Read file content for linting
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Perform linting
            logger.info(f"Starting template validation for {file.filename}")
            lint_result = await linter_service.lint_docx_file(
                file_content=file_content,
                filename=file.filename,
                options=linter_options
            )
            
            # Check linting results
            if not lint_result.success:
                logger.warning(f"Template validation failed: {lint_result.summary.total_errors} errors found")
                
                # Clean up uploaded file before returning error
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # Return comprehensive linting error response
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "template_validation_failed",
                        "message": f"Template validation failed with {lint_result.summary.total_errors} errors",
                        "linting_results": {
                            "success": lint_result.success,
                            "errors": [
                                {
                                    "line_number": error.line_number,
                                    "column": error.column,
                                    "error_type": error.error_type,
                                    "message": error.message,
                                    "context": error.context,
                                    "tag_name": error.tag_name,
                                    "suggestion": error.suggestion
                                }
                                for error in lint_result.errors
                            ],
                            "warnings": [
                                {
                                    "line_number": warning.line_number,
                                    "warning_type": warning.warning_type,
                                    "message": warning.message,
                                    "suggestion": warning.suggestion
                                }
                                for warning in lint_result.warnings
                            ],
                            "summary": {
                                "total_errors": lint_result.summary.total_errors,
                                "total_warnings": lint_result.summary.total_warnings,
                                "template_size": lint_result.summary.template_size,
                                "lines_count": lint_result.summary.lines_count,
                                "jinja_tags_count": lint_result.summary.jinja_tags_count,
                                "completeness_score": lint_result.summary.completeness_score,
                                "processing_time_ms": lint_result.summary.processing_time_ms
                            },
                            "template_preview": lint_result.template_preview
                        }
                    }
                )
            else:
                logger.info(f"Template validation passed: {lint_result.summary.completeness_score:.1f}% completeness score")
                if lint_result.warnings:
                    logger.info(f"Template has {lint_result.summary.total_warnings} warnings (non-blocking)")
            
        except Exception as e:
            logger.error(f"Template linting failed: {str(e)}")
            # Don't block processing on linting errors - just log and continue
            logger.warning("Continuing with template processing despite linting failure")
        
        # Stage 2: Template Loading and Image Processing
        try:
            document = DocxTemplate(file_path)
            logger.info("Template loaded successfully")
            
            # Process images if in enhanced mode
            if images_data:
                processed_images = process_images(images_data, document)
                # Merge template data with processed images
                context_data = template_data.copy()
                context_data.update(processed_images)
                logger.info(f"Enhanced mode: Context prepared with {len(context_data)} variables (including {len(processed_images)} images)")
            else:
                # Legacy mode: use template_data directly
                context_data = template_data
                logger.info(f"Legacy mode: Context prepared with {len(context_data)} variables")
            
            # Convert dictionary values to objects for dot notation access
            # This helps when templates use {{data.field}} but data is sent as {"data": {"field": "value"}}
            context_data_with_objects = {}
            for key, value in context_data.items():
                context_data_with_objects[key] = convert_dict_to_object(value)
            
            logger.info("Context data prepared with dot notation support")
            
        except Exception as e:
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Handle template errors
            template_error = handle_template_error(e, file.filename)
            return create_error_response(template_error, 400)
        
        # Stage 3: Template Rendering with Data Injection
        try:
            # Create custom Jinja2 environment with configurable undefined behavior
            from jinja2 import Environment
            
            # Choose undefined behavior: API parameter overrides environment variable
            # Options: "debug" (default), "silent", "strict"
            if api_undefined_behavior is not None:
                undefined_behavior = api_undefined_behavior.lower()
                logger.info(f"Using API-specified undefined behavior: {undefined_behavior}")
            else:
                undefined_behavior = os.environ.get("UNDEFINED_BEHAVIOR", "debug").lower()
                logger.info(f"Using environment-specified undefined behavior: {undefined_behavior}")
            
            if undefined_behavior == "debug":
                undefined_class = DebugUndefined
                logger.info("Using DebugUndefined - missing variables will show as [Missing variable: name]")
            elif undefined_behavior == "silent":
                undefined_class = SilentUndefined
                logger.info("Using SilentUndefined - missing variables will be empty")
            else:  # "strict" or any other value
                undefined_class = StrictUndefined
                logger.info("Using StrictUndefined - missing variables will raise errors")
            
            jinja_env = Environment(undefined=undefined_class)
            
            # Render template with context data (includes images if provided)
            document.render(context_data_with_objects, jinja_env)
            logger.info("Template rendered successfully")
            
        except Exception as e:
            # Log the actual error for debugging
            logger.error(f"Template rendering error: {type(e).__name__}: {str(e)}")
            logger.error(f"Template rendering traceback: {traceback.format_exc()}")
            
            # Handle the template error first
            template_error = handle_template_error(e, file.filename)
            
            # Clean up files after error handling
            for cleanup_path in [file_path]:
                if cleanup_path and os.path.exists(cleanup_path):
                    os.remove(cleanup_path)
            
            return create_error_response(template_error, 400)
        
        # Stage 4: Save Rendered Document
        try:
            document.save(file_path)
            logger.info("Rendered document saved successfully")
            
        except Exception as e:
            # Clean up files
            for cleanup_path in [file_path]:
                if cleanup_path and os.path.exists(cleanup_path):
                    os.remove(cleanup_path)
            
            error = FileProcessingError(
                message=f"Failed to save rendered document: {str(e)}",
                error_type="document_save_error",
                details={
                    "file_path": file_path,
                    "error": str(e)
                }
            )
            return create_error_response(error, 500)
        
        # Stage 5: PDF Conversion with Gotenberg
        try:
            gotenberg_url = get_env('GOTENBERG_API_URL')
            if not gotenberg_url:
                raise PDFConversionError(
                    message="Gotenberg service URL not configured",
                    error_type="gotenberg_not_configured",
                    details={"env_var": "GOTENBERG_API_URL"}
                )
            
            resource_url = f'{gotenberg_url}/forms/libreoffice/convert'
            
            logger.info(f"Converting to PDF via Gotenberg: {resource_url}")
            
            with open(file_path, 'rb') as doc_file:
                files = {'files': (file.filename, doc_file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                
                # Make request to Gotenberg with timeout
                response = requests.post(
                    url=resource_url, 
                    files=files,
                    timeout=60  # 60 second timeout
                )
            
            # Check Gotenberg response
            if response.status_code != 200:
                error_details = {
                    "gotenberg_url": resource_url,
                    "status_code": response.status_code,
                    "response_headers": dict(response.headers)
                }
                
                # Try to extract error message from response
                try:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        error_data = response.json()
                        error_details["error_data"] = error_data
                    else:
                        error_details["response_text"] = response.text[:500]  # First 500 chars
                except:
                    error_details["response_text"] = response.text[:500] if response.text else "No response text"
                
                if response.status_code == 400:
                    message = "Gotenberg rejected the document (bad request)"
                elif response.status_code == 422:
                    message = "Gotenberg could not process the document (unprocessable entity)"  
                elif response.status_code == 500:
                    message = "Gotenberg internal server error"
                else:
                    message = f"Gotenberg conversion failed with status {response.status_code}"
                
                error = PDFConversionError(
                    message=message,
                    error_type="gotenberg_conversion_failed",
                    details=error_details
                )
                return create_error_response(error, 500)
            
            # Validate response content
            if not response.content:
                error = PDFConversionError(
                    message="Gotenberg returned empty response",
                    error_type="empty_pdf_response",
                    details={"gotenberg_url": resource_url}
                )
                return create_error_response(error, 500)
            
            # Check if response is actually a PDF
            if not response.content.startswith(b'%PDF'):
                error = PDFConversionError(
                    message="Gotenberg response is not a valid PDF",
                    error_type="invalid_pdf_response",
                    details={
                        "gotenberg_url": resource_url,
                        "content_type": response.headers.get('content-type'),
                        "content_start": response.content[:100].decode('utf-8', errors='ignore')
                    }
                )
                return create_error_response(error, 500)
            
            logger.info(f"PDF conversion successful, size: {len(response.content)} bytes")
            
        except requests.exceptions.Timeout:
            error = PDFConversionError(
                message="Gotenberg request timed out (60s)",
                error_type="gotenberg_timeout",
                details={
                    "timeout_seconds": 60,
                    "suggestion": "Try with a smaller document or check Gotenberg service health"
                }
            )
            return create_error_response(error, 500)
            
        except requests.exceptions.ConnectionError as e:
            error = PDFConversionError(
                message=f"Cannot connect to Gotenberg service: {str(e)}",
                error_type="gotenberg_connection_error",
                details={
                    "gotenberg_url": gotenberg_url,
                    "connection_error": str(e),
                    "suggestion": "Check if Gotenberg service is running and accessible"
                }
            )
            return create_error_response(error, 500)
            
        except Exception as e:
            error = PDFConversionError(
                message=f"PDF conversion error: {str(e)}",
                error_type="pdf_conversion_error",
                details={
                    "gotenberg_url": gotenberg_url,
                    "error": str(e),
                    "error_class": type(e).__name__
                }
            )
            return create_error_response(error, 500)
        
        # Stage 6: Save PDF Response
        try:
            async with aiofiles.open(pdf_file_path, 'wb') as out_file:
                await out_file.write(response.content)
            
            logger.info(f"PDF saved successfully: {pdf_file_path}")
            
        except IOError as e:
            error = FileProcessingError(
                message=f"Failed to save PDF file: {str(e)}",
                error_type="pdf_save_error",
                details={
                    "pdf_path": pdf_file_path,
                    "io_error": str(e)
                }
            )
            return create_error_response(error, 500)
        
        # Success: Return PDF file
        return FileResponse(
            pdf_file_path, 
            media_type='application/pdf',
            filename=f"{base_name}.pdf"
        )
        
    except DocumentProcessingError as e:
        # Re-raise our custom errors to be handled by the error response
        logger.error(f"Document processing error: {e.message} - {e.details}")
        return create_error_response(e, 500)
        
    except Exception as e:
        # Unexpected error - log full traceback and return generic error
        logger.error(f"Unexpected error processing document: {str(e)}")
        logger.error(traceback.format_exc())
        
        error = DocumentProcessingError(
            message=f"An unexpected error occurred: {str(e)}",
            error_type="unexpected_error",
            details={
                "error": str(e),
                "error_class": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )
        return create_error_response(error, 500)
        
    finally:
        # Clean up temporary files (except the final PDF which FastAPI will handle)
        cleanup_files = []
        if file_path and file_path != pdf_file_path:
            cleanup_files.append(file_path)
        
        # Clean up temporary image files if they exist
        if 'processed_images' in locals():
            for image_obj in processed_images.values():
                if hasattr(image_obj, '_temp_file_path'):
                    temp_image_path = image_obj._temp_file_path
                    if temp_image_path and os.path.exists(temp_image_path):
                        cleanup_files.append(temp_image_path)
        
        for cleanup_file in cleanup_files:
            try:
                if cleanup_file and os.path.exists(cleanup_file):
                    os.remove(cleanup_file)
                    logger.debug(f"Cleaned up temporary file: {cleanup_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up file {cleanup_file}: {e}")

