import databases
import sqlalchemy
from config import config

# Using Encode Databases for async database connections

# --- Create database schema and engine ---
metadata = sqlalchemy.MetaData()

post_table = sqlalchemy.Table(
    "post",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
)

comment_table = sqlalchemy.Table(
    "comment",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("post.id"), nullable=False),
)

engine = sqlalchemy.create_engine(
    # Use connect_args only for SQLite
    config.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

metadata.create_all(engine)

# --- Database module for connecting to the database ---
# using encode/databases for interacting with the database asynchronously
database = databases.Database(
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK
)
