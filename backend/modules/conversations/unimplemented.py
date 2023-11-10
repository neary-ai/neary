# def get_active_conversations(self):
#     return self.db.query(ConversationModel).filter(ConversationModel.is_archived == False).order_by(ConversationModel.updated_at.desc()).all()

# def update_conversation(self, conversation: ConversationModel, conversation_data: dict):
#     conversation.title = conversation_data.get('title', conversation.title)
#     conversation.settings = conversation_data.get(
#         'settings', conversation.settings)
#     self.db.commit()

# def archive_conversation(self, conversation: ConversationModel):
#     conversation.is_archived = True
#     self.db.commit()

# def update_conversation_settings(self, conversation: ConversationModel, settings: dict):
#     conversation.settings = settings
#     self.db.commit()

# def create_conversation(self, space_id: int = None, title: str = "New Conversation", preset: PresetModel = None):
#     space = self.db.query(SpaceModel).filter_by(id=space_id).first() if space_id else None
#     preset = preset if preset else self.db.query(PresetModel).filter_by(is_default=True).first()
#     conversation = ConversationModel(
#         title=title, space=space, preset=preset, settings=preset.settings)

#     self.db.add(conversation)
#     self.db.flush()  # flush the changes to assign an ID to conversation

#     for plugin in preset.plugins:
#         plugin_service.create_plugin_instance(self.db, plugin, conversation)

#     self.db.commit()
#     self.db.refresh(conversation)

#     return conversation

# def create_conversation_and_plugins(self, space_id: int, plugins: list):
#     conversation = self.create_conversation(self.db, space_id)
#     for plugin in plugins:
#         plugin_service.create_plugin_instance(self.db, plugin, conversation)
#     return conversation

# def update_conversation_space(self, conversation: ConversationModel, space_id: int = None):
#     space = self.db.query(SpaceModel).filter_by(id=space_id).first() if space_id else None
#     conversation.space = space
#     self.db.commit()

# def update_conversation_preset(self, conversation: ConversationModel, preset_data: dict):
#     if preset_data:
#         preset_id = preset_data.get('id')
#         if preset_id != conversation.preset_id:
#             preset = self.db.query(PresetModel).filter_by(
#                 id=preset_id).first()
#             conversation.preset = preset
#             conversation.settings = preset.settings
#             self.db.commit()

# def remove_plugins(self, conversation: ConversationModel, plugins_to_remove: set):
#     for plugin_name in plugins_to_remove:
#         plugin = self.db.query(PluginModel).filter_by(
#             name=plugin_name).first()
#         plugin_instance = self.db.query(PluginInstanceModel).filter_by(
#             plugin=plugin, conversation=conversation).first()
#         if plugin_instance:
#             self.db.delete(plugin_instance)
#             self.db.commit()

# def update_plugin_instance(self, conversation: ConversationModel, plugin: dict):
#     plugin = self.db.query(PluginModel).filter_by(
#         name=plugin["name"]).first()
#     if plugin is None:
#         print('Plugin not found: ', plugin["name"])
#         return
#     plugin_instance = self.db.query(PluginInstanceModel).filter_by(
#         plugin=plugin, conversation=conversation).first()
#     if plugin_instance is None:
#         plugin_instance = PluginInstanceModel(
#             name=plugin["name"], plugin=plugin, conversation=conversation, settings_values=plugin.get('settings', None))
#         self.db.add(plugin_instance)
#         self.db.commit()
#     return plugin_instance

# def enable_plugin(self, plugin: PluginModel):
#     plugin.is_enabled = True
#     self.db.commit()

def update_conversation_plugins(self, conversation: ConversationModel, new_plugin_data: list):
    existing_plugin_names = [plugin.name for plugin in conversation.plugins]
    new_plugin_names = [plugin["name"] for plugin in new_plugin_data]
    plugins_to_remove = set(existing_plugin_names) - set(new_plugin_names)

    remove_plugins(self.db, conversation, plugins_to_remove)

    for plugin in new_plugin_data:
        plugin_instance = update_plugin_instance(self.db, conversation, plugin)
        if plugin_instance:
            plugin_service.enable_plugin(self.db, plugin_instance.plugin)
            plugin_service.update_function_instances(
                self.db, plugin_instance, plugin["functions"])
            plugin_service.remove_function_instances(
                self.db, plugin_instance, plugin["functions"])

# def add_document_to_conversation(self, conversation: ConversationModel, document: DocumentModel):
#     conversation.documents.append(document)
#     self.db.commit()

# def remove_document_from_conversation(self, conversation: ConversationModel, document: DocumentModel):
#     conversation.documents.remove(document)
#     self.self.db.commit()
