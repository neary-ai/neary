# def update_plugin_function_instances(
#     self, plugin_instance: models.PluginInstanceModel, plugin_functions: list
# ):
#     function_instances = plugin_instance.function_instances
#     for function in plugin_functions:
#         function_name = function["name"]
#         settings = function.get("settings") or {}
#         settings_values = {
#             key: value["value"]
#             if isinstance(value, dict) and "value" in value
#             else value
#             for key, value in settings.items()
#         }
#         existing_function_instance = None
#         for instance in function_instances:
#             if instance.name == function_name:
#                 existing_function_instance = instance
#         if existing_function_instance:
#             existing_function_instance.settings_values = settings_values
#             self.db.commit()
#         else:
#             function_registry = (
#                 self.db.query(models.FunctionModel)
#                 .filter_by(name=function_name)
#                 .first()
#             )
#             if function_registry is None:
#                 print("Function not found: ", function_name)
#                 return
#             function_instance = models.FunctionInstanceModel(
#                 name=function_name,
#                 function=function_registry,
#                 plugin_instance=plugin_instance,
#                 settings_values=settings_values,
#             )
#             self.db.add(function_instance)
#             self.db.commit()

# def remove_plugin_function_instances(
#     self, plugin_instance: models.PluginInstanceModel, plugin_functions: list
# ):
#     function_instances = plugin_instance.function_instances
#     for instance in function_instances:
#         if not any(
#             function["name"] == instance.name for function in plugin_functions
#         ):
#             self.db.delete(instance)
#             self.db.commit()


# def create_or_update_function(
#     self, function_name, function_details, plugin, function_type
# ):
#     function = self.get_function_by_name(self.db, function_name, plugin)

#     if function is None:
#         function = models.FunctionModel(
#             name=function_name, plugin=plugin, type=function_type
#         )

#     function_metadata = {}
#     integrations = []

#     # Add settings, parameters and other metadata
#     for details_key, details_value in function_details.items():
#         if details_key == "settings":
#             function.settings_metadata = details_value
#         elif details_key == "parameters":
#             function.parameters = details_value
#         elif details_key == "integrations":
#             integrations = details_value
#         else:
#             function_metadata[details_key] = details_value

#     function.metadata = function_metadata

#     self.db.add(function)
#     self.db.commit()
#     self.db.refresh(function)

#     # Add integrations
#     for integration_name in integrations:
#         integration = (
#             self.db.query(models.IntegrationModel)
#             .filter_by(name=integration_name)
#             .first()
#         )
#         if integration:
#             function.integrations.append(integration)
#             self.db.commit()

#     return function
