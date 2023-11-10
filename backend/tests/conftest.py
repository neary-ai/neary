import os
import pytest
from starlette.testclient import TestClient
from backend.main import app, run_setup
from backend.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///tests/test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session(test_app):
    # Create a new database session for a test
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        # Close the session after the test
        session.close()

@pytest.fixture(scope="module")
def test_app(request):
    print('Running setup.')
    run_setup(SQLALCHEMY_DATABASE_URL)  # setup the database
    print('Setup complete.')
    # Override dependencies
    def _get_db_override():
        db = TestingSessionLocal()
        yield db
        db.close()

    app.dependency_overrides[get_db] = _get_db_override

    return app

@pytest.fixture(scope="module")
def client(test_app):
    return TestClient(test_app)

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db(request):
    def teardown():
        if os.path.exists("tests/test.db"):
            os.remove("tests/test.db")

    request.addfinalizer(teardown)
