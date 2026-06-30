import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


def validate_api_key(api_key: str) -> bool:
    """
    Validate OpenAI API key format
    
    Args:
        api_key: OpenAI API key to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not api_key:
        return False
    
    # OpenAI API keys start with 'sk-'
    return api_key.startswith('sk-') and len(api_key) > 20


def validate_pdf_path(pdf_path: str) -> bool:
    """
    Validate that PDF file exists and is readable
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        True if file exists and readable, False otherwise
    """
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return False
    
    if not os.path.isfile(pdf_path):
        logger.error(f"Path is not a file: {pdf_path}")
        return False
    
    if not pdf_path.lower().endswith('.pdf'):
        logger.error(f"File is not a PDF: {pdf_path}")
        return False
    
    return True


def format_extracted_data(data: Dict) -> Dict:
    """
    Format extracted data for output
    
    Args:
        data: Raw extracted data
        
    Returns:
        Formatted data dictionary
    """
    formatted = {}
    
    for key, value in data.items():
        if value is None:
            formatted[key] = "N/A"
        elif isinstance(value, bool):
            formatted[key] = "Yes" if value else "No"
        elif isinstance(value, (list, dict)):
            formatted[key] = json.dumps(value, indent=2)
        else:
            formatted[key] = str(value).strip()
    
    return formatted


def get_file_size(file_path: str) -> float:
    """
    Get file size in MB
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)


def format_timestamp() -> str:
    """
    Get current timestamp in ISO format
    
    Returns:
        Formatted timestamp
    """
    return datetime.now().isoformat()


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def parse_extraction_instructions(instructions: str) -> List[str]:
    """
    Parse extraction instructions and return list of fields
    
    Args:
        instructions: Extraction instructions string
        
    Returns:
        List of fields to extract
    """
    # Split by common delimiters
    fields = []
    
    for delimiter in [',', ';', '\n', '-', '•']:
        if delimiter in instructions:
            fields = instructions.split(delimiter)
            break
    
    if not fields:
        fields = [instructions]
    
    # Clean up fields
    fields = [f.strip() for f in fields if f.strip()]
    
    return fields


def log_extraction_stats(num_pdfs: int, duration: float, success: bool) -> None:
    """
    Log extraction statistics
    
    Args:
        num_pdfs: Number of PDFs processed
        duration: Duration in seconds
        success: Whether extraction was successful
    """
    status = "SUCCESS" if success else "FAILED"
    avg_time = duration / num_pdfs if num_pdfs > 0 else 0
    
    logger.info(f"Extraction Stats - Status: {status}, PDFs: {num_pdfs}, Duration: {duration:.2f}s, Avg/PDF: {avg_time:.2f}s")
