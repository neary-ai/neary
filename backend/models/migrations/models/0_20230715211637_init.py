from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "authcredentialmodel" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "provider" VARCHAR(255) NOT NULL,
    "auth_type" VARCHAR(255) NOT NULL,
    "data" JSON NOT NULL
) /* Represents authentication credentials for use by programs. Each set of credentials has a provider, */;
CREATE TABLE IF NOT EXISTS "documentmodel" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "chunk_hash_id" VARCHAR(64) NOT NULL UNIQUE,
    "faiss_index" INT NOT NULL,
    "document_key" VARCHAR(255),
    "content" TEXT NOT NULL,
    "type" VARCHAR(255),
    "collection" VARCHAR(255),
    "title" VARCHAR(255),
    "source" VARCHAR(255),
    "timestamp" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "metadata" JSON
) /* Represents a document in the system. Each document has a hash ID, a FAISS index, */;
CREATE TABLE IF NOT EXISTS "programregistrymodel" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "class_name" VARCHAR(255) NOT NULL,
    "display_name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "icon" VARCHAR(255) NOT NULL
) /* Represents an entry in the program registry. Each entry has a class name, display name, */;
CREATE TABLE IF NOT EXISTS "programmodel" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "state" JSON,
    "settings" JSON,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "program_info_id" INT NOT NULL REFERENCES "programregistrymodel" ("id") ON DELETE CASCADE
) /* Represents a program in the system. Each program has a link to its information in the program registry, */;
CREATE TABLE IF NOT EXISTS "spacemodel" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "is_archived" INT NOT NULL  DEFAULT 0
) /* Represents a unique space, which is a container for conversations. */;
CREATE TABLE IF NOT EXISTS "conversationmodel" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "title" VARCHAR(255) NOT NULL  DEFAULT 'New conversation',
    "is_archived" INT NOT NULL  DEFAULT 0,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "program_id" INT REFERENCES "programmodel" ("id") ON DELETE CASCADE,
    "space_id" INT REFERENCES "spacemodel" ("id") ON DELETE CASCADE
) /* Represents a conversation within a space. Each conversation has a title, */;
CREATE TABLE IF NOT EXISTS "approvalrequestmodel" (
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "message_id" INT,
    "tool_name" VARCHAR(255) NOT NULL,
    "tool_args" JSON NOT NULL,
    "status" VARCHAR(20) NOT NULL  DEFAULT 'pending',
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "conversation_id" INT NOT NULL REFERENCES "conversationmodel" ("id") ON DELETE CASCADE
) /* Represents a request for approval to use a tool. Each request has a UUID, a link to the conversation */;
CREATE TABLE IF NOT EXISTS "messagemodel" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "role" VARCHAR(255) NOT NULL,
    "content" TEXT NOT NULL,
    "actions" JSON,
    "status" VARCHAR(255),
    "metadata" JSON,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_archived" INT NOT NULL  DEFAULT 0,
    "conversation_id" INT NOT NULL REFERENCES "conversationmodel" ("id") ON DELETE CASCADE
) /* Represents a message in a conversation. Each message has a role, content, actions, status, */;
CREATE TABLE IF NOT EXISTS "usermodel" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "profile" JSON,
    "onboarded" INT NOT NULL  DEFAULT 0,
    "app_state" JSON
) /* Represents the user in the system, storing authentication data and application-specific state. */;
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);
CREATE TABLE IF NOT EXISTS "documentmodel_conversationmodel" (
    "documentmodel_id" INT NOT NULL REFERENCES "documentmodel" ("id") ON DELETE CASCADE,
    "conversationmodel_id" INT NOT NULL REFERENCES "conversationmodel" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
