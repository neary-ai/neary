from sqlalchemy.orm import Session
from backend import models

def get_function_by_name(db: Session, function_name: str, plugin):
    return db.query(models.FunctionRegistryModel).filter_by(name=function_name, plugin=plugin).first()

def create_or_update_function(db: Session, function_name, function_details, plugin, function_type):
    function = get_function_by_name(db, function_name, plugin)

    if function is None:
        function = models.FunctionRegistryModel(name=function_name, plugin=plugin, type=function_type)

    function_metadata = {}
    integrations = []

    # Add settings, parameters and other metadata
    for details_key, details_value in function_details.items():
        if details_key == 'settings':
            function.settings_metadata = details_value
        elif details_key == 'parameters':
            function.parameters = details_value
        elif details_key == 'integrations':
            integrations = details_value
        else:
            function_metadata[details_key] = details_value

    function.metadata = function_metadata

    db.add(function)
    db.commit()
    db.refresh(function)

    # Add integrations
    for integration_name in integrations:
        integration = db.query(models.IntegrationRegistryModel).filter_by(name=integration_name).first()
        if integration:
            function.integrations.append(integration)
            db.commit()

    return function