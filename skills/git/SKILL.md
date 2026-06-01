## Stop tracking a file
```bash
git rm --cached <file>
```
This will remove the file from the index, but keep it in the working directory.

May need to add the `<file>` to the `.gitignore` file.

## Conventional Commits

Use this in commit messages and branch names.

* feat: -> new feature
* fix: -> bug fix
* docs: -> documentation
* refactor: -> code restructuring without changing behavior
* test: -> tests
* chore: -> maintenance tasks
