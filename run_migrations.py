from alembic.config import Config
from alembic import command
import os

# Adjust this path if alembic.ini is not at project root
alembic_cfg = Config("alembic.ini")

# Optional: Print current working directory for debug on Render
print("Running migrations from:", os.getcwd())

# Upgrade to latest migration
command.upgrade(alembic_cfg, "head")
