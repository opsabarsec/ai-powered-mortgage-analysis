from docling import Document
from pydantic import BaseModel
from typing import Optional
import openai


class ApplicantIncomeData(BaseModel):
    raw_text: str
    income_info: Optional[str] = None
    compliance_status: Optional[str] = None


def ocr_extract_text(pdf_file):
    """Extract text from PDF using docling."""
    doc = Document.from_file(pdf_file)
    return doc.text


def parse_income_data(ocr_text):
    """
    A placeholder for NLP logic to extract income details from OCR text.
    In production, use spaCy or regex to pull out pay stubs, salary, taxes, etc.
    """
    # Example (replace with real extraction logic)
    if "income" in ocr_text.lower():
        return "Found income info (details here)."
    else:
        return "Income info not found."


def verify_compliance(income_data):
    """
    Use OpenAI GPT to verify compliance of extracted income data.
    """
    # Replace 'your-openai-api-key' with your actual OpenAI API key.
    openai.api_key = "your-openai-api-key"

    prompt = (
        "You are a mortgage compliance expert. "
        "Given the following extracted income data, determine if it meets standard mortgage compliance requirements. "
        "Reply with 'Compliant' or 'Incomplete: Needs manual review' and a brief reason.\n\n"
        f"Extracted Income Data:\n{income_data}\n"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a mortgage compliance expert."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=50,
            temperature=0,
        )
        gpt_reply = response.choices[0].message["content"].strip()
        # Extract only the compliance status from the reply
        if "Compliant" in gpt_reply:
            return "Compliant"
        else:
            return "Incomplete: Needs manual review"
    except Exception as e:
        return f"Error during compliance check: {e}"


if __name__ == "__main__":
    ocr_text = ocr_extract_text("sample_applicant.pdf")
    income = parse_income_data(ocr_text)
    result = verify_compliance(income)
    applicant_data = ApplicantIncomeData(
        raw_text=ocr_text, income_info=income, compliance_status=result
    )
    print("Applicant Data:", applicant_data.json(indent=2))
