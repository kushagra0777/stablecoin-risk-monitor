"""
Excel Data Importer
Handles importing equity and financial data from Excel files for risk analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import os


class ExcelImporter:
    """
    Import and transform Excel data into formats suitable for risk analysis
    """

    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls', '.csv']

    def import_file(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Import data from Excel file
        
        Args:
            file_path: Path to Excel file
            sheet_name: Optional sheet name (default: first sheet)
            
        Returns:
            DataFrame with imported data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}. Supported: {self.supported_formats}")

        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path, sheet_name=sheet_name or 0)
            
            return df
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")

    def import_from_bytes(self, file_bytes: bytes, filename: str) -> pd.DataFrame:
        """
        Import data from file bytes (for API uploads)
        
        Args:
            file_bytes: Binary file content
            filename: Original filename (used to determine format)
            
        Returns:
            DataFrame with imported data
        """
        import io
        
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")

        try:
            if file_ext == '.csv':
                df = pd.read_csv(io.BytesIO(file_bytes))
            else:
                df = pd.read_excel(io.BytesIO(file_bytes))
            
            return df
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")

    def transform_equity_to_snapshots(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Transform equity data to risk snapshot format
        
        Expected columns:
        - Company: Company name/identifier
        - bs_cash_cash_equivalents_and_sti: Cash and cash equivalents (reserves proxy)
        - eqy_float: Equity float (circulation metric)
        - eqy_sh_out: Equity shares outstanding (supply)
        - px_last: Last price
        
        Returns:
            List of snapshot dictionaries
        """
        snapshots = []
        
        # Standardize column names (handle various naming conventions)
        df.columns = df.columns.str.strip()
        
        # Map columns
        column_mapping = {
            'Company': 'company',
            'bs_cash_cash_equivalents_and_sti': 'cash_reserves',
            'eqy_float': 'float',
            'eqy_sh_out': 'shares_out',
            'px_last': 'price'
        }
        
        for idx, row in df.iterrows():
            try:
                # Extract values with safe conversion
                company = str(row.get('Company', f'Company_{idx}'))
                cash_reserves = float(row.get('bs_cash_cash_equivalents_and_sti', 0))
                equity_float = float(row.get('eqy_float', 0))
                shares_out = float(row.get('eqy_sh_out', 0))
                price = float(row.get('px_last', 0))
                
                # Calculate derived metrics
                market_cap = shares_out * price
                float_ratio = equity_float / (shares_out + 1e-9)
                cash_to_market_cap = cash_reserves / (market_cap + 1e-9)
                
                # Create snapshot in stablecoin format
                # Map: cash_reserves -> reserves, shares_out -> supply
                snapshot = {
                    'company': company,
                    'reserves': cash_reserves,  # Cash as reserves
                    'supply': shares_out,  # Total shares as supply
                    'price': price,
                    'whale_supply': shares_out - equity_float,  # Non-float shares (institutional holdings)
                    'custodians': [],  # No custodian breakdown in this dataset
                    
                    # Additional equity-specific metrics
                    'equity_float': equity_float,
                    'market_cap': market_cap,
                    'float_ratio': float_ratio,
                    'cash_to_market_cap': cash_to_market_cap,
                    
                    # Metadata
                    'timestamp': datetime.utcnow().isoformat(),
                    'data_type': 'equity'
                }
                
                snapshots.append(snapshot)
                
            except Exception as e:
                print(f"Warning: Error processing row {idx} for {row.get('Company', 'unknown')}: {str(e)}")
                continue
        
        return snapshots

    def validate_data(self, df: pd.DataFrame, required_columns: List[str]) -> tuple[bool, List[str]]:
        """
        Validate that DataFrame has required columns
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            
        Returns:
            Tuple of (is_valid, missing_columns)
        """
        df_columns = set(df.columns.str.strip())
        required_set = set(required_columns)
        
        missing = required_set - df_columns
        
        return (len(missing) == 0, list(missing))

    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics of imported data
        
        Args:
            df: DataFrame to summarize
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'null_counts': df.isnull().sum().to_dict(),
            'numeric_columns': list(df.select_dtypes(include=[np.number]).columns),
            'basic_stats': {}
        }
        
        # Add basic stats for numeric columns
        for col in summary['numeric_columns']:
            summary['basic_stats'][col] = {
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'mean': float(df[col].mean()),
                'median': float(df[col].median()),
                'std': float(df[col].std())
            }
        
        return summary


# Singleton instance
EXCEL_IMPORTER = ExcelImporter()


def import_excel_data(file_path: str, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to import Excel file and transform to snapshots
    
    Args:
        file_path: Path to Excel file
        sheet_name: Optional sheet name
        
    Returns:
        List of risk snapshots
    """
    df = EXCEL_IMPORTER.import_file(file_path, sheet_name)
    return EXCEL_IMPORTER.transform_equity_to_snapshots(df)
