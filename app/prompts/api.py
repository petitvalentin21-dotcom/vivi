from fastapi import APIRouter, HTTPException, Query

from app.prompts.loader import DEFAULT_VERSION, list_prompts, list_versions, load_prompt
from app.prompts.schemas import PromptContentResponse, PromptListResponse


router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get(
    "",
    response_model=PromptListResponse,
    summary="Liste prompts et versions disponibles",
)
def list_prompts_endpoint() -> PromptListResponse:
    return PromptListResponse(
        current_version=DEFAULT_VERSION,
        versions=list_versions(),
        prompts=list_prompts(DEFAULT_VERSION),
    )


@router.get(
    "/{name}",
    response_model=PromptContentResponse,
    summary="Lire le contenu d'un prompt (endpoint de debug)",
)
def get_prompt_endpoint(
    name: str,
    version: str = Query(default=DEFAULT_VERSION, pattern=r"^v\d+$"),
) -> PromptContentResponse:
    try:
        content = load_prompt(name, version=version)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"prompt '{version}/{name}' not found",
        ) from exc
    return PromptContentResponse(
        name=name,
        version=version,
        content=content,
        char_count=len(content),
    )
