# 🛠️ Development Environment

## Package Management & Environment Rules
**Absolute Rules (Fail‑Fast Enforcement):**
1. **Virtual Environment Required** — At least one detection method must confirm active venv before proceeding.
2. **No System Python** — Never execute scripts using system Python (`/usr/bin/python`).
3. **Python Version Match** — Active Python version must match `requires-python` in `pyproject.toml`. Fail if mismatch.
4. **Dependency Lock Enforcement** — Verify package availability against the relevant lock file before running code.
5. **Path Validation** — Never assume file or directory structure. Always verify before access.
6. **No Silent Assumptions** — Any unavoidable assumptions must be explicitly stated in output.



## Detecting Package Management Tool
- **uv** → `uv.lock` present
- **poetry** → `poetry.lock` present and `[tool.poetry]` in `pyproject.toml`
- **pip** → `requirements.txt` present
- **pipenv** → `Pipfile` present
- **conda** → `environment.yml` present
- Run `uv --version`
```bash
# Checkhing uv version
uv --version
# expected e.g. uv 0.7.21 (77c771c7f 2025-07-14)
```
If uv is not recognized as package management tool → **STOP*** and request clarification.

## Virtual Environment Detection
At least one of the following must succeed **before proceeding**:

1. **VIRTUAL_ENV Variable**
- Use operating system
```bash
echo $VIRTUAL_ENV
```
- Use Python
```python
import os
assert os.environ.get('VIRTUAL_ENV'), "No active virtual environment"
```

2. **Executable Path**
```bash
which python
# Expect: .venv/bin/python
```

3. **Python sys.prefix Check**
```python
import sys
assert sys.prefix != sys.base_prefix, "Python is not running in a venv"
```

4. **Directory Presence**
```bash
ls -la | grep -E ".venv"
```

5. **One‑liner Detection**
```bash
python -c "import sys; exit(0) if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else exit(1)"
```

If all checks fail → STOP immediately.

## Python Version Verification
- **Never** assume Python version
```python
import sys, tomllib
with open("pyproject.toml", "rb") as f:
    required = tomllib.load(f)["project"]["requires-python"]
assert sys.version.startswith(required.replace(">=", "")), f"Python version mismatch: required {required}, running {sys.version}"
```

## Self‑Audit Checklist (Mandatory)
Before executing Python code:
- [ ] Virtual environment detected by at least one method
- [ ] Python version matches `pyproject.toml`
- [ ] Dependency lock file exists and matches installed packages
- [ ] No assumptions about file structure or package availability
- [ ] All venv‑related assumptions stated explicitly

If any box unchecked → STOP and request corrective action.
