from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config import load_settings  # noqa: E402
from app.knowledge import load_markdown_notes, retrieve_lexical, split_into_chunks  # noqa: E402
from app.knowledge.sources import Source  # noqa: E402

Pertinence = Literal["bon", "acceptable", "bruite", "incomplet", "mauvais", "hors contexte correctement vide"]


@dataclass(frozen=True)
class AuditQuestion:
    id: str
    family: str
    question: str
    expected: str
    expected_paths: tuple[str, ...] = ()
    no_source_expected: bool = False


QUESTIONS: tuple[AuditQuestion, ...] = (
    AuditQuestion(
        id="P1",
        family="Produit / cadrage MVP",
        question="Quel est l'objectif du MVP VIVI ?",
        expected="Retrouver la note de cadrage produit avec objectif MVP et vision locale.",
        expected_paths=("00_product/VIVI_MVP_CADRAGE_v0.1.md",),
    ),
    AuditQuestion(
        id="P2",
        family="Produit / cadrage MVP",
        question="Qu'est-ce qui est hors scope du MVP VIVI ?",
        expected="Retrouver le cadrage produit et les exclusions MVP.",
        expected_paths=("00_product/VIVI_MVP_CADRAGE_v0.1.md",),
    ),
    AuditQuestion(
        id="P3",
        family="Produit / cadrage MVP",
        question="Quel est le statut de la release candidate locale ?",
        expected="Retrouver une source release candidate ou une trace qui mentionne le statut RC.",
        expected_paths=(),
    ),
    AuditQuestion(
        id="B1",
        family="Backend / API",
        question="Quels endpoints FastAPI existent pour health runtime chat et knowledge search ?",
        expected="Retrouver la spec backend avec les endpoints MVP.",
        expected_paths=("02_architecture/VIVI — Backend MVP Spec v0.1.md",),
    ),
    AuditQuestion(
        id="B2",
        family="Backend / API",
        question="A quoi sert GET /runtime/info ?",
        expected="Retrouver la section runtime info de la spec backend.",
        expected_paths=("02_architecture/VIVI — Backend MVP Spec v0.1.md",),
    ),
    AuditQuestion(
        id="B3",
        family="Backend / API",
        question="A quoi sert GET /knowledge/search ?",
        expected="Retrouver l'endpoint de debug RAG dans la spec backend.",
        expected_paths=("02_architecture/VIVI — Backend MVP Spec v0.1.md",),
    ),
    AuditQuestion(
        id="R1",
        family="RAG / Obsidian",
        question="Quel est le role du vault Obsidian dans le mode document ?",
        expected="Retrouver cadrage ou spec backend sur Obsidian, contexte documentaire et sources.",
        expected_paths=(
            "00_product/VIVI_MVP_CADRAGE_v0.1.md",
            "02_architecture/VIVI — Backend MVP Spec v0.1.md",
        ),
    ),
    AuditQuestion(
        id="R2",
        family="RAG / Obsidian",
        question="Quelles sont les limites du RAG lexical actuel ?",
        expected="Retrouver les limites lexicales, absence d'embeddings et vector DB.",
        expected_paths=(
            "00_product/VIVI_MVP_CADRAGE_v0.1.md",
            "02_architecture/VIVI — Backend MVP Spec v0.1.md",
        ),
    ),
    AuditQuestion(
        id="C1",
        family="Configuration locale",
        question="Comment configurer VIVI_API_KEY VIVI_LMSTUDIO_API_KEY et VIVI_KNOWLEDGE_VAULT_PATH ?",
        expected="Retrouver la spec backend ou le cadrage avec les variables d'environnement.",
        expected_paths=("02_architecture/VIVI — Backend MVP Spec v0.1.md",),
    ),
    AuditQuestion(
        id="U1",
        family="UX / IHM",
        question="Comment l'interface web affiche-t-elle la conversation les sources et le runtime status ?",
        expected="Retrouver cadrage produit sur interface, sources visibles et runtime status.",
        expected_paths=("00_product/VIVI_MVP_CADRAGE_v0.1.md",),
    ),
    AuditQuestion(
        id="H1",
        family="Hors contexte",
        question="xylophrax qztnombr wugplest",
        expected="Ne retourner aucune source forte.",
        no_source_expected=True,
    ),
    AuditQuestion(
        id="A1",
        family="Ambigue",
        question="MVP",
        expected="Retourner un petit nombre de sources produit/backend raisonnables.",
        expected_paths=("00_product/VIVI_MVP_CADRAGE_v0.1.md",),
    ),
    AuditQuestion(
        id="A2",
        family="Ambigue",
        question="sources",
        expected="Retourner des notes liees aux sources visibles ou au RAG.",
        expected_paths=(),
    ),
    AuditQuestion(
        id="A3",
        family="Ambigue",
        question="runtime",
        expected="Retourner des notes backend ou produit mentionnant runtime status.",
        expected_paths=("02_architecture/VIVI — Backend MVP Spec v0.1.md",),
    ),
    AuditQuestion(
        id="A4",
        family="Ambigue",
        question="document",
        expected="Retourner des notes sur mode document, RAG ou cadrage.",
        expected_paths=(),
    ),
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit deterministic du RAG lexical sur le vault reel VIVI.")
    parser.add_argument("--vault", default="", help="Chemin du vault. Defaut: settings VIVI_KNOWLEDGE_VAULT_PATH.")
    parser.add_argument("--top-k", type=int, default=5, help="Nombre maximum de sources par question.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", default="", help="Fichier de sortie optionnel. Defaut: stdout seulement.")
    args = parser.parse_args()

    settings = load_settings()
    vault_path = args.vault.strip() or settings.knowledge_vault_path
    exists, notes, error = load_markdown_notes(vault_path)
    if not exists:
        print(error or f"Vault not found: {vault_path}", file=sys.stderr)
        return 1

    chunks = split_into_chunks(notes)
    rows = []
    for question in QUESTIONS:
        sources = retrieve_lexical(question.question, chunks, args.top_k)
        pertinence, problem, decision = classify(question, sources)
        rows.append(
            {
                "id": question.id,
                "family": question.family,
                "question": question.question,
                "expected": question.expected,
                "sources": [source_to_dict(source) for source in sources],
                "distinct_paths_count": len({source.path for source in sources}),
                "low_confidence_count": sum(1 for source in sources if source.is_low_confidence),
                "score_max": max((source.score for source in sources), default=0),
                "pertinence": pertinence,
                "problem": problem,
                "decision": decision,
            }
        )

    payload = {
        "vault_path": vault_path,
        "notes_count": len(notes),
        "chunks_count": len(chunks),
        "top_k": args.top_k,
        "questions_count": len(QUESTIONS),
        "rows": rows,
    }
    rendered = render_json(payload) if args.format == "json" else render_markdown(payload)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)

    return 0


def classify(question: AuditQuestion, sources: list[Source]) -> tuple[Pertinence, str, str]:
    paths = {source.path for source in sources}
    expected = set(question.expected_paths)

    if question.no_source_expected:
        if not sources:
            return "hors contexte correctement vide", "Aucun bruit observe.", "Conserver comme garde-fou."
        return "bruite", "Le RAG retourne des sources pour une requete sans recouvrement attendu.", "Prioriser un seuil minimal."

    if not sources:
        return "incomplet", "Aucune source retournee.", "Auditer l'indexation et les termes de requete."

    if expected and expected.issubset(paths):
        extra_count = len(paths - expected)
        if extra_count <= 2:
            return "bon", "Sources attendues presentes.", "Conserver comme baseline."
        return "acceptable", "Sources attendues presentes avec bruit additionnel.", "Surveiller le bruit."

    if expected and expected.intersection(paths):
        return "acceptable", "Une partie des sources attendues est presente.", "Ameliorer le rappel cible."

    if expected:
        return "incomplet", "Les chemins attendus ne sont pas retournes.", "Prioriser synonymes, titres ou chunking."

    if sources:
        return "acceptable", "Sources retournees, evaluation manuelle requise.", "Verifier qualitativement."

    return "mauvais", "Cas non couvert.", "Revoir le cas d'audit."


def source_to_dict(source: Source) -> dict:
    return {
        "path": source.path,
        "title": source.title,
        "section": source.section,
        "score": source.score,
        "confidence_label": source.confidence_label,
        "is_low_confidence": source.is_low_confidence,
        "excerpt": " ".join(source.excerpt.split()),
    }


def render_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_markdown(payload: dict) -> str:
    lines = [
        "# Audit RAG sur vault réel - résultats bruts",
        "",
        f"- Vault: `{payload['vault_path']}`",
        f"- Notes indexées: {payload['notes_count']}",
        f"- Chunks: {payload['chunks_count']}",
        f"- Questions: {payload['questions_count']}",
        f"- Top K: {payload['top_k']}",
        "",
        "| ID | Famille | Question | Sources retournées | Documents distincts | Sources faibles | Score max | Pertinence | Problème observé | Décision |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        sources = "<br>".join(
            f"{idx}. `{source['path']}` ({source['score']})" for idx, source in enumerate(row["sources"], start=1)
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_cell(row["id"]),
                    escape_cell(row["family"]),
                    escape_cell(row["question"]),
                    escape_cell(sources or "Aucune"),
                    str(row["distinct_paths_count"]),
                    str(row["low_confidence_count"]),
                    str(row["score_max"]),
                    escape_cell(row["pertinence"]),
                    escape_cell(row["problem"]),
                    escape_cell(row["decision"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Détails des extraits", ""])
    for row in payload["rows"]:
        lines.append(f"### {row['id']} - {row['question']}")
        lines.append("")
        if not row["sources"]:
            lines.append("- Aucune source retournée.")
            lines.append("")
            continue
        for idx, source in enumerate(row["sources"], start=1):
            lines.append(f"- Source {idx}: `{source['path']}`")
            lines.append(f"  - Score: {source['score']}")
            lines.append(f"  - Confiance: {source['confidence_label']}")
            lines.append(f"  - Section: {source['section']}")
            lines.append(f"  - Extrait: {source['excerpt']}")
        lines.append("")

    return "\n".join(lines)


def escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
