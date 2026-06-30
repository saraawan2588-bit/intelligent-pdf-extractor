import os
import json
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime

import pandas as pd
import pdfplumber
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntelligentExtractor:
    """
    Intelligent PDF Extractor using LangChain + GPT-4
    Understands context and extracts specific data from PDFs
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the extractor
        
        Args:
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            model: Model to use (default: gpt-4)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.llm = ChatOpenAI(
            openai_api_key=self.api_key,
            model_name=self.model,
            temperature=0.3,
            max_tokens=2000
        )
        logger.info(f"Initialized IntelligentExtractor with model: {self.model}")

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
        Use GPT-4 to intelligently extract data based on instructions
        
        Args:
            text: Text extracted from PDF
            instructions: Specific instructions on what to extract
            
        Returns:
            Dictionary with extracted data
        """
        logger.info(f"Using AI to extract data with instructions: {instructions}")
        
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
