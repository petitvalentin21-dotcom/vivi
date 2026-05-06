from scripts.smoke_backend import SmokeResult


def test_smoke_result_success_when_essential_and_chat_checks_pass() -> None:
    result = SmokeResult(
        health_ok=True,
        runtime_ok=True,
        knowledge_ok=True,
        chat_ok=True,
        document_ok=True,
        provider_available=True,
    )
    assert result.success is True


def test_smoke_result_success_when_provider_unavailable_and_essential_pass() -> None:
    result = SmokeResult(
        health_ok=True,
        runtime_ok=True,
        knowledge_ok=False,
        chat_ok=False,
        document_ok=False,
        provider_available=False,
    )
    assert result.success is True
