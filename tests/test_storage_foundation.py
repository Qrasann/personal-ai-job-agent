from app.database.migrations import CURRENT_SCHEMA_VERSION, MIGRATIONS
from app.database.models import ApplicationStatusEvent, CandidateFact, CandidateProfile, ResumeProfile, SchemaMigration, SearchProfile, User


def test_schema_versions_and_migrations_are_declared():
    assert CURRENT_SCHEMA_VERSION == 5
    assert [m.version for m in MIGRATIONS] == [1, 2, 3, 4, 5]
    assert MIGRATIONS[0].name == "profile_storage_foundation"
    assert MIGRATIONS[1].name == "candidate_fact_experience_type"
    assert MIGRATIONS[2].name == "candidate_fact_confidence_provenance"
    assert MIGRATIONS[3].name == "job_match_recommendation_scores"
    assert MIGRATIONS[4].name == "application_status_history"


def test_foundation_models_have_soft_delete_metadata():
    assert hasattr(User, "deleted_at")
    assert hasattr(CandidateProfile, "deleted_at")
    assert hasattr(CandidateFact, "deleted_at")
    assert hasattr(ResumeProfile, "deleted_at")
    assert hasattr(SearchProfile, "deleted_at")


def test_candidate_fact_has_structured_experience_type():
    assert hasattr(CandidateFact, "experience_type")
    assert hasattr(CandidateFact, "confidence")
    assert hasattr(CandidateFact, "provenance")


def test_resume_has_persistent_storage_pointer():
    assert hasattr(ResumeProfile, "storage_path")


def test_schema_migration_model_exists():
    assert SchemaMigration.__tablename__ == "schema_migrations"


def test_application_status_event_model_is_append_only_record_shape():
    assert ApplicationStatusEvent.__tablename__ == "application_status_events"
    assert hasattr(ApplicationStatusEvent, "application_id")
    assert hasattr(ApplicationStatusEvent, "user_id")
    assert hasattr(ApplicationStatusEvent, "status")
    assert hasattr(ApplicationStatusEvent, "created_at")
