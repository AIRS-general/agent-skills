## Circular imports in SQLAlchemy models

Use string-based relationships, this works in runtime.
```py
user = relationship("User")
```

If using type hints, need to use `TYPE_CHECKING` to avoid circular imports. This is only used in type checking.
```py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import User
```

## SQLAlchemy: `relationship("Account")` cannot resolve model name

### Symptom
- App fails at startup (or on first import of models) with a mapper configuration error.

### Error
```
sqlalchemy.exc.InvalidRequestError: When initializing mapper Mapper[Training(trainings)], expression 'Account' failed to locate a name ('Account'). If this is a class name, consider adding this relationship() to the <class 'app.db.models.training.Training'> class after both dependent classes have been defined.
```

### Context
- Two SQLAlchemy models, `Training` and `Account`, live in separate modules.
- `Training` declares a relationship using a string: `relationship("Account")`.

### Root cause
SQLAlchemy configures mappers when modules are imported. If `Training` is imported before `Account` is imported/registered with the declarative registry, the string `"Account"` cannot be resolved yet.

### Fix
1. Create a real models package initializer that imports/registers models up front: `app/db/models/__init__.py`
   - Ensure it imports `Account` and `Training` (and any other models referenced by string relationships).
   - Then `import app.db.models` early so the registry is populated deterministically.
   ```py
   from app.db.models.account import Account
    from app.db.models.training import Algorithm, Preprocessing, Training

    __all__ = [
        "Account",
        "Training",
    ]
   ```
2. Ensure models load early in the app startup path (commonly where DB/session dependencies are created), e.g. `app/api/deps.py` or the app factory.
```py
def _load_models() -> None:
    __import__("app.db.models")


_load_models()
```

### Verification
- Importing any model module should not error:
  - `python -c "import app.db.models"`
  - `python -c "import app.db.models.training"`
- Starting the app should no longer fail during mapper configuration.
