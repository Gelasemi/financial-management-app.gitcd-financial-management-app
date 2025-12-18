import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
import logging

from ..models import Report, PnLData, RedFlag, EntityAnalysis

logger = logging.getLogger(__name__)

def process_excel_file(file_path: str, report_id: int, db: Session):
    """
    Process an Excel file and store the data in the database.
    
    Args:
        file_path: Path to the Excel file
        report_id: ID of the report to associate the data with
        db: Database session
    """
    try:
        # Read all sheets from the Excel file
        excel_file = pd.ExcelFile(file_path)
        
        # Process each sheet
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            if sheet_name == "PnL Summary":
                process_pnl_summary_sheet(df, report_id, db)
            elif sheet_name == "RECONCILIATION":
                process_reconciliation_sheet(df, report_id, db)
            elif sheet_name == "Red flags":
                process_red_flags_sheet(df, report_id, db)
            elif sheet_name == "Analysis Per Entity":
                process_entity_analysis_sheet(df, report_id, db)
            # Add more sheet processing as needed
        
        # Commit all changes
        db.commit()
        logger.info(f"Successfully processed Excel file: {file_path}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing Excel file: {str(e)}")
        raise

def process_pnl_summary_sheet(df: pd.DataFrame, report_id: int, db: Session):
    """Process the P&L Summary sheet."""
    try:
        # Skip the first few rows which contain headers
        df = df.iloc[3:].reset_index(drop=True)
        
        # Rename columns for easier processing
        df.columns = [
            'account_name', 'jan', 'feb', 'mar', 'apr', 'may', 'jun',
            'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'total'
        ]
        
        # Process each row
        for _, row in df.iterrows():
            account_name = row['account_name']
            
            # Skip empty rows or headers
            if pd.isna(account_name) or account_name in ['Account Name', '']:
                continue
            
            # Determine category based on account name
            category = determine_category(account_name)
            
            # Process monthly data
            for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']:
                value = row[month]
                
                if pd.notna(value) and value != 0:
                    # Convert to numeric if it's a string
                    if isinstance(value, str):
                        value = value.replace(',', '').replace('$', '').replace('(', '-').replace(')', '')
                        try:
                            value = float(value)
                        except ValueError:
                            continue
                    
                    # Create PnLData record
                    pnl_data = PnLData(
                        report_id=report_id,
                        account_name=account_name,
                        category=category,
                        month=f"2025-{month_to_number(month)}",
                        actuals=value
                    )
                    db.add(pnl_data)
        
        logger.info(f"Processed P&L Summary sheet for report {report_id}")
        
    except Exception as e:
        logger.error(f"Error processing P&L Summary sheet: {str(e)}")
        raise

def process_reconciliation_sheet(df: pd.DataFrame, report_id: int, db: Session):
    """Process the RECONCILIATION sheet."""
    try:
        # Skip the first row which contains headers
        df = df.iloc[1:].reset_index(drop=True)
        
        # Rename columns for easier processing
        df.columns = [
            'id', 'account_name', 'type', 'jan', 'feb', 'mar', 'apr', 'may', 'jun',
            'jul', 'aug', 'ytd'
        ]
        
        # Process each row
        for _, row in df.iterrows():
            account_name = row['account_name']
            type_val = row['type']
            
            # Skip empty rows or headers
            if pd.isna(account_name) or account_name in ['Account Name', '']:
                continue
            
            # Only process "Actual HL" rows
            if type_val != 'Actual HL':
                continue
            
            # Determine category based on account name
            category = determine_category(account_name)
            
            # Process monthly data
            for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug']:
                value = row[month]
                
                if pd.notna(value) and value != 0:
                    # Convert to numeric if it's a string
                    if isinstance(value, str):
                        value = value.replace(',', '').replace('$', '').replace('(', '-').replace(')', '')
                        try:
                            value = float(value)
                        except ValueError:
                            continue
                    
                    # Create PnLData record
                    pnl_data = PnLData(
                        report_id=report_id,
                        account_name=account_name,
                        category=category,
                        month=f"2025-{month_to_number(month)}",
                        actuals=value
                    )
                    db.add(pnl_data)
        
        logger.info(f"Processed RECONCILIATION sheet for report {report_id}")
        
    except Exception as e:
        logger.error(f"Error processing RECONCILIATION sheet: {str(e)}")
        raise

def process_red_flags_sheet(df: pd.DataFrame, report_id: int, db: Session):
    """Process the Red flags sheet."""
    try:
        # Skip the first few rows which contain headers
        df = df.iloc[1:].reset_index(drop=True)
        
        # Rename columns for easier processing
        df.columns = [
            'no', 'account_name', 'total_revenue', 'total_cost', 'gross_profit', 'gpm', 'comment'
        ]
        
        # Process each row
        for _, row in df.iterrows():
            account_name = row['account_name']
            
            # Skip empty rows or headers
            if pd.isna(account_name) or account_name in ['Account Name', '']:
                continue
            
            # Extract project name and country from account name
            project_name, country = extract_project_and_country(account_name)
            
            # Extract GPM
            gpm = row['gpm']
            if isinstance(gpm, str):
                gpm = gpm.replace('%', '')
                try:
                    gpm = float(gpm)
                except ValueError:
                    gpm = 0
            
            # Extract comment
            comment = row['comment']
            
            # Create RedFlag record
            red_flag = RedFlag(
                report_id=report_id,
                project_name=project_name,
                country=country,
                gpm=gpm,
                comment=comment
            )
            db.add(red_flag)
        
        logger.info(f"Processed Red flags sheet for report {report_id}")
        
    except Exception as e:
        logger.error(f"Error processing Red flags sheet: {str(e)}")
        raise

def process_entity_analysis_sheet(df: pd.DataFrame, report_id: int, db: Session):
    """Process the Analysis Per Entity sheet."""
    try:
        # Find the start of the entity data
        entity_start = None
        for i, row in df.iterrows():
            if pd.notna(row.iloc[0]) and isinstance(row.iloc[0], str) and 'Revenue' in row.iloc[0]:
                entity_start = i
                break
        
        if entity_start is None:
            logger.warning("Could not find entity data in Analysis Per Entity sheet")
            return
        
        # Extract entity data
        entity_data = df.iloc[entity_start:].reset_index(drop=True)
        
        # Find all entities
        entities = []
        current_entity = None
        
        for i, row in entity_data.iterrows():
            if pd.notna(row.iloc[0]) and isinstance(row.iloc[0], str) and not row.iloc[0].startswith('Revenue'):
                current_entity = row.iloc[0]
                entities.append(current_entity)
        
        # Process each entity
        for entity in entities:
            # Find the rows for this entity
            entity_rows = entity_data[entity_data.iloc[0] == entity]
            
            if len(entity_rows) == 0:
                continue
            
            # Extract revenue data
            revenue_row = entity_data[entity_data.iloc[0] == 'Revenue']
            if len(revenue_row) > 0:
                revenue_data = revenue_row.iloc[0].iloc[1:].tolist()
                local_revenue = revenue_data[0] if len(revenue_data) > 0 and pd.notna(revenue_data[0]) else 0
                interco_revenue = revenue_data[1] if len(revenue_data) > 1 and pd.notna(revenue_data[1]) else 0
                total_revenue = revenue_data[2] if len(revenue_data) > 2 and pd.notna(revenue_data[2]) else 0
            else:
                local_revenue = interco_revenue = total_revenue = 0
            
            # Extract cost data
            cost_row = entity_data[entity_data.iloc[0] == 'Cost of Sales']
            if len(cost_row) > 0:
                cost_data = cost_row.iloc[0].iloc[1:].tolist()
                local_cost = cost_data[0] if len(cost_data) > 0 and pd.notna(cost_data[0]) else 0
                interco_cost = cost_data[1] if len(cost_data) > 1 and pd.notna(cost_data[1]) else 0
                total_cost = cost_data[2] if len(cost_data) > 2 and pd.notna(cost_data[2]) else 0
            else:
                local_cost = interco_cost = total_cost = 0
            
            # Calculate gross profit and GPM
            gross_profit = total_revenue - total_cost
            gpm = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # Create EntityAnalysis record
            entity_analysis = EntityAnalysis(
                report_id=report_id,
                entity_name=entity,
                local_revenue=local_revenue,
                interco_revenue=interco_revenue,
                total_revenue=total_revenue,
                local_cost=local_cost,
                interco_cost=interco_cost,
                total_cost=total_cost,
                gross_profit=gross_profit,
                gpm=gpm
            )
            db.add(entity_analysis)
        
        logger.info(f"Processed Analysis Per Entity sheet for report {report_id}")
        
    except Exception as e:
        logger.error(f"Error processing Analysis Per Entity sheet: {str(e)}")
        raise

def determine_category(account_name: str) -> str:
    """Determine the category of an account based on its name."""
    account_name_lower = account_name.lower()
    
    if 'revenue' in account_name_lower:
        return 'Revenue'
    elif 'cost' in account_name_lower or 'direct cost' in account_name_lower:
        return 'Direct Costs'
    elif 'opex' in account_name_lower or 'expense' in account_name_lower:
        return 'Opex'
    elif 'profit' in account_name_lower:
        return 'Profit'
    else:
        return 'Other'

def month_to_number(month: str) -> str:
    """Convert month abbreviation to month number."""
    month_map = {
        'jan': '01',
        'feb': '02',
        'mar': '03',
        'apr': '04',
        'may': '05',
        'jun': '06',
        'jul': '07',
        'aug': '08',
        'sep': '09',
        'oct': '10',
        'nov': '11',
        'dec': '12'
    }
    return month_map.get(month.lower(), '01')

def extract_project_and_country(account_name: str) -> tuple:
    """Extract project name and country from account name."""
    # Try to extract project name and country from the account name
    # This is a simplified implementation and may need to be adjusted based on the actual data format
    
    if '_' in account_name:
        parts = account_name.split('_')
        if len(parts) >= 2:
            project_name = parts[0]
            country = parts[1]
            return project_name, country
    
    # Default values if extraction fails
    return account_name, 'Unknown'