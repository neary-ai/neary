from core.routes import router as core_router
from users.routes import router as user_router
from auth.routes import router as auth_router
from modules.conversations.routes import router as conversation_router
from modules.messages.routes import router as message_router
from modules.spaces.routes import router as space_router
from modules.presets.routes import router as preset_router
from modules.plugins.routes import router as plugin_router
from modules.documents.routes import router as document_router
from modules.integrations.routes import router as integration_router

routes = [
    (core_router, ""),
    (auth_router, "/auth"),
    (user_router, "/api"),
    (conversation_router, "/api"),
    (message_router, "/api"),
    (space_router, "/api"),
    (preset_router, "/api"),
    (plugin_router, "/api"),
    (document_router, "/api"),
    (integration_router, "/api"),
]
