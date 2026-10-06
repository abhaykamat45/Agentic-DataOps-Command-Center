import pytest
from pathlib import Path
from app.config import Settings, settings
from app.core.db_metadata import MetadataDB
from app.core.db_analytical import AnalyticalDB
from app.core.synthetic_data import SyntheticDataGenerator

@pytest.fixture(autouse=True)
def patch_settings(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    parquet_dir = data_dir / "parquet"
    db_path = data_dir / "metadata.db"
    logs_dir = data_dir / "logs"

    data_dir.mkdir(parents=True, exist_ok=True)
    parquet_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(settings, "DATA_DIR", data_dir)
    monkeypatch.setattr(settings, "METADATA_DB_PATH", db_path)
    monkeypatch.setattr(settings, "PARQUET_DIR", parquet_dir)
    monkeypatch.setattr(settings, "LOGS_DIR", logs_dir)
    
    return settings

@pytest.fixture
def test_meta_db(patch_settings):
    db = MetadataDB(db_path=patch_settings.METADATA_DB_PATH)
    db.init_db()
    return db

@pytest.fixture
def test_ana_db(patch_settings):
    db = AnalyticalDB(parquet_dir=patch_settings.PARQUET_DIR)
    return db

@pytest.fixture
def seeded_env(test_meta_db, test_ana_db):
    gen = SyntheticDataGenerator(test_meta_db, test_ana_db)
    gen.generate_all()
    return {"meta_db": test_meta_db, "ana_db": test_ana_db}
