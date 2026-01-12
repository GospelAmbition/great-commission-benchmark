"""
Service for syncing model metadata from OpenRouter.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.db.models.model import Model
from app.services.openrouter import OpenRouterClient


async def sync_model_description(db: Session, model: Model) -> bool:
    """
    Sync model description from OpenRouter API.
    
    Args:
        db: Database session
        model: Model instance to update
        
    Returns:
        True if description was updated, False otherwise
    """
    openrouter = OpenRouterClient()
    try:
        model_info = await openrouter.get_model_info(model.model_id)
        if model_info and model_info.get("description"):
            model.description = model_info.get("description")
            db.commit()
            return True
    except Exception:
        # Silently fail - description sync is optional
        pass
    finally:
        await openrouter.close()
    return False


async def sync_all_model_descriptions(db: Session) -> int:
    """
    Sync descriptions for all models that don't have one.
    
    Args:
        db: Database session
        
    Returns:
        Number of models updated
    """
    models_without_description = db.query(Model).filter(
        Model.description.is_(None)
    ).all()
    
    updated_count = 0
    openrouter = OpenRouterClient()
    try:
        for model in models_without_description:
            try:
                model_info = await openrouter.get_model_info(model.model_id)
                if model_info and model_info.get("description"):
                    model.description = model_info.get("description")
                    updated_count += 1
            except Exception:
                # Continue with next model if this one fails
                continue
        
        if updated_count > 0:
            db.commit()
    finally:
        await openrouter.close()
    
    return updated_count
