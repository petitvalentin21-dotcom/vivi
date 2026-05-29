from __future__ import annotations

import json
import uuid
from typing import Any, Optional

from app.meals.preferences.models import Preference
from app.meals.preferences.repository import PreferenceRepository
from app.meals.preferences.schemas import PreferenceCreate, PreferenceUpdate, PreferenceUpsert


class PreferenceService:
    def __init__(self, repository: PreferenceRepository) -> None:
        self.repository = repository

    # ------------------------------------------------------------------
    # Helpers encode / decode
    # ------------------------------------------------------------------

    def _encode(self, value: Any, type_valeur: str) -> str:
        if type_valeur == "string":
            return str(value)
        if type_valeur == "int":
            return str(int(value))
        if type_valeur == "float":
            return str(float(value))
        if type_valeur == "bool":
            return "true" if value else "false"
        if type_valeur in ("list", "dict"):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    def _decode(self, valeur: str, type_valeur: str) -> Any:
        if type_valeur == "string":
            return valeur
        if type_valeur == "int":
            return int(valeur)
        if type_valeur == "float":
            return float(valeur)
        if type_valeur == "bool":
            return valeur.lower() in {"true", "1", "yes", "oui", "on"}
        if type_valeur in ("list", "dict"):
            return json.loads(valeur)
        return valeur

    # ------------------------------------------------------------------
    # API publique — CRUD direct
    # ------------------------------------------------------------------

    def create(self, data: PreferenceCreate) -> Preference:
        return self.repository.create(
            cle=data.cle,
            valeur=data.valeur,
            type_valeur=data.type_valeur,
            categorie=data.categorie,
            notes=data.notes,
        )

    def get(self, preference_id: uuid.UUID) -> Preference | None:
        return self.repository.get(preference_id)

    def get_by_cle(self, cle: str) -> Preference | None:
        return self.repository.get_by_cle(cle)

    def list(self, categorie: Optional[str] = None) -> list[Preference]:
        return self.repository.list(categorie=categorie)

    def update(self, preference_id: uuid.UUID, data: PreferenceUpdate) -> Preference | None:
        return self.repository.update(preference_id, data)

    def upsert_by_cle(self, cle: str, data: PreferenceUpsert) -> Preference:
        return self.repository.upsert_by_cle(
            cle=cle,
            valeur=data.valeur,
            type_valeur=data.type_valeur,
            categorie=data.categorie,
            notes=data.notes,
        )

    def soft_delete(self, preference_id: uuid.UUID) -> bool:
        return self.repository.soft_delete(preference_id)

    # ------------------------------------------------------------------
    # API publique — accès typé (pour les autres modules et le LLM)
    # ------------------------------------------------------------------

    def get_value(self, cle: str, default: Any = None) -> Any:
        """Retourne la valeur décodée, ou default si absente ou illisible. Ne lève jamais."""
        pref = self.repository.get_by_cle(cle)
        if pref is None:
            return default
        try:
            return self._decode(pref.valeur, pref.type_valeur)
        except Exception:  # noqa: BLE001
            return default

    def set_value(self, cle: str, value: Any, type_valeur: str = "string", categorie: Optional[str] = None) -> Preference:
        """Upsert avec encodage automatique."""
        valeur = self._encode(value, type_valeur)
        return self.repository.upsert_by_cle(
            cle=cle,
            valeur=valeur,
            type_valeur=type_valeur,
            categorie=categorie,
        )

    def get_all_as_dict(self) -> dict[str, Any]:
        """Vue agrégée pour les outils LLM. Les clés dont le décodage échoue sont ignorées."""
        prefs = self.repository.list()
        result: dict[str, Any] = {}
        for pref in prefs:
            try:
                result[pref.cle] = self._decode(pref.valeur, pref.type_valeur)
            except Exception:  # noqa: BLE001
                pass
        return result
