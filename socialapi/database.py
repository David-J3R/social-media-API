import databases
import sqlalchemy

# Config from our folder pydantic configuration file
from socialapi.config import config

# Using Encode Databases for async database connections

# --- Create database schema and engine ---
# metadata object to hold our table definitions
metadata = sqlalchemy.MetaData()

post_table = sqlalchemy.Table(
    "post",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
    sqlalchemy.Column("image_url", sqlalchemy.String),
)

# Users table for authentication purposes
user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("confirmed", sqlalchemy.Boolean, default=False),
)

comment_table = sqlalchemy.Table(
    "comment",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("post.id"), nullable=False),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
)

like_table = sqlalchemy.Table(
    "likes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("post.id"), nullable=False),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
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
