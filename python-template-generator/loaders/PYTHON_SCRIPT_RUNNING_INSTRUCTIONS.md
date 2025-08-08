# UsingUV Package Management
- This project uses UV for blazing-fast Python package and environment management.

## Adding a package
- **NEVER** UPDATE A DEPENDENCY DIRECTLY IN `PYPROJECT.toml`
- **ALWAYS** USE `uv add` to install a dependency
```bash
# Example of adding a dependency
uv add requests
```
- Installing a development dependency
```bash
# Example of adding a development dependency
uv add --dev pytest ruff mypy
```
- **ALWAYS** use `uv remove` for removing a package
```bash
# Example of removing a package
uv remove requests
```
## Running commands in the environment
- Runing python script
```bash
# Example of running a python script
uv run python script.py
```
- Running tests
```bash
# Example of running a test
uv run pytest
```
- Running a tool
```bash
# Example of running a tool
uv run ruff check .
```
- Installing a specific Python version
```bash
uv python install 3.12
```
### Bad vs Good script running examples
- **Bad** (silent assumption about Python and packages)
```bash
# Bad example of running python script
python script.py
```
```bash
# Bad example of running python script
cd path/to/some/distant/
uv run python script.py
```
```bash
# Bad example of running python script
uv run python path/to/some/distant/script.py
```

- **Good** (explicit, uv based)
```bash
# Good example of running a python script
uv run path/to/some/distant/script.py
```
