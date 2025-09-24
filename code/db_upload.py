from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-supabase-service-role-key")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_applicant_analysis(applicant_id, extracted_text, income_data, compliance_status):
    """
    Store OCR & verification results in Supabase.
    """
    data = {
        "applicant_id": applicant_id,
        "ocr_text": extracted_text,
        "income_data": income_data,
        "compliance_status": compliance_status
    }
    result = supabase.table("applicant_analysis").insert(data).execute()
    return result

# Example usage
if __name__ == "__main__":
    # This data would come from your document analysis pipeline
    res = save_applicant_analysis(
        applicant_id="1234",
        extracted_text="John Doe net income $4800/month",
        income_data="Net Income: $4800/month",
        compliance_status="Compliant"
    )
    print(res)