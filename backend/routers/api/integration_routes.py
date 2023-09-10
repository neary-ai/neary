from fastapi import HTTPException, APIRouter, Body

from backend.models import IntegrationRegistryModel, IntegrationInstanceModel

router = APIRouter()


@router.get("")
async def get_integrations():
    print('getting integrations!')
    integrations = await IntegrationRegistryModel.filter()
    serialized = [await integration.serialize() for integration in integrations]
    return serialized

@router.post("")
async def new_integration(integration: dict = Body(...)):
    # Retrieve the existing integration from the database
    existing_integration = await IntegrationRegistryModel.get_or_none(id=integration['id'])

    # If the integration does not exist, return a 404 error
    if existing_integration is None:
        raise HTTPException(status_code=404, detail="Integration not found")

    # Check if an instance of the integration already exists
    existing_instance = await IntegrationInstanceModel.get_or_none(integration=existing_integration)

    if existing_instance:
        # If an instance already exists, update it
        existing_instance.credentials = {'api_key': integration['api_key']}
        await existing_instance.save()
    else:
        # If no instance exists, create a new one
        new_instance = IntegrationInstanceModel(
            integration=existing_integration,
            credentials={'api_key': integration['api_key']}
        )
        await new_instance.save()

    # Serialize all entries in the integration registry
    all_integrations = await IntegrationRegistryModel.all()
    serialized_integrations = [await integration.serialize() for integration in all_integrations]

    # Return the serialized integrations
    return serialized_integrations

@router.put("/{integration_id}")
async def disconnect_integration(integration_id: int):
    # Delete the instance
    integration_instance = await IntegrationInstanceModel.get_or_none(integration_id=integration_id)
    await integration_instance.delete()

    # Serialize all entries in the integration registry
    all_integrations = await IntegrationRegistryModel.all()
    serialized_integrations = [await integration.serialize() for integration in all_integrations]

    # Return the serialized integrations
    return serialized_integrations