from supabase import create_client, Client
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseIncomeUploader:
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize Supabase client."""
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def upload_income_data(
        self, income_json: Dict[str, Any], table_name: str = "income_data"
    ) -> Optional[Dict]:
        """
        Upload income JSON data to Supabase table.

        Args:
            income_json: The JSON object returned from parse_income_data()
            table_name: Name of the Supabase table (default: "income_data")

        Returns:
            Response from Supabase or None if error
        """
        try:
            # Insert data into Supabase table
            response = self.supabase.table(table_name).insert(income_json).execute()

            if response.data:
                logger.info(
                    f"Successfully uploaded income data with ID: {response.data[0].get('id', 'N/A')}"
                )
                return response.data[0]
            else:
                logger.error("No data returned from Supabase insert")
                return None

        except Exception as e:
            logger.error(f"Error uploading to Supabase: {e}")
            return None

    def batch_upload_income_data(
        self, income_data_list: list[Dict[str, Any]], table_name: str = "income_data"
    ) -> Optional[list]:
        """
        Upload multiple income records in batch.

        Args:
            income_data_list: List of JSON objects from parse_income_data()
            table_name: Name of the Supabase table

        Returns:
            List of inserted records or None if error
        """
        try:
            response = (
                self.supabase.table(table_name).insert(income_data_list).execute()
            )

            if response.data:
                logger.info(
                    f"Successfully uploaded {len(response.data)} income records"
                )
                return response.data
            else:
                logger.error("No data returned from Supabase batch insert")
                return None

        except Exception as e:
            logger.error(f"Error batch uploading to Supabase: {e}")
            return None


# SQL to create the Supabase table (run this in Supabase SQL editor)
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS income_data (
    id BIGSERIAL PRIMARY KEY,
    raw_text TEXT NOT NULL,
    income_info TEXT,
    compliance_status TEXT NOT NULL,
    extracted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    file_name TEXT,
    applicant_id TEXT,
    batch_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_income_data_applicant_id ON income_data(applicant_id);
CREATE INDEX IF NOT EXISTS idx_income_data_compliance_status ON income_data(compliance_status);
CREATE INDEX IF NOT EXISTS idx_income_data_created_at ON income_data(created_at);
"""
