# Database with SQLAlchemy and Alembic

- Alembic for database migrations
- SQLAlchemy for database operations

## SQLAlchemy Models

1. Define a `BaseModel` class that will be used as the base for all your database models. Its `metadata` contains the common columns and relationships for your database schema.
```py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

2. Define your database models by creating subclasses of `BaseModel`.

```py
# user.py
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100))
```

```py
# post.py
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(100))
    content: Mapped[str] = mapped_column(sa.Text)
```

3. Manage relationships between models.

One-to-Many
```py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import List

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)

    # an account can have many projects
    projects: Mapped[List["Project"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)

    # a project belongs to an account
    owner_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))

    owner: Mapped["Account"] = relationship(back_populates="projects")
```
* `ForeignKey` defines DB relationship
* relationship() defines Python-level navigation
* `back_populates` links both sides

One-to-One
```py
class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)

    profile: Mapped["Profile"] = relationship(
        back_populates="account",
        uselist=False  # indicate one-to-one relationship
    )


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        unique=True
    )

    account: Mapped["Account"] = relationship(back_populates="profile")
```

Many-to-many.
Example: users <--> Teams
```py
from sqlalchemy import Table, Column

association_table = Table(
    "account_team",
    Base.metadata,
    Column("account_id", ForeignKey("accounts.id"), primary_key=True),
    Column("team_id", ForeignKey("teams.id"), primary_key=True),
)
```

```py
class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)

    teams: Mapped[list["Team"]] = relationship(
        secondary=association_table,
        back_populates="accounts"
    )


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)

    accounts: Mapped[list["Account"]] = relationship(
        secondary=association_table,
        back_populates="teams"
    )
```

### Best practices

- Always define both sides. `back_populates`. Links both sides explicitly (recommended).
- Keep FK in child table. Parent should not store child IDs.
- `cascade`. controls deletion behavior. `cascade=all, delete-orphan` deletes orphans when parent is deleted.
- Use explicit association tables for many-to-many relationships.

## Migrate

1. Generate revision
```bash
alembic revision --autogenerate -m "Add teams table"
```

Undo revision file only. Delete the file (only if nothing depends on it).

Need to check the revision file. see if it looks good.
Look at the `upgrade()` and `downgrade()` functions see if they contain the correct statements.

Need to check the `env.py` file to import the models you defined.
```py
from app.db.base import Base
from app.models import Account, Team
```

2. Apply migration
`alembic upgrade head`

Undo migration: `alembic downgrade`

## Default Datetime

```py
import sqlalchemy as sa

class Model(BaseModel):
    __tablename__ = "models"

    id: Mapped[int] = mapped_column(primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )
```
use `sa.func.now()` to set default value to current time. it uses database time.

## Check constraints

Check constraints are often not reliably detected by autogenerate across DBs/dialects, and they may be skipped unless you explicitly add them (or configure comparison options).

```py
def upgrade():

    ...

    op.create_check_constraint(
        "ck_trainings_finished_at_gte_started_at",
        "trainings",
        "(finished_at IS NULL) OR (started_at IS NULL) OR (finished_at >= started_at)",
    )

def downgrade():
    ...
    op.drop_check_constraint(
        "ck_trainings_finished_at_gte_started_at",
        "trainings",
    )
```

## Alembic revision file

Can modify the file name and the first line of the docstring.

```py
"""add_check_constraint_on_training_start_finish

Revision ID: 0fa6b1933a70
Revises: 596b0314d42c
Create Date: 2026-04-28 11:25:57.285421

"""

# revision identifiers, used by Alembic.
revision: str = "0fa6b1933a70"
down_revision: str | Sequence[str] | None = "596b0314d42c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
```

What matters to Alembic:
- The revision value inside the file (e.g. revision = "0fa6b1933a70" )
- The down_revision value
- That Alembic can import the file and read those identifiers

Can modify the file name and docstring.

## Test database
