from analysis_main import parse_income_data, ocr_extract_text
from db_upload import SupabaseIncomeUploader
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_single_document(
    file_path: str, uploader: SupabaseIncomeUploader, applicant_id: str = None
) -> bool:
    """
    Process a single PDF document and upload to Supabase.

    Args:
        file_path: Path to the PDF file
        uploader: SupabaseIncomeUploader instance
        applicant_id: Optional applicant ID for tracking

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing document: {file_path}")

        # Extract text from PDF
        ocr_text = ocr_extract_text(file_path)

        # Parse income data (returns JSON object)
        income_json = parse_income_data(ocr_text)

        # Add additional metadata
        income_json["file_name"] = os.path.basename(file_path)
        if applicant_id:
            income_json["applicant_id"] = applicant_id

        # Upload to Supabase
        result = uploader.upload_income_data(income_json)

        if result:
            logger.info(f"Successfully uploaded record with ID: {result.get('id')}")
            return True
        else:
            logger.error("Failed to upload income data")
            return False

    except Exception as e:
        logger.error(f"Error processing document {file_path}: {e}")
        return False


def process_batch_documents(
    file_paths: list[str], uploader: SupabaseIncomeUploader, batch_id: str = None
) -> int:
    """
    Process multiple PDF documents and upload in batch.

    Args:
        file_paths: List of paths to PDF files
        uploader: SupabaseIncomeUploader instance
        batch_id: Optional batch ID for tracking

    Returns:
        Number of successfully processed documents
    """
    income_data_batch = []
    successful_count = 0

    for file_path in file_paths:
        try:
            logger.info(f"Processing document: {file_path}")

            # Extract and parse each document
            ocr_text = ocr_extract_text(file_path)
            income_json = parse_income_data(ocr_text)

            # Add metadata
            income_json["file_name"] = os.path.basename(file_path)
            if batch_id:
                income_json["batch_id"] = batch_id

            income_data_batch.append(income_json)

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            continue

    # Batch upload all processed documents
    if income_data_batch:
        result = uploader.batch_upload_income_data(income_data_batch)
        if result:
            successful_count = len(result)
            logger.info(f"Successfully uploaded {successful_count} records")
        else:
            logger.error("Failed to upload batch data")

    return successful_count


def main():
    """Main execution function."""

    # Initialize Supabase client with environment variables
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")  # or SUPABASE_SERVICE_ROLE_KEY

    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error(
            "Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables"
        )
        return

    # Create uploader instance
    uploader = SupabaseIncomeUploader(SUPABASE_URL, SUPABASE_KEY)

    # Example 1: Process a single PDF
    single_file_example(uploader)

    # Example 2: Process multiple PDFs in batch
    # batch_processing_example(uploader)


def single_file_example(uploader: SupabaseIncomeUploader):
    """Example of processing a single file."""

    file_path = "path/to/your/income_document.pdf"
    applicant_id = "APPL_12345"

    # Check if file exists
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return

    success = process_single_document(file_path, uploader, applicant_id)

    if success:
        print("✅ Document processed and uploaded successfully")
    else:
        print("❌ Failed to process document")


def batch_processing_example(uploader: SupabaseIncomeUploader):
    """Example of batch processing multiple files."""

    # List of PDF files to process
    pdf_files = [
        "path/to/document1.pdf",
        "path/to/document2.pdf",
        "path/to/document3.pdf",
    ]

    # Filter existing files
    existing_files = [f for f in pdf_files if os.path.exists(f)]

    if not existing_files:
        logger.error("No valid PDF files found")
        return

    batch_id = "BATCH_001"
    successful_count = process_batch_documents(existing_files, uploader, batch_id)

    print(
        f"✅ Successfully processed {successful_count}/{len(existing_files)} documents"
    )


if __name__ == "__main__":
    main()
