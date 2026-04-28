"""API routes for data synchronization from various sources."""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Optional
import os
import tempfile
from app.services import excel_parser, sms_parser, digital_twin_sync
from app.models.schemas import DataSyncResponse

router = APIRouter()

@router.post("/sync/upload", response_model=DataSyncResponse, tags=["sync"])
async def sync_data_upload(
    file: UploadFile = File(...),
    source_type: str = Form(...)
):
    """
    Upload and sync financial data from CSV or Excel files.
    
    Args:
        file: CSV or Excel file to upload
        source_type: Type of data ('csv' or 'excel')
    
    Returns:
        DataSyncResponse with parsed and prefilled data
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    if not (file.filename.endswith('.csv') or file.filename.endswith(('.xlsx', '.xls'))):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
    try:
        # Read file content
        content = await file.read()
        
        # Parse based on source type
        if source_type == 'csv' or file.filename.endswith('.csv'):
            parsed_data = excel_parser.parse_excel_csv(content, file.filename)
        elif source_type == 'excel' or file.filename.endswith(('.xlsx', '.xls')):
            parsed_data = excel_parser.parse_excel_csv(content, file.filename)
        else:
            raise HTTPException(status_code=400, detail="Invalid source type")
        
        # Create sync response
        response = digital_twin_sync.create_sync_response(source_type, parsed_data)
        
        return DataSyncResponse(
            sync_id=response["sync_id"],
            source=response["source"],
            last_synced=response["last_synced"],
            detected=response["detected"],
            prefill_payload=response["prefill_payload"],
            summary=response["summary"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/sync/sms", response_model=DataSyncResponse, tags=["sync"])
async def sync_sms_data(sms_messages: List[str]):
    """
    Sync financial data from SMS messages.
    
    Args:
        sms_messages: List of SMS message strings
    
    Returns:
        DataSyncResponse with parsed SMS data
    """
    try:
        # Parse SMS messages
        parsed_data = sms_parser.parse_sms_messages(sms_messages)
        
        # Create sync response
        response = digital_twin_sync.create_sync_response('sms', parsed_data)
        
        return DataSyncResponse(
            sync_id=response["sync_id"],
            source=response["source"],
            last_synced=response["last_synced"],
            detected=response["detected"],
            prefill_payload=response["prefill_payload"],
            summary=response["summary"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing SMS data: {str(e)}")

@router.get("/sync/status/{sync_id}", tags=["sync"])
async def get_sync_status(sync_id: str):
    """
    Get status of a data sync operation.
    
    Args:
        sync_id: ID of the sync operation
    
    Returns:
        Status information
    """
    return {
        "sync_id": sync_id,
        "status": "completed",
        "processed_at": "current_time"
    }
