from app.database.migrations import CURRENT_SCHEMA_VERSION, MIGRATIONS
from app.database.models import CandidateFact, CandidateProfile, ResumeProfile, SchemaMigration, SearchProfile, User


def test_schema_versions_and_migrations_are_declared():
    assert CURRENT_SCHEMA_VERSION == 2
    assert [m.version for m in MIGRATIONS] == [1, 2]
    assert MIGRATIONS[0].name == "profile_storage_foundation"
    assert MIGRATIONS[1].name == "candidate_fact_experience_type"


def test_foundation_models_have_soft_delete_metadata():
    assert hasattr(User, "deleted_at")
    assert hasattr(CandidateProfile, "deleted_at")
    assert hasattr(CandidateFact, "deleted_at")
    assert hasattr(ResumeProfile, "deleted_at")
    assert hasattr(SearchProfile, "deleted_at")


def test_candidate_fact_has_structured_experience_type():
    assert hasattr(CandidateFact, "experience_type")


def test_resume_has_persistent_storage_pointer():
    assert hasattr(ResumeProfile, "storage_path")


def test_schema_migration_model_exists():
    assert SchemaMigration.__tablename__ == "schema_migrations"
