from docling import Document
from pydantic import BaseModel
from typing import Optional, Dict, Any
from pydantic_ai import Agent
import asyncio
import json


class IncomeExtractionResult(BaseModel):
    income_summary: str
    compliance_status: str


def ocr_extract_text(file_path):
    """Extract text from PDF using docling."""
    doc = Document.from_file(file_path)
    return doc.text


# Initialize the Pydantic AI Agent
income_agent = Agent(
    "openai:gpt-4",
    result_type=IncomeExtractionResult,
    system_prompt=(
        "You are an expert at extracting income details from mortgage documents. "
        "Analyze the provided document text and extract key income information "
        "(salary, wages, bonuses, employment details, etc.). "
        "Then determine if the documentation meets standard mortgage compliance requirements. "
        "Provide a clear income summary and set compliance_status to either 'Compliant' "
        "or 'Incomplete: Needs manual review' based on completeness and verification requirements."
    ),
)


def parse_income_data(ocr_text) -> Dict[str, Any]:
    """
    Extract income details and compliance status from OCR text using Pydantic AI Agent.
    Returns a JSON object (dict) that can be uploaded to a database table.
    """

    try:
        # Run the agent to extract income information
        result = asyncio.run(_extract_income_async(ocr_text))

        # Create the JSON object for database upload
        json_result = {
            "raw_text": ocr_text,
            "income_info": result.income_summary,
            "compliance_status": result.compliance_status,
            # Add timestamp for tracking
            "extracted_at": asyncio.run(_get_current_timestamp()),
        }

        return json_result

    except Exception as e:
        # Return a properly formatted JSON object even on error
        return {
            "raw_text": ocr_text,
            "income_info": None,
            "compliance_status": f"Error during income extraction: {e}",
            "extracted_at": asyncio.run(_get_current_timestamp()),
        }


async def _get_current_timestamp():
    """Get current timestamp as ISO string."""
    from datetime import datetime

    return datetime.now().isoformat()


async def _extract_income_async(ocr_text) -> IncomeExtractionResult:
    """Async helper function to run the Pydantic AI agent."""
    prompt = (
        f"Analyze the following document text and extract income information:\n\n"
        f"Document text:\n{ocr_text}\n\n"
        f"Please provide:\n"
        f"1. A summary of all income-related information found\n"
        f"2. Compliance status based on mortgage documentation requirements"
    )

    result = await income_agent.run(prompt)
    return result.data
