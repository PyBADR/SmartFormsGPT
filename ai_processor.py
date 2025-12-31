# ai_processor.py - AI Integration for Form Processing

import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from dotenv import load_dotenv
from logger import get_logger
import PyPDF2
from PIL import Image
import pytesseract

load_dotenv()
logger = get_logger(__name__)

class AIProcessor:
    """AI-powered document processor for claim forms."""
    
    def __init__(self):
        """Initialize AI processor with OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        # Load prompts
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load AI prompts from file."""
        try:
            with open("prompts/prompt.txt", "r") as f:
                content = f.read()
            
            # Parse prompts by sections
            prompts = {}
            sections = content.split("##")
            for section in sections:
                if section.strip():
                    lines = section.strip().split("\n", 1)
                    if len(lines) == 2:
                        key = lines[0].strip().lower().replace(" ", "_")
                        prompts[key] = lines[1].strip()
            
            return prompts
        except Exception as e:
            logger.error(f"Error loading prompts: {e}")
            return {}
    
    def extract_text_from_pdf(self, file_path: str) -> Tuple[str, int]:
        """
        Extract text from PDF file.
        
        Returns:
            Tuple of (extracted_text, page_count)
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            logger.info(f"Extracted {len(text)} characters from {page_count} pages")
            return text, page_count
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return "", 0
    
    def extract_text_from_image(self, file_path: str) -> str:
        """
        Extract text from image using OCR.
        
        Returns:
            Extracted text
        """
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            
            logger.info(f"Extracted {len(text)} characters from image")
            return text
        
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""
    
    def extract_claim_data(self, document_text: str) -> Dict:
        """
        Extract structured claim data from document text using AI.
        
        Returns:
            Dictionary with extracted claim data and confidence scores
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return {"error": "AI service not available"}
        
        try:
            # Prepare the extraction prompt
            system_prompt = self.prompts.get("system_prompt", "")
            extraction_prompt = self.prompts.get("extraction_prompt", "")
            
            full_prompt = f"{extraction_prompt}\n\nDocument Text:\n{document_text[:3000]}"
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Parse response
            result = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                extracted_data = json.loads(result)
            except json.JSONDecodeError:
                # If not JSON, return as text
                extracted_data = {"raw_response": result}
            
            logger.info("Successfully extracted claim data using AI")
            return extracted_data
        
        except Exception as e:
            logger.error(f"Error extracting claim data: {e}")
            return {"error": str(e)}
    
    def validate_extracted_data(self, extracted_data: Dict) -> Dict:
        """
        Validate extracted claim data using AI.
        
        Returns:
            Validation report with errors and warnings
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return {"error": "AI service not available"}
        
        try:
            validation_prompt = self.prompts.get("validation_prompt", "")
            
            full_prompt = f"{validation_prompt}\n\nExtracted Data:\n{json.dumps(extracted_data, indent=2)}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a claim validation expert."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            
            try:
                validation_report = json.loads(result)
            except json.JSONDecodeError:
                validation_report = {"raw_response": result}
            
            logger.info("Successfully validated claim data using AI")
            return validation_report
        
        except Exception as e:
            logger.error(f"Error validating claim data: {e}")
            return {"error": str(e)}
    
    def get_decision_recommendation(self, claim_data: Dict) -> Dict:
        """
        Get AI recommendation for claim decision.
        
        Returns:
            Decision recommendation with reasoning
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return {"error": "AI service not available"}
        
        try:
            decision_prompt = self.prompts.get("decision_support_prompt", "")
            
            full_prompt = f"{decision_prompt}\n\nClaim Data:\n{json.dumps(claim_data, indent=2)}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a claim decision support expert."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            result = response.choices[0].message.content
            
            try:
                recommendation = json.loads(result)
            except json.JSONDecodeError:
                recommendation = {"raw_response": result}
            
            logger.info("Successfully generated decision recommendation using AI")
            return recommendation
        
        except Exception as e:
            logger.error(f"Error generating decision recommendation: {e}")
            return {"error": str(e)}
    
    def process_document(self, file_path: str, file_type: str) -> Dict:
        """
        Complete document processing pipeline.
        
        Args:
            file_path: Path to the document file
            file_type: Type of file (pdf, png, jpg, jpeg)
        
        Returns:
            Complete processing results including extracted data and validation
        """
        start_time = datetime.utcnow()
        
        # Extract text based on file type
        if file_type.lower() == 'pdf':
            text, page_count = self.extract_text_from_pdf(file_path)
        elif file_type.lower() in ['png', 'jpg', 'jpeg']:
            text = self.extract_text_from_image(file_path)
            page_count = 1
        else:
            return {"error": f"Unsupported file type: {file_type}"}
        
        if not text:
            return {"error": "No text could be extracted from document"}
        
        # Extract claim data
        extracted_data = self.extract_claim_data(text)
        
        # Validate extracted data
        validation_report = self.validate_extracted_data(extracted_data)
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            "extracted_text": text[:500],  # First 500 chars
            "page_count": page_count,
            "extracted_data": extracted_data,
            "validation_report": validation_report,
            "processing_time": processing_time,
            "timestamp": datetime.utcnow().isoformat()
        }


# Export
__all__ = ["AIProcessor"]
