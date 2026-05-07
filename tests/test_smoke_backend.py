from scripts.smoke_backend import SmokeResult


def test_smoke_result_success_when_no_failures() -> None:
    result = SmokeResult(
        ok_count=5,
        warn_count=1,
        fail_count=0,
        auth_enabled=False,
        provider_available=True,
        model_configured=True,
        knowledge_ok=True,
        chat_ok=True,
        document_ok=True,
        document_sources_count=1,
    )
    assert result.success is True


def test_smoke_result_fails_when_any_critical_failure_exists() -> None:
    result = SmokeResult(
        ok_count=3,
        warn_count=0,
        fail_count=1,
        auth_enabled=True,
        provider_available=False,
        model_configured=False,
        knowledge_ok=False,
        chat_ok=False,
        document_ok=False,
        document_sources_count=0,
    )
    assert result.success is False

