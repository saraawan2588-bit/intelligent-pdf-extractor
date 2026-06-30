import os
import json
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime

import pandas as pd
import pdfplumber
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Try importing Gemini first, fallback to OpenAI
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from langchain.chat_models import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntelligentExtractor:
    """
    Intelligent PDF Extractor using LangChain + Gemini (or OpenAI)
    Understands context and extracts specific data from PDFs
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "auto", provider: str = "auto"):
        """
        Initialize the extractor
        
        Args:
            api_key: API key (Gemini or OpenAI, auto-detected if not provided)
            model: Model to use (default: "auto" for auto-detection)
            provider: "gemini", "openai", or "auto" for auto-detection
        """
        self.provider = provider
        self.model = model
        self.llm = None
        
        # Auto-detect provider and model
        if provider == "auto":
            self.provider = self._detect_provider()
        
        # Initialize appropriate LLM
        if self.provider == "gemini":
            self._init_gemini(api_key)
        elif self.provider == "openai":
            self._init_openai(api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        logger.info(f"Initialized IntelligentExtractor with provider: {self.provider}, model: {self.model}")

    def _detect_provider(self) -> str:
        """
        Auto-detect which provider to use based on available API keys
        
        Returns:
            "gemini" or "openai"
        """
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if gemini_key and GEMINI_AVAILABLE:
            logger.info("Using Gemini API (FREE)")
            return "gemini"
        elif openai_key and OPENAI_AVAILABLE:
            logger.info("Using OpenAI API")
            return "openai"
        else:
            # Default to Gemini if available
            if GEMINI_AVAILABLE:
                return "gemini"
            elif OPENAI_AVAILABLE:
                return "openai"
            else:
                raise ValueError("No API provider available. Install required packages.")

    def _init_gemini(self, api_key: Optional[str] = None) -> None:
        """
        Initialize Google Gemini API
        
        Args:
            api_key: Gemini API key (if None, uses GEMINI_API_KEY env var)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("langchain_google_genai not installed. Run: pip install langchain-google-genai")
        
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
        
        model_name = self.model if self.model != "auto" else "gemini-pro"
        
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model_name,
            temperature=0.3,
            convert_system_message_to_human=True
        )
        self.provider = "gemini"
        self.model = model_name

    def _init_openai(self, api_key: Optional[str] = None) -> None:
        """
        Initialize OpenAI API
        
        Args:
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai not installed. Run: pip install openai")
        
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        model_name = self.model if self.model != "auto" else "gpt-4"
        
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            model_name=model_name,
            temperature=0.3,
            max_tokens=2000
        )
        self.provider = "openai"
        self.model = model_name

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract all text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text from PDF
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Extracting text from: {pdf_path}")
        
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                logger.info(f"Total pages: {len(pdf.pages)}")
                
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    text += f"\n--- Page {i+1} ---\n{page_text}"
            
            logger.info(f"Successfully extracted text from {pdf_path}")
            return text
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def extract_with_ai(self, text: str, instructions: str) -> Dict:
        """
        Use AI (Gemini/OpenAI) to intelligently extract data based on instructions
        
        Args:
            text: Text extracted from PDF
            instructions: Specific instructions on what to extract
            
        Returns:
            Dictionary with extracted data
        """
        logger.info(f"Using {self.provider} to extract data with instructions: {instructions}")
        
        prompt_template = PromptTemplate(
            input_variables=["text", "instructions"],
            template="""You are an intelligent document analysis assistant.

Your task is to carefully read the provided document text and extract ONLY the information requested.

IMPORTANT INSTRUCTIONS:
1. Extract ONLY what is requested
2. If information is not explicitly mentioned, try to infer from context
3. Return data in JSON format
4. For each extracted item, include a confidence level (0-1)
5. If you cannot find the information, set value to null

Document Text:
{text}

Extraction Instructions:
{instructions}

Please extract the requested information and return ONLY valid JSON (no other text):"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        
        try:
            response = chain.run(text=text, instructions=instructions)
            logger.info("AI extraction completed successfully")
            
            # Parse JSON response
            extracted_data = json.loads(response)
            return extracted_data
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            logger.error(f"Response: {response}")
            return {"error": "Failed to parse extraction result", "raw_response": response}
        
        except Exception as e:
            logger.error(f"Error during AI extraction: {str(e)}")
            raise

    def extract(self, pdf_path: str, instructions: str, return_format: str = "dataframe") -> Union[pd.DataFrame, Dict]:
        """
        Main extraction method
        
        Args:
            pdf_path: Path to PDF file
            instructions: What to extract from the PDF
            return_format: 'dataframe' or 'dict'
            
        Returns:
            Extracted data as DataFrame or Dict
        """
        # Step 1: Extract text from PDF
        pdf_text = self.extract_text_from_pdf(pdf_path)
        
        # Step 2: Use AI to extract specific data
        extracted_data = self.extract_with_ai(pdf_text, instructions)
        
        # Step 3: Format results
        if return_format == "dataframe":
            df = pd.DataFrame([extracted_data])
            return df
        else:
            return extracted_data

    def to_excel(self, data: Union[pd.DataFrame, Dict], output_path: str) -> None:
        """
        Export extracted data to Excel
        
        Args:
            data: Extracted data (DataFrame or Dict)
            output_path: Path to save Excel file
        """
        logger.info(f"Exporting data to Excel: {output_path}")
        
        try:
            if isinstance(data, dict):
                data = pd.DataFrame([data])
            
            # Add metadata
            data['extraction_timestamp'] = datetime.now().isoformat()
            data['provider'] = self.provider
            
            data.to_excel(output_path, index=False, sheet_name='Extracted Data')
            logger.info(f"Successfully saved to {output_path}")
        
        except Exception as e:
            logger.error(f"Error saving to Excel: {str(e)}")
            raise

    def batch_extract(self, pdf_paths: List[str], instructions: str) -> List[Dict]:
        """
        Extract data from multiple PDFs
        
        Args:
            pdf_paths: List of PDF file paths
            instructions: Extraction instructions
            
        Returns:
            List of extracted data dictionaries
        """
        logger.info(f"Starting batch extraction for {len(pdf_paths)} PDFs")
        
        results = []
        for i, pdf_path in enumerate(pdf_paths, 1):
            try:
                logger.info(f"Processing PDF {i}/{len(pdf_paths)}: {pdf_path}")
                data = self.extract(pdf_path, instructions, return_format="dict")
                data['source_file'] = pdf_path
                results.append(data)
            
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {str(e)}")
                results.append({
                    'source_file': pdf_path,
                    'error': str(e)
                })
        
        logger.info(f"Batch extraction completed. Processed {len(results)} PDFs")
        return results

    def batch_extract_to_excel(self, pdf_paths: List[str], instructions: str, output_path: str) -> None:
        """
        Extract from multiple PDFs and save to single Excel file
        
        Args:
            pdf_paths: List of PDF file paths
            instructions: Extraction instructions
            output_path: Output Excel file path
        """
        results = self.batch_extract(pdf_paths, instructions)
        df = pd.DataFrame(results)
        self.to_excel(df, output_path)
