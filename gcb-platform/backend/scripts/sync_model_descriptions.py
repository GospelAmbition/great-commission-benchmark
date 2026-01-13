#!/usr/bin/env python3
"""
Sync model descriptions from OpenRouter API.

This script fetches descriptions for all models that don't have one yet
from the OpenRouter API and stores them in the database.

Usage:
    python scripts/sync_model_descriptions.py [--all]
    
Options:
    --all    Sync descriptions for all models, even if they already have one
"""
import sys
import os
import argparse
import asyncio

# Add the backend directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.models.model import Model
from app.services.model_sync import sync_all_model_descriptions, sync_model_description


async def sync_descriptions(all_models: bool = False):
    """Sync model descriptions from OpenRouter."""
    db: Session = SessionLocal()
    
    try:
        print("\n" + "=" * 60)
        print("Syncing model descriptions from OpenRouter")
        print("=" * 60)
        
        if all_models:
            print("\nSyncing ALL models (including those with existing descriptions)...\n")
            # Get all models
            models = db.query(Model).all()
            updated_count = 0
            
            for model in models:
                try:
                    result = await sync_model_description(db, model)
                    if result:
                        updated_count += 1
                        print(f"  ✓ Updated: {model.name} ({model.model_id})")
                    else:
                        print(f"  - No description available: {model.name} ({model.model_id})")
                except Exception as e:
                    print(f"  ✗ Error syncing {model.name}: {e}")
                    continue
            
            print(f"\n{'=' * 60}")
            print(f"Sync complete! Updated {updated_count} model(s)")
            print("=" * 60)
        else:
            print("\nSyncing only models without descriptions...\n")
            updated_count = await sync_all_model_descriptions(db)
            
            print(f"\n{'=' * 60}")
            print(f"Sync complete! Updated {updated_count} model(s)")
            print("=" * 60)
            
            # Show which models were updated
            if updated_count > 0:
                models_with_description = db.query(Model).filter(
                    Model.description.isnot(None)
                ).all()
                print(f"\nModels with descriptions: {len(models_with_description)}")
                for model in models_with_description[:10]:  # Show first 10
                    desc_preview = model.description[:60] + "..." if model.description and len(model.description) > 60 else model.description
                    print(f"  • {model.name}: {desc_preview}")
                if len(models_with_description) > 10:
                    print(f"  ... and {len(models_with_description) - 10} more")
        
    except Exception as e:
        print(f"\nError during sync: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Sync model descriptions from OpenRouter API"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Sync descriptions for all models, even if they already have one"
    )
    
    args = parser.parse_args()
    asyncio.run(sync_descriptions(all_models=args.all))


if __name__ == "__main__":
    main()
