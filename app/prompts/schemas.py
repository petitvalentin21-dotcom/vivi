from pydantic import BaseModel


class PromptListResponse(BaseModel):
    current_version: str
    versions: list[str]
    prompts: list[str]


class PromptContentResponse(BaseModel):
    name: str
    version: str
    content: str
    char_count: int
