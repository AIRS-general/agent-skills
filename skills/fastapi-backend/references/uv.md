# uv

`uv run ...` run commands in the **project’s managed environment**.
- Finds the project root (looks for pyproject.toml in the current dir or parents).
- Uses the environment uv manages for that project (creates/uses a .venv or its configured environment).
- Runs the command with that interpreter + installed deps.

Use `uv run ...` make sure the project venv is used. In case the project venv is not activated. 
