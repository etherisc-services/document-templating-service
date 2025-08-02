from fastapi import Body, FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import Json
from docxtpl import DocxTemplate
import aiofiles
from utils import remove_temporary_files, get_env
import requests
import os
import traceback
import json
from typing import Dict, Any
from jinja2 import TemplateSyntaxError, UndefinedError, TemplateRuntimeError, TemplateNotFound
from jinja2.exceptions import TemplateError
from docx.opc.exceptions import PackageNotFoundError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        return TemplateProcessingError(
            message=f"Undefined variable in template: {str(e)}",
            error_type="undefined_variable",
            details={
                "file": file_path,
                "undefined_variable": str(e),
                "suggestion": "Check your template variables match the provided data"
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

app = FastAPI(
    title="Document Template Processing Service",
    description="""
        This is the documentation of the REST API exposed by the document template processing microservice.
        This will allow you to inject data in a specific word document template and get the pdf format as a result. 🚀🚀🚀
    """,
    version="1.1.0"
)

SERVICE_STATUS = {'status': 'Service is healthy !'}

@app.get('/')
async def livenessprobe():
    remove_temporary_files()
    return SERVICE_STATUS

@app.get('/health-check')
async def healthcheck():
    remove_temporary_files()
    return SERVICE_STATUS

@app.post('/api/v1/process-template-document')
async def process_document_template(data: Json = Body(...), file: UploadFile = File(...)):
    """
    Process a Word document template with data injection and convert to PDF.
    
    Handles all stages with comprehensive error reporting:
    - File validation and upload
    - Template syntax validation  
    - Data injection with variable checking
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
        
        if data is None or (isinstance(data, (list, dict)) and len(data) == 0):
            error = TemplateProcessingError(
                message="No template data provided",
                error_type="missing_template_data",
                details={
                    "requirement": "Provide JSON data for template variable injection",
                    "example": '{"name": "John", "company": "Acme Corp"}'
                }
            )
            return create_error_response(error, 400)
        
        # Validate data is proper JSON
        try:
            if isinstance(data, str):
                data = json.loads(data)
        except json.JSONDecodeError as e:
            error = TemplateProcessingError(
                message=f"Invalid JSON data: {str(e)}",
                error_type="invalid_json",
                details={
                    "json_error": str(e),
                    "line": getattr(e, 'lineno', None),
                    "column": getattr(e, 'colno', None)
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
        
        logger.info(f"Processing template: {file.filename} with data keys: {list(data.keys()) if isinstance(data, dict) else 'non-dict data'}")
        
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
        
        # Stage 2: Template Loading and Validation
        try:
            document = DocxTemplate(file_path)
            logger.info("Template loaded successfully")
            
        except Exception as e:
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            if "not a valid" in str(e).lower() or "corrupt" in str(e).lower():
                error = FileProcessingError(
                    message="Invalid or corrupted .docx file",
                    error_type="invalid_docx_format",
                    details={
                        "file": file.filename,
                        "error": str(e),
                        "suggestion": "Ensure the file is a valid Microsoft Word .docx document"
                    }
                )
                return create_error_response(error, 400)
            else:
                error = FileProcessingError(
                    message=f"Failed to load template: {str(e)}",
                    error_type="template_load_error",
                    details={
                        "file": file.filename,
                        "error": str(e)
                    }
                )
                return create_error_response(error, 500)
        
        # Stage 3: Template Rendering with Data Injection
        try:
            # Validate template by attempting to render
            document.render(data)
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
        
        for cleanup_file in cleanup_files:
            try:
                if cleanup_file and os.path.exists(cleanup_file):
                    os.remove(cleanup_file)
                    logger.debug(f"Cleaned up temporary file: {cleanup_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up file {cleanup_file}: {e}")