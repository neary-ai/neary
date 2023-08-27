import uuid
from tortoise import fields
from tortoise.models import Model


class UserModel(Model):
    """
    Represents the user in the system, storing authentication data and application-specific state.
    """
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, null=True)
    password_hash = fields.CharField(max_length=255, null=True)
    profile = fields.JSONField(
        default={"name": "", "location": "", "notes": ""})
    app_state = fields.JSONField(null=True)


class SpaceModel(Model):
    """
    Represents a unique space, which is a container for conversations.
    """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    is_archived = fields.BooleanField(default=False)

    conversations: fields.ReverseRelation["ConversationModel"]

    def __str__(self):
        return self.name

    async def serialize(self):
        conversations = await self.conversations.filter(is_archived=False).all()
        conversation_ids = [conversation.id for conversation in conversations]

        space_data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "conversations": conversation_ids,
        }

        return space_data


class ConversationModel(Model):
    """
    Represents a conversation within a space. Each conversation has a title,
    a link to the space it's part of, and timestamps for when it was created and last updated.
    """
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, default="New conversation")
    space = fields.ForeignKeyField(
        "models.SpaceModel", related_name="conversations", null=True)
    preset = fields.ForeignKeyField(
        "models.PresetModel", related_name="conversations", on_delete=fields.SET_NULL, null=True)
    settings = fields.JSONField(null=True)
    data = fields.JSONField(null=True)
    is_archived = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    messages: fields.ReverseRelation["MessageModel"]
    plugins: fields.ReverseRelation["PluginInstanceModel"]
    documents: fields.ManyToManyRelation["DocumentModel"]
    approval_requests: fields.ReverseRelation["ApprovalRequestModel"]

    async def serialize(self):
        messages = await self.messages.all().order_by('created_at')
        recent_message = messages[-1].content if messages else None
        message_ids = [message.id for message in messages]

        plugins = await self.plugins.all()
        preset = await self.preset

        conversation_data = {
            "id": self.id,
            "space_id": self.space_id,
            "preset": preset.serialize(),
            "title": self.title,
            "settings": self.settings,
            "plugins": [await plugin.serialize() for plugin in plugins if plugin.is_enabled],
            "messages": message_ids,
            "excerpt": recent_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

        return conversation_data


class PresetModel(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    description = fields.TextField(null=True)
    icon = fields.CharField(max_length=255, null=True)
    plugins = fields.JSONField(null=True)
    settings = fields.JSONField(null=True)
    is_default = fields.BooleanField(default=False)
    is_custom = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "plugins": self.plugins,
            "settings": self.settings,
            "is_default": self.is_default,
            "is_custom": self.is_custom,
        }


class PluginRegistryModel(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    type = fields.CharField(max_length=255)
    display_name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    is_public = fields.BooleanField(default=True)
    is_active = fields.BooleanField(default=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "display_name": self.display_name,
            "description": self.description,
            "is_active": self.is_active,
        }


class PluginInstanceModel(Model):
    id = fields.IntField(pk=True)
    plugin = fields.ForeignKeyField(
        "models.PluginRegistryModel", related_name="instances")
    conversation = fields.ForeignKeyField(
        "models.ConversationModel", related_name="plugins")
    settings = fields.JSONField(null=True)
    data = fields.JSONField(null=True)
    is_enabled = fields.BooleanField(default=True)

    async def serialize(self):
        await self.fetch_related("plugin")
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "plugin_id": self.plugin_id,
            "name": self.plugin.name,
            "type": self.plugin.type,
            "display_name": self.plugin.display_name,
            "description": self.plugin.description,
            "settings": self.settings,
            "data": self.data,
            "is_enabled": self.is_enabled
        }


class IntegrationRegistryModel(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    display_name = fields.CharField(max_length=100)
    auth_method = fields.CharField(max_length=100)
    data = fields.JSONField()

    async def active_instance(self):
        return len(await self.instances.all()) > 0

    async def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "auth_method": self.auth_method,
            "data": self.data,
            "is_integrated": await self.active_instance()
        }


class IntegrationInstanceModel(Model):
    id = fields.IntField(pk=True)
    integration = fields.ForeignKeyField(
        'models.IntegrationRegistryModel', related_name='instances')
    credentials = fields.JSONField()


class MessageModel(Model):
    """
    Represents a message in a conversation. Each message has a role, content, actions, status,
    and a link to the conversation it's part of.
    """
    id = fields.IntField(pk=True)
    role = fields.CharField(max_length=255)
    content = fields.TextField()
    actions = fields.JSONField(null=True)
    status = fields.CharField(null=True, max_length=255)
    metadata = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_archived = fields.BooleanField(default=False)

    conversation: fields.ForeignKeyRelation[ConversationModel] = fields.ForeignKeyField(
        "models.ConversationModel", related_name="messages"
    )

    def serialize(self):
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "actions": self.actions,
            "metadata": self.metadata,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat(),
            "conversation_id": self.conversation_id,
        }


class DocumentModel(Model):
    """
    Represents a document in the system. Each document has a hash ID, a FAISS index,
    a key, content, and various metadata fields.
    """
    id = fields.IntField(pk=True)
    conversations = fields.ManyToManyField(
        "models.ConversationModel", related_name="documents")
    chunk_hash_id = fields.CharField(max_length=64, unique=True)
    faiss_index = fields.IntField()
    document_key = fields.CharField(max_length=255, null=True)
    content = fields.TextField()
    type = fields.CharField(max_length=255, null=True)
    collection = fields.CharField(max_length=255, null=True)
    title = fields.CharField(max_length=255, null=True)
    source = fields.CharField(max_length=255, null=True)
    timestamp = fields.DatetimeField(auto_now_add=True)
    metadata = fields.JSONField(null=True)

    async def serialize(self):
        conversation_ids = [c.id async for c in self.conversations]

        return {
            "id": self.id,
            "conversation_ids": conversation_ids,
            "chunk_hash_id": self.chunk_hash_id,
            "faiss_index": self.faiss_index,
            "document_key": self.document_key,
            "content": self.content,
            "type": self.type,
            "collection": self.collection,
            "title": self.title,
            "source": self.source,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata
        }


class ApprovalRequestModel(Model):
    """
    Represents a request for approval to use a tool. Each request has a UUID, a link to the conversation
    it's part of, the name and arguments of the tool, a status, and timestamps for when it was created and last updated.
    """
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    conversation = fields.ForeignKeyField(
        "models.ConversationModel", related_name="pending_tool_requests")
    tool_name = fields.CharField(max_length=255)
    tool_args = fields.JSONField()
    status = fields.CharField(max_length=20, default="pending")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def serialize(self):

        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class Migration(Model):
    """
    Represents a database migration.
    """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    applied_at = fields.DatetimeField(auto_now_add=True)
