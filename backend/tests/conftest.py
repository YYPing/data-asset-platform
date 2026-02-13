import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_all.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    from app.models.organization import Organization  # noqa
    from app.models.user import User  # noqa
    from app.models.asset import DataAsset  # noqa
    from app.models.stage import StageRecord  # noqa
    from app.models.material import StageMaterial  # noqa
    from app.models.audit import AuditLog  # noqa
    from app.models.approval import ApprovalRecord  # noqa
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr("app.core.config.settings.UPLOAD_DIR", str(tmp_path))
    yield
    Base.metadata.drop_all(bind=engine)
