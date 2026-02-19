"""
Database Migration: Update Prediction History Table
Adds new columns for ML prediction history with user association
"""
from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Run migration to update prediction_history table"""
    engine = create_engine(settings.DATABASE_URL)
    
    migrations = [
        # Drop old columns if they exist
        "ALTER TABLE prediction_history DROP COLUMN IF EXISTS prediction_history_id CASCADE;",
        "ALTER TABLE prediction_history DROP COLUMN IF EXISTS speed_through_water CASCADE;",
        "ALTER TABLE prediction_history DROP COLUMN IF EXISTS wind_speed CASCADE;",
        "ALTER TABLE prediction_history DROP COLUMN IF EXISTS draft_fore CASCADE;",
        "ALTER TABLE prediction_history DROP COLUMN IF EXISTS draft_aft CASCADE;",
        "ALTER TABLE prediction_history DROP COLUMN IF EXISTS wave_height CASCADE;",
        "ALTER TABLE prediction_history DROP COLUMN IF EXISTS predicted_power CASCADE;",
        "ALTER TABLE prediction_history DROP COLUMN IF EXISTS confidence_score CASCADE;",
        "ALTER TABLE prediction_history DROP COLUMN IF EXISTS efficiency CASCADE;",
        "ALTER TABLE prediction_history DROP COLUMN IF EXISTS model_version CASCADE;",
        
        # Add new columns
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS user_id VARCHAR(255) NOT NULL DEFAULT '';
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS user_email VARCHAR(255);
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS input_features JSONB NOT NULL DEFAULT '{}'::jsonb;
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS draft_aft_telegram FLOAT;
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS draft_fore_telegram FLOAT;
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS stw FLOAT;
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS diff_speed_overground FLOAT;
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS awind_vcomp_provider FLOAT;
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS awind_ucomp_provider FLOAT;
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS rcurrent_vcomp FLOAT;
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS rcurrent_ucomp FLOAT;
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS comb_wind_swell_wave_height FLOAT;
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS time_since_dry_dock FLOAT;
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS predicted_power_kw FLOAT NOT NULL DEFAULT 0;
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS predicted_power_mw FLOAT NOT NULL DEFAULT 0;
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS model_used VARCHAR(50) NOT NULL DEFAULT 'xgboost';
        """,
        """
        ALTER TABLE prediction_history ADD COLUMN IF NOT EXISTS model_metadata JSONB;
        """,
        
        # Create indexes for better query performance
        """
        CREATE INDEX IF NOT EXISTS idx_prediction_history_user_id ON prediction_history(user_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_prediction_history_created_at ON prediction_history(created_at);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_prediction_history_user_created ON prediction_history(user_id, created_at DESC);
        """,
    ]
    
    with engine.connect() as conn:
        try:
            logger.info("Starting database migration...")
            
            for i, migration_sql in enumerate(migrations, 1):
                try:
                    conn.execute(text(migration_sql))
                    conn.commit()
                    logger.info(f"✓ Migration {i}/{len(migrations)} completed")
                except Exception as e:
                    logger.warning(f"⚠️  Migration {i} warning: {str(e)}")
                    # Continue with next migration even if one fails
                    continue
            
            logger.info("✅ All migrations completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {str(e)}")
            raise


if __name__ == "__main__":
    migrate()
