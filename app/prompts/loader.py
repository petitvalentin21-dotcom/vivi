from pathlib import Path

PROMPTS_DIR = Path(__file__).parent
DEFAULT_VERSION = "v1"


def load_prompt(name: str, version: str = DEFAULT_VERSION) -> str:
    """Charge le contenu d'un prompt Markdown. Lève FileNotFoundError si absent."""
    path = PROMPTS_DIR / version / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {version}/{name}")
    return path.read_text(encoding="utf-8")


def list_prompts(version: str = DEFAULT_VERSION) -> list[str]:
    """Liste les noms de prompts disponibles pour une version (sans extension)."""
    version_dir = PROMPTS_DIR / version
    if not version_dir.exists() or not version_dir.is_dir():
        return []
    return sorted(p.stem for p in version_dir.glob("*.md"))


def list_versions() -> list[str]:
    """Liste les versions disponibles (sous-dossiers commençant par 'v')."""
    return sorted(
        d.name for d in PROMPTS_DIR.iterdir()
        if d.is_dir() and d.name.startswith("v")
    )
