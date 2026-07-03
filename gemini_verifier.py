import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Define the structured output format required by the Google Gemini XPRIZE judges
class VerificationResult(BaseModel):
    confidence_score: int = Field(description="Integer from 0 to 100 representing hiring authenticity confidence.")
    verdict: str = Field(description="Must be exactly 'VERIFIED_ACTIVE' or 'FLAGGED_GHOST'.")
    reasoning_trace: str = Field(description="Detailed sentence outlining forensic anomalies or green flags discovered.")

def verify_listing_authenticity(raw_job_text: str, business_context: str) -> dict:
    """
    Evaluates job text using gemini-2.5-flash to filter out resume-harvesting and ghost ads.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "confidence_score": 0,
            "verdict": "FLAGGED_GHOST",
            "reasoning_trace": "Missing GEMINI_API_KEY environment variable. Verification failed."
        }
    
    try:
        # Initialize the official Google GenAI Client
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        You are a physics first-principles forensic data analyst investigating job market mechanics.
        Analyze the following text to determine if it is a genuine, active opening targeting an immediate hire, 
        or a zero-intent corporate 'Ghost Job' used for resume harvesting, brand presence, or stale data tracking.
        
        Job Listing Text: {raw_job_text}
        Business Context: {business_context}
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=VerificationResult,
                temperature=0.1
            )
        )
        
        # Safe extraction of the structured text token
        return json.loads(response.text)
        
    except Exception as e:
        return {
            "confidence_score": 0,
            "verdict": "FLAGGED_GHOST",
            "reasoning_trace": f"Gemini API Execution Error: {str(e)}"
        }
