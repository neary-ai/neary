from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE "usermodel_new" (
            id INTEGER PRIMARY KEY,
            email TEXT,
            password_hash TEXT,
            profile JSON,
            app_state JSON
        );
        
        INSERT INTO "usermodel_new" (id, email, password_hash, profile, app_state)
        SELECT id, email, password_hash, profile, app_state FROM "usermodel";
        
        DROP TABLE "usermodel";
        
        ALTER TABLE "usermodel_new" RENAME TO "usermodel";
    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
    """