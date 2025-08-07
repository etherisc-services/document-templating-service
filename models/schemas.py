"""
Pydantic models for the DocX Jinja Linter API.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum


class LintResponseFormat(str, Enum):
    """Response format options for linting."""
    PDF = "pdf"
    JSON = "json"


class LintOptions(BaseModel):
    """Configuration options for linting behavior."""
    verbose: bool = Field(False, description="Enable verbose output with additional details")
    check_undefined_vars: bool = Field(True, description="Check for undefined variables in templates")
    max_line_length: int = Field(200, description="Maximum line length for warnings")
    fail_on_warnings: bool = Field(False, description="Treat warnings as errors")
    check_tag_matching: bool = Field(True, description="Check for matching Jinja tag pairs")
    check_nested_structure: bool = Field(True, description="Validate nested tag structure")
    response_format: LintResponseFormat = Field(LintResponseFormat.PDF, description="Response format: PDF report or JSON data")


class LintErrorType(str, Enum):
    """Types of linting errors."""
    SYNTAX_ERROR = "syntax_error"
    UNCLOSED_TAG = "unclosed_tag" 
    MISMATCHED_TAG = "mismatched_tag"
    NESTED_ERROR = "nested_error"
    UNDEFINED_VARIABLE = "undefined_variable"
    INVALID_EXPRESSION = "invalid_expression"
    DOCUMENT_ERROR = "document_error"


class LintWarningType(str, Enum):
    """Types of linting warnings."""
    LONG_LINE = "long_line"
    UNUSED_VARIABLE = "unused_variable"
    COMPLEX_EXPRESSION = "complex_expression"
    SUSPICIOUS_SYNTAX = "suspicious_syntax"


class LintError(BaseModel):
    """Represents a linting error found in the template."""
    line_number: Optional[int] = Field(None, description="Line number where error occurs")
    column: Optional[int] = Field(None, description="Column number where error occurs")
    error_type: LintErrorType = Field(..., description="Type of error found")
    message: str = Field(..., description="Human-readable error message")
    context: Optional[str] = Field(None, description="Surrounding code context")
    tag_name: Optional[str] = Field(None, description="Name of problematic Jinja tag")
    suggestion: Optional[str] = Field(None, description="Suggested fix for the error")


class LintWarning(BaseModel):
    """Represents a linting warning found in the template."""
    line_number: Optional[int] = Field(None, description="Line number where warning occurs")
    column: Optional[int] = Field(None, description="Column number where warning occurs")
    warning_type: LintWarningType = Field(..., description="Type of warning")
    message: str = Field(..., description="Human-readable warning message")
    context: Optional[str] = Field(None, description="Surrounding code context")
    suggestion: Optional[str] = Field(None, description="Suggested improvement")


class LintSummary(BaseModel):
    """Summary statistics of the linting results."""
    total_errors: int = Field(..., description="Total number of errors found")
    total_warnings: int = Field(..., description="Total number of warnings found")
    template_size: int = Field(..., description="Size of template in characters")
    lines_count: int = Field(..., description="Number of lines in template")
    jinja_tags_count: int = Field(0, description="Number of Jinja tags found")
    completeness_score: Optional[float] = Field(None, description="Template completeness score (0-100)")
    processing_time_ms: Optional[float] = Field(None, description="Time taken to process in milliseconds")


class LintResult(BaseModel):
    """Complete linting results for a DocX template."""
    success: bool = Field(..., description="Whether linting completed successfully")
    errors: List[LintError] = Field(default_factory=list, description="List of errors found")
    warnings: List[LintWarning] = Field(default_factory=list, description="List of warnings found")
    summary: LintSummary = Field(..., description="Summary statistics")
    template_content: Optional[str] = Field(None, description="Extracted template content")
    template_preview: Optional[str] = Field(None, description="First 500 characters of template")
    
    @property
    def has_errors(self) -> bool:
        """Check if any errors were found."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if any warnings were found."""
        return len(self.warnings) > 0


class DocxLinterException(Exception):
    """Base exception for DocX linter errors."""
    pass


class InvalidFileFormatException(DocxLinterException):
    """Exception raised when file format is invalid."""
    pass


class TemplateSyntaxException(DocxLinterException):
    """Exception raised when template syntax is invalid."""
    pass


class DocumentExtractionException(DocxLinterException):
    """Exception raised when document content extraction fails."""
    pass