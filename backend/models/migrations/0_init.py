from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "usermodel" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "email" VARCHAR(255),
        "password_hash" VARCHAR(255),
        "profile" JSON DEFAULT '{"name": "", "location": "", "notes": ""}',
        "app_state" JSON
    );
    CREATE TABLE IF NOT EXISTS "spacemodel" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "name" VARCHAR(255) NOT NULL,
        "description" TEXT,
        "is_archived" INT NOT NULL  DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS "presetmodel" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "name" VARCHAR(255) NOT NULL UNIQUE,
        "description" TEXT,
        "icon" VARCHAR(255),
        "plugins" JSON,
        "settings" JSON,
        "is_default" INT NOT NULL  DEFAULT 0,
        "is_custom" INT NOT NULL  DEFAULT 0,
        "is_active" INT NOT NULL  DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS "conversationmodel" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "title" VARCHAR(255) NOT NULL  DEFAULT 'New conversation',
        "space_id" INT REFERENCES "spacemodel" ("id") ON DELETE SET NULL,
        "preset_id" INT REFERENCES "presetmodel" ("id") ON DELETE SET NULL,
        "settings" JSON,
        "data" JSON,
        "is_archived" INT NOT NULL  DEFAULT 0,
        "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS "pluginregistrymodel" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "name" VARCHAR(255) NOT NULL,
        "display_name" VARCHAR(255) NOT NULL,
        "icon" TEXT,
        "description" TEXT,
        "author" VARCHAR(255),
        "url" VARCHAR(255),
        "version" VARCHAR(255),
        "settings" JSON,
        "functions" JSON,
        "is_enabled" BOOLEAN DEFAULT FALSE
    );
    CREATE TABLE IF NOT EXISTS "plugininstancemodel" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "name" TEXT NOT NULL,
        "plugin_id" INT NOT NULL REFERENCES "pluginregistrymodel" ("id") ON DELETE CASCADE,
        "conversation_id" INT NOT NULL REFERENCES "conversationmodel" ("id") ON DELETE CASCADE,
        "settings" JSON,
        "data" JSON,
        "functions" JSON
    );
    CREATE TABLE IF NOT EXISTS "integrationregistrymodel" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "name" VARCHAR(100) NOT NULL,
        "display_name" VARCHAR(100) NOT NULL,
        "auth_method" VARCHAR(100) NOT NULL,
        "data" JSON NOT NULL
    );
    CREATE TABLE IF NOT EXISTS "integrationinstancemodel" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "integration_id" INT NOT NULL REFERENCES "integrationregistrymodel" ("id") ON DELETE CASCADE,
        "credentials" JSON NOT NULL
    );
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
    );
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
    );
    CREATE TABLE IF NOT EXISTS "approvalrequestmodel" (
        "id" CHAR(36) NOT NULL  PRIMARY KEY,
        "conversation_id" INT NOT NULL REFERENCES "conversationmodel" ("id") ON DELETE CASCADE,
        "tool_name" VARCHAR(255) NOT NULL,
        "tool_args" JSON NOT NULL,
        "status" VARCHAR(20) NOT NULL  DEFAULT 'pending',
        "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS "migration" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "name" VARCHAR(255) NOT NULL UNIQUE,
        "applied_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS "documentmodel_conversationmodel" (
        "documentmodel_id" INT NOT NULL REFERENCES "documentmodel" ("id") ON DELETE CASCADE,
        "conversationmodel_id" INT NOT NULL REFERENCES "conversationmodel" ("id") ON DELETE CASCADE
    );
    DROP TABLE IF EXISTS aerich;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """