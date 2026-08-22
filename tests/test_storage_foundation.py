from app.database.migrations import CURRENT_SCHEMA_VERSION, MIGRATIONS
from app.database.models import CandidateFact, CandidateProfile, ResumeProfile, SchemaMigration, SearchProfile, User


def test_schema_version_and_migration_are_declared():
    assert CURRENT_SCHEMA_VERSION == 1
    assert [m.version for m in MIGRATIONS] == [1]
    assert MIGRATIONS[0].name == "profile_storage_foundation"


def test_foundation_models_have_soft_delete_metadata():
    assert hasattr(User, "deleted_at")
    assert hasattr(CandidateProfile, "deleted_at")
    assert hasattr(CandidateFact, "deleted_at")
    assert hasattr(ResumeProfile, "deleted_at")
    assert hasattr(SearchProfile, "deleted_at")


def test_resume_has_persistent_storage_pointer():
    assert hasattr(ResumeProfile, "storage_path")


def test_schema_migration_model_exists():
    assert SchemaMigration.__tablename__ == "schema_migrations"
