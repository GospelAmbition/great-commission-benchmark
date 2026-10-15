"""Persist model descriptions from OpenRouter, repairing abbreviated API text."""
import asyncio

from sqlalchemy.orm import Session

from app.db.models.model import Model
from app.services.openrouter import OpenRouterClient
from app.services.model_description import abbreviated_prefix, fetch_full_description, is_abbreviated, MAX_DESCRIPTION_BYTES, continues_description_prefix


async def _update_description(model: Model, model_info: dict, refresh: bool = False) -> bool:
    description = model_info.get("description")
    if not isinstance(description, str) or not description.strip() or len(description.encode("utf-8")) > MAX_DESCRIPTION_BYTES:
        return False
    prefix = abbreviated_prefix(description)
    if prefix:
        existing = model.description or ""
        # A refresh of an abbreviated API value must not destroy its full continuation.
        if not refresh and continues_description_prefix(existing, prefix) and not is_abbreviated(existing):
            return False
        canonical_model_id = model_info.get("id") or model.model_id
        full = await fetch_full_description(canonical_model_id, description)
        if full:
            description = full
        elif existing and not is_abbreviated(existing):
            return False
    if model.description == description:
        return False
    model.description = description
    return True


async def sync_model_description(db: Session, model: Model, commit: bool = True) -> bool:
    """Refresh one model; optional page enrichment is bounded and best-effort."""
    openrouter = OpenRouterClient()
    try:
        async with asyncio.timeout(10):
            model_info = await openrouter.get_model_info(model.model_id)
        if model_info and await _update_description(model, model_info, refresh=True):
            if commit:
                db.commit()
            return True
    except Exception:
        # Metadata synchronization must not prevent a benchmark upload.
        pass
    finally:
        await openrouter.close()
    return False


async def sync_all_model_descriptions(db: Session, all_models: bool = False, offset: int = 0, limit: int = 10) -> int:
    """Repair missing/abbreviated descriptions with one catalog request per run."""
    if offset < 0 or not 1 <= limit <= 10:
        raise ValueError("Description batch requires offset >= 0 and limit between 1 and 10")
    models = db.query(Model).order_by(Model.model_id).offset(offset).limit(limit).all()
    targets = [model for model in models if all_models or not model.description or is_abbreviated(model.description)]
    if not targets:
        return 0
    updated_count = 0
    openrouter = OpenRouterClient()
    try:
        async with asyncio.timeout(10):
            entries = await openrouter.list_models()
        catalog = {entry["id"]: entry for entry in entries if entry.get("id")}
        # Sequential enrichment prevents a backfill from flooding public model pages.
        for model in targets:
            model_info = catalog.get(model.model_id)
            if not model_info:
                model_info = await openrouter.get_model_details(model.model_id)
            if not model_info and is_abbreviated(model.description):
                model_info = {"description": model.description}
            if model_info:
                try:
                    if await _update_description(model, model_info, refresh=all_models):
                        updated_count += 1
                except Exception:
                    continue
        if updated_count:
            db.commit()
    finally:
        await openrouter.close()
    return updated_count
