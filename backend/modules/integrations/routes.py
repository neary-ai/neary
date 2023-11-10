import json
from typing import List
from fastapi import HTTPException, APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
from config import settings
from .services.integration_service import IntegrationService, OAuthHandler
from .models import *
from .schemas import IntegrationCreate, Integration

router = APIRouter()


@router.post("/integrations", response_model=List[Integration])
async def new_integration(
    integration: IntegrationCreate, db: Session = Depends(get_db)
):
    integration_service = IntegrationService(db)
    # Retrieve the existing integration from the database
    existing_integration = integration_service.get_integration_by_id(integration.id)

    # If the integration does not exist, return a 404 error
    if existing_integration is None:
        raise HTTPException(status_code=404, detail="Integration not found")

    # Check if an instance of the integration already exists
    existing_instance = integration_service.get_integration_instance(
        existing_integration
    )

    if existing_instance:
        # If an instance already exists, update it
        integration_service.update_integration_credentials(
            existing_instance, {"api_key": integration.api_key}
        )
    else:
        # If no instance exists, create a new one
        integration_service.create_integration_instance(
            existing_integration, {"api_key": integration.api_key}
        )

    # Retrieve all entries in the integration registry
    all_integrations = integration_service.get_integrations()

    # Return the integrations
    return all_integrations


@router.put("/integrations/{integration_id}", response_model=List[Integration])
async def disconnect_integration(
    integration_id: int,
    db: Session = Depends(get_db),
):
    integration_service = IntegrationService(db)
    integration_service.disconnect_integration(integration_id)
    all_integrations = integration_service.get_integrations()

    return all_integrations


@router.get("/start_oauth/{integration_id}")
async def start_oauth(integration_id: int, db: Session = Depends(get_db)):
    integration = IntegrationService(db).get_integration_by_id(integration_id)

    if integration.auth_method != "oauth":
        raise HTTPException(
            status_code=400, detail="This integration does not use OAuth."
        )

    oauth_handler = OAuthHandler(integration)

    auth_url = oauth_handler.get_auth_url()

    return {"auth_url": auth_url}


@router.get("/oauth2/callback")
async def oauth_callback(request: Request, db: Session = Depends(get_db)):
    integration_service = IntegrationService(db)
    full_url = str(request.url)

    # Get the integration from the state parameter
    state = request.query_params.get("state")
    state_data = json.loads(state)
    integration_id = state_data["integration_id"]
    integration = integration_service.get_integration_by_id(integration_id)

    # Use the OAuthHandler to fetch the token
    oauth_handler = OAuthHandler(integration)
    credentials = oauth_handler.fetch_token(full_url)

    instance = integration_service.get_integration_instance(integration)

    if instance is None:
        integration_service.create_integration_instance(integration, credentials)
    else:
        integration_service.update_integration_credentials(instance, credentials)

    # Redirect the user to a frontend route
    base_url = settings.application.get("base_url", "http://localhost:8000")
    return RedirectResponse(url=base_url, status_code=302)
