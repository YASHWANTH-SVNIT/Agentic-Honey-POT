import os
from fastapi import Header, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv

load_dotenv()

API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

import settings

async def get_api_key(api_key_header: str = Security(api_key_header)):
    expected_api_key = settings.API_KEY
    if api_key_header == expected_api_key:
        return api_key_header
    else:
        raise HTTPException(
            status_code=403, detail="Could not validate API key"
        )
