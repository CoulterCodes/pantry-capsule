from logging.config import fileConfig
import sys
from pathlib import Path
import sqlalchemy as sa
from sqlalchemy import engine_from_config, pool
from alembic import op, context


# ----------------------------
# Ensure 'backend' root is on sys.path
# ----------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# ----------------------------
# Now safe to import app modules
# ----------------------------
from app.db import Base
from app import models  # ensures models are registered
from app.core.config import DATABASE_URL

# ----------------------------
# Alembic Config object
# ----------------------------
config = context.config

# overwrite URL from alembic.ini with app config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Logging
if config.config_file_name:
    fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata

# Revision identifiers
revision = "ADD_NUTRITION_COLUMNS"
down_revision = "01317beee1c2"
branch_labels = None
depends_on = None


def run_migrations_offline() -> None:
    """Run migrations without DBAPI."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a live connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

def upgrade():
    op.add_column('food_items', sa.Column('calories', sa.Integer(), nullable=True))
    op.add_column('food_items', sa.Column('protein', sa.Float(), nullable=True))
    op.add_column('food_items', sa.Column('carbs', sa.Float(), nullable=True))
    op.add_column('food_items', sa.Column('fat', sa.Float(), nullable=True))

def downgrade():
    op.drop_column('food_items', 'fat')
    op.drop_column('food_items', 'carbs')
    op.drop_column('food_items', 'protein')
    op.drop_column('food_items', 'calories')
